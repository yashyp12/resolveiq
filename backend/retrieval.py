"""Deterministic, AWS-independent evidence retrieval for incident analysis."""

from dataclasses import dataclass, field
import re
from typing import Any, Iterable, Mapping

from .models import HistoricalIncident, Incident, Runbook


@dataclass(frozen=True)
class RetrievalConfig:
    """Tunable retrieval weights and Bedrock context limits."""

    max_historical: int = 5
    max_runbooks: int = 3
    service_weight: int = 3
    category_weight: int = 3
    tag_weight: int = 2
    symptom_weight: int = 2
    text_token_weight: int = 1
    error_token_weight: int = 1
    runbook_token_weight: int = 1


@dataclass(frozen=True)
class RetrievedEvidence:
    evidence_id: str
    evidence_type: str
    title: str
    source: str
    summary: str
    relevance_score: int
    score_breakdown: Mapping[str, int] = field(default_factory=dict)
    record: HistoricalIncident | Runbook | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class RetrievalResult:
    historical_incidents: list[RetrievedEvidence]
    runbooks: list[RetrievedEvidence]


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def retrieve_evidence(
    incident: Incident | Mapping[str, Any],
    historical_incidents: Iterable[HistoricalIncident | Mapping[str, Any]],
    runbooks: Iterable[Runbook | Mapping[str, Any]],
    config: RetrievalConfig | None = None,
) -> RetrievalResult:
    """Retrieve bounded, deterministically ordered evidence for an incident.

    This function performs in-memory scoring only. It does not query DynamoDB
    and makes no claim that DynamoDB provides semantic search.
    """

    settings = config or RetrievalConfig()
    if settings.max_historical < 0 or settings.max_runbooks < 0:
        raise ValueError("result limits must not be negative")

    current_id = _string_value(incident, "incident_id", "incidentId")
    historical = _rank_historical(incident, historical_incidents, current_id, settings)
    curated_runbooks = _rank_runbooks(incident, runbooks, settings)
    historical_ids = {item.evidence_id for item in historical}
    curated_runbooks = [item for item in curated_runbooks if item.evidence_id not in historical_ids]
    return RetrievalResult(
        historical_incidents=historical[: settings.max_historical],
        runbooks=curated_runbooks[: settings.max_runbooks],
    )


def _rank_historical(
    incident: Incident | Mapping[str, Any],
    candidates: Iterable[HistoricalIncident | Mapping[str, Any]],
    current_id: Any,
    config: RetrievalConfig,
) -> list[RetrievedEvidence]:
    by_id: dict[str, RetrievedEvidence] = {}
    for candidate in candidates:
        evidence_id = _string_value(candidate, "incident_id", "incidentId")
        if not evidence_id or evidence_id == current_id:
            continue
        score, breakdown = _historical_score(incident, candidate, config)
        if score <= 0:
            continue
        evidence = RetrievedEvidence(
            evidence_id=evidence_id,
            evidence_type="historical_incident",
            title=_string_value(candidate, "title"),
            source="Historical Incident",
            summary=_string_value(candidate, "description") or _string_value(candidate, "resolution"),
            relevance_score=score,
            score_breakdown=breakdown,
            record=candidate if isinstance(candidate, HistoricalIncident) else None,
        )
        _keep_best(by_id, evidence)
    return _ordered(by_id.values())


def _rank_runbooks(
    incident: Incident | Mapping[str, Any],
    candidates: Iterable[Runbook | Mapping[str, Any]],
    config: RetrievalConfig,
) -> list[RetrievedEvidence]:
    by_id: dict[str, RetrievedEvidence] = {}
    for candidate in candidates:
        evidence_id = _string_value(candidate, "runbook_id", "runbookId")
        if not evidence_id:
            continue
        score, breakdown = _runbook_score(incident, candidate, config)
        if score <= 0:
            continue
        evidence = RetrievedEvidence(
            evidence_id=evidence_id,
            evidence_type="runbook",
            title=_string_value(candidate, "title"),
            source="Runbook",
            summary=_string_value(candidate, "problem"),
            relevance_score=score,
            score_breakdown=breakdown,
            record=candidate if isinstance(candidate, Runbook) else None,
        )
        _keep_best(by_id, evidence)
    return _ordered(by_id.values())


