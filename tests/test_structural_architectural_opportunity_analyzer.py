from sqlglot import parse_one

from api.schemas.structural_optimization import (
    ArchitecturalOpportunityStatus,
    ArchitecturalOpportunityType,
    EvidenceStatus,
)
from api.services.structural_aggregation_analyzer import (
    StructuralAggregationAnalyzer,
)
from api.services.structural_architectural_opportunity_analyzer import (
    StructuralArchitecturalOpportunityAnalyzer,
)
from api.services.structural_cte_analyzer import StructuralCTEAnalyzer
from api.services.structural_sql_analyzer import StructuralSQLAnalyzer
from api.services.structural_window_analyzer import StructuralWindowAnalyzer

def analyze_sql(sql: str):
    expression = parse_one(sql, dialect="postgres")
    structural_analysis = StructuralSQLAnalyzer().analyze(expression)

    cte_characteristics = StructuralCTEAnalyzer().analyze(
        expression,
        structural_analysis,
    )

    aggregation_characteristics = StructuralAggregationAnalyzer().analyze(
        expression,
        structural_analysis,
    )

    window_characteristics = StructuralWindowAnalyzer().analyze(
        expression,
        structural_analysis,
    )

    aggregation_window_characteristics = (
        aggregation_characteristics.model_copy(
            update={
                "characteristics": (
                    aggregation_characteristics.characteristics
                    + window_characteristics.characteristics
                )
            }
        )
    )

    result = StructuralArchitecturalOpportunityAnalyzer().analyze(
        structural_analysis,
        cte_characteristics=cte_characteristics,
        aggregation_window_characteristics=(
            aggregation_window_characteristics
        ),
    )

    return structural_analysis, result

def test_aggregated_result_is_identified():
    _, result = analyze_sql(
        """
        SELECT customer_id, COUNT(*)
        FROM orders
        GROUP BY customer_id
        """
    )

    opportunities = [
        item
        for item in result.opportunities
        if item.opportunity_type
        == ArchitecturalOpportunityType.AGGREGATED_RESULT
    ]

    assert len(opportunities) == 1
    assert opportunities[0].status == (
        ArchitecturalOpportunityStatus.IDENTIFIED
    )
    assert opportunities[0].evidence_status == EvidenceStatus.COMPLETE


def test_filtered_relational_result_is_identified():
    _, result = analyze_sql(
        """
        SELECT *
        FROM orders
        WHERE customer_id = 10
        """
    )

    opportunities = [
        item
        for item in result.opportunities
        if item.opportunity_type
        == ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
    ]

    assert len(opportunities) == 1


def test_joined_filtered_result_is_identified():
    _, result = analyze_sql(
        """
        SELECT o.order_id
        FROM orders o
        JOIN customers c
          ON c.customer_id = o.customer_id
        WHERE c.customer_id = 10
        """
    )

    opportunities = [
        item
        for item in result.opportunities
        if item.opportunity_type
        == ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
    ]

    assert len(opportunities) == 1


def test_window_result_is_identified():
    _, result = analyze_sql(
        """
        SELECT
            customer_id,
            order_id,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY order_id
            ) AS rn
        FROM orders
        """
    )

    opportunities = [
        item
        for item in result.opportunities
        if item.opportunity_type
        == ArchitecturalOpportunityType.ANALYTICAL_RESULT
    ]

    assert len(opportunities) == 1


def test_reusable_cte_is_identified():
    _, result = analyze_sql(
        """
        WITH recent_orders AS (
            SELECT *
            FROM orders
            WHERE order_date >= DATE '2026-01-01'
        )
        SELECT *
        FROM recent_orders
        """
    )

    opportunities = [
        item
        for item in result.opportunities
        if item.opportunity_type
        == ArchitecturalOpportunityType.REUSABLE_CTE
    ]

    assert len(opportunities) == 1


def test_recursive_cte_is_identified_separately():
    _, result = analyze_sql(
        """
        WITH RECURSIVE numbers AS (
            SELECT 1 AS n
            UNION ALL
            SELECT n + 1
            FROM numbers
            WHERE n < 5
        )
        SELECT *
        FROM numbers
        """
    )

    types = [
        item.opportunity_type
        for item in result.opportunities
    ]

    assert ArchitecturalOpportunityType.RECURSIVE_CTE in types
    assert ArchitecturalOpportunityType.REUSABLE_CTE not in types


def test_multiple_aggregate_functions_produce_one_aggregate_opportunity():
    _, result = analyze_sql(
        """
        SELECT
            customer_id,
            COUNT(*) AS order_count,
            SUM(total_amount) AS total_value,
            AVG(total_amount) AS average_value
        FROM orders
        GROUP BY customer_id
        """
    )

    opportunities = [
        item
        for item in result.opportunities
        if item.opportunity_type
        == ArchitecturalOpportunityType.AGGREGATED_RESULT
    ]

    assert len(opportunities) == 1


def test_nested_query_blocks_are_analyzed_independently():
    _, result = analyze_sql(
        """
        SELECT *
        FROM (
            SELECT customer_id, COUNT(*)
            FROM orders
            GROUP BY customer_id
        ) summary
        WHERE summary.customer_id > 10
        """
    )

    aggregate_opportunities = [
        item
        for item in result.opportunities
        if item.opportunity_type
        == ArchitecturalOpportunityType.AGGREGATED_RESULT
    ]

    filtered_opportunities = [
        item
        for item in result.opportunities
        if item.opportunity_type
        == ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
    ]

    assert len(aggregate_opportunities) == 1
    assert len(filtered_opportunities) == 1


def test_plain_select_has_no_architectural_opportunity():
    _, result = analyze_sql(
        """
        SELECT customer_id
        FROM customers
        """
    )

    assert result.opportunities == []


def test_original_structural_analysis_is_not_modified():
    analysis, result = analyze_sql(
        """
        SELECT customer_id, COUNT(*)
        FROM orders
        GROUP BY customer_id
        """
    )

    assert result.opportunities
    assert analysis.status.value == "ANALYZED"
