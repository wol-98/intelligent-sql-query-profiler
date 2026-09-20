from __future__ import annotations

from api.schemas.structural_optimization import (
    AlternativeType,
    CandidateStatus,
    OptimizationCandidate,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    StructuralAnalysis,
    StructuralOpportunityResult,
)


class StructuralCandidateGenerator:
    """Generate deterministic optimization candidates from structural opportunities.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - benchmark alternatives,
      - validate performance,
      - generate concrete index DDL,
      - rewrite SQL, or
      - make production decisions.

    Candidates generated here represent alternatives that may be examined
    by later validation and benchmarking stages.
    """

    _ALTERNATIVE_BY_OPPORTUNITY = {
        OptimizationOpportunityType.PREDICATE_ANALYSIS: AlternativeType.INDEX,
        OptimizationOpportunityType.JOIN_ANALYSIS: AlternativeType.INDEX,
        OptimizationOpportunityType.AGGREGATION_ANALYSIS: AlternativeType.INDEX,
        OptimizationOpportunityType.WINDOW_ANALYSIS: AlternativeType.INDEX,
        OptimizationOpportunityType.ORDERING_ANALYSIS: AlternativeType.INDEX,
        OptimizationOpportunityType.ROW_LIMITING_ANALYSIS: AlternativeType.INDEX,
        OptimizationOpportunityType.NESTED_QUERY_ANALYSIS: AlternativeType.SQL_REWRITE,
    }

    def generate(
        self,
        analysis: StructuralAnalysis,
        opportunities: StructuralOpportunityResult,
        original_sql: str,
    ) -> list[OptimizationCandidate]:
        """Generate candidates from identified structural opportunities.

        Candidate order follows opportunity order, making generation
        deterministic. The original SQL and structural source layer are
        preserved for later validation and provenance.
        """
        candidates: list[OptimizationCandidate] = []

        for opportunity_number, opportunity in enumerate(
            opportunities.opportunities,
            start=1,
        ):
            if opportunity.finding_index >= len(analysis.findings):
                raise ValueError(
                    "Opportunity references a finding index that does "
                    f"not exist: {opportunity.finding_index}"
                )

            if opportunity.status != OptimizationOpportunityStatus.IDENTIFIED:
                continue

            alternative_type = self._ALTERNATIVE_BY_OPPORTUNITY.get(
                opportunity.opportunity_type
            )

            if alternative_type is None:
                continue

            finding = analysis.findings[opportunity.finding_index]

            candidates.append(
                OptimizationCandidate(
                    candidate_id=f"CAND-{opportunity_number:04d}",
                    alternative_type=alternative_type,
                    status=CandidateStatus.CANDIDATE,
                    title=self._build_title(
                        opportunity.opportunity_type
                    ),
                    rationale=(
                        f"{opportunity.opportunity_type.value} was identified "
                        "from an established structural opportunity and is "
                        "eligible for later optimization validation."
                    ),
                    source_layer=finding.layer,
                    original_sql=original_sql,
                    optimized_sql=None,
                    index_ddl=None,
                    architectural_recommendation=None,
                )
            )

        return candidates

    @staticmethod
    def _build_title(
        opportunity_type: OptimizationOpportunityType,
    ) -> str:
        titles = {
            OptimizationOpportunityType.PREDICATE_ANALYSIS:
                "Predicate-focused index candidate",
            OptimizationOpportunityType.JOIN_ANALYSIS:
                "Join-focused index candidate",
            OptimizationOpportunityType.AGGREGATION_ANALYSIS:
                "Aggregation-focused index candidate",
            OptimizationOpportunityType.WINDOW_ANALYSIS:
                "Window-operation index candidate",
            OptimizationOpportunityType.ORDERING_ANALYSIS:
                "Ordering-focused index candidate",
            OptimizationOpportunityType.ROW_LIMITING_ANALYSIS:
                "Row-limiting index candidate",
            OptimizationOpportunityType.NESTED_QUERY_ANALYSIS:
                "Nested-query SQL rewrite candidate",
        }

        return titles[opportunity_type]
