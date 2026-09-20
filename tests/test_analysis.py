import json
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from backend.analysis import (
    BedrockAnalysisAdapter,
    BedrockAnalysisError,
    BedrockRunbookAdapter,
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


def runbook_response(**overrides):
    value = {
        "title": "Checkout API recovery",
        "problem": "Checkout requests returned HTTP 502.",
        "preconditions": ["Confirm approval."],
        "diagnosticSteps": ["Review deployment logs."],
        "verification": ["Confirm HTTP 200 responses."],
        "remediation": ["Revert the fictional deployment."],
        "escalation": ["Contact the service owner."],
    }
    value.update(overrides)
    return value


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


def test_bedrock_request_contains_facts_and_evidence_without_unsupported_output_config():
    client = FakeBedrockClient(converse_response(analysis_response()))
    adapter = BedrockAnalysisAdapter(client=client, model_id="demo-model")

    result = adapter.analyze(incident(), evidence())

    request = client.requests[0]
    assert request["modelId"] == "demo-model"
    assert request["system"][0]["text"]
    prompt = request["messages"][0]["content"][0]["text"]
    assert "CURRENT INCIDENT FACTS" in prompt
    assert "RETRIEVED EVIDENCE" in prompt
    assert "outputConfig" not in request
    assert result == analysis_response()


def test_bedrock_parses_fenced_json_response():
    value = analysis_response()
    response = {"output": {"message": {"content": [{"text": f"```json\n{json.dumps(value)}\n```"}]}}}
    adapter = BedrockAnalysisAdapter(client=FakeBedrockClient(response), model_id="demo-model")

    assert adapter.analyze(incident(), evidence()) == value


def test_bedrock_parses_raw_json_response():
    value = analysis_response()
    adapter = BedrockAnalysisAdapter(client=FakeBedrockClient(converse_response(value)), model_id="demo-model")

    assert adapter.analyze(incident(), evidence()) == value


def test_bedrock_parses_json_surrounded_by_harmless_text():
    value = analysis_response()
    response = {"output": {"message": {"content": [{"text": f"Here is the analysis:\n{json.dumps(value)}\nEnd of analysis."}]}}}
    adapter = BedrockAnalysisAdapter(client=FakeBedrockClient(response), model_id="demo-model")

    assert adapter.analyze(incident(), evidence()) == value


def test_malformed_bedrock_response_is_sanitized():
    response = {"output": {"message": {"content": [{"text": "not json"}]}}}
    adapter = BedrockAnalysisAdapter(client=FakeBedrockClient(response), model_id="demo-model")

    with pytest.raises(BedrockAnalysisError, match="invalid analysis response"):
        adapter.analyze(incident(), evidence())


def test_bedrock_runbook_adapter_returns_structured_runbook():
    value = runbook_response()
    client = FakeBedrockClient(converse_response(value))
    adapter = BedrockRunbookAdapter(client=client, model_id="demo-model")

    result = adapter.generate(
        incident(),
        "Reverted the fictional deployment.",
        evidence(),
        analysis_response(),
    )

    assert result == value
    assert client.requests[0]["modelId"] == "demo-model"
    assert "SUCCESSFUL RESOLUTION" in client.requests[0]["messages"][0]["content"][0]["text"]
    assert "VALIDATED ANALYSIS" in client.requests[0]["messages"][0]["content"][0]["text"]


def test_bedrock_runbook_prompt_requires_raw_json():
    client = FakeBedrockClient(converse_response(runbook_response()))
    adapter = BedrockRunbookAdapter(client=client, model_id="demo-model")

    adapter.generate(incident(), "Reverted the fictional deployment.", evidence())

    system_prompt = client.requests[0]["system"][0]["text"]
    assert "raw JSON object" in system_prompt
    assert "Markdown code fences" in system_prompt
    assert "diagnosticSteps" in system_prompt


def test_bedrock_runbook_parses_json_surrounded_by_harmless_text():
    value = runbook_response()
    response = {"output": {"message": {"content": [{"text": f"Runbook:\n{json.dumps(value)}\nDone."}]}}}
    adapter = BedrockRunbookAdapter(client=FakeBedrockClient(response), model_id="demo-model")

    assert adapter.generate(incident(), "Reverted the fictional deployment.", evidence()) == value


@pytest.mark.parametrize("field", ["preconditions", "diagnosticSteps", "verification", "remediation", "escalation"])
def test_bedrock_runbook_normalizes_non_empty_string_list_fields(field):
    value = runbook_response(**{field: "Review the fictional service."})
    adapter = BedrockRunbookAdapter(client=FakeBedrockClient(converse_response(value)), model_id="demo-model")

    result = adapter.generate(incident(), "Reverted the fictional deployment.", evidence())

    assert result[field] == ["Review the fictional service."]


@pytest.mark.parametrize("field_value", [123, {}, [["nested"]]])
def test_bedrock_runbook_rejects_invalid_list_field_types(field_value):
    value = runbook_response(preconditions=field_value)
    adapter = BedrockRunbookAdapter(client=FakeBedrockClient(converse_response(value)), model_id="demo-model")

    with pytest.raises(BedrockAnalysisError, match="invalid runbook response"):
        adapter.generate(incident(), "Reverted the fictional deployment.", evidence())


@pytest.mark.parametrize("field", ["title", "problem"])
def test_bedrock_runbook_adapter_normalizes_single_item_string_array(field):
    value = runbook_response(**{field: ["Checkout API recovery."]})
    adapter = BedrockRunbookAdapter(client=FakeBedrockClient(converse_response(value)), model_id="demo-model")

    assert adapter.generate(incident(), "Reverted the fictional deployment.", evidence())[field] == "Checkout API recovery."


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
