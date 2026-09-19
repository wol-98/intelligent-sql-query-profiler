from pydantic import BaseModel, Field


class QueryPlan(BaseModel):
    node_types: list[str] = Field(default_factory=list)
    sequential_scans: int | None = None
    index_scans: int | None = None
    bitmap_scans: int | None = None
    joins: int | None = None
    has_filter: bool | None = None
    has_index_condition: bool | None = None


class QueryResponse(BaseModel):
    query_profile_id: int
    fingerprint: str
    template: str | None = None
    query_type: str
    query_text: str
    execution_count: int | None = None
    total_execution_time_ms: float | None = None
    average_execution_time_ms: float | None = None
    rows_processed: int | None = None
    table_name: str | None = None
    captured_at: str | None = None
    plan: QueryPlan | None = None
    recommendation_ids: list[int] = Field(default_factory=list)
