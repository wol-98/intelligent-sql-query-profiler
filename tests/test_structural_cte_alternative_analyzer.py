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

    assert preserved is not result
    assert preserved.candidates == [first, second]
    assert preserved.candidates[0] is not first
    assert preserved.candidates[1] is not second


def test_rule_engine_remains_available() -> None:
    engine = StructuralCTEAlternativeRuleEngine()

    rule = engine.get_rule(CTEAlternativeType.CTE)

    assert rule.source_type == CTEAlternativeType.CTE
    assert rule.requires_semantic_validation is True


def test_analyzer_preserves_candidate_status_before_semantic_validation() -> None:
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


def test_ordinary_cte_semantic_preconditions_require_validation() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    candidate = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    result = analyzer.analyze_semantic_preconditions(candidate)

    assert (
        result.alternative_type
        == CTEAlternativeType.CTE
    )
    assert (
        result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    finding_names = {
        finding.name
        for finding in result.findings
    }

    assert "CTE_DEFINITION" in finding_names
    assert "CTE_REFERENCES" in finding_names
    assert "CTE_OUTPUT_COLUMNS" in finding_names
    assert "QUERY_SCOPE" in finding_names


def test_recursive_cte_semantic_preconditions_require_validation() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

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
        evidence_status=EvidenceStatus.COMPLETE,
        title="Recursive CTE structural alternative",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=sql,
        alternative_sql=None,
    )

    result = analyzer.analyze_semantic_preconditions(candidate)

    assert (
        result.alternative_type
        == CTEAlternativeType.RECURSIVE_CTE
    )
    assert (
        result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    finding_names = {
        finding.name
        for finding in result.findings
    }

    assert "RECURSIVE_CTE" in finding_names
    assert "RECURSIVE_ANCHOR" in finding_names
    assert "RECURSIVE_MEMBER" in finding_names
    assert "RECURSIVE_SET_OPERATION" in finding_names
    assert "RECURSIVE_REFERENCES" in finding_names
    assert "RECURSIVE_TERMINATION" in finding_names


def test_missing_cte_returns_not_assessed() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.CTE,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.COMPLETE,
        title="Missing CTE candidate",
        rationale="Candidate requires structural validation.",
        source_layer=StructuralLayer.CTE,
        original_sql="SELECT * FROM orders",
        alternative_sql=None,
    )

    result = analyzer.analyze_semantic_preconditions(candidate)

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert result.findings == ()


def test_recursive_type_on_ordinary_cte_returns_not_assessed() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.RECURSIVE_CTE,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.COMPLETE,
        title="Recursive CTE candidate",
        rationale="Candidate requires structural validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=(
            "WITH data AS "
            "(SELECT customer_id FROM orders) "
            "SELECT * FROM data"
        ),
        alternative_sql=None,
    )

    result = analyzer.analyze_semantic_preconditions(candidate)

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert result.findings == ()


def test_semantic_analysis_does_not_modify_candidate() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    candidate = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

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


def test_semantic_precondition_analysis_is_deterministic() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

    candidate = make_candidate(
        "CTE-CAND-0001",
        CTEAlternativeType.CTE,
    )

    first = analyzer.analyze_semantic_preconditions(candidate)
    second = analyzer.analyze_semantic_preconditions(candidate)

    assert first == second


def test_recursive_semantic_precondition_analysis_is_deterministic() -> None:
    analyzer = StructuralCTEAlternativeAnalyzer()

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
        evidence_status=EvidenceStatus.COMPLETE,
        title="Recursive CTE structural alternative",
        rationale="Eligible for later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=sql,
        alternative_sql=None,
    )

    first = analyzer.analyze_semantic_preconditions(candidate)
    second = analyzer.analyze_semantic_preconditions(candidate)

    assert first == second
