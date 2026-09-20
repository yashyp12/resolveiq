"""DynamoDB persistence operations for ResolveIQ records."""

from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from .models import HistoricalIncident, Incident, Runbook


class ResolveIQRepository:
    def __init__(self, incidents_table: Any, runbooks_table: Any) -> None:
        self._incidents = incidents_table
        self._runbooks = runbooks_table

    def save_incident(self, incident: Incident) -> None:
        self._incidents.put_item(Item=incident.to_item())

    def save_incident_analysis(self, incident_id: str, analysis: dict[str, Any]) -> None:
        self._incidents.update_item(
            Key={"incidentId": incident_id},
            UpdateExpression="SET analysis = :analysis",
            ExpressionAttributeValues={":analysis": _to_dynamodb_value(analysis)},
        )

    def get_incident_analysis(self, incident_id: str) -> dict[str, Any] | None:
        response = self._incidents.get_item(Key={"incidentId": incident_id})
        analysis = response.get("Item", {}).get("analysis")
        converted = _from_dynamodb_value(analysis)
        return converted if isinstance(converted, dict) else None

    def save_historical_incident(self, incident: HistoricalIncident) -> None:
        self._incidents.put_item(Item=incident.to_item())

    def get_incident(self, incident_id: str) -> Incident | None:
        response = self._incidents.get_item(Key={"incidentId": incident_id})
        item = response.get("Item")
        return Incident.from_item(item) if item else None

    def save_runbook(self, runbook: Runbook) -> None:
        self._runbooks.put_item(Item=runbook.to_item())

    def get_runbook(self, runbook_id: str) -> Runbook | None:
        response = self._runbooks.get_item(Key={"runbookId": runbook_id})
        item = response.get("Item")
        return Runbook.from_item(item) if item else None

    def retrieve_historical_incidents(self, limit: int = 30) -> list[HistoricalIncident]:
        items = self._scan_by_type(self._incidents, "historical", limit)
        return [HistoricalIncident.from_item(item) for item in items]

    def retrieve_curated_runbooks(self, limit: int = 10) -> list[Runbook]:
        items = self._scan_by_type(self._runbooks, "curated", limit)
        return [Runbook.from_item(item) for item in items]

    @staticmethod
    def _scan_by_type(table: Any, record_type: str, limit: int) -> list[dict[str, Any]]:
        if limit < 1:
            return []
        items: list[dict[str, Any]] = []
        scan_kwargs = {
            "FilterExpression": "#recordType = :recordType",
            "ExpressionAttributeNames": {"#recordType": "recordType"},
            "ExpressionAttributeValues": {":recordType": record_type},
            "Limit": limit,
        }
        while len(items) < limit:
            response = table.scan(**scan_kwargs)
            items.extend(response.get("Items", []))
            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break
            scan_kwargs["ExclusiveStartKey"] = last_key
        return sorted(items, key=lambda item: item.get("incidentId", item.get("runbookId", "")))[:limit]


def seed_repository(repository: ResolveIQRepository, historical: Iterable[HistoricalIncident], runbooks: Iterable[Runbook]) -> None:
    for record in historical:
        repository.save_historical_incident(record)
    for runbook in runbooks:
        repository.save_runbook(runbook)


def _to_dynamodb_value(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {key: _to_dynamodb_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_dynamodb_value(item) for item in value]
    return value


def _from_dynamodb_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: _from_dynamodb_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_from_dynamodb_value(item) for item in value]
    return value
