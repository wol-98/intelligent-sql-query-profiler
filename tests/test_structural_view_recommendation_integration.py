from sqlglot import parse_one

from api.schemas.structural_optimization import (
    CandidateStatus,
    SemanticSafetyStatus,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    ViewRecommendationType,
)
from api.services.structural_analysis_enricher import (
    StructuralAnalysisEnricher,
)
from api.services.structural_sql_analyzer import (
    StructuralSQLAnalyzer,
)


def analyze_sql(sql: str):
    expression = parse_one(
        sql,
        dialect="postgres",
    )

    analysis = StructuralSQLAnalyzer().analyze(
        expression,
    )

    result = StructuralAnalysisEnricher().generate_view_recommendations(
        expression,
        analysis,
        sql,
    )

    return expression, analysis, result


def test_aggregated_query_generates_materialized_view_analysis():
    sql = """
    SELECT
        customer_id,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    """

    _, _, result = analyze_sql(sql)

    assert len(result) == 1

    item = result[0]

    assert (
        item.recommendation.recommendation_type
        == ViewRecommendationType.MATERIALIZED_VIEW
    )

    assert (
        item.recommendation.status
        == CandidateStatus.CANDIDATE
    )

    assert (
        item.recommendation.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )

    assert (
        item.semantic_preconditions.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )


def test_reusable_cte_generates_view_analysis():
    sql = """
    WITH paid_orders AS (
        SELECT
            customer_id,
            order_id
        FROM orders
        WHERE status = 'PAID'
    )
    SELECT
        customer_id,
        COUNT(*) AS order_count
    FROM paid_orders
    GROUP BY customer_id
    """

    _, _, result = analyze_sql(sql)

    view_items = [
        item
        for item in result
        if item.recommendation.recommendation_type
        == ViewRecommendationType.VIEW
    ]

    assert view_items

    assert all(
        item.semantic_preconditions.recommendation_type
        == ViewRecommendationType.VIEW
        for item in view_items
    )


def test_filtered_relational_query_generates_view_analysis():
    sql = """
    SELECT
        order_id,
        customer_id
    FROM orders
    WHERE status = 'PAID'
    """

    _, _, result = analyze_sql(sql)

    assert len(result) == 1

    item = result[0]

    assert (
        item.recommendation.recommendation_type
        == ViewRecommendationType.VIEW
    )

    assert (
        item.semantic_preconditions.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )


def test_window_query_generates_view_analysis():
    sql = """
    SELECT
        customer_id,
        order_id,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY order_id
        ) AS rn
    FROM orders
    """

    _, _, result = analyze_sql(sql)

    assert result

    assert any(
        item.recommendation.recommendation_type
        == ViewRecommendationType.VIEW
        for item in result
    )


def test_original_sql_is_preserved():
    sql = """
    SELECT
        customer_id,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    """

    _, _, result = analyze_sql(sql)

    assert result

    assert all(
        item.recommendation.original_sql == sql
        for item in result
    )


def test_candidate_state_is_preserved_after_integration():
    sql = """
    SELECT
        customer_id,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    """

    _, _, result = analyze_sql(sql)

    assert result

    for item in result:
        assert item.recommendation.status == CandidateStatus.CANDIDATE

        assert (
            item.recommendation.semantic_safety
            == SemanticSafetyStatus.NOT_ASSESSED
        )

        assert (
            item.semantic_preconditions.semantic_safety
            == SemanticSafetyStatus.REQUIRES_VALIDATION
        )


def test_integration_does_not_modify_structural_analysis():
    sql = """
    SELECT
        customer_id,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    """

    expression = parse_one(
        sql,
        dialect="postgres",
    )

    analysis = StructuralSQLAnalyzer().analyze(expression)

    original_findings = [
        finding.model_copy(deep=True)
        for finding in analysis.findings
    ]

    StructuralAnalysisEnricher().generate_view_recommendations(
        expression,
        analysis,
        sql,
    )

    assert analysis.findings == original_findings


def test_integration_is_deterministic():
    sql = """
    SELECT
        customer_id,
        COUNT(*) AS order_count
    FROM orders
    WHERE status = 'PAID'
    GROUP BY customer_id
    """

    expression = parse_one(
        sql,
        dialect="postgres",
    )

    analysis = StructuralSQLAnalyzer().analyze(expression)

    enricher = StructuralAnalysisEnricher()

    first = enricher.generate_view_recommendations(
        expression,
        analysis,
        sql,
    )

    second = enricher.generate_view_recommendations(
        expression,
        analysis,
        sql,
    )

    assert first == second
