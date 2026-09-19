from pydantic import BaseModel

from api.schemas.common import EvidenceStatus


class ReadBenefit(BaseModel):
    average_improvement_percent: float | None = None
    median_improvement_percent: float | None = None
    savings_ms: float | None = None
    index_used: bool | None = None
    plan_changed: bool | None = None
    rows_preserved: bool | None = None


class StorageImpact(BaseModel):
    index_size_bytes: int | None = None
    table_size_bytes: int | None = None
    ratio_percent: float | None = None


class WriteImpact(BaseModel):
    average_overhead_percent: float | None = None
    median_overhead_percent: float | None = None
    absolute_overhead_ms: float | None = None


class CostBenefitResponse(BaseModel):
    experiment_id: str
    recommendation_id: int | None = None

    read: ReadBenefit
    storage: StorageImpact
    write: WriteImpact

    evidence_status: EvidenceStatus
