"""Integration layer for structural analysis classification, opportunities, and candidates."""

from api.schemas.structural_optimization import (
    OptimizationCandidate,
    StructuralAnalysis,
    StructuralClassificationResult,
    StructuralOpportunityResult,
)
from api.services.structural_candidate_generator import (
    StructuralCandidateGenerator,
)
from api.services.structural_finding_classifier import (
    StructuralFindingClassifier,
)
from api.services.structural_opportunity_analyzer import (
    StructuralOpportunityAnalyzer,
)


class StructuralAnalysisEnricher:
    """Integrate structural analysis classification, opportunities, and candidates.

    This service deliberately keeps StructuralAnalysis unchanged. It acts as
    an integration layer between structural analysis, finding classification,
    structural opportunity analysis, and candidate generation without
    performing SQL execution, benchmarking, or decision-making.
    """

    def __init__(
        self,
        classifier: StructuralFindingClassifier | None = None,
        opportunity_analyzer: StructuralOpportunityAnalyzer | None = None,
        candidate_generator: StructuralCandidateGenerator | None = None,
    ) -> None:
        self._classifier = classifier or StructuralFindingClassifier()
        self._opportunity_analyzer = (
            opportunity_analyzer or StructuralOpportunityAnalyzer()
        )
        self._candidate_generator = (
            candidate_generator or StructuralCandidateGenerator()
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

    def generate_candidates(
        self,
        analysis: StructuralAnalysis,
        original_sql: str,
    ) -> list[OptimizationCandidate]:
        """Generate optimization candidates from structural opportunities.

        The established classification and opportunity-analysis stages are
        executed first. Identified opportunities are then passed to the
        candidate generator together with the original SQL.

        The original StructuralAnalysis instance is not modified.
        """
        classifications = self._classifier.classify(analysis.findings)

        opportunities = self._opportunity_analyzer.analyze(
            analysis,
            classifications,
        )

        return self._candidate_generator.generate(
            analysis,
            opportunities,
            original_sql,
        )
