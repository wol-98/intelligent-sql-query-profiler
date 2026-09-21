"""Tests for M21.7.5 semantic-safety preconditions."""

import pytest

from api.schemas.structural_optimization import (
    SemanticSafetyStatus,
    SubqueryAlternativeType,
)
from api.services.structural_semantic_preconditions import (
    StructuralSemanticPreconditionAnalyzer,
)


@pytest.fixture
def analyzer() -> StructuralSemanticPreconditionAnalyzer:
    return StructuralSemanticPreconditionAnalyzer()


def names(result):
    return {
        finding.name
        for finding in result.findings
        if finding.detected
    }


def test_exists_requires_validation(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT c.customer_id
        FROM customers c
        WHERE EXISTS (
            SELECT 1
            FROM orders o
            WHERE o.customer_id = c.customer_id
        )
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.EXISTS,
    )

    assert result.semantic_safety == SemanticSafetyStatus.REQUIRES_VALIDATION
    assert "correlated_reference" in names(result)


def test_uncorrelated_exists_is_not_claimed_safe(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE EXISTS (
            SELECT 1
            FROM orders
        )
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.EXISTS,
    )

    assert result.semantic_safety == SemanticSafetyStatus.REQUIRES_VALIDATION
    assert "correlated_reference" in {
        finding.name for finding in result.findings
    }


def test_in_detects_membership_and_null_conditions(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id IN (
            SELECT customer_id
            FROM orders
            WHERE customer_id IS NOT NULL
        )
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.IN,
    )

    assert result.semantic_safety == SemanticSafetyStatus.REQUIRES_VALIDATION
    assert "membership_expression" in names(result)
    assert "null_sensitive_expression" in names(result)


def test_any_records_comparison_operator(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id > ANY (
            SELECT customer_id
            FROM orders
        )
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.ANY,
    )

    assert result.semantic_safety == SemanticSafetyStatus.REQUIRES_VALIDATION

    comparison = next(
        finding
        for finding in result.findings
        if finding.name == "comparison_operator"
    )

    assert comparison.detected is True
    assert ">" in comparison.rationale


def test_any_without_supported_comparison_operator_is_not_assumed_safe(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id = ANY (
            SELECT customer_id
            FROM orders
        )
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.ANY,
    )

    comparison = next(
        finding
        for finding in result.findings
        if finding.name == "comparison_operator"
    )

    assert comparison.detected is True


def test_derived_table_detects_projection_and_alias(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT x.customer_id
        FROM (
            SELECT customer_id
            FROM orders
        ) x
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.DERIVED_TABLE,
    )

    assert result.semantic_safety == SemanticSafetyStatus.REQUIRES_VALIDATION
    assert "projection" in names(result)
    assert "alias" in names(result)


def test_derived_table_detects_aggregation(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT x.customer_id, x.order_count
        FROM (
            SELECT customer_id, COUNT(*) AS order_count
            FROM orders
            GROUP BY customer_id
        ) x
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.DERIVED_TABLE,
    )

    detected = names(result)

    assert "aggregation" in detected
    assert "group_by" in detected


def test_derived_table_detects_limit_and_offset(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT x.customer_id
        FROM (
            SELECT customer_id
            FROM orders
            ORDER BY customer_id
            LIMIT 10
            OFFSET 5
        ) x
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.DERIVED_TABLE,
    )

    detected = names(result)

    assert "limit" in detected
    assert "offset" in detected


def test_subquery_with_distinct_is_flagged(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id IN (
            SELECT DISTINCT customer_id
            FROM orders
        )
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.IN,
    )

    assert "distinct" in names(result)


def test_subquery_with_window_function_is_flagged(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id IN (
            SELECT customer_id
            FROM (
                SELECT
                    customer_id,
                    ROW_NUMBER() OVER (
                        PARTITION BY customer_id
                        ORDER BY order_id
                    ) AS rn
                FROM orders
            ) q
        )
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.IN,
    )

    assert "window_function" in names(result)


def test_missing_target_does_not_claim_safety(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.EXISTS,
    )

    assert result.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert result.findings == ()


def test_precondition_analysis_does_not_generate_sql(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id IN (
            SELECT customer_id
            FROM orders
        )
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.IN,
    )

    assert not hasattr(result, "alternative_sql")
    assert not hasattr(result, "optimized_sql")


def test_precondition_analysis_does_not_execute_sql(
    analyzer: StructuralSemanticPreconditionAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id IN (
            SELECT customer_id
            FROM orders
        )
    """

    result = analyzer.analyze(
        sql,
        SubqueryAlternativeType.IN,
    )

    assert result.alternative_type == SubqueryAlternativeType.IN
