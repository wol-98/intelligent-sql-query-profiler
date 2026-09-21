"""Tests for ordering and row-limiting structural analysis."""

from sqlglot import parse_one

from api.schemas.structural_optimization import (
    OrderingLimitCharacteristicType,
)
from api.services.structural_ordering_limit_analyzer import (
    StructuralOrderingLimitAnalyzer,
)
from api.services.structural_sql_analyzer import StructuralSQLAnalyzer


def _analyze(sql: str):
    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    result = StructuralOrderingLimitAnalyzer().analyze(
        expression,
        analysis,
    )

    return analysis, result


def test_ordering_characteristic_is_detected():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        ORDER BY order_date DESC
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.ORDERING,
    ]


def test_limit_characteristic_is_detected():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        LIMIT 10
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.LIMIT,
    ]


def test_offset_characteristic_is_detected():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        OFFSET 10
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.OFFSET,
    ]


def test_ordering_limit_and_offset_are_detected_in_deterministic_order():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        ORDER BY order_date DESC
        LIMIT 10
        OFFSET 20
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.ORDERING,
        OrderingLimitCharacteristicType.LIMIT,
        OrderingLimitCharacteristicType.OFFSET,
    ]


def test_filter_with_limit_is_detected():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        LIMIT 10
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.LIMIT,
        OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT,
    ]


def test_filter_with_offset_is_detected():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        OFFSET 10
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.OFFSET,
        OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT,
    ]


def test_plain_query_produces_no_ordering_or_row_limiting_characteristics():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        """
    )

    assert result.characteristics == []


def test_where_without_row_limiting_does_not_create_filter_relationship():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        """
    )

    assert result.characteristics == []


def test_characteristics_link_to_existing_structural_findings():
    analysis, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        ORDER BY order_date DESC
        LIMIT 10
        """
    )

    valid_finding_indices = {
        index
        for index, finding in enumerate(analysis.findings)
        if finding.layer in {
            "WHERE",
            "ORDER_BY",
            "LIMIT_OFFSET",
        }
    }

    assert result.characteristics
    assert all(
        characteristic.finding_index in valid_finding_indices
        for characteristic in result.characteristics
    )


def test_nested_query_keeps_query_blocks_separate():
    analysis, result = _analyze(
        """
        SELECT *
        FROM (
            SELECT *
            FROM orders
            WHERE status = 'PAID'
            LIMIT 10
        ) AS filtered_orders
        ORDER BY order_date
        """
    )

    types = [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ]

    assert types == [
        OrderingLimitCharacteristicType.ORDERING,
        OrderingLimitCharacteristicType.LIMIT,
        OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT,
    ]

    assert all(
        characteristic.finding_index < len(analysis.findings)
        for characteristic in result.characteristics
    )


def test_filter_with_ordering_is_detected():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        ORDER BY order_date DESC
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.ORDERING,
        OrderingLimitCharacteristicType.FILTER_WITH_ORDERING,
    ]


def test_filter_with_ordering_and_limit_are_detected():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        ORDER BY order_date DESC
        LIMIT 10
        """
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


def test_filter_without_ordering_does_not_create_filter_ordering_relationship():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        LIMIT 10
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.LIMIT,
        OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT,
    ]


def test_ordering_without_filter_does_not_create_filter_ordering_relationship():
    _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        ORDER BY order_date DESC
        LIMIT 10
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.ORDERING,
        OrderingLimitCharacteristicType.LIMIT,
    ]


def test_filter_with_ordering_preserves_same_query_block_provenance():
    analysis, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'PAID'
        ORDER BY order_date DESC
        """
    )

    ordering_findings = {
        index
        for index, finding in enumerate(analysis.findings)
        if finding.layer == "ORDER_BY"
        and finding.evidence is not None
        and "query_block=1;" in finding.evidence
    }

    filter_ordering_characteristics = [
        characteristic
        for characteristic in result.characteristics
        if characteristic.characteristic_type
        == OrderingLimitCharacteristicType.FILTER_WITH_ORDERING
    ]

    assert len(filter_ordering_characteristics) == 1
    assert (
        filter_ordering_characteristics[0].finding_index
        in ordering_findings
    )


def test_nested_query_does_not_cross_query_blocks_for_filter_ordering():
    _, result = _analyze(
        """
        SELECT *
        FROM (
            SELECT *
            FROM orders
            WHERE status = 'PAID'
        ) AS filtered_orders
        ORDER BY customer_id
        """
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.ORDERING,
    ]
