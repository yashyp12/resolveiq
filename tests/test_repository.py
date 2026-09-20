from decimal import Decimal

from backend.models import Incident, Runbook
from backend.repository import ResolveIQRepository


class FakeTable:
    def __init__(self):
        self.items = {}
        self.put_calls = []

    def put_item(self, Item):
        self.put_calls.append(Item)
        key = Item.get("incidentId", Item.get("runbookId"))
        self.items[key] = Item

    def update_item(self, Key, UpdateExpression, ExpressionAttributeValues):
        key = next(iter(Key.values()))
        self.items[key]["analysis"] = ExpressionAttributeValues[":analysis"]

    def get_item(self, Key):
        key = next(iter(Key.values()))
        return {"Item": self.items[key]} if key in self.items else {}

    def scan(self, **kwargs):
        record_type = next(iter(kwargs["ExpressionAttributeValues"].values()))
        return {"Items": [item for item in self.items.values() if item.get("recordType") == record_type]}


def test_repository_saves_and_gets_incident_and_runbook():
    incidents, runbooks = FakeTable(), FakeTable()
    repository = ResolveIQRepository(incidents, runbooks)
    incident = Incident("INC-001", "Demo outage", "Unavailable.", "fictional-demo")
    runbook = Runbook("RB-GEN-001", "Generated guide", "A demo problem.", ["Scope"], ["Check"], ["Verify"], ["Fix"], ["Escalate"], "generated")

    repository.save_incident(incident)
    repository.save_runbook(runbook)

    assert repository.get_incident("INC-001") == incident
    assert repository.get_incident("INC-404") is None
    analysis = {"category": "network", "likelyCauses": [], "similarIncidents": [], "recommendedChecks": [], "uncertainty": "Unknown."}
    repository.save_incident_analysis("INC-001", analysis)
    assert repository.get_incident_analysis("INC-001") == analysis
    assert repository.get_runbook("RB-GEN-001") == runbook
    assert repository.get_runbook("RB-404") is None


def test_repository_converts_analysis_floats_for_dynamodb():
    incidents, runbooks = FakeTable(), FakeTable()
    repository = ResolveIQRepository(incidents, runbooks)
    repository.save_incident(Incident("INC-001", "Current", "Current issue.", "demo"))
    analysis = {
        "category": "network",
        "likelyCauses": [{"cause": "Connectivity", "confidence": 0.75, "evidenceIds": ["HIST-001"]}],
        "similarIncidents": ["HIST-001"],
        "recommendedChecks": ["Check connectivity."],
        "uncertainty": "Unknown.",
    }

    repository.save_incident_analysis("INC-001", analysis)

    assert incidents.items["INC-001"]["analysis"]["likelyCauses"][0]["confidence"] == Decimal("0.75")
    assert repository.get_incident_analysis("INC-001") == analysis


def test_repository_retrieves_only_requested_record_types():
    incidents, runbooks = FakeTable(), FakeTable()
    repository = ResolveIQRepository(incidents, runbooks)
    repository.save_incident(Incident("INC-001", "Current", "Current issue.", "demo"))
    incidents.put_item(Item={"incidentId": "HIST-001", "recordType": "historical", "title": "Past", "description": "Past issue.", "environment": "demo", "category": "network", "symptoms": [], "resolution": "Checked it.", "tags": []})
    repository.save_runbook(Runbook("RB-001", "Curated", "Problem", ["Scope"], ["Check"], ["Verify"], ["Fix"], ["Escalate"]))
    repository.save_runbook(Runbook("RB-GEN-001", "Generated", "Problem", ["Scope"], ["Check"], ["Verify"], ["Fix"], ["Escalate"], "generated"))

    assert [record.incident_id for record in repository.retrieve_historical_incidents()] == ["HIST-001"]
    assert [record.runbook_id for record in repository.retrieve_curated_runbooks()] == ["RB-001"]
