"""Integration layer for structural analysis classification and opportunities."""

from api.schemas.structural_optimization import (
    StructuralAnalysis,
    StructuralClassificationResult,
    StructuralOpportunityResult,
)
from api.services.structural_finding_classifier import (
    StructuralFindingClassifier,
)
from api.services.structural_opportunity_analyzer import (
    StructuralOpportunityAnalyzer,
)


class StructuralAnalysisEnricher:
    """Integrate structural finding classification and opportunity analysis.

    This service deliberately keeps StructuralAnalysis unchanged. It acts as
    an integration layer between structural analysis, finding classification,
    and structural opportunity analysis without performing optimization,
    benchmarking, or decision-making.
    """

    def __init__(
        self,
        classifier: StructuralFindingClassifier | None = None,
        opportunity_analyzer: StructuralOpportunityAnalyzer | None = None,
    ) -> None:
        self._classifier = classifier or StructuralFindingClassifier()
        self._opportunity_analyzer = (
            opportunity_analyzer or StructuralOpportunityAnalyzer()
        )

    def classify(
        self,
        analysis: StructuralAnalysis,
    ) -> StructuralClassificationResult:
        """Return classifications for the findings in an analysis.

        The original StructuralAnalysis instance is not modified.
        """
        return self._classifier.classify(analysis.findings)

    def analyze_opportunities(
        self,
        analysis: StructuralAnalysis,
    ) -> StructuralOpportunityResult:
        """Return structural optimization-analysis opportunities.

        Classification is performed first using the established classifier,
        then the resulting classifications are passed to the opportunity
        analyzer.

        The original StructuralAnalysis instance is not modified.
        """
        classifications = self._classifier.classify(analysis.findings)

        return self._opportunity_analyzer.analyze(
            analysis,
            classifications,
        )
