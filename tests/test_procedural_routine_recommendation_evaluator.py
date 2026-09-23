from api.schemas.structural_optimization import (
    DatabaseRoutineRecommendationType,
    EvidenceStatus,
    OpportunityEvidenceScope,
    ProceduralWorkloadOpportunityStatus,
    ProceduralWorkloadOpportunityType,
    StructuralProceduralWorkloadOpportunity,
)
from api.services.procedural_routine_recommendation_evaluator import (
    ProceduralRoutineRecommendationEvaluation,
    ProceduralRoutineRecommendationEvaluator,
)


def make_opportunity(
    opportunity_type: ProceduralWorkloadOpportunityType,
    *,
    status: ProceduralWorkloadOpportunityStatus = (
        ProceduralWorkloadOpportunityStatus.IDENTIFIED
    ),
    evidence_status: EvidenceStatus = EvidenceStatus.COMPLETE,
    finding_index: int = 0,
) -> StructuralProceduralWorkloadOpportunity:
    return StructuralProceduralWorkloadOpportunity(
        finding_index=finding_index,
        opportunity_type=opportunity_type,
        status=status,
        evidence_status=evidence_status,
        evidence_scope=OpportunityEvidenceScope.FINDING,
        rationale="Procedural workload opportunity identified.",
    )


def test_complete_reusable_computation_is_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
        )
    )

    assert isinstance(
        result,
        ProceduralRoutineRecommendationEvaluation,
    )

    assert result.eligible is True
    assert (
        result.rule.recommendation_type
        == DatabaseRoutineRecommendationType.FUNCTION
    )


def test_complete_parameterized_operation_is_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
        )
    )

    assert result.eligible is True
    assert (
        result.rule.recommendation_type
        == DatabaseRoutineRecommendationType.FUNCTION
    )


def test_complete_multi_step_operation_is_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
        )
    )

    assert result.eligible is True
    assert (
        result.rule.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_complete_data_mutation_workflow_is_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.DATA_MUTATION_WORKFLOW
        )
    )

    assert result.eligible is True
    assert (
        result.rule.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_complete_complex_procedural_logic_is_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.COMPLEX_PROCEDURAL_LOGIC
        )
    )

    assert result.eligible is True
    assert (
        result.rule.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_complete_side_effecting_workflow_is_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW
        )
    )

    assert result.eligible is True
    assert (
        result.rule.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_partial_evidence_is_not_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION,
            evidence_status=EvidenceStatus.PARTIAL,
        )
    )

    assert result.eligible is False


def test_insufficient_evidence_is_not_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION,
            evidence_status=EvidenceStatus.INSUFFICIENT,
        )
    )

    assert result.eligible is False


def test_not_assessed_opportunity_is_not_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION,
            status=ProceduralWorkloadOpportunityStatus.NOT_ASSESSED,
        )
    )

    assert result.eligible is False


def test_structurally_neutral_opportunity_is_not_eligible():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
            status=(
                ProceduralWorkloadOpportunityStatus.STRUCTURALLY_NEUTRAL
            ),
        )
    )

    assert result.eligible is False


def test_evaluation_is_deterministic():
    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
    )

    evaluator = ProceduralRoutineRecommendationEvaluator()

    first = evaluator.evaluate(opportunity)
    second = evaluator.evaluate(opportunity)

    assert first == second


def test_evaluation_does_not_modify_opportunity():
    opportunity = make_opportunity(
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
    )

    before = opportunity.model_copy(deep=True)

    ProceduralRoutineRecommendationEvaluator().evaluate(
        opportunity
    )

    assert opportunity == before


def test_complete_evidence_is_required_by_the_rule():
    evaluator = ProceduralRoutineRecommendationEvaluator()

    for opportunity_type in ProceduralWorkloadOpportunityType:
        result = evaluator.evaluate(
            make_opportunity(opportunity_type)
        )

        assert (
            result.rule.required_evidence_status
            == EvidenceStatus.COMPLETE
        )


def test_evaluation_does_not_mean_behavioral_validation():
    result = ProceduralRoutineRecommendationEvaluator().evaluate(
        make_opportunity(
            ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
        )
    )

    assert result.eligible is True
    assert result.rule.requires_behavioral_validation is True
    assert "validation" in result.rationale.lower()