def _historical_score(
    incident: Incident | Mapping[str, Any],
    candidate: HistoricalIncident | Mapping[str, Any],
    config: RetrievalConfig,
) -> tuple[int, dict[str, int]]:
    breakdown: dict[str, int] = {}
    if _same(incident, candidate, "service"):
        breakdown["service"] = config.service_weight
    if _same(incident, candidate, "category"):
        breakdown["category"] = config.category_weight

    incident_tags = _tokens(_value(incident, "tags"))
    candidate_tags = _tokens(_value(candidate, "tags"))
    if incident_tags and candidate_tags:
        breakdown["tags"] = len(incident_tags & candidate_tags) * config.tag_weight

    incident_symptoms = _tokens(_value(incident, "symptoms"))
    candidate_symptoms = _tokens(_value(candidate, "symptoms"))
    if incident_symptoms and candidate_symptoms:
        breakdown["symptoms"] = len(incident_symptoms & candidate_symptoms) * config.symptom_weight

    incident_text = _tokens(
        " ".join(
            [
                _string_value(incident, "title"),
                _string_value(incident, "description"),
            ]
        )
    )
    candidate_text = _tokens(
        " ".join(
            [
                _string_value(candidate, "title"),
                _string_value(candidate, "description"),
            ]
        )
    )
    text_overlap = incident_text & candidate_text
    if text_overlap:
        breakdown["text_tokens"] = len(text_overlap) * config.text_token_weight

    incident_error = _tokens(_value(incident, "error"))
    candidate_error = _tokens(_value(candidate, "error"))
    if incident_error and candidate_error:
        error_overlap = incident_error & candidate_error
        if error_overlap:
            breakdown["error_tokens"] = len(error_overlap) * config.error_token_weight
    return sum(breakdown.values()), breakdown


def _runbook_score(
    incident: Incident | Mapping[str, Any],
    candidate: Runbook | Mapping[str, Any],
    config: RetrievalConfig,
) -> tuple[int, dict[str, int]]:
    incident_tokens = _tokens(
        " ".join(
            [
                _string_value(incident, "title"),
                _string_value(incident, "description"),
                _string_value(incident, "error"),
                _string_value(incident, "service"),
            ]
        )
    )
    runbook_tokens = _tokens(
        " ".join(
            [
                _string_value(candidate, "title"),
                _string_value(candidate, "problem"),
            ]
        )
    )
    overlap = incident_tokens & runbook_tokens
    if not overlap:
        return 0, {}
    return len(overlap) * config.runbook_token_weight, {"title_problem_tokens": len(overlap) * config.runbook_token_weight}


def _keep_best(by_id: dict[str, RetrievedEvidence], evidence: RetrievedEvidence) -> None:
    existing = by_id.get(evidence.evidence_id)
    if existing is None or (evidence.relevance_score, evidence.title) > (existing.relevance_score, existing.title):
        by_id[evidence.evidence_id] = evidence


def _ordered(evidence: Iterable[RetrievedEvidence]) -> list[RetrievedEvidence]:
    return sorted(evidence, key=lambda item: (-item.relevance_score, item.evidence_id))


def _same(left: Any, right: Any, name: str) -> bool:
    left_value = _string_value(left, name)
    right_value = _string_value(right, name)
    return bool(left_value and right_value and left_value.casefold() == right_value.casefold())


def _tokens(value: Any) -> set[str]:
    if isinstance(value, (list, tuple, set)):
        value = " ".join(str(item) for item in value)
    return set(_TOKEN_RE.findall(str(value or "").casefold()))


def _value(record: Any, *names: str) -> Any:
    for name in names:
        if isinstance(record, Mapping) and name in record:
            return record[name]
        if hasattr(record, name):
            return getattr(record, name)
    return None


def _string_value(record: Any, *names: str) -> str:
    value = _value(record, *names)
    return value.strip() if isinstance(value, str) else ""
