"""Tests for M21.7.3 structural alternative rules."""

import sqlglot
from sqlglot import exp

import pytest

from api.schemas.structural_optimization import (
    StructuralLayer,
    SubqueryAlternativeType,
)
from api.services.structural_alternative_rules import (
    StructuralAlternativeRule,
    StructuralAlternativeRuleEngine,
)


@pytest.fixture
def engine() -> StructuralAlternativeRuleEngine:
    return StructuralAlternativeRuleEngine()


@pytest.mark.parametrize(
    "alternative_type,expected_family,expected_layer",
    [
        (
            SubqueryAlternativeType.EXISTS,
            "EXISTS_TO_SUBQUERY_ALTERNATIVE",
            StructuralLayer.SUBQUERY,
        ),
        (
            SubqueryAlternativeType.IN,
            "IN_TO_EXISTS",
            StructuralLayer.SUBQUERY,
        ),
        (
            SubqueryAlternativeType.ANY,
            "ANY_TO_OPERATOR_SPECIFIC_ALTERNATIVE",
            StructuralLayer.SUBQUERY,
        ),
        (
            SubqueryAlternativeType.DERIVED_TABLE,
            "DERIVED_TABLE_TO_STRUCTURAL_ALTERNATIVE",
            StructuralLayer.FROM,
        ),
    ],
)
def test_all_supported_types_have_deterministic_rules(
    engine: StructuralAlternativeRuleEngine,
    alternative_type: SubqueryAlternativeType,
    expected_family: str,
    expected_layer: StructuralLayer,
) -> None:
    rule = engine.get_rule(alternative_type)

    assert isinstance(rule, StructuralAlternativeRule)
    assert rule.source_type == alternative_type
    assert rule.alternative_family == expected_family
    assert rule.source_layer == expected_layer
    assert rule.requires_semantic_validation is True


@pytest.mark.parametrize(
    "sql,expected_type",
    [
        (
            """
            SELECT customer_id
            FROM customers
            WHERE EXISTS (
                SELECT 1
                FROM orders
                WHERE orders.customer_id = customers.customer_id
            )
            """,
            SubqueryAlternativeType.EXISTS,
        ),
        (
            """
            SELECT customer_id
            FROM customers
            WHERE customer_id IN (
                SELECT customer_id
                FROM orders
            )
            """,
            SubqueryAlternativeType.IN,
        ),
        (
            """
            SELECT customer_id
            FROM customers
            WHERE customer_id = ANY (
                SELECT customer_id
                FROM orders
            )
            """,
            SubqueryAlternativeType.ANY,
        ),
        (
            """
            SELECT x.customer_id
            FROM (
                SELECT customer_id
                FROM orders
            ) x
            """,
            SubqueryAlternativeType.DERIVED_TABLE,
        ),
    ],
)
def test_rule_can_be_resolved_from_actual_sqlglot_node(
    engine: StructuralAlternativeRuleEngine,
    sql: str,
    expected_type: SubqueryAlternativeType,
) -> None:
    tree = sqlglot.parse_one(sql, dialect="postgres")

    matching_nodes = []

    for node in tree.walk():
        rule = engine.get_rule_for_node(node)

        if rule is not None:
            matching_nodes.append(rule)

    assert len(matching_nodes) == 1
    assert matching_nodes[0].source_type == expected_type


def test_in_subquery_is_not_a_derived_table(
    engine: StructuralAlternativeRuleEngine,
) -> None:
    sql = """
        SELECT *
        FROM orders
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
        )
    """

    tree = sqlglot.parse_one(sql, dialect="postgres")

    rules = [
        engine.get_rule_for_node(node)
        for node in tree.walk()
    ]

    rules = [rule for rule in rules if rule is not None]

    assert [rule.source_type for rule in rules] == [
        SubqueryAlternativeType.IN
    ]


def test_derived_table_is_classified_from_from_parent(
    engine: StructuralAlternativeRuleEngine,
) -> None:
    sql = """
        SELECT x.customer_id
        FROM (
            SELECT customer_id
            FROM orders
        ) x
    """

    tree = sqlglot.parse_one(sql, dialect="postgres")

    rules = [
        engine.get_rule_for_node(node)
        for node in tree.walk()
    ]

    rules = [rule for rule in rules if rule is not None]

    assert [rule.source_type for rule in rules] == [
        SubqueryAlternativeType.DERIVED_TABLE
    ]
    assert rules[0].source_layer == StructuralLayer.FROM


def test_any_rule_is_operator_sensitive(
    engine: StructuralAlternativeRuleEngine,
) -> None:
    sql = """
        SELECT customer_id
        FROM customers
        WHERE customer_id > ANY (
            SELECT customer_id
            FROM orders
        )
    """

    tree = sqlglot.parse_one(sql, dialect="postgres")

    rules = [
        engine.get_rule_for_node(node)
        for node in tree.walk()
    ]

    rules = [rule for rule in rules if rule is not None]

    assert len(rules) == 1
    assert (
        rules[0].alternative_family
        == "ANY_TO_OPERATOR_SPECIFIC_ALTERNATIVE"
    )
    assert "comparison operator" in rules[0].safety_constraints[0]


@pytest.mark.parametrize(
    "alternative_type",
    list(SubqueryAlternativeType),
)
def test_every_rule_requires_semantic_validation(
    engine: StructuralAlternativeRuleEngine,
    alternative_type: SubqueryAlternativeType,
) -> None:
    rule = engine.get_rule(alternative_type)

    assert rule.requires_semantic_validation is True
    assert len(rule.safety_constraints) > 0


def test_exists_rule_contains_correlation_constraint(
    engine: StructuralAlternativeRuleEngine,
) -> None:
    rule = engine.get_rule(SubqueryAlternativeType.EXISTS)

    assert any(
        "correlated-reference" in constraint
        for constraint in rule.safety_constraints
    )


def test_in_rule_contains_null_and_membership_constraints(
    engine: StructuralAlternativeRuleEngine,
) -> None:
    rule = engine.get_rule(SubqueryAlternativeType.IN)

    assert any(
        "NULL-sensitive" in constraint
        for constraint in rule.safety_constraints
    )
    assert any(
        "membership" in constraint
        for constraint in rule.safety_constraints
    )


def test_derived_table_rule_contains_projection_and_scope_constraints(
    engine: StructuralAlternativeRuleEngine,
) -> None:
    rule = engine.get_rule(SubqueryAlternativeType.DERIVED_TABLE)

    assert any(
        "projected columns" in constraint
        for constraint in rule.safety_constraints
    )
    assert any(
        "query-scope" in constraint
        for constraint in rule.safety_constraints
    )


def test_rule_lookup_is_deterministic(
    engine: StructuralAlternativeRuleEngine,
) -> None:
    first = engine.get_rule(SubqueryAlternativeType.IN)
    second = engine.get_rule(SubqueryAlternativeType.IN)

    assert first == second


def test_unsupported_ast_node_returns_no_rule(
    engine: StructuralAlternativeRuleEngine,
) -> None:
    node = exp.Select(
        expressions=[
            exp.Literal.number(1),
        ]
    )

    assert engine.get_rule_for_node(node) is None


def test_rules_do_not_generate_sql(
    engine: StructuralAlternativeRuleEngine,
) -> None:
    for alternative_type in SubqueryAlternativeType:
        rule = engine.get_rule(alternative_type)

        assert not hasattr(rule, "alternative_sql")
        assert not hasattr(rule, "optimized_sql")
