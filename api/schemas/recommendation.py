from pydantic import BaseModel, Field

from api.schemas.common import (
    DecisionState,
    EvidenceStatus,
    GuardrailStatus,
    ProvenanceStatus,
    ValidationOutcome,
)


class RecommendationQuery(BaseModel):
    fingerprint: str | None = None
    template: str | None = None
    query_type: str | None = None


class RecommendationWorkload(BaseModel):
    priority: str | None = None
    execution_count: int | None = None
    time_share: float | None = None
    frequency_share: float | None = None


class RecommendationValidation(BaseModel):
    outcome: ValidationOutcome | None = None
    improvement: float | None = None
    median_improvement: float | None = None
    savings_ms: float | None = None
    index_used: bool | None = None
    plan_changed: bool | None = None
    rows_preserved: bool | None = None


class RecommendationCost(BaseModel):
    storage_ratio_percent: float | None = None
    write_overhead_percent: float | None = None
    median_write_overhead_percent: float | None = None
    evidence_status: EvidenceStatus


class RecommendationDecision(BaseModel):
    state: DecisionState
    guardrail: GuardrailStatus


class RecommendationProvenance(BaseModel):
    linked_experiment_id: str | None = None
    status: ProvenanceStatus
    evidence_status: EvidenceStatus


class RecommendationResponse(BaseModel):
    recommendation_id: int
    index_name: str | None = None
    table_name: str
    columns: list[str] = Field(default_factory=list)
    index_type: str | None = None
    candidate_type: str | None = None
    source_type: str | None = None
    score: float
    priority: str

    reason: str | None = None

    query: RecommendationQuery
    workload: RecommendationWorkload
    validation: RecommendationValidation
    cost: RecommendationCost
    decision: RecommendationDecision
    provenance: RecommendationProvenance
