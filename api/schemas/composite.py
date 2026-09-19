from pydantic import BaseModel, Field


class CompositeIndexResponse(BaseModel):
    recommendation_id: int | None = None
    index_name: str
    table_name: str

    columns: list[str] = Field(default_factory=list)
    column_count: int

    source_type: str | None = None
    candidate_type: str | None = None
    reason: str | None = None

    original_order: list[str] = Field(default_factory=list)
    alternative_order: list[str] = Field(default_factory=list)

    original_improvement_percent: float | None = None
    alternative_improvement_percent: float | None = None
    order_effect_percentage_points: float | None = None

    original_index_used: bool | None = None
    alternative_index_used: bool | None = None
