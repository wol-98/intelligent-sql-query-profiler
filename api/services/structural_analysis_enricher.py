"""Integration layer for structural analysis classification, opportunities, and candidates."""

from sqlglot import exp

from api.schemas.structural_optimization import (
    AggregationWindowCharacteristicResult,
    OptimizationCandidate,
    OrderingLimitCharacteristicResult,
    StructuralAnalysis,
    StructuralClassificationResult,
    StructuralOpportunityResult,
)
from api.services.structural_aggregation_analyzer import (
    StructuralAggregationAnalyzer,
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
from api.services.structural_ordering_limit_analyzer import (
    StructuralOrderingLimitAnalyzer,
)
from api.services.structural_window_analyzer import (
    StructuralWindowAnalyzer,
)


class StructuralAnalysisEnricher:
    """Integrate structural analysis classification, opportunities, and candidates.

    This service deliberately keeps StructuralAnalysis unchanged. It acts as
    an integration layer between structural analysis, finding classification,
    structural opportunity analysis, candidate generation, aggregation and
    window analysis, and ordering/row-limiting analysis without performing
    SQL execution, benchmarking, or decision-making.
    """

    def __init__(
        self,
        classifier: StructuralFindingClassifier | None = None,
        opportunity_analyzer: StructuralOpportunityAnalyzer | None = None,
        candidate_generator: StructuralCandidateGenerator | None = None,
        aggregation_analyzer: StructuralAggregationAnalyzer | None = None,
        window_analyzer: StructuralWindowAnalyzer | None = None,
        ordering_limit_analyzer: StructuralOrderingLimitAnalyzer | None = None,
    ) -> None:
        self._classifier = classifier or StructuralFindingClassifier()
        self._opportunity_analyzer = (
            opportunity_analyzer or StructuralOpportunityAnalyzer()
        )
        self._candidate_generator = (
            candidate_generator or StructuralCandidateGenerator()
        )
        self._aggregation_analyzer = (
            aggregation_analyzer or StructuralAggregationAnalyzer()
        )
        self._window_analyzer = (
            window_analyzer or StructuralWindowAnalyzer()
        )
        self._ordering_limit_analyzer = (
            ordering_limit_analyzer or StructuralOrderingLimitAnalyzer()
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

    def analyze_aggregation_window_characteristics(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> AggregationWindowCharacteristicResult:
        """Return aggregation and window characteristics for a SQL AST.

        The established aggregation and window analyzers are executed
        independently and their results are combined without modifying the
        original StructuralAnalysis instance.
        """
        aggregation_result = self._aggregation_analyzer.analyze(
            expression,
            analysis,
        )

        window_result = self._window_analyzer.analyze(
            expression,
            analysis,
        )

        return AggregationWindowCharacteristicResult(
            characteristics=[
                *aggregation_result.characteristics,
                *window_result.characteristics,
            ]
        )

    def analyze_ordering_limit_characteristics(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> OrderingLimitCharacteristicResult:
        """Return ordering and row-limiting characteristics for a SQL AST.

        The established ordering/row-limiting analyzer is executed without
        modifying the original StructuralAnalysis instance.
        """
        return self._ordering_limit_analyzer.analyze(
            expression,
            analysis,
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
