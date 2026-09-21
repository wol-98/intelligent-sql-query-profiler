"""Tests for M21.7.2 structural alternative detection."""

import pytest

from api.schemas.structural_optimization import (
    CandidateStatus,
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralLayer,
    SubqueryAlternativeType,
)
from api.services.structural_alternative_detector import (
    StructuralAlternativeDetector,
)


@pytest.fixture
def detector() -> StructuralAlternativeDetector:
    return StructuralAlternativeDetector()


def test_detects_exists_subquery(
    detector: StructuralAlternativeDetector,
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

    result = detector.detect(sql)

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.alternative_type == SubqueryAlternativeType.EXISTS
    assert candidate.source_layer == StructuralLayer.SUBQUERY
    assert candidate.original_sql == sql


def test_detects_in_subquery(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT c.customer_id
        FROM customers c
        WHERE c.customer_id IN (
            SELECT o.customer_id
            FROM orders o
        )
    """

    result = detector.detect(sql)

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.alternative_type == SubqueryAlternativeType.IN
    assert candidate.source_layer == StructuralLayer.SUBQUERY


def test_detects_any_subquery(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT c.customer_id
        FROM customers c
        WHERE c.customer_id = ANY (
            SELECT o.customer_id
            FROM orders o
        )
    """

    result = detector.detect(sql)

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.alternative_type == SubqueryAlternativeType.ANY
    assert candidate.source_layer == StructuralLayer.SUBQUERY


def test_detects_derived_table(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT x.customer_id
        FROM (
            SELECT customer_id
            FROM orders
        ) x
    """

    result = detector.detect(sql)

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.alternative_type == SubqueryAlternativeType.DERIVED_TABLE
    assert candidate.source_layer == StructuralLayer.FROM


def test_in_subquery_is_not_classified_as_derived_table(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT *
        FROM orders
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
        )
    """

    result = detector.detect(sql)

    assert [
        candidate.alternative_type
        for candidate in result.candidates
    ] == [SubqueryAlternativeType.IN]


def test_multiple_structures_are_detected_in_deterministic_order(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT c.customer_id
        FROM (
            SELECT customer_id
            FROM customers
        ) c
        WHERE c.customer_id IN (
            SELECT o.customer_id
            FROM orders o
            WHERE EXISTS (
                SELECT 1
                FROM shipments s
                WHERE s.order_id = o.order_id
            )
        )
    """

    result = detector.detect(sql)

    assert [
        candidate.alternative_type
        for candidate in result.candidates
    ] == [
        SubqueryAlternativeType.DERIVED_TABLE,
        SubqueryAlternativeType.IN,
        SubqueryAlternativeType.EXISTS,
    ]

    assert [
        candidate.candidate_id
        for candidate in result.candidates
    ] == [
        "ALT-0001",
        "ALT-0002",
        "ALT-0003",
    ]


def test_candidates_remain_unvalidated(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT customer_id
        FROM orders
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
        )
    """

    result = detector.detect(sql)
    candidate = result.candidates[0]

    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert candidate.evidence_status == EvidenceStatus.COMPLETE
    assert candidate.alternative_sql is None


def test_original_sql_is_preserved_exactly(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = (
        "select  customer_id\n"
        "FROM orders\n"
        "where customer_id IN "
        "(SELECT customer_id FROM customers)"
    )

    result = detector.detect(sql)

    assert result.candidates[0].original_sql == sql


def test_no_subquery_returns_empty_result(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT customer_id
        FROM orders
        WHERE customer_id = 845
    """

    result = detector.detect(sql)

    assert result.candidates == []


def test_exists_is_not_misclassified_as_any(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE EXISTS (
            SELECT 1
            FROM orders
        )
    """

    result = detector.detect(sql)

    assert [
        candidate.alternative_type
        for candidate in result.candidates
    ] == [SubqueryAlternativeType.EXISTS]


def test_any_is_not_misclassified_as_in(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id = ANY (
            SELECT customer_id
            FROM orders
        )
    """

    result = detector.detect(sql)

    assert [
        candidate.alternative_type
        for candidate in result.candidates
    ] == [SubqueryAlternativeType.ANY]


def test_nested_subquery_without_supported_outer_structure_is_not_derived_table(
    detector: StructuralAlternativeDetector,
) -> None:
    sql = """
        SELECT *
        FROM orders
        WHERE EXISTS (
            SELECT 1
            FROM customers
            WHERE customers.customer_id IN (
                SELECT customer_id
                FROM shipments
            )
        )
    """

    result = detector.detect(sql)

    assert [
        candidate.alternative_type
        for candidate in result.candidates
    ] == [
        SubqueryAlternativeType.EXISTS,
        SubqueryAlternativeType.IN,
    ]
