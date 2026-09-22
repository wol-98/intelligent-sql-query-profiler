from __future__ import annotations

from api.schemas.structural_optimization import (
    CandidateStatus,
    SemanticSafetyStatus,
    StructuralArchitecturalOpportunityResult,
    StructuralViewRecommendation,
    StructuralViewRecommendationResult,
)
from api.services.architectural_recommendation_evaluator import (
    ArchitecturalRecommendationEvaluator,
)


class StructuralViewRecommendationGenerator:
    """
    Generate architectural view/materialized-view recommendation candidates
    from structurally identified and evidence-eligible opportunities.

    This service does not:
      - rewrite SQL,
      - generate CREATE VIEW DDL,
      - execute SQL,
      - benchmark alternatives,
      - establish semantic equivalence,
      - establish performance improvement, or
      - make production decisions.
    """

    def __init__(
        self,
        evaluator: ArchitecturalRecommendationEvaluator | None = None,
    ) -> None:
        self._evaluator = (
            evaluator or ArchitecturalRecommendationEvaluator()
        )

    def generate(
        self,
        opportunities: StructuralArchitecturalOpportunityResult,
        *,
        original_sql: str,
        source_layers: dict[int, object] | None = None,
    ) -> StructuralViewRecommendationResult:
        recommendations: list[StructuralViewRecommendation] = []

        for opportunity in opportunities.opportunities:
            evaluation = self._evaluator.evaluate(opportunity)

            if not evaluation.eligible:
                continue

            if evaluation.rule.recommendation_type is None:
                continue

            source_layer = None

            if source_layers is not None:
                source_layer = source_layers.get(
                    opportunity.finding_index
                )

            recommendation_number = len(recommendations) + 1

            recommendations.append(
                StructuralViewRecommendation(
                    recommendation_id=(
                        f"VIEW-REC-{recommendation_number:04d}"
                    ),
                    recommendation_type=(
                        evaluation.rule.recommendation_type
                    ),
                    status=CandidateStatus.CANDIDATE,
                    semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
                    evidence_status=opportunity.evidence_status,
                    title=(
                        f"{evaluation.rule.recommendation_type.value} "
                        "architectural candidate"
                    ),
                    rationale=(
                        evaluation.rationale
                        + " This is a structural candidate only; "
                        "semantic validation and later evidence are required."
                    ),
                    source_layer=source_layer,
                    original_sql=original_sql,
                )
            )

        return StructuralViewRecommendationResult(
            recommendations=recommendations
        )
