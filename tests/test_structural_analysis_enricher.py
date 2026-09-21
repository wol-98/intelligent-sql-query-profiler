"""Tests for structural analysis classification integration."""

from sqlglot import parse_one

from api.schemas.structural_optimization import (
    AggregationWindowCharacteristicResult,
    AlternativeType,
    CandidateStatus,
    EvidenceStatus,
    OptimizationCandidate,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    OptimizationRelevance,
    OrderingLimitCharacteristicType,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralClassificationResult,
    StructuralFinding,
    StructuralFindingClassificationType,
    StructuralOpportunityResult,
    SubqueryAlternativeCharacteristicType,
)

from api.services.structural_analysis_enricher import (
    StructuralAnalysisEnricher,
)

from api.services.structural_sql_analyzer import (
    StructuralSQLAnalyzer,
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

    assert [
        item.finding_index
        for item in result.classifications
    ] == [0, 1, 2]

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


def test_generate_candidates_integrates_classification_opportunity_and_generation():
    original_sql = (
        "SELECT customer_id FROM orders WHERE status = 'completed'"
    )

    analysis = StructuralAnalysis(
        query=original_sql,
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

    result = StructuralAnalysisEnricher().generate_candidates(
        analysis,
        original_sql,
    )

    assert isinstance(result, list)

    assert len(result) == 1

    candidate = result[0]

    assert isinstance(candidate, OptimizationCandidate)
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.alternative_type == AlternativeType.INDEX
    assert candidate.source_layer == "WHERE"
    assert candidate.original_sql == original_sql
    assert candidate.optimized_sql is None
    assert candidate.index_ddl is None


def test_analyze_aggregation_window_characteristics_integrates_analyzers():
    sql = """
        SELECT
            customer_id,
            COUNT(*) AS order_count,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY order_date DESC
            ) AS row_num
        FROM orders
        GROUP BY customer_id
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = (
        StructuralAnalysisEnricher()
        .analyze_aggregation_window_characteristics(
            expression,
            analysis,
        )
    )

    assert isinstance(
        result,
        AggregationWindowCharacteristicResult,
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        "GROUPING",
        "AGGREGATE_FUNCTION",
        "WINDOW_FUNCTION",
        "WINDOW_PARTITION",
        "WINDOW_ORDERING",
    ]


def test_analyze_ordering_limit_characteristics_integrates_with_enricher():
    sql = """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        ORDER BY order_date DESC
        LIMIT 10
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = (
        StructuralAnalysisEnricher()
        .analyze_ordering_limit_characteristics(
            expression,
            analysis,
        )
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.ORDERING,
        OrderingLimitCharacteristicType.LIMIT,
        OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT,
        OrderingLimitCharacteristicType.FILTER_WITH_ORDERING,
    ]


def test_analyze_ordering_limit_characteristics_preserves_finding_provenance():
    sql = """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        ORDER BY order_date DESC
        LIMIT 10
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = (
        StructuralAnalysisEnricher()
        .analyze_ordering_limit_characteristics(
            expression,
            analysis,
        )
    )

    ordering_findings = {
        index
        for index, finding in enumerate(analysis.findings)
        if finding.layer == "ORDER_BY"
        and finding.evidence is not None
        and "query_block=1;" in finding.evidence
    }

    filter_ordering = [
        characteristic
        for characteristic in result.characteristics
        if characteristic.characteristic_type
        == OrderingLimitCharacteristicType.FILTER_WITH_ORDERING
    ]

    assert len(filter_ordering) == 1

    assert (
        filter_ordering[0].finding_index
        in ordering_findings
    )


def test_analyze_ordering_limit_characteristics_keeps_nested_query_blocks_separate():
    sql = """
        SELECT *
        FROM (
            SELECT customer_id
            FROM orders
            WHERE status = 'PAID'
            ORDER BY order_date DESC
            LIMIT 5
        ) AS filtered_orders
        ORDER BY customer_id
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = (
        StructuralAnalysisEnricher()
        .analyze_ordering_limit_characteristics(
            expression,
            analysis,
        )
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.ORDERING,
        OrderingLimitCharacteristicType.ORDERING,
        OrderingLimitCharacteristicType.LIMIT,
        OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT,
        OrderingLimitCharacteristicType.FILTER_WITH_ORDERING,
    ]


def test_analyze_ordering_limit_characteristics_does_not_modify_analysis():
    sql = """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        ORDER BY order_date DESC
        LIMIT 10
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    original_findings = [
        (
            finding.finding_type,
            finding.layer,
            finding.severity,
            finding.description,
            finding.evidence,
        )
        for finding in analysis.findings
    ]

    StructuralAnalysisEnricher().analyze_ordering_limit_characteristics(
        expression,
        analysis,
    )

    resulting_findings = [
        (
            finding.finding_type,
            finding.layer,
            finding.severity,
            finding.description,
            finding.evidence,
        )
        for finding in analysis.findings
    ]

    assert resulting_findings == original_findings


def test_analyze_subquery_opportunities_integrates_detection_and_analysis():
    sql = """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM order_items oi
            WHERE oi.order_id = o.order_id
        )
    """

    expression = parse_one(sql, dialect="postgres")

    analysis = StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding(
                "SELECT",
                "query_block=1; expressions=*",
            ),
            _finding(
                "FROM",
                "query_block=1; from=orders AS o",
            ),
            _finding(
                "WHERE",
                "query_block=1; where=WHERE EXISTS (...)",
            ),
            _finding(
                "SELECT",
                "query_block=2; expressions=1",
            ),
            _finding(
                "FROM",
                "query_block=2; from=order_items AS oi",
            ),
            _finding(
                "WHERE",
                "query_block=2; where=WHERE oi.order_id = o.order_id",
            ),
        ],
    )

    enricher = StructuralAnalysisEnricher()

    result = enricher.analyze_subquery_opportunities(
        expression,
        analysis,
    )

    assert isinstance(result, StructuralOpportunityResult)

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        OptimizationOpportunityType.SUBQUERY_EXISTS_ANALYSIS,
    ]

    assert result.opportunities[0].status == (
        OptimizationOpportunityStatus.IDENTIFIED
    )

    assert result.opportunities[0].finding_index == 2


def test_analyze_subquery_opportunities_handles_in():
    sql = """
        SELECT *
        FROM orders
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
        )
    """

    expression = parse_one(sql, dialect="postgres")

    analysis = StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding(
                "SELECT",
                "query_block=1; expressions=*",
            ),
            _finding(
                "FROM",
                "query_block=1; from=orders",
            ),
            _finding(
                "WHERE",
                "query_block=1; where=WHERE customer_id IN (...)",
            ),
            _finding(
                "SELECT",
                "query_block=2; expressions=customer_id",
            ),
            _finding(
                "FROM",
                "query_block=2; from=customers",
            ),
        ],
    )

    result = StructuralAnalysisEnricher().analyze_subquery_opportunities(
        expression,
        analysis,
    )

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS,
    ]


def test_analyze_subquery_opportunities_handles_derived_table():
    sql = """
        SELECT x.customer_id
        FROM (
            SELECT customer_id
            FROM orders
        ) AS x
    """

    expression = parse_one(sql, dialect="postgres")

    analysis = StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            _finding(
                "SELECT",
                "query_block=1; expressions=x.customer_id",
            ),
            _finding(
                "FROM",
                "query_block=1; from=(SELECT ...) AS x",
            ),
            _finding(
                "SELECT",
                "query_block=2; expressions=customer_id",
            ),
            _finding(
                "FROM",
                "query_block=2; from=orders",
            ),
        ],
    )

    result = StructuralAnalysisEnricher().analyze_subquery_opportunities(
        expression,
        analysis,
    )

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        OptimizationOpportunityType.DERIVED_TABLE_ANALYSIS,
    ]


def test_generate_subquery_candidates_integrates_full_pipeline():
    sql = """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM order_items oi
            WHERE oi.order_id = o.order_id
        )
    """

    expression = parse_one(sql, dialect="postgres")

    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = StructuralAnalysisEnricher().generate_subquery_candidates(
        expression,
        analysis,
        sql,
    )

    assert result.candidates

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.candidate_id == "SUBQ-CAND-0001"
    assert candidate.alternative_type.value == "EXISTS"
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety.value == "NOT_ASSESSED"
    assert candidate.original_sql == sql
    assert candidate.alternative_sql is None


def test_generate_subquery_candidates_handles_in():
    sql = """
        SELECT *
        FROM orders
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
        )
    """

    expression = parse_one(sql, dialect="postgres")

    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = StructuralAnalysisEnricher().generate_subquery_candidates(
        expression,
        analysis,
        sql,
    )

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.alternative_type.value == "IN"
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety.value == "NOT_ASSESSED"
    assert candidate.alternative_sql is None


def test_generate_subquery_candidates_handles_any():
    sql = """
        SELECT *
        FROM orders
        WHERE customer_id = ANY (
            SELECT customer_id
            FROM customers
        )
    """

    expression = parse_one(sql, dialect="postgres")

    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = StructuralAnalysisEnricher().generate_subquery_candidates(
        expression,
        analysis,
        sql,
    )

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.candidate_id == "SUBQ-CAND-0001"
    assert candidate.alternative_type.value == "ANY"
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety.value == "NOT_ASSESSED"
    assert candidate.original_sql == sql
    assert candidate.alternative_sql is None


def test_generate_subquery_candidates_handles_derived_table():
    sql = """
        SELECT x.customer_id
        FROM (
            SELECT customer_id
            FROM orders
        ) AS x
    """

    expression = parse_one(sql, dialect="postgres")

    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = StructuralAnalysisEnricher().generate_subquery_candidates(
        expression,
        analysis,
        sql,
    )

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.alternative_type.value == "DERIVED_TABLE"
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety.value == "NOT_ASSESSED"
    assert candidate.alternative_sql is None


def test_generate_subquery_candidates_does_not_create_candidate_for_correlation_alone():
    sql = """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM order_items oi
            WHERE oi.order_id = o.order_id
        )
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = StructuralAnalysisEnricher().generate_subquery_candidates(
        expression,
        analysis,
        sql,
    )

    candidate_types = [
        candidate.alternative_type.value
        for candidate in result.candidates
    ]

    assert candidate_types == ["EXISTS"]


