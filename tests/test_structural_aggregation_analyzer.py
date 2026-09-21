from sqlglot import parse_one

from api.schemas.structural_optimization import (
    AggregationWindowCharacteristicType,
    StructuralLayer,
)
from api.services.structural_aggregation_analyzer import (
    StructuralAggregationAnalyzer,
)
from api.services.structural_sql_analyzer import StructuralSQLAnalyzer


def analyze(sql: str):
    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)

    return expression, analysis


def characteristics_for(result, characteristic_type):
    return [
        characteristic
        for characteristic in result.characteristics
        if characteristic.characteristic_type == characteristic_type
    ]


def test_group_by_creates_grouping_characteristic():
    expression, analysis = analyze(
        """
        SELECT customer_id, COUNT(*)
        FROM orders
        GROUP BY customer_id;
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    grouping = characteristics_for(
        result,
        AggregationWindowCharacteristicType.GROUPING,
    )

    assert len(grouping) == 1
    assert grouping[0].evidence_status.value == "COMPLETE"
    assert grouping[0].evidence_quality.value == "EXACT"
    assert (
        analysis.findings[grouping[0].finding_index].layer
        == StructuralLayer.GROUP_BY
    )


def test_single_aggregate_creates_one_characteristic():
    expression, analysis = analyze(
        """
        SELECT COUNT(*)
        FROM orders;
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    aggregates = characteristics_for(
        result,
        AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
    )

    assert len(aggregates) == 1


def test_multiple_aggregates_create_multiple_characteristics():
    expression, analysis = analyze(
        """
        SELECT
            COUNT(*),
            SUM(total_amount),
            AVG(total_amount),
            MIN(total_amount),
            MAX(total_amount)
        FROM orders;
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    aggregates = characteristics_for(
        result,
        AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
    )

    assert len(aggregates) == 5


def test_having_creates_having_characteristic():
    expression, analysis = analyze(
        """
        SELECT customer_id, COUNT(*)
        FROM orders
        GROUP BY customer_id
        HAVING COUNT(*) > 5;
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    having = characteristics_for(
        result,
        AggregationWindowCharacteristicType.HAVING_FILTER,
    )

    assert len(having) == 1
    assert (
        analysis.findings[having[0].finding_index].layer
        == StructuralLayer.HAVING
    )


def test_group_by_having_and_aggregate_are_all_detected():
    expression, analysis = analyze(
        """
        SELECT customer_id, COUNT(*), SUM(total_amount)
        FROM orders
        GROUP BY customer_id
        HAVING COUNT(*) > 5;
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    assert len(
        characteristics_for(
            result,
            AggregationWindowCharacteristicType.GROUPING,
        )
    ) == 1

    assert len(
        characteristics_for(
            result,
            AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
        )
    ) == 3

    assert len(
        characteristics_for(
            result,
            AggregationWindowCharacteristicType.HAVING_FILTER,
        )
    ) == 1


def test_query_without_aggregation_returns_no_characteristics():
    expression, analysis = analyze(
        """
        SELECT customer_id, total_amount
        FROM orders
        WHERE status = 'completed';
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    assert result.characteristics == []


def test_aggregate_without_group_by_is_detected():
    expression, analysis = analyze(
        """
        SELECT COUNT(*), AVG(total_amount)
        FROM orders;
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    aggregates = characteristics_for(
        result,
        AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
    )

    assert len(aggregates) == 2

    assert not characteristics_for(
        result,
        AggregationWindowCharacteristicType.GROUPING,
    )


def test_aggregate_in_having_is_counted_as_an_occurrence():
    expression, analysis = analyze(
        """
        SELECT customer_id, COUNT(*)
        FROM orders
        GROUP BY customer_id
        HAVING COUNT(*) > 5;
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    aggregates = characteristics_for(
        result,
        AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
    )

    assert len(aggregates) == 2


def test_nested_query_keeps_aggregation_characteristics_in_query_block():
    expression, analysis = analyze(
        """
        SELECT customer_id
        FROM (
            SELECT customer_id, COUNT(*)
            FROM orders
            GROUP BY customer_id
        ) AS grouped_orders;
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    grouping = characteristics_for(
        result,
        AggregationWindowCharacteristicType.GROUPING,
    )

    aggregates = characteristics_for(
        result,
        AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
    )

    assert len(grouping) == 1
    assert len(aggregates) == 1

    assert (
        analysis.findings[grouping[0].finding_index].layer
        == StructuralLayer.GROUP_BY
    )


def test_cte_and_outer_query_keep_aggregation_in_correct_block():
    expression, analysis = analyze(
        """
        WITH customer_totals AS (
            SELECT customer_id, SUM(total_amount) AS total_amount
            FROM orders
            GROUP BY customer_id
        )
        SELECT customer_id
        FROM customer_totals;
        """
    )

    result = StructuralAggregationAnalyzer().analyze(
        expression,
        analysis,
    )

    grouping = characteristics_for(
        result,
        AggregationWindowCharacteristicType.GROUPING,
    )

    aggregates = characteristics_for(
        result,
        AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
    )

    assert len(grouping) == 1
    assert len(aggregates) == 1

    grouping_finding = analysis.findings[grouping[0].finding_index]
    aggregate_finding = analysis.findings[aggregates[0].finding_index]

    assert grouping_finding.layer == StructuralLayer.GROUP_BY
    assert aggregate_finding.layer == StructuralLayer.SELECT
