import pytest

from api.schemas.structural_optimization import (
    CTEAlternativeType,
    StructuralLayer,
)
from api.services.structural_cte_alternative_rules import (
    StructuralCTEAlternativeRule,
    StructuralCTEAlternativeRuleEngine,
)


@pytest.fixture
def engine() -> StructuralCTEAlternativeRuleEngine:
    return StructuralCTEAlternativeRuleEngine()


@pytest.mark.parametrize(
    "alternative_type,expected_family",
    [
        (
            CTEAlternativeType.CTE,
            "CTE_TO_STRUCTURAL_ALTERNATIVE",
        ),
        (
            CTEAlternativeType.RECURSIVE_CTE,
            "RECURSIVE_CTE_TO_STRUCTURAL_ALTERNATIVE",
        ),
    ],
)
def test_all_supported_types_have_deterministic_rules(
    engine: StructuralCTEAlternativeRuleEngine,
    alternative_type: CTEAlternativeType,
    expected_family: str,
) -> None:
    rule = engine.get_rule(alternative_type)

    assert isinstance(rule, StructuralCTEAlternativeRule)
    assert rule.source_type == alternative_type
    assert rule.alternative_family == expected_family
    assert rule.source_layer == StructuralLayer.CTE
    assert rule.requires_semantic_validation is True
    assert len(rule.safety_constraints) > 0


def test_cte_rule_contains_output_and_scope_constraints(
    engine: StructuralCTEAlternativeRuleEngine,
) -> None:
    rule = engine.get_rule(CTEAlternativeType.CTE)

    assert any(
        "output columns" in constraint
        for constraint in rule.safety_constraints
    )
    assert any(
        "query-scope" in constraint
        for constraint in rule.safety_constraints
    )
    assert any(
        "materialization" in constraint
        for constraint in rule.safety_constraints
    )


def test_recursive_cte_rule_contains_recursive_constraints(
    engine: StructuralCTEAlternativeRuleEngine,
) -> None:
    rule = engine.get_rule(CTEAlternativeType.RECURSIVE_CTE)

    assert any(
        "recursive anchor" in constraint
        for constraint in rule.safety_constraints
    )
    assert any(
        "recursive member" in constraint
        for constraint in rule.safety_constraints
    )
    assert any(
        "UNION or UNION ALL" in constraint
        for constraint in rule.safety_constraints
    )
    assert any(
        "termination" in constraint
        for constraint in rule.safety_constraints
    )


@pytest.mark.parametrize(
    "alternative_type",
    list(CTEAlternativeType),
)
def test_every_cte_rule_requires_semantic_validation(
    engine: StructuralCTEAlternativeRuleEngine,
    alternative_type: CTEAlternativeType,
) -> None:
    rule = engine.get_rule(alternative_type)

    assert rule.requires_semantic_validation is True
    assert len(rule.safety_constraints) > 0


def test_rule_lookup_is_deterministic(
    engine: StructuralCTEAlternativeRuleEngine,
) -> None:
    first = engine.get_rule(CTEAlternativeType.CTE)
    second = engine.get_rule(CTEAlternativeType.CTE)

    assert first == second


def test_recursive_rule_lookup_is_deterministic(
    engine: StructuralCTEAlternativeRuleEngine,
) -> None:
    first = engine.get_rule(CTEAlternativeType.RECURSIVE_CTE)
    second = engine.get_rule(CTEAlternativeType.RECURSIVE_CTE)

    assert first == second


def test_rules_do_not_generate_sql(
    engine: StructuralCTEAlternativeRuleEngine,
) -> None:
    for alternative_type in CTEAlternativeType:
        rule = engine.get_rule(alternative_type)

        assert not hasattr(rule, "alternative_sql")
        assert not hasattr(rule, "optimized_sql")
