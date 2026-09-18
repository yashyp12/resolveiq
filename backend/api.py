"""Application entry point for the ResolveIQ incident-analysis API."""

from datetime import datetime, timezone
import json
import os
from typing import Any, Callable, Mapping
from uuid import uuid4

from .analysis import AnalysisAdapter, MockBedrockAdapter, validate_analysis_response
from .models import Incident
from .repository import ResolveIQRepository
from .retrieval import RetrievalConfig, retrieve_evidence

REQUEST_LIMITS = {"title": 200, "description": 3000, "environment": 100, "service": 100, "error": 1000}
RETRIEVAL_CONFIG = RetrievalConfig(max_historical=5, max_runbooks=3)


def analyze_incident(
    payload: Mapping[str, Any],
    repository: ResolveIQRepository,
    adapter: AnalysisAdapter | None = None,
    id_factory: Callable[[], str] | None = None,
) -> dict[str, Any]:
    request = validate_request(payload)
    incident_id = id_factory() if id_factory else f"INC-{uuid4().hex}"
    incident = Incident(
        incident_id=incident_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        **request,
    )
    repository.save_incident(incident)

    historical = repository.retrieve_historical_incidents(limit=30)
    runbooks = repository.retrieve_curated_runbooks(limit=10)
    retrieved = retrieve_evidence(incident, historical, runbooks, RETRIEVAL_CONFIG)
    evidence = [*retrieved.historical_incidents, *retrieved.runbooks]
    raw_analysis = (adapter or MockBedrockAdapter()).analyze(incident, retrieved)
    analysis = validate_analysis_response(raw_analysis, evidence)
    return {
        "incident": _incident_response(incident),
        "evidence": [_evidence_response(item) for item in evidence],
        "analysis": analysis,
    }


def validate_request(payload: Mapping[str, Any]) -> dict[str, str | None]:
    if not isinstance(payload, Mapping):
        raise ValueError("request body must be an object")
    unknown = set(payload) - set(REQUEST_LIMITS)
    if unknown:
        raise ValueError(f"unknown fields: {', '.join(sorted(unknown))}")
    result: dict[str, str | None] = {}
    for name, maximum in REQUEST_LIMITS.items():
        value = payload.get(name)
        required = name in {"title", "description", "environment"}
        if value is None:
            if required:
                raise ValueError(f"{name} is required")
            result[name] = None
            continue
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")
        if len(value) > maximum:
            raise ValueError(f"{name} must be at most {maximum} characters")
        result[name] = value
    return result


def lambda_handler(event: Mapping[str, Any], context: Any = None) -> dict[str, Any]:
    try:
        body = event.get("body", event)
        if isinstance(body, str):
            body = json.loads(body)
        repository = _default_repository()
        result = analyze_incident(body, repository)
        return _response(200, result)
    except (ValueError, json.JSONDecodeError) as error:
        return _error_response(400, "VALIDATION_ERROR", str(error))
    except Exception as error:
        return _error_response(500, "INTERNAL_ERROR", str(error))


def _default_repository() -> ResolveIQRepository:
    import boto3

    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    return ResolveIQRepository(
        dynamodb.Table(os.getenv("INCIDENTS_TABLE_NAME", "ResolveIQ-Incidents")),
        dynamodb.Table(os.getenv("RUNBOOKS_TABLE_NAME", "ResolveIQ-Runbooks")),
    )


def _incident_response(incident: Incident) -> dict[str, Any]:
    return {key: value for key, value in incident.to_item().items() if key != "recordType"}


def _evidence_response(item: Any) -> dict[str, Any]:
    return {
        "evidenceId": item.evidence_id,
        "type": item.evidence_type,
        "title": item.title,
        "source": item.source,
        "summary": item.summary,
        "relevanceScore": item.relevance_score,
    }


def _response(status_code: int, body: Mapping[str, Any]) -> dict[str, Any]:
    return {"statusCode": status_code, "headers": {"Content-Type": "application/json"}, "body": json.dumps(body)}


def _error_response(status_code: int, code: str, message: str) -> dict[str, Any]:
    return _response(status_code, {"error": {"code": code, "message": message}})
