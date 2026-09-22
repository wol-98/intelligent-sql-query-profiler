"""Tests for M21.7.4 structural alternative integration."""

from __future__ import annotations

import pytest

from api.schemas.structural_optimization import (
    CandidateStatus,
    CTEAlternativeType,
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralAlternativeCandidate,
    StructuralCTEAlternativeCandidate,
    StructuralCTEAlternativeResult,
    StructuralLayer,
    SubqueryAlternativeType,
)

from api.services.structural_alternative_analyzer import (
    StructuralAlternativeAnalysis,
    StructuralAlternativeAnalyzer,
    StructuralAlternativeFrameworkAnalysis,
)

@pytest.fixture
def analyzer() -> StructuralAlternativeAnalyzer:
    return StructuralAlternativeAnalyzer()


@pytest.mark.parametrize(
    "sql,expected_type",
    [
        (
            """
            SELECT customer_id
            FROM customers
            WHERE EXISTS (
                SELECT 1
                FROM orders
                WHERE orders.customer_id = customers.customer_id
            )
            """,
            SubqueryAlternativeType.EXISTS,
        ),
        (
            """
            SELECT customer_id
            FROM customers
            WHERE customer_id IN (
                SELECT customer_id
                FROM orders
            )
            """,
            SubqueryAlternativeType.IN,
        ),
        (
            """
            SELECT customer_id
            FROM customers
            WHERE customer_id = ANY (
                SELECT customer_id
                FROM orders
            )
            """,
            SubqueryAlternativeType.ANY,
        ),
        (
            """
            SELECT x.customer_id
            FROM (
                SELECT customer_id
                FROM orders
            ) x
            """,
            SubqueryAlternativeType.DERIVED_TABLE,
        ),
    ],
)
def test_analyzer_integrates_detection_and_rule_resolution(
    analyzer: StructuralAlternativeAnalyzer,
    sql: str,
    expected_type: SubqueryAlternativeType,
) -> None:
    analyses = analyzer.analyze(sql)

    assert len(analyses) == 1

    analysis = analyses[0]

    assert isinstance(analysis, StructuralAlternativeAnalysis)
    assert analysis.candidate.alternative_type == expected_type
    assert analysis.rule.source_type == expected_type
    assert analysis.rule.requires_semantic_validation is True


