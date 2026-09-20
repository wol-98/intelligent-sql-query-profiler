from sqlglot import parse_one

from api.schemas.structural_optimization import (
    StructuralAnalysisStatus,
    StructuralLayer,
)
from api.services.structural_sql_analyzer import StructuralSQLAnalyzer


def analyze(sql: str):
    expression = parse_one(sql, dialect="postgres")
    return StructuralSQLAnalyzer().analyze(expression)


def layers(result):
    return set(result.layers_detected)


def test_basic_select_and_where():
    result = analyze(
        """
        SELECT customer_id, total_amount
        FROM orders
        WHERE status = 'completed';
        """
    )

    assert result.status == StructuralAnalysisStatus.ANALYZED
    assert StructuralLayer.SELECT in layers(result)
    assert StructuralLayer.FROM in layers(result)
    assert StructuralLayer.WHERE in layers(result)

    assert result.joins_detected == 0
    assert result.subqueries_detected == 0
    assert result.aggregates_detected == 0
    assert result.window_functions_detected == 0
    assert result.has_order_by is False
    assert result.has_limit is False
    assert result.has_offset is False


def test_join_and_where():
    result = analyze(
        """
        SELECT o.order_id, c.name
        FROM orders o
        JOIN customers c
          ON o.customer_id = c.customer_id
        WHERE o.status = 'completed';
        """
    )

    assert StructuralLayer.SELECT in layers(result)
    assert StructuralLayer.FROM in layers(result)
    assert StructuralLayer.JOIN in layers(result)
    assert StructuralLayer.WHERE in layers(result)

    assert result.joins_detected == 1


def test_aggregation_group_having_order_limit_offset():
    result = analyze(
        """
        SELECT customer_id, COUNT(*) AS order_count
        FROM orders
        WHERE status = 'completed'
        GROUP BY customer_id
        HAVING COUNT(*) > 2
        ORDER BY order_count DESC
        LIMIT 10 OFFSET 5;
        """
    )

    assert StructuralLayer.SELECT in layers(result)
    assert StructuralLayer.FROM in layers(result)
    assert StructuralLayer.WHERE in layers(result)
    assert StructuralLayer.GROUP_BY in layers(result)
    assert StructuralLayer.HAVING in layers(result)
    assert StructuralLayer.ORDER_BY in layers(result)
    assert StructuralLayer.LIMIT_OFFSET in layers(result)

    assert result.aggregates_detected == 2
    assert result.has_order_by is True
    assert result.has_limit is True
    assert result.has_offset is True


def test_window_function():
    result = analyze(
        """
        SELECT
            order_id,
            customer_id,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY order_date DESC
            ) AS rn
        FROM orders;
        """
    )

    assert StructuralLayer.SELECT in layers(result)
    assert StructuralLayer.FROM in layers(result)
    assert StructuralLayer.WINDOW in layers(result)

    assert result.window_functions_detected == 1


def test_subquery():
    result = analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
            WHERE name IS NOT NULL
        );
        """
    )

    assert StructuralLayer.SELECT in layers(result)
    assert StructuralLayer.FROM in layers(result)
    assert StructuralLayer.WHERE in layers(result)
    assert StructuralLayer.SUBQUERY in layers(result)

    assert result.subqueries_detected == 1


def test_set_operation():
    result = analyze(
        """
        SELECT customer_id FROM orders
        UNION
        SELECT customer_id FROM customers;
        """
    )

    assert StructuralLayer.SELECT in layers(result)
    assert StructuralLayer.FROM in layers(result)
    assert StructuralLayer.SET_OPERATION in layers(result)


def test_cte_is_structurally_analyzed():
    result = analyze(
        """
        WITH recent AS (
            SELECT customer_id, order_date
            FROM orders
            WHERE order_date >= DATE '2026-01-01'
        )
        SELECT customer_id, order_date
        FROM recent;
        """
    )

    assert result.status == StructuralAnalysisStatus.ANALYZED
    assert StructuralLayer.SELECT in layers(result)
    assert StructuralLayer.FROM in layers(result)
    assert StructuralLayer.WHERE in layers(result)

    assert result.subqueries_detected == 0


def test_tables_can_be_supplied_by_caller():
    expression = parse_one(
        """
        SELECT customer_id
        FROM orders;
        """,
        dialect="postgres",
    )

    result = StructuralSQLAnalyzer().analyze(
        expression,
        query_type="SELECT",
        tables=["public.orders"],
    )

    assert result.query_type == "SELECT"
    assert result.tables == ["public.orders"]


def test_findings_have_structural_layers():
    result = analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'completed'
        ORDER BY customer_id
        LIMIT 10;
        """
    )

    assert result.findings

    finding_layers = {
        finding.layer
        for finding in result.findings
    }

    assert StructuralLayer.SELECT in finding_layers
    assert StructuralLayer.FROM in finding_layers
    assert StructuralLayer.WHERE in finding_layers
    assert StructuralLayer.ORDER_BY in finding_layers
    assert StructuralLayer.LIMIT_OFFSET in finding_layers
