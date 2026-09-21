from sqlglot import parse_one

from api.schemas.structural_optimization import (
    CTECharacteristicType,
    StructuralLayer,
)
from api.services.structural_cte_analyzer import StructuralCTEAnalyzer
from api.services.structural_sql_analyzer import StructuralSQLAnalyzer


def analyze(sql: str):
    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)
    return expression, analysis


def test_analyzer_detects_cte_definition_and_reference_characteristics():
    sql = """
        WITH customer_orders AS (
            SELECT customer_id
            FROM orders
        )
        SELECT *
        FROM customer_orders
    """

    expression, analysis = analyze(sql)

    result = StructuralCTEAnalyzer().analyze(
        expression,
        analysis,
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        CTECharacteristicType.CTE_DEFINITION,
        CTECharacteristicType.CTE_REFERENCE,
    ]

    assert all(
        characteristic.evidence_status.value == "COMPLETE"
        for characteristic in result.characteristics
    )

    assert all(
        analysis.findings[characteristic.finding_index].layer
        == StructuralLayer.CTE
        for characteristic in result.characteristics
    )


def test_analyzer_detects_multiple_ctes():
    sql = """
        WITH
        customer_orders AS (
            SELECT customer_id
            FROM orders
        ),
        active_customers AS (
            SELECT customer_id
            FROM customers
        )
        SELECT co.customer_id
        FROM customer_orders co
        JOIN active_customers ac
            ON co.customer_id = ac.customer_id
    """

    expression, analysis = analyze(sql)

    result = StructuralCTEAnalyzer().analyze(
        expression,
        analysis,
    )

    types = [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ]

    assert types == [
        CTECharacteristicType.CTE_DEFINITION,
        CTECharacteristicType.CTE_DEFINITION,
        CTECharacteristicType.CTE_REFERENCE,
        CTECharacteristicType.CTE_REFERENCE,
    ]


def test_analyzer_detects_recursive_cte():
    sql = """
        WITH RECURSIVE numbers AS (
            SELECT 1 AS n
            UNION ALL
            SELECT n + 1
            FROM numbers
            WHERE n < 10
        )
        SELECT *
        FROM numbers
    """

    expression, analysis = analyze(sql)

    result = StructuralCTEAnalyzer().analyze(
        expression,
        analysis,
    )

    types = [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ]

    assert CTECharacteristicType.CTE_DEFINITION in types
    assert CTECharacteristicType.CTE_REFERENCE in types
    assert CTECharacteristicType.RECURSIVE_CTE in types


def test_analyzer_returns_empty_result_without_cte():
    sql = """
        SELECT customer_id
        FROM customers
    """

    expression, analysis = analyze(sql)

    result = StructuralCTEAnalyzer().analyze(
        expression,
        analysis,
    )

    assert result.characteristics == []


def test_analyzer_preserves_finding_indices():
    sql = """
        WITH customer_orders AS (
            SELECT customer_id
            FROM orders
        )
        SELECT *
        FROM customer_orders
    """

    expression, analysis = analyze(sql)

    result = StructuralCTEAnalyzer().analyze(
        expression,
        analysis,
    )

    assert len(result.characteristics) == 2

    for characteristic in result.characteristics:
        assert characteristic.finding_index >= 0
        assert characteristic.finding_index < len(analysis.findings)
