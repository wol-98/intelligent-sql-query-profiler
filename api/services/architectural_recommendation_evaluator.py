from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    ArchitecturalOpportunityStatus,
    ArchitecturalOpportunityType,
    EvidenceStatus,
    StructuralArchitecturalOpportunity,
)
from api.services.architectural_recommendation_rules import (
    ArchitecturalRecommendationRule,
    ArchitecturalRecommendationRuleEngine,
)


@dataclass(frozen=True)
class ArchitecturalRecommendationEvaluation:
    opportunity: StructuralArchitecturalOpportunity
    rule: ArchitecturalRecommendationRule
    eligible: bool
    rationale: str


class ArchitecturalRecommendationEvaluator:
    """
    Evaluate whether a structural architectural opportunity satisfies the
    deterministic evidence requirements for a later recommendation candidate.

    This evaluator does not generate recommendations, execute SQL,
    benchmark alternatives, or establish performance improvement.
    """

    def __init__(
        self,
        rule_engine: ArchitecturalRecommendationRuleEngine | None = None,
    ) -> None:
        self._rule_engine = (
            rule_engine or ArchitecturalRecommendationRuleEngine()
        )

    def evaluate(
        self,
        opportunity: StructuralArchitecturalOpportunity,
    ) -> ArchitecturalRecommendationEvaluation:
        rule = self._rule_engine.get_rule(
            opportunity.opportunity_type
        )

        eligible = (
            opportunity.status == ArchitecturalOpportunityStatus.IDENTIFIED
            and opportunity.evidence_status
            == rule.required_evidence_status
            and rule.recommendation_type is not None
        )

        return ArchitecturalRecommendationEvaluation(
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
        opportunity: StructuralArchitecturalOpportunity,
        rule: ArchitecturalRecommendationRule,
        eligible: bool,
    ) -> str:
        if opportunity.opportunity_type == (
            ArchitecturalOpportunityType.RECURSIVE_CTE
        ):
            return (
                "Recursive CTE structure requires dedicated semantic and "
                "architectural validation; no automatic view or "
                "materialized-view recommendation is eligible."
            )

        if opportunity.status != ArchitecturalOpportunityStatus.IDENTIFIED:
            return (
                f"{opportunity.opportunity_type.value} is not eligible "
                "because its structural opportunity status is not "
                "IDENTIFIED."
            )

        if opportunity.evidence_status != rule.required_evidence_status:
            return (
                f"{opportunity.opportunity_type.value} is not eligible "
                f"because its evidence status is "
                f"{opportunity.evidence_status.value}; "
                f"{rule.required_evidence_status.value} evidence is required."
            )

        if not eligible:
            return (
                f"{opportunity.opportunity_type.value} is not eligible "
                "for an automatic architectural recommendation under the "
                "current rule set."
            )

        return (
            f"{opportunity.opportunity_type.value} satisfies the current "
            f"structural and evidence requirements for a "
            f"{rule.recommendation_type.value} candidate. "
            "Semantic validation is still required."
        )
