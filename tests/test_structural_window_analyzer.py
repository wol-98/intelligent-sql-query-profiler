from sqlglot import parse_one

from api.schemas.structural_optimization import (
    AggregationWindowCharacteristicType,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralFinding,
    StructuralLayer,
)
from api.services.structural_sql_analyzer import StructuralSQLAnalyzer
from api.services.structural_window_analyzer import StructuralWindowAnalyzer


def _analyze(sql: str):
    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = StructuralWindowAnalyzer().analyze(
        expression,
        analysis,
    )

    return expression, analysis, result


def _types(result):
    return [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ]


def test_window_function_creates_window_function_characteristic():
    _, _, result = _analyze(
        """
        SELECT
            customer_id,
            ROW_NUMBER() OVER (ORDER BY order_date) AS rn
        FROM orders
        """
    )

    assert _types(result) == [
        AggregationWindowCharacteristicType.WINDOW_FUNCTION,
        AggregationWindowCharacteristicType.WINDOW_ORDERING,
    ]


def test_window_partition_creates_partition_characteristic():
    _, _, result = _analyze(
        """
        SELECT
            customer_id,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
            ) AS rn
        FROM orders
        """
    )

    assert _types(result) == [
        AggregationWindowCharacteristicType.WINDOW_FUNCTION,
        AggregationWindowCharacteristicType.WINDOW_PARTITION,
    ]


def test_window_ordering_creates_ordering_characteristic():
    _, _, result = _analyze(
        """
        SELECT
            order_id,
            ROW_NUMBER() OVER (
                ORDER BY order_date
            ) AS rn
        FROM orders
        """
    )

    assert _types(result) == [
        AggregationWindowCharacteristicType.WINDOW_FUNCTION,
        AggregationWindowCharacteristicType.WINDOW_ORDERING,
    ]


def test_window_with_partition_and_ordering_creates_all_three():
    _, _, result = _analyze(
        """
        SELECT
            customer_id,
            SUM(total_amount) OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS running_total
        FROM orders
        """
    )

    assert _types(result) == [
        AggregationWindowCharacteristicType.WINDOW_FUNCTION,
        AggregationWindowCharacteristicType.WINDOW_PARTITION,
        AggregationWindowCharacteristicType.WINDOW_ORDERING,
    ]


def test_window_without_partition_does_not_create_partition_characteristic():
    _, _, result = _analyze(
        """
        SELECT
            order_id,
            ROW_NUMBER() OVER (
                ORDER BY total_amount DESC
            ) AS rn
        FROM orders
        """
    )

    assert (
        AggregationWindowCharacteristicType.WINDOW_PARTITION
        not in _types(result)
    )


def test_window_without_ordering_does_not_create_ordering_characteristic():
    _, _, result = _analyze(
        """
        SELECT
            customer_id,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
            ) AS rn
        FROM orders
        """
    )

    assert (
        AggregationWindowCharacteristicType.WINDOW_ORDERING
        not in _types(result)
    )


def test_multiple_windows_create_multiple_window_function_characteristics():
    _, _, result = _analyze(
        """
        SELECT
            customer_id,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS rn,
            SUM(total_amount) OVER (
                PARTITION BY customer_id
            ) AS total_amount
        FROM orders
        """
    )

    types = _types(result)

    assert types.count(
        AggregationWindowCharacteristicType.WINDOW_FUNCTION
    ) == 2
    assert types.count(
        AggregationWindowCharacteristicType.WINDOW_PARTITION
    ) == 2
    assert types.count(
        AggregationWindowCharacteristicType.WINDOW_ORDERING
    ) == 1


def test_window_characteristics_link_to_window_finding():
    _, analysis, result = _analyze(
        """
        SELECT
            customer_id,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS rn
        FROM orders
        """
    )

    window_indices = [
        index
        for index, finding in enumerate(analysis.findings)
        if finding.layer == StructuralLayer.WINDOW
    ]

    assert len(window_indices) == 1

    assert all(
        characteristic.finding_index == window_indices[0]
        for characteristic in result.characteristics
    )


def test_nested_query_keeps_window_characteristics_in_correct_block():
    sql = """
        SELECT customer_id
        FROM (
            SELECT
                customer_id,
                ROW_NUMBER() OVER (
                    PARTITION BY customer_id
                    ORDER BY order_date
                ) AS rn
            FROM orders
        ) ranked
    """

    _, analysis, result = _analyze(sql)

    window_findings = [
        (index, finding)
        for index, finding in enumerate(analysis.findings)
        if finding.layer == StructuralLayer.WINDOW
    ]

    assert len(window_findings) == 1
    window_index, finding = window_findings[0]

    assert "query_block=2;" in finding.evidence

    assert all(
        characteristic.finding_index == window_index
        for characteristic in result.characteristics
    )


def test_cte_and_outer_query_keep_window_blocks_distinct():
    sql = """
        WITH ranked AS (
            SELECT
                customer_id,
                ROW_NUMBER() OVER (
                    PARTITION BY customer_id
                    ORDER BY order_date
                ) AS rn
            FROM orders
        )
        SELECT
            customer_id,
            ROW_NUMBER() OVER (
                ORDER BY customer_id
            ) AS outer_rn
        FROM ranked
    """

    _, analysis, result = _analyze(sql)

    window_findings = [
        (index, finding)
        for index, finding in enumerate(analysis.findings)
        if finding.layer == StructuralLayer.WINDOW
    ]

    assert len(window_findings) == 2

    first_index, first_finding = window_findings[0]
    second_index, second_finding = window_findings[1]

    assert "query_block=1;" in first_finding.evidence
    assert "query_block=2;" in second_finding.evidence

    characteristics_by_finding = {}
    for characteristic in result.characteristics:
        characteristics_by_finding.setdefault(
            characteristic.finding_index,
            [],
        ).append(characteristic)

    assert first_index in characteristics_by_finding
    assert second_index in characteristics_by_finding


def test_query_without_windows_returns_no_characteristics():
    _, _, result = _analyze(
        """
        SELECT customer_id, total_amount
        FROM orders
        """
    )

    assert result.characteristics == []
