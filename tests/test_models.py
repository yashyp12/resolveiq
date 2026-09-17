import pytest

from backend.models import GeneratedRunbook, HistoricalIncident, Incident, Runbook


def test_incident_round_trips_to_dynamodb_item():
    incident = Incident("INC-001", "Demo outage", "The demo service is unavailable.", "fictional-demo", "api")
    assert Incident.from_item(incident.to_item()) == incident
    assert incident.to_item()["recordType"] == "incident"


def test_historical_incident_round_trips_to_dynamodb_item():
    record = HistoricalIncident(
        "HIST-001", "Past outage", "A fictional outage.", "fictional-demo", "network",
        ["timeout"], "Corrected the demo route.", ["network"], "api",
    )
    assert HistoricalIncident.from_item(record.to_item()) == record
    assert record.to_item()["recordType"] == "historical"


def test_runbook_rejects_invalid_record_type():
    with pytest.raises(ValueError, match="record_type"):
        Runbook("RB-001", "Title", "Problem", ["Precondition"], ["Step"], ["Verify"], ["Remediate"], ["Escalate"], "unknown")


def test_generated_runbook_defaults_to_generated_record_type():
    runbook = GeneratedRunbook("RB-GEN-001", "Generated", "Problem", ["Scope"], ["Check"], ["Verify"], ["Fix"], ["Escalate"])
    assert runbook.to_item()["recordType"] == "generated"
