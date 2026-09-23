from __future__ import annotations

from api.schemas.structural_optimization import (
    CandidateStatus,
    SemanticSafetyStatus,
    StructuralAnalysis,
    StructuralDatabaseRoutineRecommendation,
    StructuralDatabaseRoutineRecommendationResult,
    StructuralProceduralWorkloadOpportunityResult,
)
from api.services.procedural_routine_recommendation_evaluator import (
    ProceduralRoutineRecommendationEvaluator,
)


class StructuralDatabaseRoutineRecommendationGenerator:
    """
    Generate deterministic database function/procedure recommendation
    candidates from eligible procedural workload opportunities.

    This service is analytical only. It does not:
      - generate CREATE FUNCTION statements,
      - generate CREATE PROCEDURE statements,
      - rewrite SQL,
      - execute SQL,
      - execute routines,
      - benchmark alternatives,
      - establish behavioral equivalence,
      - establish performance improvement, or
      - make production decisions.

    Generated recommendations remain candidates until later validation
    stages establish the required evidence.
    """

    def __init__(
        self,
        evaluator: ProceduralRoutineRecommendationEvaluator | None = None,
    ) -> None:
        self._evaluator = (
            evaluator or ProceduralRoutineRecommendationEvaluator()
        )

    def generate(
        self,
        analysis: StructuralAnalysis,
        opportunities: StructuralProceduralWorkloadOpportunityResult,
        original_sql: str,
    ) -> StructuralDatabaseRoutineRecommendationResult:
        """
        Generate deterministic routine recommendation candidates.

        Candidate order follows the eligible opportunity order.

        The original SQL is preserved exactly.
        """

        recommendations: list[
            StructuralDatabaseRoutineRecommendation
        ] = []

        for opportunity in opportunities.opportunities:
            if opportunity.finding_index >= len(analysis.findings):
                raise ValueError(
                    "Opportunity references a finding index that does "
                    f"not exist: {opportunity.finding_index}"
                )

            evaluation = self._evaluator.evaluate(
                opportunity
            )

            if not evaluation.eligible:
                continue

            finding = analysis.findings[
                opportunity.finding_index
            ]

            recommendation_number = len(
                recommendations
            ) + 1

            recommendation_type = (
                evaluation.rule.recommendation_type
            )

            recommendations.append(
                StructuralDatabaseRoutineRecommendation(
                    recommendation_id=(
                        f"ROUTINE-REC-{recommendation_number:04d}"
                    ),
                    recommendation_type=recommendation_type,
                    status=CandidateStatus.CANDIDATE,
                    semantic_safety=(
                        SemanticSafetyStatus.NOT_ASSESSED
                    ),
                    evidence_status=(
                        opportunity.evidence_status
                    ),
                    title=self._build_title(
                        recommendation_type.value
                    ),
                    rationale=self._build_rationale(
                        evaluation.rationale,
                        recommendation_type.value,
                    ),
                    source_layer=finding.layer,
                    original_sql=original_sql,
                )
            )

        return StructuralDatabaseRoutineRecommendationResult(
            recommendations=recommendations
        )

    @staticmethod
    def _build_title(
        recommendation_type: str,
    ) -> str:
        if recommendation_type == "FUNCTION":
            return "Database function architectural candidate"

        return "Stored procedure architectural candidate"

    @staticmethod
    def _build_rationale(
        evaluation_rationale: str,
        recommendation_type: str,
    ) -> str:
        routine_label = (
            "database function"
            if recommendation_type == "FUNCTION"
            else "stored procedure"
        )

        return (
            f"{evaluation_rationale} A {routine_label} candidate is "
            "recorded for later semantic and behavioral validation. "
            "This candidate does not establish that the routine "
            "should be created or used in production."
        )
