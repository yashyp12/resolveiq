import json

import pytest

from backend.analysis import MockBedrockAdapter
from backend.api import analyze_incident, generate_runbook, lambda_handler
from backend.repository import ResolveIQRepository
from backend.seed_data import curated_runbooks, historical_incidents


class FakeTable:
    def __init__(self):
        self.items = {}
        self.put_calls = []

    def put_item(self, Item):
        self.put_calls.append(Item)
        key = Item.get("incidentId", Item.get("runbookId"))
        self.items[key] = Item

    def get_item(self, Key):
        key = next(iter(Key.values()))
        return {"Item": self.items[key]} if key in self.items else {}

    def scan(self, **kwargs):
        record_type = next(iter(kwargs["ExpressionAttributeValues"].values()))
        return {"Items": [item for item in self.items.values() if item.get("recordType") == record_type]}


def repository_with_seed_data():
    incidents, runbooks = FakeTable(), FakeTable()
    repository = ResolveIQRepository(incidents, runbooks)
    for incident in historical_incidents():
        repository.save_historical_incident(incident)
    for runbook in curated_runbooks():
        repository.save_runbook(runbook)
    return repository, incidents


def valid_payload():
    return {
        "title": "Application server timeout",
        "description": "The application endpoint reports a connection timeout.",
        "environment": "fictional-demo",
        "service": "application-server",
        "error": "connection timeout",
    }


def test_valid_request_persists_and_returns_retrieved_analysis():
    repository, incidents = repository_with_seed_data()
    result = analyze_incident(valid_payload(), repository, id_factory=lambda: "INC-TEST")

    assert result["incident"]["incidentId"] == "INC-TEST"
    assert incidents.items["INC-TEST"]["title"] == valid_payload()["title"]
    assert result["evidence"]
    assert result["analysis"]["likelyCauses"][0]["evidenceIds"]


@pytest.mark.parametrize("field", ["title", "description", "environment"])
def test_missing_required_field_is_rejected_before_persistence(field):
    repository, incidents = repository_with_seed_data()
    payload = valid_payload()
    del payload[field]

    with pytest.raises(ValueError, match=field):
        analyze_incident(payload, repository)
    assert not any(key.startswith("INC-") for key in incidents.items)


@pytest.mark.parametrize("field", ["title", "description", "environment", "service", "error"])
def test_input_length_limits_are_enforced(field):
    repository, _ = repository_with_seed_data()
    payload = valid_payload()
    limits = {"title": 200, "description": 3000, "environment": 100, "service": 100, "error": 1000}
    payload[field] = "x" * (limits[field] + 1)

    with pytest.raises(ValueError, match="at most"):
        analyze_incident(payload, repository)


def test_empty_evidence_still_returns_valid_mock_analysis():
    repository = ResolveIQRepository(FakeTable(), FakeTable())
    result = analyze_incident(
        {"title": "Unfamiliar issue", "description": "No matching facts.", "environment": "demo"},
        repository,
        id_factory=lambda: "INC-EMPTY",
    )

    assert result["evidence"] == []
    assert result["analysis"]["likelyCauses"] == []
    assert result["analysis"]["similarIncidents"] == []


def test_invalid_evidence_id_is_rejected():
    repository, _ = repository_with_seed_data()

    class InvalidAdapter(MockBedrockAdapter):
        def analyze(self, incident, evidence):
            response = dict(super().analyze(incident, evidence))
            response["similarIncidents"] = ["NOT-RETRIEVED"]
            return response

    with pytest.raises(ValueError, match="unknown evidence ID"):
        analyze_incident(valid_payload(), repository, InvalidAdapter())


def test_runbook_requires_resolution_and_persists_successful_context():
    repository, incidents = repository_with_seed_data()
    incident = analyze_incident(valid_payload(), repository, id_factory=lambda: "INC-RUNBOOK")

    result = generate_runbook(
        incident["incident"]["incidentId"],
        {"resolution": "Reverted the fictional deployment and verified connectivity."},
        repository,
        id_factory=lambda: "RB-GENERATED",
    )

    assert result["runbook"]["runbookId"] == "RB-GENERATED"
    assert result["runbook"]["remediation"] == ["Reverted the fictional deployment and verified connectivity."]
    assert repository.get_runbook("RB-GENERATED") is not None


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_invalid_confidence_is_rejected(confidence):
    repository, _ = repository_with_seed_data()

    class InvalidAdapter(MockBedrockAdapter):
        def analyze(self, incident, evidence):
            response = dict(super().analyze(incident, evidence))
            response["likelyCauses"] = [{"cause": "bad", "confidence": confidence, "evidenceIds": []}]
            return response

    with pytest.raises(ValueError, match="confidence"):
        analyze_incident(valid_payload(), repository, InvalidAdapter())


def test_malformed_analysis_response_is_rejected():
    repository, _ = repository_with_seed_data()

    class InvalidAdapter:
        def analyze(self, incident, evidence):
            return {"category": "network"}

    with pytest.raises(ValueError, match="missing required fields"):
        analyze_incident(valid_payload(), repository, InvalidAdapter())


def test_lambda_handler_returns_consistent_validation_error():
    response = lambda_handler({"body": json.dumps({"title": "only title"})})
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["error"]["code"] == "VALIDATION_ERROR"
