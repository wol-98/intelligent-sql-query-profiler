from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    ArchitecturalOpportunityType,
    EvidenceStatus,
    ViewRecommendationType,
)


@dataclass(frozen=True)
class ArchitecturalRecommendationRule:
    opportunity_type: ArchitecturalOpportunityType
    recommendation_type: ViewRecommendationType | None
    required_evidence_status: EvidenceStatus
    requires_semantic_validation: bool
    rationale: str


class ArchitecturalRecommendationRuleEngine:
    """
    Deterministic rules for translating structural architectural
    opportunities into eligible view/materialized-view recommendation types.

    This rule engine does not:
      - generate recommendations,
      - execute SQL,
      - benchmark alternatives,
      - establish performance improvement, or
      - make production decisions.
    """

    _RULES = {
        ArchitecturalOpportunityType.REUSABLE_CTE: (
            ArchitecturalRecommendationRule(
                opportunity_type=ArchitecturalOpportunityType.REUSABLE_CTE,
                recommendation_type=ViewRecommendationType.VIEW,
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_semantic_validation=True,
                rationale=(
                    "A reusable CTE structure may be considered for a "
                    "view-based architectural alternative after semantic "
                    "validation."
                ),
            )
        ),
        ArchitecturalOpportunityType.AGGREGATED_RESULT: (
            ArchitecturalRecommendationRule(
                opportunity_type=(
                    ArchitecturalOpportunityType.AGGREGATED_RESULT
                ),
                recommendation_type=ViewRecommendationType.MATERIALIZED_VIEW,
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_semantic_validation=True,
                rationale=(
                    "An aggregated result structure may be considered for "
                    "a materialized-view architectural alternative after "
                    "semantic validation."
                ),
            )
        ),
        ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT: (
            ArchitecturalRecommendationRule(
                opportunity_type=(
                    ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
                ),
                recommendation_type=ViewRecommendationType.VIEW,
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_semantic_validation=True,
                rationale=(
                    "A filtered relational result may be considered for "
                    "a view-based architectural alternative after semantic "
                    "validation."
                ),
            )
        ),
        ArchitecturalOpportunityType.ANALYTICAL_RESULT: (
            ArchitecturalRecommendationRule(
                opportunity_type=ArchitecturalOpportunityType.ANALYTICAL_RESULT,
                recommendation_type=ViewRecommendationType.VIEW,
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_semantic_validation=True,
                rationale=(
                    "An analytical result structure may be considered for "
                    "a view-based architectural alternative after semantic "
                    "validation."
                ),
            )
        ),
        ArchitecturalOpportunityType.RECURSIVE_CTE: (
            ArchitecturalRecommendationRule(
                opportunity_type=ArchitecturalOpportunityType.RECURSIVE_CTE,
                recommendation_type=None,
                required_evidence_status=EvidenceStatus.COMPLETE,
                requires_semantic_validation=True,
                rationale=(
                    "Recursive CTE structures require dedicated semantic "
                    "and architectural validation; no automatic "
                    "view/materialized-view recommendation is defined."
                ),
            )
        ),
    }

    def get_rule(
        self,
        opportunity_type: ArchitecturalOpportunityType,
    ) -> ArchitecturalRecommendationRule:
        try:
            return self._RULES[opportunity_type]
        except KeyError as exc:
            raise ValueError(
                f"No architectural recommendation rule exists for "
                f"{opportunity_type}"
            ) from exc
