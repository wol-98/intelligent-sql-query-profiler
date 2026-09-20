"""Tests for structural analysis classification integration."""

from api.schemas.structural_optimization import (
    EvidenceStatus,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    OptimizationRelevance,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralClassificationResult,
    StructuralFinding,
    StructuralFindingClassificationType,
    StructuralOpportunityResult,
)

from api.services.structural_analysis_enricher import (
    StructuralAnalysisEnricher,
)


def _finding(layer: str, evidence: str) -> StructuralFinding:
    return StructuralFinding(
        finding_type=layer,
        layer=layer,
        severity="INFO",
        description=f"Structural finding for {layer}",
        evidence=evidence,
    )


def test_analyze_opportunities_integrates_classification_and_opportunity_analysis():
    analysis = StructuralAnalysis(
        query=(
            "SELECT o.customer_id, COUNT(*) "
            "FROM orders o "
            "JOIN customers c "
            "ON o.customer_id = c.customer_id "
            "WHERE o.status = 'completed' "
            "GROUP BY o.customer_id "
            "ORDER BY COUNT(*) DESC "
            "LIMIT 10"
        ),
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding(
                "SELECT",
                "expressions=o.customer_id, COUNT(*)",
            ),
            _finding(
                "FROM",
                "from=orders AS o",
            ),
            _finding(
                "JOIN",
                "join=JOIN customers AS c ON "
                "o.customer_id = c.customer_id",
            ),
            _finding(
                "WHERE",
                "where=WHERE o.status = 'completed'",
            ),
            _finding(
                "GROUP_BY",
                "group_by=GROUP BY o.customer_id",
            ),
            _finding(
                "ORDER_BY",
                "order_by=ORDER BY COUNT(*) DESC",
            ),
            _finding(
                "LIMIT_OFFSET",
                "limit=LIMIT 10",
            ),
        ],
    )

    result = StructuralAnalysisEnricher().analyze_opportunities(analysis)

    assert isinstance(result, StructuralOpportunityResult)

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        OptimizationOpportunityType.JOIN_ANALYSIS,
        OptimizationOpportunityType.PREDICATE_ANALYSIS,
        OptimizationOpportunityType.AGGREGATION_ANALYSIS,
        OptimizationOpportunityType.ORDERING_ANALYSIS,
        OptimizationOpportunityType.ROW_LIMITING_ANALYSIS,
    ]

    assert [
        opportunity.finding_index
        for opportunity in result.opportunities
    ] == [2, 3, 4, 5, 6]

    assert all(
        opportunity.status == OptimizationOpportunityStatus.IDENTIFIED
        for opportunity in result.opportunities
    )


def test_classifies_all_findings_and_preserves_indexes() -> None:
    analysis = StructuralAnalysis(
        query="SELECT customer_id FROM orders WHERE status = 'completed'",
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding(
                "SELECT",
                "expressions=customer_id",
            ),
            _finding(
                "FROM",
                "from=orders",
            ),
            _finding(
                "WHERE",
                "where=status = 'completed'",
            ),
        ],
    )

    enricher = StructuralAnalysisEnricher()

    result = enricher.classify(analysis)

    assert len(result.classifications) == len(analysis.findings)

    assert [item.finding_index for item in result.classifications] == [0, 1, 2]

    assert [
        item.classification
        for item in result.classifications
    ] == [
        StructuralFindingClassificationType.DIRECT_OPERATION,
        StructuralFindingClassificationType.SOURCE_DEFINITION,
        StructuralFindingClassificationType.PREDICATE,
    ]


def test_preserves_query_block_evidence() -> None:
    analysis = StructuralAnalysis(
        query=(
            "SELECT customer_id "
            "FROM orders "
            "WHERE customer_id IN "
            "(SELECT customer_id FROM customers WHERE name IS NOT NULL)"
        ),
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding(
                "WHERE",
                (
                    "query_block=1; "
                    "where=WHERE customer_id IN "
                    "(SELECT customer_id FROM customers "
                    "WHERE NOT name IS NULL)"
                ),
            ),
            _finding(
                "WHERE",
                "query_block=2; where=WHERE NOT name IS NULL",
            ),
        ],
    )

    original_evidence = [
        finding.evidence
        for finding in analysis.findings
    ]

    result = StructuralAnalysisEnricher().classify(analysis)

    assert len(result.classifications) == 2

    assert all(
        item.classification
        == StructuralFindingClassificationType.PREDICATE
        for item in result.classifications
    )

    assert [
        finding.evidence
        for finding in analysis.findings
    ] == original_evidence


