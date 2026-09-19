from pydantic import BaseModel, Field


class WorkloadResponse(BaseModel):
    fingerprint: str
    template: str | None = None
    execution_count: int
    total_execution_time_ms: float
    average_execution_time_ms: float | None = None
    time_share: float | None = None
    frequency_share: float | None = None
    priority: str | None = None
    recommendation_ids: list[int] = Field(default_factory=list)
