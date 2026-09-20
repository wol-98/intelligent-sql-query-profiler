from __future__ import annotations

from api.schemas.structural_optimization import (
    EvidenceStatus,
    OpportunityEvidenceScope,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    OptimizationRelevance,
    StructuralAnalysis,
    StructuralClassificationResult,
    StructuralFindingClassificationType,
    StructuralOptimizationOpportunity,
    StructuralOpportunityResult,
)


class StructuralOpportunityAnalyzer:
    """
    Identify structural characteristics that may warrant later
    optimization analysis.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate indexes,
      - rewrite SQL,
      - benchmark alternatives, or
      - make optimization decisions.

    The analyzer consumes the structural analysis and the established
    finding classifications. It does not duplicate classification logic.
    """

    _OPPORTUNITY_BY_CLASSIFICATION = {
       StructuralFindingClassificationType.PREDICATE:
           OptimizationOpportunityType.PREDICATE_ANALYSIS,
       StructuralFindingClassificationType.RELATIONSHIP:
           OptimizationOpportunityType.JOIN_ANALYSIS,
       StructuralFindingClassificationType.AGGREGATION:
           OptimizationOpportunityType.AGGREGATION_ANALYSIS,
       StructuralFindingClassificationType.WINDOW_OPERATION:
           OptimizationOpportunityType.WINDOW_ANALYSIS,
       StructuralFindingClassificationType.ORDERING:
           OptimizationOpportunityType.ORDERING_ANALYSIS,
       StructuralFindingClassificationType.ROW_LIMITING:
           OptimizationOpportunityType.ROW_LIMITING_ANALYSIS,
       StructuralFindingClassificationType.NESTED_QUERY:
           OptimizationOpportunityType.NESTED_QUERY_ANALYSIS,
}

    def analyze(
        self,
        analysis: StructuralAnalysis,
        classifications: StructuralClassificationResult,
    ) -> StructuralOpportunityResult:
        """
        Identify optimization-analysis opportunities from established
        structural findings and classifications.

        Classification order does not need to match the findings list.
        Each classification is linked explicitly through finding_index.
        """
        opportunities: list[StructuralOptimizationOpportunity] = []

        for classification in classifications.classifications:
            finding_index = classification.finding_index

            if finding_index >= len(analysis.findings):
                raise ValueError(
                    "Classification references a finding index that does "
                    f"not exist: {finding_index}"
           )

            opportunity_type = self._OPPORTUNITY_BY_CLASSIFICATION.get(
                classification.classification
           )

            if opportunity_type is None:
                continue

            status = self._status_for(
                evidence_status=classification.evidence_status,
                relevance=classification.optimization_relevance,
            )

            opportunities.append(
                StructuralOptimizationOpportunity(
                    finding_index=finding_index,
                    opportunity_type=opportunity_type,
                    status=status,
                    evidence_status=classification.evidence_status,
                    evidence_scope=OpportunityEvidenceScope.CLASSIFICATION,
                    rationale=self._build_rationale(
                        opportunity_type=opportunity_type,
                        status=status,
                        evidence_status=classification.evidence_status,
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
        relevance: OptimizationRelevance,
    ) -> OptimizationOpportunityStatus:
        if evidence_status == EvidenceStatus.INSUFFICIENT:
            return OptimizationOpportunityStatus.NOT_ASSESSED

        if relevance != OptimizationRelevance.POTENTIALLY_RELEVANT:
            return OptimizationOpportunityStatus.STRUCTURALLY_NEUTRAL

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
                "for further optimization analysis."
            )

        if status == OptimizationOpportunityStatus.STRUCTURALLY_NEUTRAL:
            return (
                f"{opportunity_type.value} is structurally present, "
                "but the established classification does not identify it "
                "as potentially relevant at this analytical stage."
            )

        return (
            f"{opportunity_type.value} was identified from an established "
            "structural classification and may be examined by a later "
            "optimization-analysis stage. This does not establish an "
            "optimization problem or recommendation."
        )
