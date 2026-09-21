from __future__ import annotations

from api.schemas.structural_optimization import (
    EvidenceStatus,
    OpportunityEvidenceScope,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    StructuralOptimizationOpportunity,
    StructuralOpportunityResult,
    SubqueryAlternativeCharacteristicResult,
    SubqueryAlternativeCharacteristicType,
)


class StructuralSubqueryOpportunityAnalyzer:
    """
    Identify subquery-related structures that may warrant later
    alternative-analysis work.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - rewrite SQL,
      - generate candidates,
      - benchmark alternatives, or
      - make optimization decisions.

    It consumes the structural subquery characteristics produced by
    StructuralSubqueryAnalyzer.
    """

    _OPPORTUNITY_BY_CHARACTERISTIC = {
        SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE:
            OptimizationOpportunityType.SUBQUERY_EXISTS_ANALYSIS,
        SubqueryAlternativeCharacteristicType.IN_PREDICATE:
            OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS,
        SubqueryAlternativeCharacteristicType.ANY_PREDICATE:
            OptimizationOpportunityType.SUBQUERY_ANY_ANALYSIS,
        SubqueryAlternativeCharacteristicType.DERIVED_TABLE:
            OptimizationOpportunityType.DERIVED_TABLE_ANALYSIS,
    }

    def analyze(
        self,
        characteristics: SubqueryAlternativeCharacteristicResult,
    ) -> StructuralOpportunityResult:
        """
        Identify deterministic subquery-analysis opportunities.

        Characteristics that do not have a direct opportunity mapping,
        such as CORRELATED_SUBQUERY, are retained as structural evidence
        for later stages but do not independently create an opportunity.
        """

        opportunities: list[StructuralOptimizationOpportunity] = []

        for characteristic in characteristics.characteristics:
            opportunity_type = self._OPPORTUNITY_BY_CHARACTERISTIC.get(
                characteristic.characteristic_type
            )

            if opportunity_type is None:
                continue

            status = self._status_for(
                evidence_status=characteristic.evidence_status,
            )

            opportunities.append(
                StructuralOptimizationOpportunity(
                    finding_index=characteristic.finding_index,
                    opportunity_type=opportunity_type,
                    status=status,
                    evidence_status=characteristic.evidence_status,
                    evidence_scope=OpportunityEvidenceScope.FINDING,
                    rationale=self._build_rationale(
                        opportunity_type=opportunity_type,
                        status=status,
                        evidence_status=characteristic.evidence_status,
                    ),
                )
            )

        return StructuralOpportunityResult(
            opportunities=opportunities
        )

    @staticmethod
    def _status_for(
        *,
        evidence_status: EvidenceStatus,
    ) -> OptimizationOpportunityStatus:
        if evidence_status == EvidenceStatus.INSUFFICIENT:
            return OptimizationOpportunityStatus.NOT_ASSESSED

        return OptimizationOpportunityStatus.IDENTIFIED

    @staticmethod
    def _build_rationale(
        *,
        opportunity_type: OptimizationOpportunityType,
        status: OptimizationOpportunityStatus,
        evidence_status: EvidenceStatus,
    ) -> str:
        if status == OptimizationOpportunityStatus.NOT_ASSESSED:
            return (
                f"{opportunity_type.value} was structurally identified, "
                f"but the available evidence is "
                f"{evidence_status.value.lower()} and is insufficient "
                "for further alternative analysis."
            )

        return (
            f"{opportunity_type.value} was identified from an established "
            "subquery structural characteristic and may be examined by a "
            "later alternative-analysis stage. This does not establish "
            "semantic equivalence, performance improvement, or a "
            "recommendation."
        )
