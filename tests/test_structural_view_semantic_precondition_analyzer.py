from api.schemas.structural_optimization import (
    SemanticSafetyStatus,
    ViewRecommendationType,
)
from api.services.structural_view_semantic_precondition_analyzer import (
    StructuralViewSemanticPreconditionAnalyzer,
)
from api.services.structural_view_semantic_preconditions import (
    StructuralViewSemanticPreconditionRuleEngine,
)


def finding_map(result):
    return {
        finding.name: finding
        for finding in result.findings
    }


def test_view_analyzer_detects_basic_query_structure():
    sql = """
    SELECT customer_id AS customer,
           COUNT(*) AS order_count
    FROM orders
    WHERE status = 'PAID'
    GROUP BY customer_id
    """

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.VIEW,
    )

    findings = finding_map(result)

    assert result.semantic_safety == SemanticSafetyStatus.REQUIRES_VALIDATION
    assert findings["PROJECTED_COLUMNS"].detected is True
    assert findings["PROJECTED_ALIASES"].detected is True
    assert findings["QUERY_SCOPE"].detected is True
    assert findings["SOURCE_DEPENDENCIES"].detected is True
    assert findings["FILTER_PREDICATES"].detected is True
    assert findings["GROUPING_AGGREGATION"].detected is True


def test_analyzer_detects_join_and_having():
    sql = """
    SELECT c.customer_id, COUNT(*) AS order_count
    FROM customers c
    JOIN orders o
      ON o.customer_id = c.customer_id
    GROUP BY c.customer_id
    HAVING COUNT(*) > 5
    """

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.VIEW,
    )

    findings = finding_map(result)

    assert findings["JOIN_SEMANTICS"].detected is True
    assert findings["GROUPING_AGGREGATION"].detected is True
    assert findings["HAVING_FILTER"].detected is True


def test_analyzer_detects_window_distinct_order_and_limit():
    sql = """
    SELECT DISTINCT
           customer_id,
           ROW_NUMBER() OVER (
               PARTITION BY customer_id
               ORDER BY order_id
           ) AS rn
    FROM orders
    ORDER BY customer_id
    LIMIT 10
    OFFSET 5
    """

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.VIEW,
    )

    findings = finding_map(result)

    assert findings["WINDOW_EXPRESSIONS"].detected is True
    assert findings["DISTINCT_SEMANTICS"].detected is True
    assert findings["ORDERING_BEHAVIOR"].detected is True
    assert findings["ROW_LIMITING"].detected is True


def test_analyzer_detects_set_operations():
    sql = """
    SELECT customer_id
    FROM customers
    UNION
    SELECT customer_id
    FROM archived_customers
    """

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.VIEW,
    )

    findings = finding_map(result)

    assert findings["SET_OPERATION_SEMANTICS"].detected is True


def test_analyzer_detects_nested_query():
    sql = """
    SELECT customer_id
    FROM (
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
    ) AS paid_orders
    """

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.VIEW,
    )

    findings = finding_map(result)

    assert findings["NESTED_QUERY_SEMANTICS"].detected is True


def test_analyzer_detects_cte_as_nested_query_structure():
    sql = """
    WITH paid_orders AS (
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
    )
    SELECT customer_id
    FROM paid_orders
    """

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.VIEW,
    )

    findings = finding_map(result)

    assert findings["NESTED_QUERY_SEMANTICS"].detected is True
    assert findings["SOURCE_DEPENDENCIES"].detected is True


def test_analyzer_reports_absent_optional_structures_as_false():
    sql = "SELECT customer_id FROM customers"

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.VIEW,
    )

    findings = finding_map(result)

    assert findings["PROJECTED_COLUMNS"].detected is True
    assert findings["QUERY_SCOPE"].detected is True
    assert findings["SOURCE_DEPENDENCIES"].detected is True

    assert findings["PROJECTED_ALIASES"].detected is False
    assert findings["FILTER_PREDICATES"].detected is False
    assert findings["JOIN_SEMANTICS"].detected is False
    assert findings["GROUPING_AGGREGATION"].detected is False
    assert findings["HAVING_FILTER"].detected is False
    assert findings["WINDOW_EXPRESSIONS"].detected is False
    assert findings["DISTINCT_SEMANTICS"].detected is False
    assert findings["SET_OPERATION_SEMANTICS"].detected is False
    assert findings["NESTED_QUERY_SEMANTICS"].detected is False
    assert findings["ORDERING_BEHAVIOR"].detected is False
    assert findings["ROW_LIMITING"].detected is False


def test_materialized_view_reports_operational_conditions_as_unestablished():
    sql = """
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    """

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.MATERIALIZED_VIEW,
    )

    findings = finding_map(result)

    assert result.semantic_safety == SemanticSafetyStatus.REQUIRES_VALIDATION

    assert findings["MATERIALIZATION_BEHAVIOR"].detected is False
    assert findings["REFRESH_BEHAVIOR"].detected is False
    assert findings["DATA_FRESHNESS_REQUIREMENTS"].detected is False


def test_materialized_view_preserves_structural_analysis_conditions():
    sql = """
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    WHERE status = 'PAID'
    GROUP BY customer_id
    """

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.MATERIALIZED_VIEW,
    )

    findings = finding_map(result)

    assert findings["PROJECTED_COLUMNS"].detected is True
    assert findings["PROJECTED_ALIASES"].detected is True
    assert findings["FILTER_PREDICATES"].detected is True
    assert findings["GROUPING_AGGREGATION"].detected is True


def test_invalid_sql_is_not_assessed():
    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        "SELECT FROM",
        ViewRecommendationType.VIEW,
    )

    assert result.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert result.findings == ()


def test_missing_rule_is_not_assessed():
    engine = StructuralViewSemanticPreconditionRuleEngine()

    analyzer = StructuralViewSemanticPreconditionAnalyzer(
        rule_engine=engine
    )

    result = analyzer.analyze(
        "SELECT customer_id FROM customers",
        ViewRecommendationType.VIEW,
    )

    assert result.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert result.findings == ()


def test_analysis_is_deterministic():
    sql = """
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    WHERE status = 'PAID'
    GROUP BY customer_id
    ORDER BY customer_id
    LIMIT 10
    """

    analyzer = StructuralViewSemanticPreconditionAnalyzer()

    first = analyzer.analyze(
        sql,
        ViewRecommendationType.VIEW,
    )
    second = analyzer.analyze(
        sql,
        ViewRecommendationType.VIEW,
    )

    assert first == second


def test_semantic_analysis_does_not_claim_safety():
    sql = "SELECT customer_id FROM customers"

    result = StructuralViewSemanticPreconditionAnalyzer().analyze(
        sql,
        ViewRecommendationType.VIEW,
    )

    assert result.semantic_safety == SemanticSafetyStatus.REQUIRES_VALIDATION
    assert result.semantic_safety != SemanticSafetyStatus.NOT_ASSESSED
