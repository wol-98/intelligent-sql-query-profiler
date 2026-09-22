import sqlglot
from sqlglot import exp

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
def test_rule_can_be_resolved_from_actual_cte_ast_node(
    engine: StructuralCTEAlternativeRuleEngine,
) -> None:
    import sqlglot

    sql = """
        WITH recent_orders AS (
            SELECT *
            FROM orders
        )
        SELECT *
        FROM recent_orders
    """

    tree = sqlglot.parse_one(sql, dialect="postgres")

    matching_rules = []

    for node in tree.walk():
        rule = engine.get_rule_for_node(node)

        if rule is not None:
            matching_rules.append(rule)

    assert len(matching_rules) == 1
    assert (
        matching_rules[0].source_type
        == CTEAlternativeType.CTE
    )
    assert (
        matching_rules[0].source_layer
        == StructuralLayer.CTE
    )


def test_recursive_cte_rule_can_be_resolved_from_actual_ast_node(
    engine: StructuralCTEAlternativeRuleEngine,
) -> None:
    import sqlglot

    sql = """
        WITH RECURSIVE tree AS (
            SELECT id
            FROM nodes
            WHERE parent_id IS NULL

            UNION ALL

            SELECT n.id
            FROM nodes n
            JOIN tree t
                ON n.parent_id = t.id
        )
        SELECT *
        FROM tree
    """

    tree = sqlglot.parse_one(sql, dialect="postgres")

    matching_rules = []

    for node in tree.walk():
        rule = engine.get_rule_for_node(node)

        if rule is not None:
            matching_rules.append(rule)

    assert len(matching_rules) == 1
    assert (
        matching_rules[0].source_type
        == CTEAlternativeType.RECURSIVE_CTE
    )
    assert (
        matching_rules[0].source_layer
        == StructuralLayer.CTE
    )


def test_cte_reference_table_is_not_classified_as_cte_candidate(
    engine: StructuralCTEAlternativeRuleEngine,
) -> None:
    import sqlglot

    sql = """
        WITH recent_orders AS (
            SELECT *
            FROM orders
        )
        SELECT *
        FROM recent_orders
    """

    tree = sqlglot.parse_one(sql, dialect="postgres")

    table_rules = []

    for node in tree.find_all(exp.Table):
        rule = engine.get_rule_for_node(node)

        if rule is not None:
            table_rules.append(rule)

    assert table_rules == []


def test_non_cte_ast_node_returns_no_rule(
    engine: StructuralCTEAlternativeRuleEngine,
) -> None:
    import sqlglot

    tree = sqlglot.parse_one(
        "SELECT * FROM orders",
        dialect="postgres",
    )

    for node in tree.walk():
        if isinstance(node, exp.Select):
            assert engine.get_rule_for_node(node) is None
            break