def test_classifies_multiple_structural_layers() -> None:
    analysis = StructuralAnalysis(
        query=(
            "SELECT o.customer_id, COUNT(*) "
            "FROM orders o "
            "JOIN customers c ON o.customer_id = c.customer_id "
            "WHERE o.status = 'completed' "
            "GROUP BY o.customer_id "
            "ORDER BY COUNT(*) DESC "
            "LIMIT 10"
        ),
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding("SELECT", "expressions=o.customer_id, COUNT(*)"),
            _finding("FROM", "from=orders AS o"),
            _finding(
                "JOIN",
                "join=JOIN customers AS c ON o.customer_id = c.customer_id",
            ),
            _finding(
                "WHERE",
                "where=WHERE o.status = 'completed'",
            ),
            _finding(
                "GROUP_BY",
                "group_by=GROUP BY o.customer_id",
            ),
            _finding(
                "ORDER_BY",
                "order_by=ORDER BY COUNT(*) DESC",
            ),
            _finding(
                "LIMIT_OFFSET",
                "limit=LIMIT 10",
            ),
        ],
    )

    result = StructuralAnalysisEnricher().classify(analysis)

    assert [
        item.classification
        for item in result.classifications
    ] == [
        StructuralFindingClassificationType.DIRECT_OPERATION,
        StructuralFindingClassificationType.SOURCE_DEFINITION,
        StructuralFindingClassificationType.RELATIONSHIP,
        StructuralFindingClassificationType.PREDICATE,
        StructuralFindingClassificationType.AGGREGATION,
        StructuralFindingClassificationType.ORDERING,
        StructuralFindingClassificationType.ROW_LIMITING,
    ]


def test_nested_query_findings_are_classified() -> None:
    analysis = StructuralAnalysis(
        query=(
            "SELECT customer_id "
            "FROM orders "
            "WHERE customer_id IN "
            "(SELECT customer_id FROM customers WHERE name IS NOT NULL)"
        ),
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding(
                "SUBQUERY",
                "subquery_count=1",
            ),
            _finding(
                "WHERE",
                "query_block=1; where=WHERE customer_id IN (...)",
            ),
            _finding(
                "WHERE",
                "query_block=2; where=WHERE NOT name IS NULL",
            ),
        ],
    )

    result = StructuralAnalysisEnricher().classify(analysis)

    assert [
        item.classification
        for item in result.classifications
    ] == [
        StructuralFindingClassificationType.NESTED_QUERY,
        StructuralFindingClassificationType.PREDICATE,
        StructuralFindingClassificationType.PREDICATE,
    ]

    assert (
        result.classifications[0].evidence_status
        == EvidenceStatus.PARTIAL
    )

    assert (
       result.classifications[0].optimization_relevance
       == OptimizationRelevance.POTENTIALLY_RELEVANT
   )


def test_cte_source_definition_is_classified() -> None:
    analysis = StructuralAnalysis(
        query=(
            "WITH recent_orders AS "
            "(SELECT customer_id FROM orders WHERE status = 'completed') "
            "SELECT customer_id FROM recent_orders"
        ),
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding(
                "FROM",
                "from=recent_orders",
            ),
            _finding(
                "WHERE",
                "query_block=1; where=WHERE status = 'completed'",
            ),
        ],
    )

    result = StructuralAnalysisEnricher().classify(analysis)

    assert len(result.classifications) == 2

    assert (
        result.classifications[0].classification
        == StructuralFindingClassificationType.SOURCE_DEFINITION
    )

    assert (
        result.classifications[1].classification
        == StructuralFindingClassificationType.PREDICATE
    )


def test_empty_analysis_returns_empty_classification_result() -> None:
    analysis = StructuralAnalysis(
        query="SELECT 1",
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[],
    )

    result = StructuralAnalysisEnricher().classify(analysis)

    assert result.classifications == []


def test_original_analysis_is_not_modified() -> None:
    analysis = StructuralAnalysis(
        query="SELECT customer_id FROM orders WHERE status = 'completed'",
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding("SELECT", "expressions=customer_id"),
            _finding("FROM", "from=orders"),
            _finding(
                "WHERE",
                "where=WHERE status = 'completed'",
            ),
        ],
    )

    original_findings = list(analysis.findings)
    original_values = [
        finding.model_dump()
        for finding in analysis.findings
    ]

    result = StructuralAnalysisEnricher().classify(analysis)

    assert result.classifications

    assert analysis.findings == original_findings

    assert [
        finding.model_dump()
        for finding in analysis.findings
    ] == original_values


def test_classification_indexes_match_original_findings() -> None:
    analysis = StructuralAnalysis(
        query="SELECT customer_id FROM orders",
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding("SELECT", "expressions=customer_id"),
            _finding("FROM", "from=orders"),
        ],
    )

    result = StructuralAnalysisEnricher().classify(analysis)

    for classification in result.classifications:
        finding = analysis.findings[classification.finding_index]

        assert classification.finding_index >= 0
        assert finding.layer in {
            "SELECT",
            "FROM",
            "JOIN",
            "WHERE",
            "GROUP_BY",
            "HAVING",
            "WINDOW",
            "ORDER_BY",
            "LIMIT_OFFSET",
            "SUBQUERY",
            "SET_OPERATION",
        }


def test_classifier_can_be_injected() -> None:
    class RecordingClassifier:
        def __init__(self) -> None:
            self.received = None

        def classify(self, findings):
            self.received = findings
            return StructuralClassificationResult(classifications=[])

    classifier = RecordingClassifier()
    enricher = StructuralAnalysisEnricher(classifier=classifier)

    analysis = StructuralAnalysis(
        query="SELECT 1",
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding("SELECT", "expressions=1"),
        ],
    )

    result = enricher.classify(analysis)

    assert result.classifications == []
    assert classifier.received is analysis.findings