def test_analyze_cte_opportunities_integrates_cte_analysis():
    sql = """
        WITH customer_orders AS (
            SELECT customer_id, COUNT(*) AS order_count
            FROM orders
            GROUP BY customer_id
        )
        SELECT *
        FROM customer_orders
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = StructuralAnalysisEnricher().analyze_cte_opportunities(
        expression,
        analysis,
    )

    assert isinstance(result, StructuralOpportunityResult)

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        OptimizationOpportunityType.CTE_ANALYSIS,
        OptimizationOpportunityType.CTE_ANALYSIS,
    ]

    assert [
        opportunity.finding_index
        for opportunity in result.opportunities
    ] == [0, 1]

    assert all(
        opportunity.status == OptimizationOpportunityStatus.IDENTIFIED
        for opportunity in result.opportunities
    )


def test_analyze_cte_opportunities_integrates_recursive_cte():
    sql = """
        WITH RECURSIVE numbers AS (
            SELECT 1 AS n
            UNION ALL
            SELECT n + 1
            FROM numbers
            WHERE n < 5
        )
        SELECT n
        FROM numbers
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = StructuralAnalysisEnricher().analyze_cte_opportunities(
        expression,
        analysis,
    )

    assert isinstance(result, StructuralOpportunityResult)

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        OptimizationOpportunityType.CTE_ANALYSIS,
        OptimizationOpportunityType.CTE_ANALYSIS,
        OptimizationOpportunityType.CTE_ANALYSIS,
        OptimizationOpportunityType.RECURSIVE_CTE_ANALYSIS,
    ]

    assert [
        opportunity.finding_index
        for opportunity in result.opportunities
    ] == [0, 3, 3, 1]

    assert all(
        opportunity.status == OptimizationOpportunityStatus.IDENTIFIED
        for opportunity in result.opportunities
    )
