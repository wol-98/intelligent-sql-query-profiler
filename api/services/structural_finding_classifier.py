from __future__ import annotations

from api.schemas.structural_optimization import (
    EvidenceQuality,
    EvidenceStatus,
    OptimizationRelevance,
    StructuralClassificationResult,
    StructuralFinding,
    StructuralFindingClassification,
    StructuralFindingClassificationType,
    StructuralLayer,
)


class StructuralFindingClassifier:
    """
    Deterministically classify structural findings and assess their
    evidence quality and potential relevance to later optimization analysis.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate optimization candidates,
      - benchmark alternatives, or
      - make optimization decisions.
    """

    _CLASSIFICATION_BY_LAYER: dict[
        StructuralLayer,
        StructuralFindingClassificationType,
    ] = {
        StructuralLayer.SELECT:
            StructuralFindingClassificationType.DIRECT_OPERATION,
        StructuralLayer.FROM:
            StructuralFindingClassificationType.SOURCE_DEFINITION,
        StructuralLayer.JOIN:
            StructuralFindingClassificationType.RELATIONSHIP,
        StructuralLayer.WHERE:
            StructuralFindingClassificationType.PREDICATE,
        StructuralLayer.GROUP_BY:
            StructuralFindingClassificationType.AGGREGATION,
        StructuralLayer.HAVING:
            StructuralFindingClassificationType.AGGREGATION,
        StructuralLayer.WINDOW:
            StructuralFindingClassificationType.WINDOW_OPERATION,
        StructuralLayer.ORDER_BY:
            StructuralFindingClassificationType.ORDERING,
        StructuralLayer.LIMIT_OFFSET:
            StructuralFindingClassificationType.ROW_LIMITING,
        StructuralLayer.SUBQUERY:
            StructuralFindingClassificationType.NESTED_QUERY,
        StructuralLayer.SET_OPERATION:
            StructuralFindingClassificationType.SET_OPERATION,
    }

    _RELEVANCE_BY_CLASSIFICATION: dict[
        StructuralFindingClassificationType,
        OptimizationRelevance,
    ] = {
        StructuralFindingClassificationType.DIRECT_OPERATION:
            OptimizationRelevance.CONTEXTUAL,
        StructuralFindingClassificationType.SOURCE_DEFINITION:
            OptimizationRelevance.CONTEXTUAL,
        StructuralFindingClassificationType.RELATIONSHIP:
            OptimizationRelevance.POTENTIALLY_RELEVANT,
        StructuralFindingClassificationType.PREDICATE:
            OptimizationRelevance.POTENTIALLY_RELEVANT,
        StructuralFindingClassificationType.AGGREGATION:
            OptimizationRelevance.POTENTIALLY_RELEVANT,
        StructuralFindingClassificationType.WINDOW_OPERATION:
            OptimizationRelevance.POTENTIALLY_RELEVANT,
        StructuralFindingClassificationType.ORDERING:
            OptimizationRelevance.POTENTIALLY_RELEVANT,
        StructuralFindingClassificationType.ROW_LIMITING:
            OptimizationRelevance.POTENTIALLY_RELEVANT,
        StructuralFindingClassificationType.NESTED_QUERY:
            OptimizationRelevance.POTENTIALLY_RELEVANT,
        StructuralFindingClassificationType.SET_OPERATION:
            OptimizationRelevance.CONTEXTUAL,
    }

    def classify(
        self,
        findings: list[StructuralFinding],
    ) -> StructuralClassificationResult:
        """
        Return deterministic classifications for the supplied findings.

        Finding order is preserved. The finding_index identifies the
        corresponding position in the original findings list.
        """
        classifications = [
            self._classify_finding(index, finding)
            for index, finding in enumerate(findings)
        ]

        return StructuralClassificationResult(
            classifications=classifications
        )

    def _classify_finding(
        self,
        finding_index: int,
        finding: StructuralFinding,
    ) -> StructuralFindingClassification:
        classification = self._classification_for(finding)
        evidence_status, evidence_quality = self._evidence_for(finding)

        if evidence_status == EvidenceStatus.INSUFFICIENT:
            relevance = OptimizationRelevance.NOT_ASSESSED
        else:
            relevance = self._RELEVANCE_BY_CLASSIFICATION[classification]

        rationale = self._build_rationale(
            classification=classification,
            evidence_status=evidence_status,
            evidence_quality=evidence_quality,
            relevance=relevance,
        )

        return StructuralFindingClassification(
            finding_index=finding_index,
            classification=classification,
            evidence_status=evidence_status,
            evidence_quality=evidence_quality,
            optimization_relevance=relevance,
            rationale=rationale,
        )

    def _classification_for(
        self,
        finding: StructuralFinding,
    ) -> StructuralFindingClassificationType:
        try:
            return self._CLASSIFICATION_BY_LAYER[finding.layer]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported structural layer: {finding.layer}"
            ) from exc

    @staticmethod
    def _evidence_for(
        finding: StructuralFinding,
    ) -> tuple[EvidenceStatus, EvidenceQuality]:
        evidence = finding.evidence

        if evidence is None or not evidence.strip():
            return EvidenceStatus.INSUFFICIENT, EvidenceQuality.MISSING

        if StructuralFindingClassifier._is_exact_evidence(evidence):
            return EvidenceStatus.COMPLETE, EvidenceQuality.EXACT

        if StructuralFindingClassifier._is_summary_evidence(evidence):
            return EvidenceStatus.PARTIAL, EvidenceQuality.SUMMARY

        return EvidenceStatus.COMPLETE, EvidenceQuality.STRUCTURED

    @staticmethod
    def _is_exact_evidence(evidence: str) -> bool:
        exact_markers = (
            "where=",
            "join=",
            "expressions=",
            "from=",
            "group_by=",
            "having=",
            "window=",
            "order_by=",
            "limit=",
            "offset=",
        )

        return any(marker in evidence for marker in exact_markers)

    @staticmethod
    def _is_summary_evidence(evidence: str) -> bool:
        summary_markers = (
            "subquery_count=",
        )

        return any(marker in evidence for marker in summary_markers)

    @staticmethod
    def _build_rationale(
        *,
        classification: StructuralFindingClassificationType,
        evidence_status: EvidenceStatus,
        evidence_quality: EvidenceQuality,
        relevance: OptimizationRelevance,
    ) -> str:
        if evidence_status == EvidenceStatus.INSUFFICIENT:
            return (
                f"The finding is classified as {classification.value}, "
                "but its structural evidence is insufficient for assessing "
                "optimization relevance."
            )

        if relevance == OptimizationRelevance.POTENTIALLY_RELEVANT:
            return (
                f"The finding is classified as {classification.value} with "
                f"{evidence_quality.value.lower()} structural evidence. "
                "It may be considered by a later optimization analysis, "
                "but this classification does not establish an optimization "
                "problem or recommendation."
            )

        return (
            f"The finding is classified as {classification.value} with "
            f"{evidence_quality.value.lower()} structural evidence and is "
            f"treated as {relevance.value.lower().replace('_', ' ')} "
            "at this analytical stage."
        )