def test_analyze_result_preserves_established_contract(
    analyzer: StructuralAlternativeAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id IN (
            SELECT customer_id
            FROM orders
        )
    """

    result = analyzer.analyze_result(sql)

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.alternative_type == SubqueryAlternativeType.IN
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert candidate.alternative_sql is None


def test_original_sql_is_preserved_exactly(
    analyzer: StructuralAlternativeAnalyzer,
) -> None:
    sql = (
        "select  customer_id\n"
        "FROM customers\n"
        "where customer_id IN "
        "(SELECT customer_id FROM orders)"
    )

    analyses = analyzer.analyze(sql)

    assert analyses[0].candidate.original_sql == sql


def test_rule_metadata_is_available_without_rewriting_sql(
    analyzer: StructuralAlternativeAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id IN (
            SELECT customer_id
            FROM orders
        )
    """

    analysis = analyzer.analyze(sql)[0]

    assert analysis.rule.alternative_family == "IN_TO_EXISTS"
    assert analysis.rule.requires_semantic_validation is True
    assert analysis.candidate.alternative_sql is None


def test_multiple_structural_alternatives_preserve_detection_order(
    analyzer: StructuralAlternativeAnalyzer,
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

    analyses = analyzer.analyze(sql)

    assert [
        analysis.candidate.alternative_type
        for analysis in analyses
    ] == [
        SubqueryAlternativeType.DERIVED_TABLE,
        SubqueryAlternativeType.IN,
        SubqueryAlternativeType.EXISTS,
    ]

    assert [
        analysis.rule.alternative_family
        for analysis in analyses
    ] == [
        "DERIVED_TABLE_TO_STRUCTURAL_ALTERNATIVE",
        "IN_TO_EXISTS",
        "EXISTS_TO_SUBQUERY_ALTERNATIVE",
    ]


def test_no_supported_structure_returns_empty_result(
    analyzer: StructuralAlternativeAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM orders
        WHERE customer_id = 845
    """

    assert analyzer.analyze(sql) == []
    assert analyzer.analyze_result(sql).candidates == []


def test_any_rule_preserves_operator_sensitive_rule_family(
    analyzer: StructuralAlternativeAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id > ANY (
            SELECT customer_id
            FROM orders
        )
    """

    analysis = analyzer.analyze(sql)[0]

    assert analysis.candidate.alternative_type == SubqueryAlternativeType.ANY
    assert (
        analysis.rule.alternative_family
        == "ANY_TO_OPERATOR_SPECIFIC_ALTERNATIVE"
    )


def test_derived_table_uses_from_layer_rule(
    analyzer: StructuralAlternativeAnalyzer,
) -> None:
    sql = """
        SELECT x.customer_id
        FROM (
            SELECT customer_id
            FROM orders
        ) x
    """

    analysis = analyzer.analyze(sql)[0]

    assert (
        analysis.candidate.alternative_type
        == SubqueryAlternativeType.DERIVED_TABLE
    )
    assert analysis.candidate.source_layer.value == "FROM"
    assert analysis.rule.source_layer.value == "FROM"


def test_integrated_result_does_not_claim_validation(
    analyzer: StructuralAlternativeAnalyzer,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE EXISTS (
            SELECT 1
            FROM orders
        )
    """

    result = analyzer.analyze_result(sql)
    candidate = result.candidates[0]

    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert candidate.alternative_sql is None

def make_cte_candidate(
    candidate_id: str,
    alternative_type: CTEAlternativeType,
) -> StructuralCTEAlternativeCandidate:
    return StructuralCTEAlternativeCandidate(
        candidate_id=candidate_id,
        alternative_type=alternative_type,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.COMPLETE,
        title="Test CTE alternative",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=(
            "WITH data AS (SELECT * FROM orders) "
            "SELECT * FROM data"
        ),
        alternative_sql=None,
    )


def test_framework_preserves_existing_subquery_analysis() -> None:
    analyzer = StructuralAlternativeAnalyzer()

    sql = """
        SELECT customer_id
        FROM customers
        WHERE EXISTS (
            SELECT 1
            FROM orders
            WHERE orders.customer_id = customers.customer_id
        )
    """

    framework = analyzer.analyze_framework(sql)

    assert isinstance(
        framework,
        StructuralAlternativeFrameworkAnalysis,
    )

    assert len(framework.subquery_analyses) == 1
    assert framework.cte_analyses == ()

    analysis = framework.subquery_analyses[0]

    assert isinstance(
        analysis,
        StructuralAlternativeAnalysis,
    )

    assert analysis.candidate.alternative_type.value == "EXISTS"


def test_framework_integrates_ordinary_cte_alternative() -> None:
    analyzer = StructuralAlternativeAnalyzer()

    cte_candidate = make_cte_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    cte_result = StructuralCTEAlternativeResult(
        candidates=[cte_candidate]
    )

    framework = analyzer.analyze_framework(
        "SELECT 1",
        cte_result,
    )

    assert framework.subquery_analyses == ()
    assert len(framework.cte_analyses) == 1

    analysis = framework.cte_analyses[0]

    assert analysis.candidate == cte_candidate
    assert (
        analysis.rule.source_type
        == CTEAlternativeType.CTE
    )


def test_framework_integrates_recursive_cte_alternative() -> None:
    analyzer = StructuralAlternativeAnalyzer()

    cte_candidate = make_cte_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.RECURSIVE_CTE,
    )

    cte_result = StructuralCTEAlternativeResult(
        candidates=[cte_candidate]
    )

    framework = analyzer.analyze_framework(
        "SELECT 1",
        cte_result,
    )

    assert len(framework.cte_analyses) == 1

    analysis = framework.cte_analyses[0]

    assert (
        analysis.rule.source_type
        == CTEAlternativeType.RECURSIVE_CTE
    )
    assert (
        analysis.rule.alternative_family
        == "RECURSIVE_CTE_TO_STRUCTURAL_ALTERNATIVE"
    )


def test_framework_preserves_both_alternative_families() -> None:
    analyzer = StructuralAlternativeAnalyzer()

    sql = """
        SELECT customer_id
        FROM customers
        WHERE EXISTS (
            SELECT 1
            FROM orders
            WHERE orders.customer_id = customers.customer_id
        )
    """

    cte_candidate = make_cte_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    cte_result = StructuralCTEAlternativeResult(
        candidates=[cte_candidate]
    )

    framework = analyzer.analyze_framework(
        sql,
        cte_result,
    )

    assert len(framework.subquery_analyses) == 1
    assert len(framework.cte_analyses) == 1

    assert (
        framework.subquery_analyses[0]
        .candidate.alternative_type.value
        == "EXISTS"
    )

    assert (
        framework.cte_analyses[0]
        .candidate.alternative_type
        == CTEAlternativeType.CTE
    )


def test_framework_does_not_change_cte_candidate_state() -> None:
    analyzer = StructuralAlternativeAnalyzer()

    candidate = make_cte_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    result = StructuralCTEAlternativeResult(
        candidates=[candidate]
    )

    framework = analyzer.analyze_framework(
        "SELECT 1",
        result,
    )

    analyzed_candidate = framework.cte_analyses[0].candidate

    assert analyzed_candidate.status == CandidateStatus.CANDIDATE
    assert (
        analyzed_candidate.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert analyzed_candidate.alternative_sql is None
    assert analyzed_candidate.original_sql == candidate.original_sql


def test_framework_is_deterministic_for_same_inputs() -> None:
    analyzer = StructuralAlternativeAnalyzer()

    candidate = make_cte_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    result = StructuralCTEAlternativeResult(
        candidates=[candidate]
    )

    first = analyzer.analyze_framework(
        "SELECT 1",
        result,
    )

    second = analyzer.analyze_framework(
        "SELECT 1",
        result,
    )

    assert first == second
