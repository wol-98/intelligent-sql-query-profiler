import pytest

from api.schemas.structural_optimization import (
    DatabaseRoutineRecommendationType,
)
from api.services.database_routine_semantic_preconditions import (
    DatabaseRoutineSemanticPreconditionRule,
    DatabaseRoutineSemanticPreconditionRuleEngine,
)


def test_function_rule_exists():
    engine = (
        DatabaseRoutineSemanticPreconditionRuleEngine
        .with_default_rules()
    )

    rule = engine.get_rule(
        DatabaseRoutineRecommendationType.FUNCTION
    )

    assert isinstance(
        rule,
        DatabaseRoutineSemanticPreconditionRule,
    )


def test_procedure_rule_exists():
    engine = (
        DatabaseRoutineSemanticPreconditionRuleEngine
        .with_default_rules()
    )

    rule = engine.get_rule(
        DatabaseRoutineRecommendationType.PROCEDURE
    )

    assert isinstance(
        rule,
        DatabaseRoutineSemanticPreconditionRule,
    )


def test_function_rule_contains_function_conditions():
    engine = (
        DatabaseRoutineSemanticPreconditionRuleEngine
        .with_default_rules()
    )

    rule = engine.get_rule(
        DatabaseRoutineRecommendationType.FUNCTION
    )

    assert rule.required_conditions == (
        "PARAMETER_SIGNATURE",
        "RETURN_VALUE_SEMANTICS",
        "INPUT_DATA_DEPENDENCIES",
        "NULL_AND_TYPE_SEMANTICS",
        "DETERMINISM_VOLATILITY",
        "ERROR_BEHAVIOR",
        "SIDE_EFFECT_BEHAVIOR",
        "SECURITY_CONTEXT",
    )


def test_procedure_rule_contains_procedure_conditions():
    engine = (
        DatabaseRoutineSemanticPreconditionRuleEngine
        .with_default_rules()
    )

    rule = engine.get_rule(
        DatabaseRoutineRecommendationType.PROCEDURE
    )

    assert rule.required_conditions == (
        "PARAMETER_SIGNATURE",
        "OUTPUT_OR_RESULT_SEMANTICS",
        "MULTI_STEP_EXECUTION",
        "DATA_MUTATION_BEHAVIOR",
        "TRANSACTION_BEHAVIOR",
        "SIDE_EFFECT_BEHAVIOR",
        "ERROR_AND_ROLLBACK_BEHAVIOR",
        "SECURITY_CONTEXT",
    )


def test_function_rule_does_not_use_procedure_conditions():
    engine = (
        DatabaseRoutineSemanticPreconditionRuleEngine
        .with_default_rules()
    )

    rule = engine.get_rule(
        DatabaseRoutineRecommendationType.FUNCTION
    )

    assert "TRANSACTION_BEHAVIOR" not in (
        rule.required_conditions
    )


def test_procedure_rule_does_not_use_function_volatility_condition():
    engine = (
        DatabaseRoutineSemanticPreconditionRuleEngine
        .with_default_rules()
    )

    rule = engine.get_rule(
        DatabaseRoutineRecommendationType.PROCEDURE
    )

    assert "DETERMINISM_VOLATILITY" not in (
        rule.required_conditions
    )


def test_rules_are_deterministic():
    engine = (
        DatabaseRoutineSemanticPreconditionRuleEngine
        .with_default_rules()
    )

    first = engine.get_rule(
        DatabaseRoutineRecommendationType.FUNCTION
    )

    second = engine.get_rule(
        DatabaseRoutineRecommendationType.FUNCTION
    )

    assert first == second


def test_duplicate_rules_are_rejected():
    rule = DatabaseRoutineSemanticPreconditionRule(
        recommendation_type=(
            DatabaseRoutineRecommendationType.FUNCTION
        ),
        required_conditions=(
            "PARAMETER_SIGNATURE",
        ),
        rationale="Test rule.",
    )

    with pytest.raises(
        ValueError,
        match="Duplicate database routine semantic precondition rule",
    ):
        DatabaseRoutineSemanticPreconditionRuleEngine(
            rules=(rule, rule)
        )


def test_unknown_recommendation_type_is_rejected():
    engine = (
        DatabaseRoutineSemanticPreconditionRuleEngine
        .with_default_rules()
    )

    with pytest.raises(
        ValueError,
        match="No database routine semantic precondition rule exists",
    ):
        engine.get_rule("UNKNOWN")
