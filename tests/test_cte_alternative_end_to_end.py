from sqlglot import parse_one

from api.schemas.structural_optimization import (
    CandidateStatus,
    CTEAlternativeType,
    SemanticSafetyStatus,
)
from api.services.structural_analysis_enricher import (
    StructuralAnalysisEnricher,
)
from api.services.structural_alternative_analyzer import (
    StructuralAlternativeAnalyzer,
)
from api.services.structural_cte_candidate_generator import (
    StructuralCTECandidateGenerator,
)
from api.services.structural_sql_analyzer import (
    StructuralSQLAnalyzer,
)


def test_ordinary_cte_end_to_end() -> None:
    sql = """
        WITH recent_orders AS (
            SELECT customer_id, order_date
            FROM orders
            WHERE order_date >= DATE '2026-01-01'
        )
        SELECT *
        FROM recent_orders
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)
    enricher = StructuralAnalysisEnricher()

    opportunities = enricher.analyze_cte_opportunities(
        expression,
        analysis,
    )

    candidates = StructuralCTECandidateGenerator().generate(
        analysis,
        opportunities,
        sql,
    )

    assert candidates.candidates

    assert all(
        candidate.alternative_type == CTEAlternativeType.CTE
        for candidate in candidates.candidates
    )

    assert all(
        candidate.status == CandidateStatus.CANDIDATE
        for candidate in candidates.candidates
    )

    assert all(
        candidate.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
        for candidate in candidates.candidates
    )

    assert all(
        candidate.original_sql == sql
        for candidate in candidates.candidates
    )

    assert all(
        candidate.alternative_sql is None
        for candidate in candidates.candidates
    )

    framework = StructuralAlternativeAnalyzer().analyze_framework(
        sql,
        candidates,
    )

    assert len(framework.cte_analyses) == len(
        candidates.candidates
    )

    for integrated in framework.cte_analyses:
        assert integrated.rule.source_type == CTEAlternativeType.CTE
        assert integrated.rule.requires_semantic_validation is True


def test_recursive_cte_end_to_end() -> None:
    sql = """
        WITH RECURSIVE tree AS (
            SELECT id, parent_id
            FROM nodes
            WHERE parent_id IS NULL

            UNION ALL

            SELECT n.id, n.parent_id
            FROM nodes n
            JOIN tree t
                ON n.parent_id = t.id
        )
        SELECT *
        FROM tree
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)
    enricher = StructuralAnalysisEnricher()

    opportunities = enricher.analyze_cte_opportunities(
        expression,
        analysis,
    )

    candidates = StructuralCTECandidateGenerator().generate(
        analysis,
        opportunities,
        sql,
    )

    assert candidates.candidates

    candidate_types = [
        candidate.alternative_type
        for candidate in candidates.candidates
    ]

    assert CTEAlternativeType.CTE in candidate_types
    assert CTEAlternativeType.RECURSIVE_CTE in candidate_types

    for candidate in candidates.candidates:
        assert candidate.status == CandidateStatus.CANDIDATE
        assert (
            candidate.semantic_safety
            == SemanticSafetyStatus.NOT_ASSESSED
        )
        assert candidate.original_sql == sql
        assert candidate.alternative_sql is None

    framework = StructuralAlternativeAnalyzer().analyze_framework(
        sql,
        candidates,
    )

    assert len(framework.cte_analyses) == len(
        candidates.candidates
    )

    rule_types = [
        item.rule.source_type
        for item in framework.cte_analyses
    ]

    assert CTEAlternativeType.CTE in rule_types
    assert CTEAlternativeType.RECURSIVE_CTE in rule_types

    for item in framework.cte_analyses:
        assert item.candidate.status == CandidateStatus.CANDIDATE
        assert (
            item.candidate.semantic_safety
            == SemanticSafetyStatus.NOT_ASSESSED
        )
        assert item.candidate.alternative_sql is None


def test_cte_and_subquery_families_coexist() -> None:
    sql = """
        WITH recent_orders AS (
            SELECT customer_id
            FROM orders
        )
        SELECT customer_id
        FROM customers
        WHERE EXISTS (
            SELECT 1
            FROM recent_orders r
            WHERE r.customer_id = customers.customer_id
        )
    """

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)
    enricher = StructuralAnalysisEnricher()

    cte_opportunities = enricher.analyze_cte_opportunities(
        expression,
        analysis,
    )

    cte_candidates = StructuralCTECandidateGenerator().generate(
        analysis,
        cte_opportunities,
        sql,
    )

    framework = StructuralAlternativeAnalyzer().analyze_framework(
        sql,
        cte_candidates,
    )

    assert framework.cte_analyses
    assert len(framework.subquery_analyses) == 1

    assert all(
        item.candidate.alternative_type
        == CTEAlternativeType.CTE
        for item in framework.cte_analyses
    )

    assert (
        framework.subquery_analyses[0]
        .candidate.alternative_type.value
        == "EXISTS"
    )


def test_cte_end_to_end_preserves_original_sql_exactly() -> None:
    sql = (
        "WITH data AS (SELECT customer_id FROM orders) "
        "SELECT * FROM data"
    )

    expression = parse_one(sql, dialect="postgres")
    analysis = StructuralSQLAnalyzer().analyze(expression)
    enricher = StructuralAnalysisEnricher()

    opportunities = enricher.analyze_cte_opportunities(
        expression,
        analysis,
    )

    candidates = StructuralCTECandidateGenerator().generate(
        analysis,
        opportunities,
        sql,
    )

    framework = StructuralAlternativeAnalyzer().analyze_framework(
        sql,
        candidates,
    )

    assert framework.cte_analyses

    for analysis_result in framework.cte_analyses:
        assert (
            analysis_result.candidate.original_sql
            == sql
        )
