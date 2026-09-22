from api.schemas.structural_optimization import (
    CandidateStatus,
    CTEAlternativeType,
    EvidenceStatus,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    SemanticSafetyStatus,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralCTEAlternativeResult,
    StructuralFinding,
    StructuralLayer,
    StructuralOptimizationOpportunity,
    StructuralOpportunityResult,
)
from api.services.structural_cte_candidate_generator import (
    StructuralCTECandidateGenerator,
)


def _analysis():
    return StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            StructuralFinding(
                layer=StructuralLayer.CTE,
                finding_type="CTE_DEFINITION",
                severity="INFO",
                description="CTE definition",
                evidence="cte_name=recent_orders; definition=SELECT * FROM orders",
            ),
            StructuralFinding(
                layer=StructuralLayer.CTE,
                finding_type="RECURSIVE_CTE",
                severity="INFO",
                description="Recursive CTE",
                evidence="cte_names=tree",
            ),
        ],
    )


def _opportunity(
    finding_index,
    opportunity_type,
    evidence_status=EvidenceStatus.COMPLETE,
):
    return StructuralOptimizationOpportunity(
        finding_index=finding_index,
        opportunity_type=opportunity_type,
        status=OptimizationOpportunityStatus.IDENTIFIED,
        evidence_status=evidence_status,
        evidence_scope="FINDING",
        rationale="Structural opportunity identified.",
    )


def test_cte_generates_cte_candidate():
    result = StructuralCTECandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.CTE_ANALYSIS,
                )
            ]
        ),
        "WITH recent_orders AS (SELECT * FROM orders) SELECT * FROM recent_orders",
    )

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.candidate_id == "CTE-CAND-0001"
    assert candidate.alternative_type == CTEAlternativeType.CTE
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert candidate.source_layer == StructuralLayer.CTE
    assert candidate.alternative_sql is None


def test_recursive_cte_generates_recursive_candidate():
    result = StructuralCTECandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    1,
                    OptimizationOpportunityType.RECURSIVE_CTE_ANALYSIS,
                )
            ]
        ),
        "WITH RECURSIVE tree AS (...) SELECT * FROM tree",
    )

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.candidate_id == "CTE-CAND-0001"
    assert candidate.alternative_type == CTEAlternativeType.RECURSIVE_CTE
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert candidate.source_layer == StructuralLayer.CTE
    assert candidate.alternative_sql is None


def test_original_sql_is_preserved_exactly():
    sql = """
WITH recent_orders AS (
    SELECT *
    FROM orders
)
SELECT *
FROM recent_orders
"""

    result = StructuralCTECandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.CTE_ANALYSIS,
                )
            ]
        ),
        sql,
    )

    assert result.candidates[0].original_sql == sql


def test_non_identified_opportunity_is_skipped():
    opportunity = StructuralOptimizationOpportunity(
        finding_index=0,
        opportunity_type=OptimizationOpportunityType.CTE_ANALYSIS,
        status=OptimizationOpportunityStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.INSUFFICIENT,
        evidence_scope="FINDING",
        rationale="Evidence insufficient.",
    )

    result = StructuralCTECandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[opportunity],
        ),
        "WITH recent_orders AS (...) SELECT * FROM recent_orders",
    )

    assert result.candidates == []


def test_insufficient_evidence_is_preserved():
    result = StructuralCTECandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.CTE_ANALYSIS,
                    EvidenceStatus.INSUFFICIENT,
                )
            ]
        ),
        "WITH recent_orders AS (...) SELECT * FROM recent_orders",
    )

    candidate = result.candidates[0]

    assert candidate.evidence_status == EvidenceStatus.INSUFFICIENT


def test_multiple_candidates_are_deterministic():
    result = StructuralCTECandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.CTE_ANALYSIS,
                ),
                _opportunity(
                    1,
                    OptimizationOpportunityType.RECURSIVE_CTE_ANALYSIS,
                ),
            ]
        ),
        "WITH x AS (...) SELECT * FROM x",
    )

    assert [
        candidate.candidate_id
        for candidate in result.candidates
    ] == [
        "CTE-CAND-0001",
        "CTE-CAND-0002",
    ]

    assert [
        candidate.alternative_type
        for candidate in result.candidates
    ] == [
        CTEAlternativeType.CTE,
        CTEAlternativeType.RECURSIVE_CTE,
    ]


def test_unknown_opportunity_type_is_ignored():
    result = StructuralCTECandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.NESTED_QUERY_ANALYSIS,
                )
            ]
        ),
        "SELECT * FROM orders",
    )

    assert result.candidates == []


def test_invalid_finding_index_raises_error():
    result = StructuralOpportunityResult(
        opportunities=[
            _opportunity(
                99,
                OptimizationOpportunityType.CTE_ANALYSIS,
            )
        ]
    )

    try:
        StructuralCTECandidateGenerator().generate(
            _analysis(),
            result,
            "WITH x AS (...) SELECT * FROM x",
        )
    except ValueError as exc:
        assert "finding index" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid finding index")


def test_recursive_candidate_rationale_does_not_claim_equivalence():
    result = StructuralCTECandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    1,
                    OptimizationOpportunityType.RECURSIVE_CTE_ANALYSIS,
                )
            ]
        ),
        "WITH RECURSIVE tree AS (...) SELECT * FROM tree",
    )

    rationale = result.candidates[0].rationale.lower()

    assert "semantic equivalence" in rationale
    assert "performance improvement" in rationale
    assert "established" in rationale
