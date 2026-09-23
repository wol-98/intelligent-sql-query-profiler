from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    StructuralDatabaseRoutineRecommendation,
    StructuralDatabaseRoutineRecommendationResult,
)
from api.services.database_routine_semantic_preconditions import (
    DatabaseRoutineSemanticPreconditionResult,
)
from api.services.structural_database_routine_semantic_precondition_analyzer import (
    StructuralDatabaseRoutineSemanticPreconditionAnalyzer,
)


@dataclass(frozen=True)
class StructuralDatabaseRoutineRecommendationAnalysis:
    """
    Combined database-routine recommendation and semantic-precondition
    analysis.

    The recommendation itself remains unchanged. The attached
    precondition result records structural conditions that require
    later semantic/behavioral validation.
    """

    recommendation: StructuralDatabaseRoutineRecommendation
    semantic_preconditions: DatabaseRoutineSemanticPreconditionResult


@dataclass(frozen=True)
class StructuralDatabaseRoutineRecommendationAnalysisResult:
    """
    Integrated M21.12 database-routine recommendation analysis result.

    This service does not:
      - execute SQL,
      - rewrite SQL,
      - generate DDL,
      - establish semantic equivalence,
      - establish safety,
      - benchmark alternatives, or
      - make production decisions.
    """

    analyses: tuple[
        StructuralDatabaseRoutineRecommendationAnalysis,
        ...,
    ] = ()


class StructuralDatabaseRoutineRecommendationIntegrator:
    """
    Integrate database-routine recommendation candidates with their
    semantic/behavioral precondition analysis.
    """

    def __init__(
        self,
        semantic_precondition_analyzer: (
            StructuralDatabaseRoutineSemanticPreconditionAnalyzer | None
        ) = None,
    ) -> None:
        self._semantic_precondition_analyzer = (
            semantic_precondition_analyzer
            or StructuralDatabaseRoutineSemanticPreconditionAnalyzer()
        )

    def analyze(
        self,
        result: StructuralDatabaseRoutineRecommendationResult,
    ) -> StructuralDatabaseRoutineRecommendationAnalysisResult:
        """
        Attach semantic-precondition analysis to every recommendation.

        Candidate order is preserved.

        The original recommendation object is preserved unchanged.
        """
        analyses = tuple(
            self._analyze_recommendation(
                recommendation
            )
            for recommendation in result.recommendations
        )

        return StructuralDatabaseRoutineRecommendationAnalysisResult(
            analyses=analyses
        )

    def _analyze_recommendation(
        self,
        recommendation: StructuralDatabaseRoutineRecommendation,
    ) -> StructuralDatabaseRoutineRecommendationAnalysis:
        """
        Analyze one database-routine recommendation.
        """
        semantic_preconditions = (
            self._semantic_precondition_analyzer.analyze(
                recommendation.original_sql,
                recommendation.recommendation_type,
            )
        )

        return StructuralDatabaseRoutineRecommendationAnalysis(
            recommendation=recommendation,
            semantic_preconditions=semantic_preconditions,
        )
