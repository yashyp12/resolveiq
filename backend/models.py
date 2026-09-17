"""Typed data models for the ResolveIQ DynamoDB records."""

from dataclasses import dataclass, field
from typing import Any, Mapping


def _required(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _string_list(values: list[str], field_name: str) -> list[str]:
    if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{field_name} must contain non-empty strings")
    return list(values)


@dataclass(frozen=True)
class Incident:
    incident_id: str
    title: str
    description: str
    environment: str
    service: str | None = None
    error: str | None = None
    created_at: str | None = None
    status: str = "new"

    def __post_init__(self) -> None:
        for name in ("incident_id", "title", "description", "environment", "status"):
            _required(getattr(self, name), name)
        if self.service is not None:
            _required(self.service, "service")
        if self.error is not None:
            _required(self.error, "error")

    def to_item(self) -> dict[str, Any]:
        item = {
            "incidentId": self.incident_id,
            "recordType": "incident",
            "title": self.title,
            "description": self.description,
            "environment": self.environment,
            "status": self.status,
        }
        for key, value in (("service", self.service), ("error", self.error), ("createdAt", self.created_at)):
            if value is not None:
                item[key] = value
        return item

    @classmethod
    def from_item(cls, item: Mapping[str, Any]) -> "Incident":
        return cls(
            incident_id=item["incidentId"],
            title=item["title"],
            description=item["description"],
            environment=item["environment"],
            service=item.get("service"),
            error=item.get("error"),
            created_at=item.get("createdAt"),
            status=item.get("status", "new"),
        )


@dataclass(frozen=True)
class HistoricalIncident:
    incident_id: str
    title: str
    description: str
    environment: str
    category: str
    symptoms: list[str] = field(default_factory=list)
    resolution: str = ""
    tags: list[str] = field(default_factory=list)
    service: str | None = None
    created_at: str | None = None

    def __post_init__(self) -> None:
        for name in ("incident_id", "title", "description", "environment", "category", "resolution"):
            _required(getattr(self, name), name)
        _string_list(self.symptoms, "symptoms")
        _string_list(self.tags, "tags")

    def to_item(self) -> dict[str, Any]:
        item = {
            "incidentId": self.incident_id,
            "recordType": "historical",
            "title": self.title,
            "description": self.description,
            "environment": self.environment,
            "category": self.category,
            "symptoms": list(self.symptoms),
            "resolution": self.resolution,
            "tags": list(self.tags),
        }
        if self.service is not None:
            item["service"] = self.service
        if self.created_at is not None:
            item["createdAt"] = self.created_at
        return item

    @classmethod
    def from_item(cls, item: Mapping[str, Any]) -> "HistoricalIncident":
        return cls(
            incident_id=item["incidentId"],
            title=item["title"],
            description=item["description"],
            environment=item["environment"],
            category=item["category"],
            symptoms=list(item.get("symptoms", [])),
            resolution=item.get("resolution", ""),
            tags=list(item.get("tags", [])),
            service=item.get("service"),
            created_at=item.get("createdAt"),
        )


@dataclass(frozen=True)
class Runbook:
    runbook_id: str
    title: str
    problem: str
    preconditions: list[str]
    diagnostic_steps: list[str]
    verification: list[str]
    remediation: list[str]
    escalation: list[str]
    record_type: str = "curated"
    created_at: str | None = None

    def __post_init__(self) -> None:
        for name in ("runbook_id", "title", "problem", "record_type"):
            _required(getattr(self, name), name)
        for name in ("preconditions", "diagnostic_steps", "verification", "remediation", "escalation"):
            _string_list(getattr(self, name), name)
        if self.record_type not in {"curated", "generated"}:
            raise ValueError("record_type must be curated or generated")

    def to_item(self) -> dict[str, Any]:
        item = {
            "runbookId": self.runbook_id,
            "recordType": self.record_type,
            "title": self.title,
            "problem": self.problem,
            "preconditions": list(self.preconditions),
            "diagnosticSteps": list(self.diagnostic_steps),
            "verification": list(self.verification),
            "remediation": list(self.remediation),
            "escalation": list(self.escalation),
        }
        if self.created_at is not None:
            item["createdAt"] = self.created_at
        return item

    @classmethod
    def from_item(cls, item: Mapping[str, Any]) -> "Runbook":
        return cls(
            runbook_id=item["runbookId"],
            title=item["title"],
            problem=item["problem"],
            preconditions=list(item.get("preconditions", [])),
            diagnostic_steps=list(item.get("diagnosticSteps", [])),
            verification=list(item.get("verification", [])),
            remediation=list(item.get("remediation", [])),
            escalation=list(item.get("escalation", [])),
            record_type=item.get("recordType", "curated"),
            created_at=item.get("createdAt"),
        )


@dataclass(frozen=True)
class GeneratedRunbook(Runbook):
    """A persisted runbook generated for a specific incident."""

    record_type: str = "generated"
