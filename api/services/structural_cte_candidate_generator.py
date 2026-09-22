from __future__ import annotations

from api.schemas.structural_optimization import (
    CandidateStatus,
    CTEAlternativeType,
    EvidenceStatus,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    SemanticSafetyStatus,
    StructuralAnalysis,
    StructuralCTEAlternativeCandidate,
    StructuralCTEAlternativeResult,
    StructuralOpportunityResult,
)


class StructuralCTECandidateGenerator:
    """
    Generate deterministic structural candidates for CTE alternatives.

    This service is analytical only. It does not:
      - execute SQL,
      - rewrite SQL,
      - claim semantic equivalence,
      - benchmark alternatives,
      - validate performance, or
      - make optimization decisions.

    Generated candidates remain explicitly unvalidated until later
    semantic-safety and alternative-validation stages.
    """

    _ALTERNATIVE_BY_OPPORTUNITY = {
        OptimizationOpportunityType.CTE_ANALYSIS: CTEAlternativeType.CTE,
        OptimizationOpportunityType.RECURSIVE_CTE_ANALYSIS: (
            CTEAlternativeType.RECURSIVE_CTE
        ),
    }

    def generate(
        self,
        analysis: StructuralAnalysis,
        opportunities: StructuralOpportunityResult,
        original_sql: str,
    ) -> StructuralCTEAlternativeResult:
        """
        Generate deterministic CTE alternative candidates.

        Candidate order follows opportunity order.
        The original SQL is preserved exactly.
        """

        candidates: list[StructuralCTEAlternativeCandidate] = []

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

            candidates.append(
                StructuralCTEAlternativeCandidate(
                    candidate_id=f"CTE-CAND-{candidate_number:04d}",
                    alternative_type=alternative_type,
                    status=CandidateStatus.CANDIDATE,
                    semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
                    evidence_status=opportunity.evidence_status,
                    title=self._build_title(alternative_type),
                    rationale=self._build_rationale(alternative_type),
                    source_layer=analysis.findings[
                        opportunity.finding_index
                    ].layer,
                    original_sql=original_sql,
                    alternative_sql=None,
                )
            )

        return StructuralCTEAlternativeResult(
            candidates=candidates,
        )

    @staticmethod
    def _build_title(
        alternative_type: CTEAlternativeType,
    ) -> str:
        titles = {
            CTEAlternativeType.CTE:
                "CTE structural alternative candidate",
            CTEAlternativeType.RECURSIVE_CTE:
                "Recursive CTE structural alternative candidate",
        }

        return titles[alternative_type]

    @staticmethod
    def _build_rationale(
        alternative_type: CTEAlternativeType,
    ) -> str:
        if alternative_type == CTEAlternativeType.RECURSIVE_CTE:
            return (
                "A recursive CTE structure was identified and is eligible "
                "for later structural and semantic validation before any "
                "alternative is considered. No semantic equivalence or "
                "performance improvement has been established at this stage."
            )

        return (
            "A CTE structure was identified and is eligible for later "
            "semantic-safety and alternative validation. No semantic "
            "equivalence or performance improvement has been established "
            "at this stage."
        )
