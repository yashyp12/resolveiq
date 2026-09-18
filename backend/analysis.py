"""Mock analysis adapter and validation for the incident-analysis contract."""

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from .models import Incident
from .retrieval import RetrievedEvidence, RetrievalResult

MAX_CAUSES = 5
MAX_SIMILAR_INCIDENTS = 5
MAX_RECOMMENDED_CHECKS = 10
MAX_EVIDENCE_IDS = 10
MAX_CATEGORY_LENGTH = 100
MAX_CAUSE_LENGTH = 300
MAX_CHECK_LENGTH = 500
MAX_UNCERTAINTY_LENGTH = 1000


class AnalysisAdapter(Protocol):
    def analyze(self, incident: Incident, evidence: RetrievalResult) -> Mapping[str, Any]:
        """Return a structured analysis for the supplied bounded context."""


class MockBedrockAdapter:
    """Deterministic stand-in for Bedrock until the real adapter is introduced."""

    def analyze(self, incident: Incident, evidence: RetrievalResult) -> Mapping[str, Any]:
        historical = evidence.historical_incidents
        runbooks = evidence.runbooks
        evidence_items = [*historical, *runbooks]
        similar_ids = [item.evidence_id for item in historical[:MAX_SIMILAR_INCIDENTS]]

        if historical:
            category = _category_from_evidence(historical[0])
            cause = f"Potential {category} issue"
            confidence = 0.75
            cause_evidence = [historical[0].evidence_id]
        else:
            category = "unknown"
            cause = ""
            confidence = 0.0
            cause_evidence = []

        checks = _checks_from_runbooks(runbooks)
        if not checks:
            checks = ["Review the incident facts and collect service-level diagnostics."]

        causes = []
        if cause:
            causes.append(
                {
                    "cause": cause,
                    "confidence": confidence,
                    "evidenceIds": cause_evidence,
                }
            )

        return {
            "category": category,
            "likelyCauses": causes,
            "similarIncidents": similar_ids,
            "recommendedChecks": checks,
            "uncertainty": (
                "The root cause is not confirmed from the available evidence."
                if evidence_items
                else "Insufficient historical evidence is available to infer a likely cause."
            ),
        }


def validate_analysis_response(
    response: Mapping[str, Any],
    retrieved_evidence: Sequence[RetrievedEvidence],
) -> dict[str, Any]:
    """Validate and return a JSON-compatible analysis response.

    Evidence references are checked against the exact bounded retrieval result,
    not against the repository or the model's unrestricted output.
    """

    if not isinstance(response, Mapping):
        raise ValueError("analysis response must be an object")
    required = ("category", "likelyCauses", "similarIncidents", "recommendedChecks", "uncertainty")
    missing = [name for name in required if name not in response]
    if missing:
        raise ValueError(f"analysis response is missing required fields: {', '.join(missing)}")

    category = _string(response["category"], "category", MAX_CATEGORY_LENGTH)
    uncertainty = _string(response["uncertainty"], "uncertainty", MAX_UNCERTAINTY_LENGTH)
    causes_value = response["likelyCauses"]
    similar_value = response["similarIncidents"]
    checks_value = response["recommendedChecks"]
    _bounded_list(causes_value, "likelyCauses", MAX_CAUSES)
    _bounded_list(similar_value, "similarIncidents", MAX_SIMILAR_INCIDENTS)
    _bounded_list(checks_value, "recommendedChecks", MAX_RECOMMENDED_CHECKS)

    valid_ids = {item.evidence_id for item in retrieved_evidence}
    valid_similar_ids = {
        item.evidence_id for item in retrieved_evidence if item.evidence_type == "historical_incident"
    }
    causes: list[dict[str, Any]] = []
    for index, cause_value in enumerate(causes_value):
        if not isinstance(cause_value, Mapping):
            raise ValueError(f"likelyCauses[{index}] must be an object")
        for field in ("cause", "confidence", "evidenceIds"):
            if field not in cause_value:
                raise ValueError(f"likelyCauses[{index}] is missing {field}")
        cause = _string(cause_value["cause"], f"likelyCauses[{index}].cause", MAX_CAUSE_LENGTH)
        confidence = cause_value["confidence"]
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise ValueError(f"likelyCauses[{index}].confidence must be between 0 and 1")
        evidence_ids = _evidence_ids(cause_value["evidenceIds"], f"likelyCauses[{index}].evidenceIds", valid_ids)
        causes.append({"cause": cause, "confidence": confidence, "evidenceIds": evidence_ids})

    similar_incidents = _evidence_ids(similar_value, "similarIncidents", valid_similar_ids, MAX_SIMILAR_INCIDENTS)
    checks = [_string(value, f"recommendedChecks[{index}]", MAX_CHECK_LENGTH) for index, value in enumerate(checks_value)]
    return {
        "category": category,
        "likelyCauses": causes,
        "similarIncidents": similar_incidents,
        "recommendedChecks": checks,
        "uncertainty": uncertainty,
    }


def _category_from_evidence(item: RetrievedEvidence) -> str:
    record = item.record
    category = getattr(record, "category", None)
    return category if isinstance(category, str) and category.strip() else "general"


def _checks_from_runbooks(runbooks: Sequence[RetrievedEvidence]) -> list[str]:
    checks: list[str] = []
    for item in runbooks:
        record = item.record
        steps = getattr(record, "diagnostic_steps", [])
        for step in steps:
            if step not in checks:
                checks.append(step)
            if len(checks) == MAX_RECOMMENDED_CHECKS:
                return checks
    return checks


def _bounded_list(value: Any, name: str, maximum: int) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be an array")
    if len(value) > maximum:
        raise ValueError(f"{name} must contain at most {maximum} items")


def _evidence_ids(
    value: Any,
    name: str,
    valid_ids: set[str],
    maximum: int = MAX_EVIDENCE_IDS,
) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be an array")
    if len(value) > maximum:
        raise ValueError(f"{name} must contain at most {maximum} items")
    result: list[str] = []
    for index, evidence_id in enumerate(value):
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError(f"{name}[{index}] must be a non-empty string")
        if evidence_id not in valid_ids:
            raise ValueError(f"{name}[{index}] references unknown evidence ID: {evidence_id}")
        if evidence_id not in result:
            result.append(evidence_id)
    return result


def _string(value: Any, name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{name} must be at most {maximum} characters")
    return value
