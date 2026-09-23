import pytest

from api.schemas.structural_optimization import (
    DatabaseRoutineRecommendationType,
    EvidenceStatus,
    ProceduralWorkloadOpportunityType,
)
from api.services.procedural_routine_recommendation_rules import (
    ProceduralRoutineRecommendationRule,
    ProceduralRoutineRecommendationRuleEngine,
)


def test_reusable_computation_maps_to_function():
    rule = ProceduralRoutineRecommendationRuleEngine().get_rule(
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
    )

    assert isinstance(
        rule,
        ProceduralRoutineRecommendationRule,
    )

    assert (
        rule.recommendation_type
        == DatabaseRoutineRecommendationType.FUNCTION
    )

    assert rule.required_evidence_status == EvidenceStatus.COMPLETE
    assert rule.requires_behavioral_validation is True


def test_parameterized_operation_maps_to_function():
    rule = ProceduralRoutineRecommendationRuleEngine().get_rule(
        ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
    )

    assert (
        rule.recommendation_type
        == DatabaseRoutineRecommendationType.FUNCTION
    )

    assert rule.required_evidence_status == EvidenceStatus.COMPLETE
    assert rule.requires_behavioral_validation is True


def test_multi_step_operation_maps_to_procedure():
    rule = ProceduralRoutineRecommendationRuleEngine().get_rule(
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
    )

    assert (
        rule.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )

    assert rule.required_evidence_status == EvidenceStatus.COMPLETE
    assert rule.requires_behavioral_validation is True


def test_data_mutation_workflow_maps_to_procedure():
    rule = ProceduralRoutineRecommendationRuleEngine().get_rule(
        ProceduralWorkloadOpportunityType.DATA_MUTATION_WORKFLOW
    )

    assert (
        rule.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_complex_procedural_logic_maps_to_procedure():
    rule = ProceduralRoutineRecommendationRuleEngine().get_rule(
        ProceduralWorkloadOpportunityType.COMPLEX_PROCEDURAL_LOGIC
    )

    assert (
        rule.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_side_effecting_workflow_maps_to_procedure():
    rule = ProceduralRoutineRecommendationRuleEngine().get_rule(
        ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW
    )

    assert (
        rule.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_all_opportunity_types_have_rules():
    engine = ProceduralRoutineRecommendationRuleEngine()

    for opportunity_type in ProceduralWorkloadOpportunityType:
        rule = engine.get_rule(opportunity_type)

        assert isinstance(
            rule,
            ProceduralRoutineRecommendationRule,
        )

        assert rule.required_evidence_status == EvidenceStatus.COMPLETE
        assert rule.requires_behavioral_validation is True


def test_rules_are_deterministic():
    engine = ProceduralRoutineRecommendationRuleEngine()

    first = engine.get_rule(
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
    )

    second = engine.get_rule(
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
    )

    assert first == second


def test_function_rule_has_function_type():
    engine = ProceduralRoutineRecommendationRuleEngine()

    for opportunity_type in (
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION,
        ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
    ):
        rule = engine.get_rule(opportunity_type)

        assert (
            rule.recommendation_type
            == DatabaseRoutineRecommendationType.FUNCTION
        )


def test_procedure_rule_has_procedure_type():
    engine = ProceduralRoutineRecommendationRuleEngine()

    for opportunity_type in (
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION,
        ProceduralWorkloadOpportunityType.DATA_MUTATION_WORKFLOW,
        ProceduralWorkloadOpportunityType.COMPLEX_PROCEDURAL_LOGIC,
        ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW,
    ):
        rule = engine.get_rule(opportunity_type)

        assert (
            rule.recommendation_type
            == DatabaseRoutineRecommendationType.PROCEDURE
        )


def test_rules_require_complete_evidence():
    engine = ProceduralRoutineRecommendationRuleEngine()

    for opportunity_type in ProceduralWorkloadOpportunityType:
        rule = engine.get_rule(opportunity_type)

        assert (
            rule.required_evidence_status
            == EvidenceStatus.COMPLETE
        )


def test_rules_require_behavioral_validation():
    engine = ProceduralRoutineRecommendationRuleEngine()

    for opportunity_type in ProceduralWorkloadOpportunityType:
        rule = engine.get_rule(opportunity_type)

        assert rule.requires_behavioral_validation is True


def test_rule_rationales_do_not_claim_performance_improvement():
    engine = ProceduralRoutineRecommendationRuleEngine()

    for opportunity_type in ProceduralWorkloadOpportunityType:
        rule = engine.get_rule(opportunity_type)

        assert "performance improvement" not in (
            rule.rationale.lower()
        )

        assert "benchmark" not in (
            rule.rationale.lower()
        )


def test_unknown_opportunity_type_is_rejected():
    engine = ProceduralRoutineRecommendationRuleEngine()

    with pytest.raises(
        ValueError,
        match="No procedural routine recommendation rule exists",
    ):
        engine.get_rule("UNKNOWN")
