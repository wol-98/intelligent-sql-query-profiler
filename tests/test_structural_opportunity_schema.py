import pytest
from pydantic import ValidationError

from api.schemas.structural_optimization import (
    EvidenceStatus,
    OpportunityEvidenceScope,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    StructuralOptimizationOpportunity,
    StructuralOpportunityResult,
)


def test_valid_structural_optimization_opportunity():
    opportunity = StructuralOptimizationOpportunity(
        finding_index=0,
        opportunity_type=OptimizationOpportunityType.PREDICATE_ANALYSIS,
        status=OptimizationOpportunityStatus.IDENTIFIED,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_scope=OpportunityEvidenceScope.FINDING,
        rationale="A predicate was structurally identified for further analysis.",
    )

    assert opportunity.finding_index == 0
    assert opportunity.opportunity_type == (
        OptimizationOpportunityType.PREDICATE_ANALYSIS
    )
    assert opportunity.status == OptimizationOpportunityStatus.IDENTIFIED
    assert opportunity.evidence_status == EvidenceStatus.COMPLETE
    assert opportunity.evidence_scope == OpportunityEvidenceScope.FINDING


def test_all_opportunity_types_are_supported():
    for opportunity_type in OptimizationOpportunityType:
        opportunity = StructuralOptimizationOpportunity(
            finding_index=0,
            opportunity_type=opportunity_type,
            status=OptimizationOpportunityStatus.IDENTIFIED,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_scope=OpportunityEvidenceScope.CLASSIFICATION,
            rationale="Structural opportunity identified for later analysis.",
        )

        assert opportunity.opportunity_type == opportunity_type


def test_all_opportunity_statuses_are_supported():
    for status in OptimizationOpportunityStatus:
        opportunity = StructuralOptimizationOpportunity(
            finding_index=0,
            opportunity_type=OptimizationOpportunityType.JOIN_ANALYSIS,
            status=status,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_scope=OpportunityEvidenceScope.FINDING,
            rationale="Status is represented explicitly in the opportunity contract.",
        )

        assert opportunity.status == status


def test_evidence_status_is_preserved():
    for evidence_status in EvidenceStatus:
        opportunity = StructuralOptimizationOpportunity(
            finding_index=1,
            opportunity_type=OptimizationOpportunityType.AGGREGATION_ANALYSIS,
            status=OptimizationOpportunityStatus.IDENTIFIED,
            evidence_status=evidence_status,
            evidence_scope=OpportunityEvidenceScope.FINDING,
            rationale="Evidence status is explicitly represented.",
        )

        assert opportunity.evidence_status == evidence_status


def test_evidence_scope_is_preserved():
    for scope in OpportunityEvidenceScope:
        opportunity = StructuralOptimizationOpportunity(
            finding_index=2,
            opportunity_type=OptimizationOpportunityType.ORDERING_ANALYSIS,
            status=OptimizationOpportunityStatus.IDENTIFIED,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_scope=scope,
            rationale="Evidence provenance is explicitly represented.",
        )

        assert opportunity.evidence_scope == scope


def test_negative_finding_index_is_rejected():
    with pytest.raises(ValidationError):
        StructuralOptimizationOpportunity(
            finding_index=-1,
            opportunity_type=OptimizationOpportunityType.PREDICATE_ANALYSIS,
            status=OptimizationOpportunityStatus.IDENTIFIED,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_scope=OpportunityEvidenceScope.FINDING,
            rationale="Invalid finding index.",
        )


def test_invalid_opportunity_type_is_rejected():
    with pytest.raises(ValidationError):
        StructuralOptimizationOpportunity(
            finding_index=0,
            opportunity_type="INVALID_TYPE",
            status=OptimizationOpportunityStatus.IDENTIFIED,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_scope=OpportunityEvidenceScope.FINDING,
            rationale="Invalid opportunity type.",
        )


def test_invalid_status_is_rejected():
    with pytest.raises(ValidationError):
        StructuralOptimizationOpportunity(
            finding_index=0,
            opportunity_type=OptimizationOpportunityType.WINDOW_ANALYSIS,
            status="INVALID_STATUS",
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_scope=OpportunityEvidenceScope.FINDING,
            rationale="Invalid opportunity status.",
        )


def test_invalid_evidence_scope_is_rejected():
    with pytest.raises(ValidationError):
        StructuralOptimizationOpportunity(
            finding_index=0,
            opportunity_type=OptimizationOpportunityType.NESTED_QUERY_ANALYSIS,
            status=OptimizationOpportunityStatus.IDENTIFIED,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_scope="INVALID_SCOPE",
            rationale="Invalid evidence scope.",
        )


def test_structural_opportunity_result_defaults_to_empty():
    result = StructuralOpportunityResult()

    assert result.opportunities == []


def test_structural_opportunity_result_preserves_opportunities():
    opportunity = StructuralOptimizationOpportunity(
        finding_index=3,
        opportunity_type=OptimizationOpportunityType.ROW_LIMITING_ANALYSIS,
        status=OptimizationOpportunityStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.INSUFFICIENT,
        evidence_scope=OpportunityEvidenceScope.CLASSIFICATION,
        rationale="Insufficient evidence prevents further assessment.",
    )

    result = StructuralOpportunityResult(opportunities=[opportunity])

    assert len(result.opportunities) == 1
    assert result.opportunities[0] == opportunity


def test_opportunity_rationale_is_required():
    with pytest.raises(ValidationError):
        StructuralOptimizationOpportunity(
            finding_index=0,
            opportunity_type=OptimizationOpportunityType.JOIN_ANALYSIS,
            status=OptimizationOpportunityStatus.IDENTIFIED,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_scope=OpportunityEvidenceScope.FINDING,
        )
