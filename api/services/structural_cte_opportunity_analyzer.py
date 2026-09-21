from api.schemas.structural_optimization import (
    CTECharacteristicType,
    CTECharacteristicResult,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    OpportunityEvidenceScope,
    StructuralOpportunityResult,
    StructuralOptimizationOpportunity,
)


class StructuralCTEOpportunityAnalyzer:
    """Analyze CTE characteristics for structural optimization opportunities.

    This service is analytical only. It does not generate SQL rewrites,
    establish semantic equivalence, benchmark queries, or make production
    decisions.
    """

    _OPPORTUNITY_BY_CHARACTERISTIC = {
        CTECharacteristicType.CTE_DEFINITION: (
            OptimizationOpportunityType.CTE_ANALYSIS
        ),
        CTECharacteristicType.CTE_REFERENCE: (
            OptimizationOpportunityType.CTE_ANALYSIS
        ),
        CTECharacteristicType.RECURSIVE_CTE: (
            OptimizationOpportunityType.RECURSIVE_CTE_ANALYSIS
        ),
    }

    def analyze(
        self,
        characteristics: CTECharacteristicResult,
    ) -> StructuralOpportunityResult:
        """Convert CTE characteristics into deterministic opportunities."""

        opportunities: list[StructuralOptimizationOpportunity] = []

        for characteristic in characteristics.characteristics:
            opportunity_type = self._OPPORTUNITY_BY_CHARACTERISTIC.get(
                characteristic.characteristic_type
            )

            if opportunity_type is None:
                continue

            if (
                characteristic.evidence_status.value == "INSUFFICIENT"
            ):
                status = OptimizationOpportunityStatus.NOT_ASSESSED
            else:
                status = OptimizationOpportunityStatus.IDENTIFIED

            opportunities.append(
                StructuralOptimizationOpportunity(
                    finding_index=characteristic.finding_index,
                    opportunity_type=opportunity_type,
                    status=status,
                    evidence_status=characteristic.evidence_status,
                    evidence_scope=OpportunityEvidenceScope.FINDING,
                    rationale=self._rationale(
                        characteristic.characteristic_type,
                        status,
                    ),
                )
            )

        return StructuralOpportunityResult(
            opportunities=opportunities
        )

    @staticmethod
    def _rationale(
        characteristic_type: CTECharacteristicType,
        status: OptimizationOpportunityStatus,
    ) -> str:
        if status == OptimizationOpportunityStatus.NOT_ASSESSED:
            return (
                f"{characteristic_type.value} was identified, but the "
                "available evidence is insufficient for further "
                "structural opportunity assessment."
            )

        if characteristic_type == CTECharacteristicType.CTE_DEFINITION:
            return (
                "A CTE definition is present and is eligible for "
                "further structural analysis. No rewrite or performance "
                "conclusion is established."
            )

        if characteristic_type == CTECharacteristicType.CTE_REFERENCE:
            return (
                "A reference to a defined CTE is present and is eligible "
                "for further structural analysis. No rewrite or "
                "performance conclusion is established."
            )

        if characteristic_type == CTECharacteristicType.RECURSIVE_CTE:
            return (
                "A recursive CTE is present and requires dedicated "
                "structural and semantic analysis before any alternative "
                "can be considered."
            )

        return (
            f"{characteristic_type.value} is eligible for further "
            "structural analysis."
        )
