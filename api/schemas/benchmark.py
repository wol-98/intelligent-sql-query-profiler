from pydantic import BaseModel

from api.schemas.common import ValidationOutcome


class BenchmarkResponse(BaseModel):
    benchmark_id: int | None = None
    recommendation_id: int | None = None
    experiment_id: str | None = None

    baseline_time_ms: float | None = None
    indexed_time_ms: float | None = None
    improvement_percent: float | None = None
    median_improvement_percent: float | None = None
    savings_ms: float | None = None

    rows_preserved: bool | None = None
    index_used: bool | None = None
    plan_changed: bool | None = None

    outcome: ValidationOutcome | None = None
    scope: str | None = None
