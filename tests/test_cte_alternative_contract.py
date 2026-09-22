from api.schemas.structural_optimization import (
    CandidateStatus,
    CTEAlternativeType,
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralCTEAlternativeCandidate,
    StructuralCTEAlternativeResult,
    StructuralLayer,
)


def test_cte_alternative_type_values():
    assert CTEAlternativeType.CTE.value == "CTE"
    assert CTEAlternativeType.RECURSIVE_CTE.value == "RECURSIVE_CTE"


def test_cte_candidate_defaults():
    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.CTE,
        evidence_status=EvidenceStatus.COMPLETE,
        title="CTE structural alternative candidate",
        rationale="Eligible for later validation.",
        source_layer=StructuralLayer.CTE,
        original_sql="WITH recent_orders AS (SELECT * FROM orders) SELECT * FROM recent_orders",
    )

    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert candidate.alternative_sql is None


def test_recursive_cte_candidate():
    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0002",
        alternative_type=CTEAlternativeType.RECURSIVE_CTE,
        evidence_status=EvidenceStatus.COMPLETE,
        title="Recursive CTE structural alternative candidate",
        rationale="Requires later structural and semantic validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=(
            "WITH RECURSIVE tree AS "
            "(SELECT id FROM nodes UNION ALL SELECT n.id FROM nodes n "
            "JOIN tree t ON n.parent_id = t.id) "
            "SELECT * FROM tree"
        ),
    )

    assert candidate.alternative_type == CTEAlternativeType.RECURSIVE_CTE
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED


def test_cte_candidate_preserves_original_sql():
    sql = """
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
        evidence_status=EvidenceStatus.COMPLETE,
        title="CTE structural alternative candidate",
        rationale="Eligible for later validation.",
        source_layer=StructuralLayer.CTE,
        original_sql=sql,
    )

    assert candidate.original_sql == sql


def test_cte_candidate_supports_insufficient_evidence():
    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.CTE,
        evidence_status=EvidenceStatus.INSUFFICIENT,
        title="CTE structural alternative candidate",
        rationale="Evidence is insufficient for further assessment.",
        source_layer=StructuralLayer.CTE,
        original_sql="SELECT 1",
    )

    assert candidate.evidence_status == EvidenceStatus.INSUFFICIENT


def test_cte_alternative_result_defaults_to_empty():
    result = StructuralCTEAlternativeResult()

    assert result.candidates == []


def test_cte_alternative_result_accepts_candidates():
    candidate = StructuralCTEAlternativeCandidate(
        candidate_id="CTE-CAND-0001",
        alternative_type=CTEAlternativeType.CTE,
        evidence_status=EvidenceStatus.COMPLETE,
        title="CTE structural alternative candidate",
        rationale="Eligible for later validation.",
        source_layer=StructuralLayer.CTE,
        original_sql="WITH x AS (SELECT 1) SELECT * FROM x",
    )

    result = StructuralCTEAlternativeResult(
        candidates=[candidate]
    )

    assert len(result.candidates) == 1
    assert result.candidates[0].candidate_id == "CTE-CAND-0001"
