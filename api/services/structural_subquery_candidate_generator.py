from __future__ import annotations

from api.schemas.structural_optimization import (
    CandidateStatus,
    EvidenceStatus,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    SemanticSafetyStatus,
    StructuralAlternativeCandidate,
    StructuralAlternativeResult,
    StructuralAnalysis,
    StructuralOpportunityResult,
    SubqueryAlternativeType,
)


class StructuralSubqueryCandidateGenerator:
    """
    Generate deterministic structural candidates for subquery alternatives.

    This service is analytical only. It does not:
      - execute SQL,
      - rewrite SQL,
      - claim semantic equivalence,
      - benchmark alternatives,
      - validate performance, or
      - make optimization decisions.

    Generated candidates remain explicitly unvalidated until later
    semantic-safety and benchmarking stages.
    """

    _ALTERNATIVE_BY_OPPORTUNITY = {
        OptimizationOpportunityType.SUBQUERY_EXISTS_ANALYSIS:
            SubqueryAlternativeType.EXISTS,
        OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS:
            SubqueryAlternativeType.IN,
        OptimizationOpportunityType.SUBQUERY_ANY_ANALYSIS:
            SubqueryAlternativeType.ANY,
        OptimizationOpportunityType.DERIVED_TABLE_ANALYSIS:
            SubqueryAlternativeType.DERIVED_TABLE,
    }

    def generate(
        self,
        analysis: StructuralAnalysis,
        opportunities: StructuralOpportunityResult,
        original_sql: str,
    ) -> StructuralAlternativeResult:
        """
        Generate deterministic subquery alternative candidates.

        Candidate order follows opportunity order.
        The original SQL is preserved exactly.
        """

        candidates: list[StructuralAlternativeCandidate] = []

        for candidate_number, opportunity in enumerate(
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
                StructuralAlternativeCandidate(
                    candidate_id=f"SUBQ-CAND-{candidate_number:04d}",
                    alternative_type=alternative_type,
                    status=CandidateStatus.CANDIDATE,
                    semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
                    evidence_status=opportunity.evidence_status,
                    title=self._build_title(alternative_type),
                    rationale=self._build_rationale(
                        alternative_type,
                    ),
                    source_layer=finding.layer,
                    original_sql=original_sql,
                    alternative_sql=None,
                )
            )

        return StructuralAlternativeResult(
            candidates=candidates,
        )

    @staticmethod
    def _build_title(
        alternative_type: SubqueryAlternativeType,
    ) -> str:
        titles = {
            SubqueryAlternativeType.EXISTS:
                "EXISTS structural alternative candidate",
            SubqueryAlternativeType.IN:
                "IN structural alternative candidate",
            SubqueryAlternativeType.ANY:
                "ANY structural alternative candidate",
            SubqueryAlternativeType.DERIVED_TABLE:
                "Derived-table structural alternative candidate",
        }

        return titles[alternative_type]

    @staticmethod
    def _build_rationale(
        alternative_type: SubqueryAlternativeType,
    ) -> str:
        return (
            f"A {alternative_type.value} subquery structure was identified "
            "and is eligible for later semantic-safety and alternative "
            "validation. No semantic equivalence or performance improvement "
            "has been established at this stage."
        )
