from backend.seed_data import curated_runbooks, historical_incidents


def test_seed_data_has_expected_demo_counts_and_record_types():
    incidents = historical_incidents()
    runbooks = curated_runbooks()

    assert 20 <= len(incidents) <= 30
    assert 5 <= len(runbooks) <= 10
    assert len({incident.incident_id for incident in incidents}) == len(incidents)
    assert len({runbook.runbook_id for runbook in runbooks}) == len(runbooks)
    assert all(runbook.record_type == "curated" for runbook in runbooks)
