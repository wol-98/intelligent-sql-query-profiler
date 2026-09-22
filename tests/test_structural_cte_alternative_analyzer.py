from api.schemas.structural_optimization import (
    CandidateStatus,
    CTEAlternativeType,
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralCTEAlternativeCandidate,
    StructuralCTEAlternativeResult,
    StructuralLayer,
)
from api.services.structural_cte_alternative_analyzer import (
    StructuralCTEAlternativeAnalysis,
    StructuralCTEAlternativeAnalyzer,
)
from api.services.structural_cte_alternative_rules import (
    StructuralCTEAlternativeRuleEngine,
)


def make_candidate(
    candidate_id: str,
    alternative_type: CTEAlternativeType,
) -> StructuralCTEAlternativeCandidate:
    return StructuralCTEAlternativeCandidate(
        candidate_id=candidate_id,
        alternative_type=alternative_type,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.COMPLETE,
        title="Test CTE alternative candidate",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql="WITH data AS (SELECT * FROM orders) SELECT * FROM data",
        alternative_sql=None,
    )


def test_analyzer_resolves_ordinary_cte_rule() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    candidate = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    analysis = analyzer.analyze(candidate)

    assert isinstance(analysis, StructuralCTEAlternativeAnalysis)
    assert analysis.candidate == candidate
    assert analysis.rule.source_type == CTEAlternativeType.CTE
    assert analysis.rule.alternative_family == (
        "CTE_TO_STRUCTURAL_ALTERNATIVE"
    )


def test_analyzer_resolves_recursive_cte_rule() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    candidate = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.RECURSIVE_CTE,
    )

    analysis = analyzer.analyze(candidate)

    assert isinstance(analysis, StructuralCTEAlternativeAnalysis)
    assert analysis.candidate == candidate
    assert (
        analysis.rule.source_type
        == CTEAlternativeType.RECURSIVE_CTE
    )
    assert analysis.rule.alternative_family == (
        "RECURSIVE_CTE_TO_STRUCTURAL_ALTERNATIVE"
    )


def test_analyze_result_preserves_candidate_order() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    first = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )
    second = make_candidate(
        "CTE-CAND-0002",
        CTEAlternativeType.RECURSIVE_CTE,
    )

    result = StructuralCTEAlternativeResult(
        candidates=[first, second]
    )

    analyses = analyzer.analyze_result(result)

    assert len(analyses) == 2
    assert analyses[0].candidate.candidate_id == "CTE-CAND-0001"
    assert analyses[1].candidate.candidate_id == "CTE-CAND-0002"
    assert (
        analyses[0].rule.source_type
        == CTEAlternativeType.CTE
    )
    assert (
        analyses[1].rule.source_type
        == CTEAlternativeType.RECURSIVE_CTE
    )


def test_analyzer_preserves_candidate_semantic_state() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    candidate = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    analysis = analyzer.analyze(candidate)

    assert analysis.candidate.status == CandidateStatus.CANDIDATE
    assert (
        analysis.candidate.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert analysis.candidate.alternative_sql is None


def test_analyzer_preserves_original_sql() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    original_sql = """
        WITH recent_orders AS (
            SELECT *
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
        evidence_status=EvidenceStatus.COMPLETE,
        title="CTE structural alternative",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=original_sql,
        alternative_sql=None,
    )

    analysis = analyzer.analyze(candidate)

    assert analysis.candidate.original_sql == original_sql


def test_preserve_candidate_returns_equivalent_candidate() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    candidate = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    preserved = analyzer.preserve_candidate(candidate)

    assert preserved == candidate
    assert preserved is not candidate


def test_preserve_result_keeps_candidate_order_and_values() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    first = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )
    second = make_candidate(
        "CTE-CAND-0002",
        CTEAlternativeType.RECURSIVE_CTE,
    )

    result = StructuralCTEAlternativeResult(
        candidates=[first, second]
    )

    preserved = analyzer.preserve_result(result)

    assert preserved.candidates == [first, second]
    assert preserved.candidates is not result.candidates


def test_rule_engine_can_be_injected() -> None:
    rule_engine = StructuralCTEAlternativeRuleEngine()
    analyzer = StructuralCTEAlternativeAnalyzer(rule_engine)

    candidate = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    analysis = analyzer.analyze(candidate)

    assert analysis.rule == rule_engine.get_rule(
        CTEAlternativeType.CTE
    )
