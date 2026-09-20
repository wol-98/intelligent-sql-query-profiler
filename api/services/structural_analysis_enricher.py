"""Integration layer for structural analysis classification."""

from api.schemas.structural_optimization import (
    StructuralAnalysis,
    StructuralClassificationResult,
)
from api.services.structural_finding_classifier import (
    StructuralFindingClassifier,
)


class StructuralAnalysisEnricher:
    """Classify findings produced by StructuralSQLAnalyzer.

    This service deliberately keeps StructuralAnalysis unchanged. It acts as
    an integration layer between structural analysis and finding
    classification without performing optimization, benchmarking, or
    decision-making.
    """

    def __init__(
        self,
        classifier: StructuralFindingClassifier | None = None,
    ) -> None:
        self._classifier = classifier or StructuralFindingClassifier()

    def classify(
        self,
        analysis: StructuralAnalysis,
    ) -> StructuralClassificationResult:
        """Return classifications for the findings in an analysis.

        The original StructuralAnalysis instance is not modified.
        """
        return self._classifier.classify(analysis.findings)
