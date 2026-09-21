from api.schemas.structural_optimization import (
    CandidateStatus,
    EvidenceStatus,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    SemanticSafetyStatus,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralFinding,
    StructuralLayer,
    StructuralOptimizationOpportunity,
    StructuralOpportunityResult,
    SubqueryAlternativeType,
)
from api.services.structural_subquery_candidate_generator import (
    StructuralSubqueryCandidateGenerator,
)


def _analysis():
    return StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[
            StructuralFinding(
                layer=StructuralLayer.WHERE,
                finding_type="WHERE",
                severity="INFO",
                description="WHERE finding",
                evidence="query_block=1; where=present",
            ),
            StructuralFinding(
                layer=StructuralLayer.FROM,
                finding_type="FROM",
                severity="INFO",
                description="FROM finding",
                evidence="query_block=1; from=present",
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


def test_exists_generates_exists_candidate():
    result = StructuralSubqueryCandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.SUBQUERY_EXISTS_ANALYSIS,
                )
            ]
        ),
        "SELECT * FROM orders WHERE EXISTS (...)",
    )

    assert len(result.candidates) == 1

    candidate = result.candidates[0]

    assert candidate.candidate_id == "SUBQ-CAND-0001"
    assert candidate.alternative_type == SubqueryAlternativeType.EXISTS
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert candidate.alternative_sql is None


def test_in_generates_in_candidate():
    result = StructuralSubqueryCandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS,
                )
            ]
        ),
        "SELECT * FROM orders WHERE customer_id IN (...)",
    )

    assert (
        result.candidates[0].alternative_type
        == SubqueryAlternativeType.IN
    )


def test_any_generates_any_candidate():
    result = StructuralSubqueryCandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.SUBQUERY_ANY_ANALYSIS,
                )
            ]
        ),
        "SELECT * FROM orders WHERE customer_id = ANY (...)",
    )

    assert (
        result.candidates[0].alternative_type
        == SubqueryAlternativeType.ANY
    )


def test_derived_table_generates_candidate():
    result = StructuralSubqueryCandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    1,
                    OptimizationOpportunityType.DERIVED_TABLE_ANALYSIS,
                )
            ]
        ),
        "SELECT x.customer_id FROM (...) AS x",
    )

    candidate = result.candidates[0]

    assert candidate.alternative_type == SubqueryAlternativeType.DERIVED_TABLE
    assert candidate.source_layer == StructuralLayer.FROM


def test_original_sql_is_preserved_exactly():
    sql = """
SELECT *
FROM orders
WHERE customer_id IN (
    SELECT customer_id
    FROM customers
)
"""

    result = StructuralSubqueryCandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS,
                )
            ]
        ),
        sql,
    )

    assert result.candidates[0].original_sql == sql


def test_non_identified_opportunity_is_skipped():
    opportunity = StructuralOptimizationOpportunity(
        finding_index=0,
        opportunity_type=OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS,
        status=OptimizationOpportunityStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.INSUFFICIENT,
        evidence_scope="FINDING",
        rationale="Evidence insufficient.",
    )

    result = StructuralSubqueryCandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[opportunity]
        ),
        "SELECT * FROM orders",
    )

    assert result.candidates == []


def test_insufficient_evidence_is_preserved():
    result = StructuralSubqueryCandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS,
                    EvidenceStatus.INSUFFICIENT,
                )
            ]
        ),
        "SELECT * FROM orders",
    )

    # The opportunity status is IDENTIFIED in this helper, so the
    # candidate is still generated, but its evidence remains insufficient.
    candidate = result.candidates[0]

    assert candidate.evidence_status == EvidenceStatus.INSUFFICIENT


def test_multiple_candidates_are_deterministic():
    result = StructuralSubqueryCandidateGenerator().generate(
        _analysis(),
        StructuralOpportunityResult(
            opportunities=[
                _opportunity(
                    0,
                    OptimizationOpportunityType.SUBQUERY_EXISTS_ANALYSIS,
                ),
                _opportunity(
                    0,
                    OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS,
                ),
                _opportunity(
                    1,
                    OptimizationOpportunityType.DERIVED_TABLE_ANALYSIS,
                ),
            ]
        ),
        "SELECT * FROM orders",
    )

    assert [
        candidate.candidate_id
        for candidate in result.candidates
    ] == [
        "SUBQ-CAND-0001",
        "SUBQ-CAND-0002",
        "SUBQ-CAND-0003",
    ]

    assert [
        candidate.alternative_type
        for candidate in result.candidates
    ] == [
        SubqueryAlternativeType.EXISTS,
        SubqueryAlternativeType.IN,
        SubqueryAlternativeType.DERIVED_TABLE,
    ]


def test_unknown_opportunity_type_is_ignored():
    result = StructuralSubqueryCandidateGenerator().generate(
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
                OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS,
            )
        ]
    )

    try:
        StructuralSubqueryCandidateGenerator().generate(
            _analysis(),
            result,
            "SELECT * FROM orders",
        )
    except ValueError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
