from api.schemas.structural_optimization import (
    CandidateStatus,
    CTEAlternativeType,
    SemanticSafetyStatus,
    StructuralCTEAlternativeCandidate,
    StructuralLayer,
)
from api.services.structural_analysis_enricher import (
    StructuralAnalysisEnricher,
)
from api.services.structural_alternative_analyzer import (
    StructuralAlternativeAnalyzer,
)
from api.services.structural_cte_alternative_analyzer import (
    StructuralCTEAlternativeAnalyzer,
)


def test_ordinary_cte_end_to_end_semantic_precondition() -> None:
    sql = """
        WITH recent_orders AS (
            SELECT customer_id, order_date
            FROM orders
            WHERE order_date >= DATE '2026-01-01'
        )
        SELECT *
        FROM recent_orders
    """

    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.CTE,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status="COMPLETE",
        title="CTE structural alternative",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=sql,
        alternative_sql=None,
    )

    analyzer = StructuralCTEAlternativeAnalyzer()

    rule_analysis = analyzer.analyze(candidate)
    semantic_result = analyzer.analyze_semantic_preconditions(candidate)

    assert (
        rule_analysis.rule.source_type
        == CTEAlternativeType.CTE
    )

    assert (
        semantic_result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    assert candidate.status == CandidateStatus.CANDIDATE
    assert (
        candidate.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert candidate.alternative_sql is None


def test_recursive_cte_end_to_end_semantic_precondition() -> None:
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
            WHERE n.id < 100
        )
        SELECT *
        FROM tree
    """

    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.RECURSIVE_CTE,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status="COMPLETE",
        title="Recursive CTE structural alternative",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=sql,
        alternative_sql=None,
    )

    analyzer = StructuralCTEAlternativeAnalyzer()

    rule_analysis = analyzer.analyze(candidate)
    semantic_result = analyzer.analyze_semantic_preconditions(candidate)

    assert (
        rule_analysis.rule.source_type
        == CTEAlternativeType.RECURSIVE_CTE
    )

    assert (
        semantic_result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    finding_names = {
        finding.name
        for finding in semantic_result.findings
    }

    assert "RECURSIVE_CTE" in finding_names
    assert "RECURSIVE_ANCHOR" in finding_names
    assert "RECURSIVE_MEMBER" in finding_names
    assert "RECURSIVE_SET_OPERATION" in finding_names
    assert "RECURSIVE_REFERENCES" in finding_names
    assert "RECURSIVE_TERMINATION" in finding_names

    assert candidate.status == CandidateStatus.CANDIDATE
    assert (
        candidate.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert candidate.alternative_sql is None


def test_cte_and_subquery_families_remain_separate() -> None:
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

    cte_candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.CTE,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status="COMPLETE",
        title="CTE structural alternative",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=sql,
        alternative_sql=None,
    )

    cte_analyzer = StructuralCTEAlternativeAnalyzer()

    cte_semantic_result = (
        cte_analyzer.analyze_semantic_preconditions(
            cte_candidate
        )
    )

    framework = StructuralAlternativeAnalyzer().analyze_framework(
        sql,
        None,
    )

    assert (
        cte_semantic_result.alternative_type
        == CTEAlternativeType.CTE
    )

    assert (
        cte_semantic_result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    assert len(framework.cte_analyses) == 0

    assert len(framework.subquery_analyses) == 1

    assert (
        framework.subquery_analyses[0]
        .candidate.alternative_type.value
        == "EXISTS"
    )


def test_semantic_precondition_preserves_original_sql_exactly() -> None:
    sql = (
        "WITH data AS (SELECT customer_id FROM orders) "
        "SELECT * FROM data"
    )

    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.CTE,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status="COMPLETE",
        title="CTE structural alternative",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=sql,
        alternative_sql=None,
    )

    analyzer = StructuralCTEAlternativeAnalyzer()

    result = analyzer.analyze_semantic_preconditions(candidate)

    assert candidate.original_sql == sql
    assert result.alternative_type == CTEAlternativeType.CTE
    assert (
        result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )


def test_semantic_precondition_does_not_validate_candidate() -> None:
    sql = """
        WITH recent_orders AS (
            SELECT customer_id
            FROM orders
        )
        SELECT *
        FROM recent_orders
    """

    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.CTE,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status="COMPLETE",
        title="CTE structural alternative",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=sql,
        alternative_sql=None,
    )

    analyzer = StructuralCTEAlternativeAnalyzer()

    result = analyzer.analyze_semantic_preconditions(candidate)

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    assert candidate.status == CandidateStatus.CANDIDATE

    assert (
        candidate.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )

    assert candidate.alternative_sql is None
