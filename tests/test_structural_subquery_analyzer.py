import sqlglot
from sqlglot import exp

from api.schemas.structural_optimization import (
    EvidenceQuality,
    EvidenceStatus,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralFinding,
    StructuralLayer,
    SubqueryAlternativeCharacteristicType,
)
from api.services.structural_subquery_analyzer import (
    StructuralSubqueryAnalyzer,
)


def _analysis_for(expression):
    findings = []

    for block_number, select in enumerate(
        expression.find_all(exp.Select),
        start=1,
    ):
        findings.extend(
            [
                StructuralFinding(
                    layer=StructuralLayer.SELECT,
                    finding_type="SELECT",
                    severity="INFO",
                    description="SELECT query block detected.",
                    evidence=(
                        f"query_block={block_number};"
                        f"select={select.sql(dialect='postgres')}"
                    ),
                ),
                StructuralFinding(
                    layer=StructuralLayer.FROM,
                    finding_type="FROM",
                    severity="INFO",
                    description="FROM query block detected.",
                    evidence=f"query_block={block_number};from=present",
                ),
                StructuralFinding(
                    layer=StructuralLayer.WHERE,
                    finding_type="WHERE",
                    severity="INFO",
                    description="WHERE query block detected.",
                    evidence=f"query_block={block_number};where=present",
                ),
            ]
        )

    return StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        findings=findings,
    )


def _analyze(sql):
    expression = sqlglot.parse_one(sql, dialect="postgres")

    return StructuralSubqueryAnalyzer().analyze(
        expression,
        _analysis_for(expression),
    )


def _types(result):
    return [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ]


def test_detects_exists_predicate():
    result = _analyze(
        """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM customers c
            WHERE c.customer_id = o.customer_id
        )
        """
    )

    assert (
        SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE
        in _types(result)
    )


def test_detects_in_predicate():
    result = _analyze(
        """
        SELECT *
        FROM orders
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
        )
        """
    )

    assert (
        SubqueryAlternativeCharacteristicType.IN_PREDICATE
        in _types(result)
    )


def test_detects_any_predicate():
    result = _analyze(
        """
        SELECT *
        FROM orders
        WHERE customer_id = ANY (
            SELECT customer_id
            FROM customers
        )
        """
    )

    assert (
        SubqueryAlternativeCharacteristicType.ANY_PREDICATE
        in _types(result)
    )


def test_detects_correlated_subquery():
    result = _analyze(
        """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM order_items oi
            WHERE oi.order_id = o.order_id
        )
        """
    )

    assert (
        SubqueryAlternativeCharacteristicType.CORRELATED_SUBQUERY
        in _types(result)
    )


def test_does_not_mark_uncorrelated_subquery_as_correlated():
    result = _analyze(
        """
        SELECT *
        FROM orders
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
        )
        """
    )

    assert (
        SubqueryAlternativeCharacteristicType.CORRELATED_SUBQUERY
        not in _types(result)
    )


def test_detects_derived_table():
    result = _analyze(
        """
        SELECT x.customer_id
        FROM (
            SELECT customer_id
            FROM orders
        ) AS x
        """
    )

    assert (
        SubqueryAlternativeCharacteristicType.DERIVED_TABLE
        in _types(result)
    )


def test_plain_query_has_no_subquery_characteristics():
    result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE status = 'completed'
        """
    )

    assert result.characteristics == []


def test_characteristics_have_complete_exact_evidence():
    result = _analyze(
        """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM customers c
            WHERE c.customer_id = o.customer_id
        )
        """
    )

    assert result.characteristics

    for characteristic in result.characteristics:
        assert characteristic.evidence_status == EvidenceStatus.COMPLETE
        assert characteristic.evidence_quality == EvidenceQuality.EXACT

def test_derived_table_is_not_marked_as_correlated_without_outer_reference():
    result = _analyze(
        """
        SELECT x.customer_id
        FROM (
            SELECT customer_id
            FROM orders
        ) AS x
        """
    )

    assert (
        SubqueryAlternativeCharacteristicType.CORRELATED_SUBQUERY
        not in _types(result)
    )


def test_inner_table_reference_is_not_outer_correlation():
    result = _analyze(
        """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM order_items oi
            WHERE oi.order_id = oi.order_id
        )
        """
    )

    assert (
        SubqueryAlternativeCharacteristicType.CORRELATED_SUBQUERY
        not in _types(result)
    )


def test_correlated_exists_preserves_exists_and_correlation_characteristics():
    result = _analyze(
        """
        SELECT *
        FROM orders o
        WHERE EXISTS (
            SELECT 1
            FROM order_items oi
            WHERE oi.order_id = o.order_id
        )
        """
    )

    types = _types(result)

    assert (
        SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE
        in types
    )
    assert (
        SubqueryAlternativeCharacteristicType.CORRELATED_SUBQUERY
        in types
    )
