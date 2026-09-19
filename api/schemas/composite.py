from pydantic import BaseModel, Field


class CompositeIndexResponse(BaseModel):
    recommendation_id: int
    original_order: list[str] = Field(default_factory=list)
    alternative_order: list[str] = Field(default_factory=list)

    column_count: int

    original_improvement_percent: float | None = None
    alternative_improvement_percent: float | None = None
    order_effect_percentage_points: float | None = None

    original_index_used: bool | None = None
    alternative_index_used: bool | None = None

    original_rows_preserved: bool | None = None
    alternative_rows_preserved: bool | None = None

    evidence_source: str = "M16.2"
