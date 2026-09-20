import pytest

from api.schemas.structural_optimization import (
    AlternativeType,
    CandidateStatus,
    EvidenceStatus,
    OpportunityEvidenceScope,
    OptimizationCandidate,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralLayer,
    StructuralOptimizationOpportunity,
    StructuralOpportunityResult,
)
from api.services.structural_candidate_generator import (
    StructuralCandidateGenerator,
)


ORIGINAL_SQL = (
    "SELECT customer_id FROM orders WHERE status = 'completed'"
)


def _analysis(
    findings: list | None = None,
) -> StructuralAnalysis:
    return StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        findings=findings or [],
    )


def _finding(layer: StructuralLayer):
    from api.schemas.structural_optimization import StructuralFinding

    return StructuralFinding(
        layer=layer,
        finding_type=layer.value,
        severity="INFO",
        description=f"Structural finding for {layer.value}.",
        evidence=f"{layer.value.lower()}=example",
    )


def _opportunity(
    *,
    finding_index: int,
    opportunity_type: OptimizationOpportunityType,
    status: OptimizationOpportunityStatus = (
        OptimizationOpportunityStatus.IDENTIFIED
    ),
) -> StructuralOptimizationOpportunity:
    return StructuralOptimizationOpportunity(
        finding_index=finding_index,
        opportunity_type=opportunity_type,
        status=status,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_scope=OpportunityEvidenceScope.CLASSIFICATION,
        rationale="Established structural opportunity.",
    )


def test_predicate_opportunity_generates_index_candidate():
    analysis = _analysis(
        findings=[_finding(StructuralLayer.WHERE)]
    )

    opportunities = StructuralOpportunityResult(
        opportunities=[
            _opportunity(
                finding_index=0,
                opportunity_type=OptimizationOpportunityType.PREDICATE_ANALYSIS,
            )
        ]
    )

    result = StructuralCandidateGenerator().generate(
        analysis,
        opportunities,
        ORIGINAL_SQL,
    )

    assert len(result) == 1

    candidate = result[0]

    assert isinstance(candidate, OptimizationCandidate)
    assert candidate.candidate_id == "CAND-0001"
    assert candidate.alternative_type == AlternativeType.INDEX
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.source_layer == StructuralLayer.WHERE
    assert candidate.original_sql == ORIGINAL_SQL
    assert candidate.optimized_sql is None
    assert candidate.index_ddl is None
    assert candidate.architectural_recommendation is None


@pytest.mark.parametrize(
    ("opportunity_type", "alternative_type"),
    [
        (
            OptimizationOpportunityType.PREDICATE_ANALYSIS,
            AlternativeType.INDEX,
        ),
        (
            OptimizationOpportunityType.JOIN_ANALYSIS,
            AlternativeType.INDEX,
        ),
        (
            OptimizationOpportunityType.AGGREGATION_ANALYSIS,
            AlternativeType.INDEX,
        ),
        (
            OptimizationOpportunityType.WINDOW_ANALYSIS,
            AlternativeType.INDEX,
        ),
        (
            OptimizationOpportunityType.ORDERING_ANALYSIS,
            AlternativeType.INDEX,
        ),
        (
            OptimizationOpportunityType.ROW_LIMITING_ANALYSIS,
            AlternativeType.INDEX,
        ),
        (
            OptimizationOpportunityType.NESTED_QUERY_ANALYSIS,
            AlternativeType.SQL_REWRITE,
        ),
    ],
)
def test_opportunity_types_map_to_expected_alternative_types(
    opportunity_type,
    alternative_type,
):
    analysis = _analysis(
        findings=[_finding(StructuralLayer.WHERE)]
    )

    opportunities = StructuralOpportunityResult(
        opportunities=[
            _opportunity(
                finding_index=0,
                opportunity_type=opportunity_type,
            )
        ]
    )

    result = StructuralCandidateGenerator().generate(
        analysis,
        opportunities,
        ORIGINAL_SQL,
    )

    assert len(result) == 1
    assert result[0].alternative_type == alternative_type


@pytest.mark.parametrize(
    "status",
    [
        OptimizationOpportunityStatus.NOT_ASSESSED,
        OptimizationOpportunityStatus.STRUCTURALLY_NEUTRAL,
    ],
)
def test_non_identified_opportunities_generate_no_candidates(status):
    analysis = _analysis(
        findings=[_finding(StructuralLayer.WHERE)]
    )

    opportunities = StructuralOpportunityResult(
        opportunities=[
            _opportunity(
                finding_index=0,
                opportunity_type=OptimizationOpportunityType.PREDICATE_ANALYSIS,
                status=status,
            )
        ]
    )

    result = StructuralCandidateGenerator().generate(
        analysis,
        opportunities,
        ORIGINAL_SQL,
    )

    assert result == []


def test_candidate_ids_are_deterministic_and_follow_opportunity_order():
    analysis = _analysis(
        findings=[
            _finding(StructuralLayer.WHERE),
            _finding(StructuralLayer.ORDER_BY),
        ]
    )

    opportunities = StructuralOpportunityResult(
        opportunities=[
            _opportunity(
                finding_index=0,
                opportunity_type=OptimizationOpportunityType.PREDICATE_ANALYSIS,
            ),
            _opportunity(
                finding_index=1,
                opportunity_type=OptimizationOpportunityType.ORDERING_ANALYSIS,
            ),
        ]
    )

    result = StructuralCandidateGenerator().generate(
        analysis,
        opportunities,
        ORIGINAL_SQL,
    )

    assert [candidate.candidate_id for candidate in result] == [
        "CAND-0001",
        "CAND-0002",
    ]

    assert [candidate.source_layer for candidate in result] == [
        StructuralLayer.WHERE,
        StructuralLayer.ORDER_BY,
    ]


def test_invalid_finding_index_raises_error():
    analysis = _analysis(
        findings=[_finding(StructuralLayer.WHERE)]
    )

    opportunities = StructuralOpportunityResult(
        opportunities=[
            _opportunity(
                finding_index=5,
                opportunity_type=OptimizationOpportunityType.PREDICATE_ANALYSIS,
            )
        ]
    )

    with pytest.raises(ValueError, match="finding index"):
        StructuralCandidateGenerator().generate(
            analysis,
            opportunities,
            ORIGINAL_SQL,
        )


def test_original_analysis_is_not_modified():
    analysis = _analysis(
        findings=[
            _finding(StructuralLayer.WHERE),
            _finding(StructuralLayer.ORDER_BY),
        ]
    )

    original = analysis.model_dump()

    opportunities = StructuralOpportunityResult(
        opportunities=[
            _opportunity(
                finding_index=0,
                opportunity_type=OptimizationOpportunityType.PREDICATE_ANALYSIS,
            ),
            _opportunity(
                finding_index=1,
                opportunity_type=OptimizationOpportunityType.ORDERING_ANALYSIS,
            ),
        ]
    )

    StructuralCandidateGenerator().generate(
        analysis,
        opportunities,
        ORIGINAL_SQL,
    )

    assert analysis.model_dump() == original
