from api.schemas.structural_optimization import (
    ArchitecturalOpportunityStatus,
    ArchitecturalOpportunityType,
    EvidenceStatus,
    OpportunityEvidenceScope,
    StructuralArchitecturalOpportunity,
    StructuralArchitecturalOpportunityResult,
)


def make_opportunity(
    opportunity_type: ArchitecturalOpportunityType,
    *,
    status: ArchitecturalOpportunityStatus = (
        ArchitecturalOpportunityStatus.IDENTIFIED
    ),
    evidence_status: EvidenceStatus = EvidenceStatus.COMPLETE,
):
    return StructuralArchitecturalOpportunity(
        finding_index=0,
        opportunity_type=opportunity_type,
        status=status,
        evidence_status=evidence_status,
        evidence_scope=OpportunityEvidenceScope.FINDING,
        rationale="Architectural structure identified for later analysis.",
    )


def test_reusable_cte_opportunity():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.REUSABLE_CTE
    )

    assert opportunity.opportunity_type == (
        ArchitecturalOpportunityType.REUSABLE_CTE
    )
    assert opportunity.status == ArchitecturalOpportunityStatus.IDENTIFIED


def test_aggregated_result_opportunity():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.AGGREGATED_RESULT
    )

    assert opportunity.opportunity_type == (
        ArchitecturalOpportunityType.AGGREGATED_RESULT
    )


def test_filtered_relational_result_opportunity():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
    )

    assert opportunity.opportunity_type == (
        ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
    )


def test_analytical_result_opportunity():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.ANALYTICAL_RESULT
    )

    assert opportunity.opportunity_type == (
        ArchitecturalOpportunityType.ANALYTICAL_RESULT
    )


def test_recursive_cte_opportunity():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.RECURSIVE_CTE
    )

    assert opportunity.opportunity_type == (
        ArchitecturalOpportunityType.RECURSIVE_CTE
    )


def test_not_assessed_status_is_preserved():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.RECURSIVE_CTE,
        status=ArchitecturalOpportunityStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.INSUFFICIENT,
    )

    assert opportunity.status == ArchitecturalOpportunityStatus.NOT_ASSESSED
    assert opportunity.evidence_status == EvidenceStatus.INSUFFICIENT


def test_structurally_neutral_status_is_preserved():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.ANALYTICAL_RESULT,
        status=ArchitecturalOpportunityStatus.STRUCTURALLY_NEUTRAL,
    )

    assert opportunity.status == (
        ArchitecturalOpportunityStatus.STRUCTURALLY_NEUTRAL
    )


def test_finding_scope_is_preserved():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.REUSABLE_CTE
    )

    assert opportunity.evidence_scope == OpportunityEvidenceScope.FINDING


def test_finding_index_must_be_non_negative():
    opportunity = StructuralArchitecturalOpportunity(
        finding_index=3,
        opportunity_type=ArchitecturalOpportunityType.AGGREGATED_RESULT,
        status=ArchitecturalOpportunityStatus.IDENTIFIED,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_scope=OpportunityEvidenceScope.FINDING,
        rationale="Architectural structure identified.",
    )

    assert opportunity.finding_index == 3


def test_empty_opportunity_result_is_valid():
    result = StructuralArchitecturalOpportunityResult()

    assert result.opportunities == []


def test_opportunity_result_preserves_order():
    first = make_opportunity(
        ArchitecturalOpportunityType.REUSABLE_CTE
    )
    second = make_opportunity(
        ArchitecturalOpportunityType.AGGREGATED_RESULT
    )

    result = StructuralArchitecturalOpportunityResult(
        opportunities=[first, second]
    )

    assert len(result.opportunities) == 2
    assert result.opportunities[0].opportunity_type == (
        ArchitecturalOpportunityType.REUSABLE_CTE
    )
    assert result.opportunities[1].opportunity_type == (
        ArchitecturalOpportunityType.AGGREGATED_RESULT
    )
