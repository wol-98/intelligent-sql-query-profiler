from pydantic import BaseModel


class OverviewCounts(BaseModel):
    recommendations: int = 0
    evaluated_recommendations: int = 0
    benchmark_evaluations: int = 0
    successful_recommendations: int = 0
    neutral_recommendations: int = 0
    unsuccessful_recommendations: int = 0

class OverviewPerformance(BaseModel):
    average_improvement_percent: float | None = None
    median_improvement_percent: float | None = None
    index_usage_percent: float | None = None
    rows_preserved_percent: float | None = None


class OverviewEvidence(BaseModel):
    complete: int = 0
    partial: int = 0
    insufficient: int = 0


class OverviewResponse(BaseModel):
    counts: OverviewCounts
    performance: OverviewPerformance
    evidence: OverviewEvidence
