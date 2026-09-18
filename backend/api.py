"""Application entry point for the ResolveIQ incident-analysis API."""

from datetime import datetime, timezone
import base64
import json
import logging
import os
from typing import Any, Callable, Mapping
from uuid import uuid4

from .analysis import (
    AnalysisAdapter,
    BedrockAnalysisAdapter,
    BedrockAnalysisError,
    MockBedrockAdapter,
    validate_analysis_response,
)
from .models import GeneratedRunbook, Incident
from .repository import ResolveIQRepository
from .retrieval import RetrievalConfig, retrieve_evidence

REQUEST_LIMITS = {"title": 200, "description": 3000, "environment": 100, "service": 100, "error": 1000}
RETRIEVAL_CONFIG = RetrievalConfig(max_historical=5, max_runbooks=3)
LOGGER = logging.getLogger(__name__)


def analyze_incident(
    payload: Mapping[str, Any],
    repository: ResolveIQRepository,
    adapter: AnalysisAdapter | None = None,
    id_factory: Callable[[], str] | None = None,
) -> dict[str, Any]:
    request = validate_request(payload)
    selected_adapter = adapter or _analysis_adapter()
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
    raw_analysis = selected_adapter.analyze(incident, retrieved)
    analysis = validate_analysis_response(raw_analysis, evidence)
    return {
        "incident": _incident_response(incident),
        "evidence": [_evidence_response(item) for item in evidence],
        "analysis": analysis,
    }


def generate_runbook(
    incident_id: str,
    payload: Mapping[str, Any],
    repository: ResolveIQRepository,
    id_factory: Callable[[], str] | None = None,
) -> dict[str, Any]:
    resolution = payload.get("resolution") if isinstance(payload, Mapping) else None
    if not isinstance(resolution, str) or not resolution.strip():
        raise ValueError("resolution is required")
    if len(resolution) > 3000:
        raise ValueError("resolution must be at most 3000 characters")
    incident = repository.get_incident(incident_id)
    if incident is None:
        raise LookupError("incident was not found")
    runbook_id = id_factory() if id_factory else f"RB-{uuid4().hex}"
    runbook = GeneratedRunbook(
        runbook_id=runbook_id,
        title=f"Runbook: {incident.title}",
        problem=incident.description,
        preconditions=["Confirm human approval before making any production change."],
        diagnostic_steps=[
            "Review the incident facts and reproduce the observed symptom where safe.",
            f"Apply the documented successful resolution: {resolution}",
        ],
        verification=["Confirm the original symptom is no longer present.", "Record the verification evidence."],
        remediation=[resolution],
        escalation=["Escalate to the service owner if verification fails or evidence is insufficient."],
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    repository.save_runbook(runbook)
    return {"runbook": {key: value for key, value in runbook.to_item().items() if key != "recordType"}}


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
        if event.get("isBase64Encoded") and isinstance(body, str):
            body = base64.b64decode(body).decode("utf-8")
        if isinstance(body, str):
            body = json.loads(body)
        repository = _default_repository()
        path = str(event.get("rawPath", event.get("path", "")))
        method = str(event.get("requestContext", {}).get("http", {}).get("method", event.get("httpMethod", ""))).upper()
        if method == "POST" and path.endswith("/runbook"):
            incident_id = path.rstrip("/").split("/")[-2]
            return _response(200, generate_runbook(incident_id, body, repository))
        result = analyze_incident(body, repository)
        return _response(200, result)
    except (ValueError, json.JSONDecodeError) as error:
        return _error_response(400, "VALIDATION_ERROR", str(error))
    except BedrockAnalysisError as error:
        return _error_response(502, "ANALYSIS_PROVIDER_ERROR", str(error))
    except LookupError as error:
        return _error_response(404, "NOT_FOUND", str(error))
    except Exception as error:
        LOGGER.exception("Unhandled incident analysis failure")
        return _error_response(500, "INTERNAL_ERROR", "The incident analysis request failed.")


def _analysis_adapter() -> AnalysisAdapter:
    provider = os.getenv("ANALYSIS_PROVIDER", "mock").strip().lower()
    if provider == "mock":
        return MockBedrockAdapter()
    if provider == "bedrock":
        return BedrockAnalysisAdapter()
    raise ValueError("ANALYSIS_PROVIDER must be either mock or bedrock")


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
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": os.getenv("CORS_ALLOW_ORIGIN", "*"),
            "Access-Control-Allow-Headers": "content-type",
        },
        "body": json.dumps(body),
    }


def _error_response(status_code: int, code: str, message: str) -> dict[str, Any]:
    return _response(status_code, {"error": {"code": code, "message": message}})
