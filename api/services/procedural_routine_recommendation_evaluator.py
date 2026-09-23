from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    EvidenceStatus,
    ProceduralWorkloadOpportunityStatus,
    StructuralProceduralWorkloadOpportunity,
)
from api.services.procedural_routine_recommendation_rules import (
    ProceduralRoutineRecommendationRule,
    ProceduralRoutineRecommendationRuleEngine,
)


@dataclass(frozen=True)
class ProceduralRoutineRecommendationEvaluation:
    opportunity: StructuralProceduralWorkloadOpportunity
    rule: ProceduralRoutineRecommendationRule
    eligible: bool
    rationale: str


class ProceduralRoutineRecommendationEvaluator:
    """
    Evaluate whether a procedural workload opportunity satisfies the
    deterministic evidence requirements for a later recommendation candidate.

    This evaluator does not:
      - generate recommendations,
      - generate SQL,
      - execute SQL,
      - create functions or procedures,
      - benchmark alternatives,
      - establish behavioral equivalence,
      - establish performance improvement, or
      - make production decisions.
    """

    def __init__(
        self,
        rule_engine: ProceduralRoutineRecommendationRuleEngine | None = None,
    ) -> None:
        self._rule_engine = (
            rule_engine or ProceduralRoutineRecommendationRuleEngine()
        )

    def evaluate(
        self,
        opportunity: StructuralProceduralWorkloadOpportunity,
    ) -> ProceduralRoutineRecommendationEvaluation:
        rule = self._rule_engine.get_rule(
            opportunity.opportunity_type
        )

        eligible = (
            opportunity.status
            == ProceduralWorkloadOpportunityStatus.IDENTIFIED
            and opportunity.evidence_status
            == rule.required_evidence_status
        )

        return ProceduralRoutineRecommendationEvaluation(
            opportunity=opportunity,
            rule=rule,
            eligible=eligible,
            rationale=self._build_rationale(
                opportunity=opportunity,
                rule=rule,
                eligible=eligible,
            ),
        )

    @staticmethod
    def _build_rationale(
        *,
        opportunity: StructuralProceduralWorkloadOpportunity,
        rule: ProceduralRoutineRecommendationRule,
        eligible: bool,
    ) -> str:
        if eligible:
            return (
                "The procedural workload opportunity is identified and "
                "contains the complete evidence required by its "
                "recommendation rule. It is eligible for later "
                "recommendation-candidate generation. Behavioral "
                "validation remains required."
            )

        if opportunity.status != (
            ProceduralWorkloadOpportunityStatus.IDENTIFIED
        ):
            return (
                "The procedural workload opportunity is not eligible "
                "because its structural status is not IDENTIFIED."
            )

        if opportunity.evidence_status != rule.required_evidence_status:
            return (
                "The procedural workload opportunity is not eligible "
                "because its evidence status does not satisfy the "
                "required evidence status for the recommendation rule."
            )

        return (
            "The procedural workload opportunity is not eligible for "
            "later recommendation-candidate generation."
        )
