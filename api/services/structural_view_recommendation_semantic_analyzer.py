from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    StructuralViewRecommendation,
    StructuralViewRecommendationResult,
)
from api.services.structural_view_semantic_precondition_analyzer import (
    StructuralViewSemanticPreconditionAnalyzer,
)
from api.services.structural_view_semantic_preconditions import (
    ViewSemanticPreconditionResult,
)


@dataclass(frozen=True)
class StructuralViewRecommendationAnalysis:
    """
    Associate a generated architectural recommendation candidate
    with its semantic-precondition analysis.

    The recommendation itself is preserved unchanged.
    """

    recommendation: StructuralViewRecommendation
    semantic_preconditions: ViewSemanticPreconditionResult


class StructuralViewRecommendationSemanticAnalyzer:
    """
    Integrate generated VIEW/MATERIALIZED VIEW candidates with
    deterministic semantic-precondition analysis.

    This service does not:
      - modify recommendation candidates,
      - establish semantic equivalence,
      - establish safety,
      - execute SQL,
      - benchmark performance, or
      - make production decisions.
    """

    def __init__(
        self,
        semantic_precondition_analyzer: (
            StructuralViewSemanticPreconditionAnalyzer | None
        ) = None,
    ) -> None:
        self._semantic_precondition_analyzer = (
            semantic_precondition_analyzer
            or StructuralViewSemanticPreconditionAnalyzer()
        )

    def analyze(
        self,
        recommendation: StructuralViewRecommendation,
    ) -> StructuralViewRecommendationAnalysis:
        """
        Analyze semantic preconditions for one recommendation candidate.

        The original recommendation instance is preserved unchanged.
        """

        semantic_preconditions = self._semantic_precondition_analyzer.analyze(
            recommendation.original_sql,
            recommendation.recommendation_type,
        )

        return StructuralViewRecommendationAnalysis(
            recommendation=recommendation,
            semantic_preconditions=semantic_preconditions,
        )

    def analyze_result(
        self,
        result: StructuralViewRecommendationResult,
    ) -> tuple[StructuralViewRecommendationAnalysis, ...]:
        """
        Analyze all recommendation candidates while preserving order.
        """

        return tuple(
            self.analyze(recommendation)
            for recommendation in result.recommendations
        )
