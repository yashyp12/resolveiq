from backend.models import HistoricalIncident, Incident, Runbook
from backend.retrieval import retrieve_evidence


def incident(**overrides):
    values = {
        "incident_id": "INC-CURRENT",
        "title": "API gateway timeout",
        "description": "The API gateway reports a connection timeout.",
        "environment": "demo",
        "service": "api-gateway",
        "error": "connection timeout",
    }
    values.update(overrides)
    return Incident(**values)


def historical(incident_id, **overrides):
    values = {
        "incident_id": incident_id,
        "title": "API gateway timeout",
        "description": "A connection timeout affected the API gateway.",
        "environment": "demo",
        "category": "network",
        "symptoms": ["timeout"],
        "resolution": "Checked the gateway route.",
        "tags": ["timeout"],
        "service": "api-gateway",
    }
    values.update(overrides)
    return HistoricalIncident(**values)


def runbook(runbook_id, **overrides):
    values = {
        "runbook_id": runbook_id,
        "title": "API gateway timeout troubleshooting",
        "problem": "Diagnose API gateway connection timeout.",
        "preconditions": ["Confirm the affected gateway."],
        "diagnostic_steps": ["Check connectivity."],
        "verification": ["Confirm the endpoint responds."],
        "remediation": ["Apply an approved fix."],
        "escalation": ["Escalate if unresolved."],
    }
    values.update(overrides)
    return Runbook(**values)


def test_service_matching_ranks_a_matching_historical_incident():
    result = retrieve_evidence(
        incident(),
        [historical("HIST-MATCH"), historical("HIST-OTHER", service="worker")],
        [],
    )

    assert result.historical_incidents[0].evidence_id == "HIST-MATCH"
    assert result.historical_incidents[0].score_breakdown["service"] == 3
    assert result.historical_incidents[0].relevance_score > result.historical_incidents[1].relevance_score


def test_keyword_tag_and_symptom_matching_are_explainable():
    current = incident(
        title="Cache saturation",
        description="Cache requests fail with timeout",
        error="cache timeout",
    )
    candidate = historical(
        "HIST-KEYWORDS",
        title="Cache timeout",
        description="Cache requests fail",
        symptoms=["timeout"],
        tags=["cache"],
        service=None,
    )
    candidate = {**candidate.__dict__, "error": "cache timeout"}
    current_dict = {**current.__dict__, "tags": ["cache"], "symptoms": ["timeout"]}

    result = retrieve_evidence(current_dict, [candidate], [])

    breakdown = result.historical_incidents[0].score_breakdown
    assert breakdown["tags"] == 2
    assert breakdown["symptoms"] == 2
    assert breakdown["text_tokens"] >= 1
    assert breakdown["error_tokens"] >= 1


def test_runbook_title_and_problem_overlap_is_retrieved():
    result = retrieve_evidence(incident(), [], [runbook("RB-API")])

    assert [item.evidence_id for item in result.runbooks] == ["RB-API"]
    assert result.runbooks[0].score_breakdown["title_problem_tokens"] > 0


def test_ordering_is_score_descending_then_id_and_limits_are_bounded():
    candidates = [
        historical(f"HIST-{index:02d}", title="API gateway timeout")
        for index in range(7, 0, -1)
    ]
    result = retrieve_evidence(incident(), candidates, [runbook(f"RB-{index:02d}") for index in range(5, 0, -1)])

    assert len(result.historical_incidents) == 5
    assert len(result.runbooks) == 3
    assert [item.evidence_id for item in result.historical_incidents] == [
        "HIST-01",
        "HIST-02",
        "HIST-03",
        "HIST-04",
        "HIST-05",
    ]
    assert [item.evidence_id for item in result.runbooks] == ["RB-01", "RB-02", "RB-03"]


def test_empty_and_no_match_inputs_return_empty_results():
    result = retrieve_evidence(incident(), [], [runbook("RB-UNRELATED", title="Database backup", problem="Backup failure")])

    assert result.historical_incidents == []
    assert result.runbooks == []


def test_current_incident_is_excluded_and_duplicate_ids_are_collapsed():
    result = retrieve_evidence(
        incident(),
        [
            historical("INC-CURRENT"),
            historical("HIST-DUP", title="API timeout"),
            historical("HIST-DUP", title="API gateway timeout"),
        ],
        [],
    )

    assert [item.evidence_id for item in result.historical_incidents] == ["HIST-DUP"]


def test_duplicate_ids_across_evidence_types_are_returned_only_once():
    result = retrieve_evidence(
        incident(),
        [historical("SHARED-ID")],
        [runbook("SHARED-ID")],
    )

    evidence_ids = [item.evidence_id for item in result.historical_incidents + result.runbooks]
    assert evidence_ids == ["SHARED-ID"]
