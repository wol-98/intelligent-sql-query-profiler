import pytest
from pydantic import ValidationError

from api.schemas.structural_optimization import (
    EvidenceStatus,
    OpportunityEvidenceScope,
    ProceduralWorkloadOpportunityStatus,
    ProceduralWorkloadOpportunityType,
    StructuralLayer,
    StructuralProceduralWorkloadOpportunity,
    StructuralProceduralWorkloadOpportunityResult,
)


def make_opportunity(
    opportunity_type: ProceduralWorkloadOpportunityType,
    *,
    finding_index: int = 0,
    status: ProceduralWorkloadOpportunityStatus = (
        ProceduralWorkloadOpportunityStatus.IDENTIFIED
    ),
    evidence_status: EvidenceStatus = EvidenceStatus.COMPLETE,
    evidence_scope: OpportunityEvidenceScope = (
        OpportunityEvidenceScope.FINDING
    ),
    rationale: str = "Procedural workload opportunity identified.",
) -> StructuralProceduralWorkloadOpportunity:
    return StructuralProceduralWorkloadOpportunity(
        finding_index=finding_index,
        opportunity_type=opportunity_type,
        status=status,
        evidence_status=evidence_status,
        evidence_scope=evidence_scope,
        rationale=rationale,
    )


def test_all_procedural_opportunity_types_exist():
    assert (
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION.value
        == "REUSABLE_COMPUTATION"
    )

    assert (
        ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION.value
        == "PARAMETERIZED_OPERATION"
    )

    assert (
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION.value
        == "MULTI_STEP_DATA_OPERATION"
    )

    assert (
        ProceduralWorkloadOpportunityType.DATA_MUTATION_WORKFLOW.value
        == "DATA_MUTATION_WORKFLOW"
    )

    assert (
        ProceduralWorkloadOpportunityType.COMPLEX_PROCEDURAL_LOGIC.value
        == "COMPLEX_PROCEDURAL_LOGIC"
    )

    assert (
        ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW.value
        == "SIDE_EFFECTING_WORKFLOW"
    )


def test_all_procedural_opportunity_statuses_exist():
    assert (
        ProceduralWorkloadOpportunityStatus.IDENTIFIED.value
        == "IDENTIFIED"
    )

    assert (
        ProceduralWorkloadOpportunityStatus.NOT_ASSESSED.value
        == "NOT_ASSESSED"
    )

    assert (
        ProceduralWorkloadOpportunityStatus.STRUCTURALLY_NEUTRAL.value
        == "STRUCTURALLY_NEUTRAL"
    )


def test_reusable_computation_opportunity_contract():
    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
    )

    assert (
        opportunity.opportunity_type
        == ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
    )

    assert (
        opportunity.status
        == ProceduralWorkloadOpportunityStatus.IDENTIFIED
    )


def test_multi_step_data_operation_opportunity_contract():
    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
    )

    assert (
        opportunity.opportunity_type
        == ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
    )

    assert (
        opportunity.status
        == ProceduralWorkloadOpportunityStatus.IDENTIFIED
    )


def test_side_effecting_workflow_opportunity_contract():
    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW
    )

    assert (
        opportunity.opportunity_type
        == ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW
    )


def test_finding_index_must_be_non_negative():
    with pytest.raises(ValidationError):
        make_opportunity(
            ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION,
            finding_index=-1,
        )


def test_evidence_status_is_preserved():
    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.DATA_MUTATION_WORKFLOW,
        evidence_status=EvidenceStatus.PARTIAL,
    )

    assert opportunity.evidence_status == EvidenceStatus.PARTIAL


def test_evidence_scope_is_preserved():
    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.COMPLEX_PROCEDURAL_LOGIC,
        evidence_scope=OpportunityEvidenceScope.CLASSIFICATION,
    )

    assert opportunity.evidence_scope == OpportunityEvidenceScope.CLASSIFICATION

def test_optional_structural_layer_provenance_is_not_part_of_contract():
    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
    )

    assert not hasattr(opportunity, "source_layer")


def test_result_defaults_to_empty_opportunity_list():
    result = StructuralProceduralWorkloadOpportunityResult()

    assert result.opportunities == []


def test_result_preserves_opportunity_order():
    first = make_opportunity(
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION,
        finding_index=1,
    )

    second = make_opportunity(
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION,
        finding_index=4,
    )

    third = make_opportunity(
        ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW,
        finding_index=7,
    )

    result = StructuralProceduralWorkloadOpportunityResult(
        opportunities=[
            first,
            second,
            third,
        ]
    )

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION,
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION,
        ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW,
    ]

    assert [
        opportunity.finding_index
        for opportunity in result.opportunities
    ] == [1, 4, 7]


def test_structural_neutral_status_is_preserved():
    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
        status=ProceduralWorkloadOpportunityStatus.STRUCTURALLY_NEUTRAL,
    )

    assert (
        opportunity.status
        == ProceduralWorkloadOpportunityStatus.STRUCTURALLY_NEUTRAL
    )


def test_original_rationale_is_preserved():
    rationale = (
        "The workload contains reusable computation requiring "
        "later procedural analysis."
    )

    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION,
        rationale=rationale,
    )

    assert opportunity.rationale == rationale
