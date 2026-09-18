import json
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from backend.analysis import (
    BedrockAnalysisAdapter,
    BedrockAnalysisError,
    MockBedrockAdapter,
)
from backend.api import _analysis_adapter, analyze_incident
from backend.models import Incident
from backend.retrieval import RetrievalResult


def incident() -> Incident:
    return Incident(
        incident_id="INC-CURRENT",
        title="API timeout",
        description="The API endpoint returns a connection timeout.",
        environment="demo",
        service="api",
        error="connection timeout",
    )


def evidence() -> RetrievalResult:
    return RetrievalResult([], [])


def analysis_response() -> dict:
    return {
        "category": "network",
        "likelyCauses": [],
        "similarIncidents": [],
        "recommendedChecks": ["Check connectivity."],
        "uncertainty": "The root cause is not confirmed.",
    }


class FakeBedrockClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.requests = []

    def converse(self, **request):
        self.requests.append(request)
        if self.error:
            raise self.error
        return self.response


def converse_response(value):
    return {"output": {"message": {"content": [{"text": json.dumps(value)}]}}}


def test_mock_provider_is_selected_by_default(monkeypatch):
    monkeypatch.delenv("ANALYSIS_PROVIDER", raising=False)
    assert isinstance(_analysis_adapter(), MockBedrockAdapter)


def test_bedrock_provider_is_selected(monkeypatch):
    monkeypatch.setenv("ANALYSIS_PROVIDER", "bedrock")
    monkeypatch.setenv("BEDROCK_MODEL_ID", "demo-model")
    fake_client = FakeBedrockClient()
    with patch("backend.analysis.boto3.client", return_value=fake_client):
        adapter = _analysis_adapter()
    assert isinstance(adapter, BedrockAnalysisAdapter)
    assert adapter.model_id == "demo-model"


def test_bedrock_provider_requires_model_id(monkeypatch):
    monkeypatch.setenv("ANALYSIS_PROVIDER", "bedrock")
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)
    with pytest.raises(ValueError, match="BEDROCK_MODEL_ID"):
        _analysis_adapter()


def test_bedrock_request_contains_facts_evidence_and_structured_output():
    client = FakeBedrockClient(converse_response(analysis_response()))
    adapter = BedrockAnalysisAdapter(client=client, model_id="demo-model")

    result = adapter.analyze(incident(), evidence())

    request = client.requests[0]
    assert request["modelId"] == "demo-model"
    assert request["system"][0]["text"]
    prompt = request["messages"][0]["content"][0]["text"]
    assert "CURRENT INCIDENT FACTS" in prompt
    assert "RETRIEVED EVIDENCE" in prompt
    assert request["outputConfig"]["textFormat"]["type"] == "json_schema"
    assert result == analysis_response()


def test_bedrock_parses_fenced_json_response():
    value = analysis_response()
    response = {"output": {"message": {"content": [{"text": f"```json\n{json.dumps(value)}\n```"}]}}}
    adapter = BedrockAnalysisAdapter(client=FakeBedrockClient(response), model_id="demo-model")

    assert adapter.analyze(incident(), evidence()) == value


def test_malformed_bedrock_response_is_sanitized():
    response = {"output": {"message": {"content": [{"text": "not json"}]}}}
    adapter = BedrockAnalysisAdapter(client=FakeBedrockClient(response), model_id="demo-model")

    with pytest.raises(BedrockAnalysisError, match="invalid analysis response"):
        adapter.analyze(incident(), evidence())


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("AccessDeniedException", "access was denied"),
        ("ThrottlingException", "temporarily throttled"),
        ("ServiceUnavailableException", "service returned an error"),
    ],
)
def test_bedrock_service_failures_are_sanitized(code, message):
    error = ClientError({"Error": {"Code": code, "Message": "sensitive details"}}, "Converse")
    adapter = BedrockAnalysisAdapter(client=FakeBedrockClient(error=error), model_id="demo-model")

    with pytest.raises(BedrockAnalysisError, match=message):
        adapter.analyze(incident(), evidence())


def test_validation_rejects_bedrock_invalid_evidence_id():
    value = analysis_response()
    value["similarIncidents"] = ["NOT-RETRIEVED"]
    adapter = BedrockAnalysisAdapter(
        client=FakeBedrockClient(converse_response(value)),
        model_id="demo-model",
    )
    with pytest.raises(ValueError, match="unknown evidence ID"):
        analyze_incident(
            {
                "title": "API timeout",
                "description": "The API endpoint returns a connection timeout.",
                "environment": "demo",
            },
            _empty_repository(),
            adapter,
            id_factory=lambda: "INC-BEDROCK",
        )


def test_validation_rejects_bedrock_invalid_confidence():
    value = analysis_response()
    value["likelyCauses"] = [{"cause": "Unsupported", "confidence": 1.1, "evidenceIds": []}]
    adapter = BedrockAnalysisAdapter(
        client=FakeBedrockClient(converse_response(value)),
        model_id="demo-model",
    )
    with pytest.raises(ValueError, match="confidence"):
        analyze_incident(
            {
                "title": "API timeout",
                "description": "The API endpoint returns a connection timeout.",
                "environment": "demo",
                "service": "api",
                "error": "connection timeout",
            },
            _empty_repository(),
            adapter,
            id_factory=lambda: "INC-BEDROCK",
        )


def _empty_repository():
    from backend.repository import ResolveIQRepository

    class EmptyTable:
        def put_item(self, Item):
            return None

        def scan(self, **kwargs):
            return {"Items": []}

    return ResolveIQRepository(EmptyTable(), EmptyTable())
