"""Integration layer for structural analysis classification, opportunities, and candidates."""

from sqlglot import exp

from api.schemas.structural_optimization import (
    AggregationWindowCharacteristicResult,
    CTECharacteristicResult,
    OptimizationCandidate,
    OrderingLimitCharacteristicResult,
    StructuralAlternativeResult,
    StructuralAnalysis,
    StructuralClassificationResult,
    StructuralOpportunityResult,
    StructuralViewRecommendationResult,
    SubqueryAlternativeCharacteristicResult,
)

from api.services.structural_aggregation_analyzer import (
    StructuralAggregationAnalyzer,
)
from api.services.structural_architectural_opportunity_analyzer import (
    StructuralArchitecturalOpportunityAnalyzer,
)
from api.services.structural_candidate_generator import (
    StructuralCandidateGenerator,
)
from api.services.structural_cte_analyzer import (
    StructuralCTEAnalyzer,
)
from api.services.structural_cte_opportunity_analyzer import (
    StructuralCTEOpportunityAnalyzer,
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
from api.services.structural_subquery_analyzer import (
    StructuralSubqueryAnalyzer,
)
from api.services.structural_subquery_candidate_generator import (
    StructuralSubqueryCandidateGenerator,
)
from api.services.structural_subquery_opportunity_analyzer import (
    StructuralSubqueryOpportunityAnalyzer,
)
from api.services.structural_view_recommendation_generator import (
    StructuralViewRecommendationGenerator,
)
from api.services.structural_view_recommendation_semantic_analyzer import (
    StructuralViewRecommendationAnalysis,
    StructuralViewRecommendationSemanticAnalyzer,
)
from api.services.structural_window_analyzer import (
    StructuralWindowAnalyzer,
)


class StructuralAnalysisEnricher:
    """Integrate structural analysis classification, opportunities, and candidates.

    This service deliberately keeps StructuralAnalysis unchanged. It acts as
    an integration layer between structural analysis, finding classification,
    structural opportunity analysis, candidate generation, aggregation and
    window analysis, ordering/row-limiting analysis, subquery analysis,
    architectural opportunity analysis, CTE analysis, view recommendation
    generation, and semantic-precondition analysis without performing SQL
    execution, benchmarking, or decision-making.
    """

    def __init__(
        self,
        classifier: StructuralFindingClassifier | None = None,
        opportunity_analyzer: StructuralOpportunityAnalyzer | None = None,
        candidate_generator: StructuralCandidateGenerator | None = None,
        aggregation_analyzer: StructuralAggregationAnalyzer | None = None,
        window_analyzer: StructuralWindowAnalyzer | None = None,
        ordering_limit_analyzer: StructuralOrderingLimitAnalyzer | None = None,
        subquery_analyzer: StructuralSubqueryAnalyzer | None = None,
        subquery_opportunity_analyzer: (
            StructuralSubqueryOpportunityAnalyzer | None
        ) = None,
        subquery_candidate_generator: (
            StructuralSubqueryCandidateGenerator | None
        ) = None,
        cte_analyzer: StructuralCTEAnalyzer | None = None,
        cte_opportunity_analyzer: (
            StructuralCTEOpportunityAnalyzer | None
        ) = None,
        architectural_opportunity_analyzer: (
            StructuralArchitecturalOpportunityAnalyzer | None
        ) = None,
        view_recommendation_generator: (
            StructuralViewRecommendationGenerator | None
        ) = None,
        view_recommendation_semantic_analyzer: (
            StructuralViewRecommendationSemanticAnalyzer | None
        ) = None,
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

        self._subquery_analyzer = (
            subquery_analyzer or StructuralSubqueryAnalyzer()
        )

        self._subquery_opportunity_analyzer = (
            subquery_opportunity_analyzer
            or StructuralSubqueryOpportunityAnalyzer()
        )

        self._subquery_candidate_generator = (
            subquery_candidate_generator
            or StructuralSubqueryCandidateGenerator()
        )

        self._cte_analyzer = (
            cte_analyzer or StructuralCTEAnalyzer()
        )

        self._cte_opportunity_analyzer = (
            cte_opportunity_analyzer
            or StructuralCTEOpportunityAnalyzer()
        )

        self._architectural_opportunity_analyzer = (
            architectural_opportunity_analyzer
            or StructuralArchitecturalOpportunityAnalyzer()
        )

        self._view_recommendation_generator = (
            view_recommendation_generator
            or StructuralViewRecommendationGenerator()
        )

        self._view_recommendation_semantic_analyzer = (
            view_recommendation_semantic_analyzer
            or StructuralViewRecommendationSemanticAnalyzer()
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
        """Return generic structural optimization-analysis opportunities.

        Classification is performed first using the established classifier,
        then the resulting classifications are passed to the generic
        opportunity analyzer.

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

    def analyze_subquery_opportunities(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> StructuralOpportunityResult:
        """Return subquery-related structural opportunities.

        Subquery characteristics are detected first and then passed to the
        dedicated subquery opportunity analyzer.

        The original StructuralAnalysis instance is not modified.
        """
        characteristics: SubqueryAlternativeCharacteristicResult = (
            self._subquery_analyzer.analyze(
                expression,
                analysis,
            )
        )

        return self._subquery_opportunity_analyzer.analyze(
            characteristics,
        )

    def analyze_cte_opportunities(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> StructuralOpportunityResult:
        """Return CTE-related structural opportunities.

        CTE characteristics are detected first and then passed to the
        dedicated CTE opportunity analyzer.

        The original StructuralAnalysis instance is not modified.
        """
        characteristics: CTECharacteristicResult = (
            self._cte_analyzer.analyze(
                expression,
                analysis,
            )
        )

        return self._cte_opportunity_analyzer.analyze(
            characteristics,
        )

    def analyze_architectural_opportunities(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ):
        """Return deterministic architectural view-analysis opportunities.

        CTE, aggregation, and window characteristics are derived from the
        supplied SQL AST and StructuralAnalysis, then passed to the dedicated
        architectural opportunity analyzer.

        The original StructuralAnalysis instance is not modified.
        """
        cte_characteristics = self._cte_analyzer.analyze(
            expression,
            analysis,
        )

        aggregation_window_characteristics = (
            self.analyze_aggregation_window_characteristics(
                expression,
                analysis,
            )
        )

        return self._architectural_opportunity_analyzer.analyze(
            analysis,
            cte_characteristics=cte_characteristics,
            aggregation_window_characteristics=(
                aggregation_window_characteristics
            ),
        )

    def generate_view_recommendations(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
        original_sql: str,
    ) -> tuple[StructuralViewRecommendationAnalysis, ...]:
        """Run the complete architectural view recommendation flow.

        The flow derives architectural opportunities, generates VIEW or
        MATERIALIZED VIEW candidates, and attaches deterministic semantic
        precondition analysis.

        The original StructuralAnalysis instance is not modified.

        This integration layer does not:
          - rewrite SQL,
          - create VIEW or MATERIALIZED VIEW DDL,
          - execute SQL,
          - benchmark alternatives,
          - establish semantic equivalence,
          - establish safety, or
          - make production decisions.
        """
        opportunities = self.analyze_architectural_opportunities(
            expression,
            analysis,
        )

        source_layers = {
            index: finding.layer
            for index, finding in enumerate(analysis.findings)
        }

        recommendations: StructuralViewRecommendationResult = (
            self._view_recommendation_generator.generate(
                opportunities,
                original_sql=original_sql,
                source_layers=source_layers,
            )
        )

        return self._view_recommendation_semantic_analyzer.analyze_result(
            recommendations,
        )

    def generate_subquery_candidates(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
        original_sql: str,
    ) -> StructuralAlternativeResult:
        """Generate structural candidates for subquery alternatives.

        Subquery characteristics are detected first, followed by dedicated
        subquery opportunity analysis and deterministic candidate generation.

        Candidates remain unvalidated and do not contain rewritten SQL.
        The original StructuralAnalysis instance is not modified.
        """
        characteristics: SubqueryAlternativeCharacteristicResult = (
            self._subquery_analyzer.analyze(
                expression,
                analysis,
            )
        )

        opportunities = self._subquery_opportunity_analyzer.analyze(
            characteristics,
        )

        return self._subquery_candidate_generator.generate(
            analysis,
            opportunities,
            original_sql,
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
