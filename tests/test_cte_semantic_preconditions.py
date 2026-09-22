import pytest

from api.schemas.structural_optimization import (
    CTEAlternativeType,
    SemanticSafetyStatus,
)
from api.services.structural_cte_semantic_preconditions import (
    CTESemanticPreconditionFinding,
    CTESemanticPreconditionResult,
    StructuralCTESemanticPreconditionAnalyzer,
    StructuralCTESemanticPreconditionRuleEngine,
)


def test_cte_semantic_precondition_finding_is_immutable() -> None:
    finding = CTESemanticPreconditionFinding(
        name="CTE_DEFINITION",
        detected=True,
        rationale="A CTE definition was identified.",
    )

    assert finding.name == "CTE_DEFINITION"
    assert finding.detected is True

    with pytest.raises(Exception):
        finding.name = "OTHER"


@pytest.mark.parametrize(
    "alternative_type",
    [
        CTEAlternativeType.CTE,
        CTEAlternativeType.RECURSIVE_CTE,
    ],
)
def test_cte_semantic_precondition_result_contract(
    alternative_type: CTEAlternativeType,
) -> None:
    result = CTESemanticPreconditionResult(
        alternative_type=alternative_type,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
    )

    assert result.alternative_type == alternative_type
    assert (
        result.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert result.findings == ()


def test_ordinary_cte_preconditions_are_detected() -> None:
    sql = """
        WITH recent_orders AS (
            SELECT customer_id, order_date
            FROM orders
            WHERE order_date >= DATE '2026-01-01'
        )
        SELECT *
        FROM recent_orders
    """

    result = StructuralCTESemanticPreconditionAnalyzer().analyze(
        sql,
        CTEAlternativeType.CTE,
    )

    assert result.alternative_type == CTEAlternativeType.CTE
    assert (
        result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    findings = {
        finding.name: finding
        for finding in result.findings
    }

    assert findings["CTE_DEFINITION"].detected is True
    assert findings["CTE_REFERENCES"].detected is True
    assert findings["CTE_OUTPUT_COLUMNS"].detected is True
    assert findings["QUERY_SCOPE"].detected is True
    assert findings["MATERIALIZATION_BEHAVIOR"].detected is False


def test_ordinary_cte_aliases_are_detected() -> None:
    sql = """
        WITH recent_orders(customer, order_day) AS (
            SELECT customer_id, order_date
            FROM orders
        )
        SELECT *
        FROM recent_orders
    """

    result = StructuralCTESemanticPreconditionAnalyzer().analyze(
        sql,
        CTEAlternativeType.CTE,
    )

    findings = {
        finding.name: finding
        for finding in result.findings
    }

    assert findings["CTE_ALIASES"].detected is True


def test_explicit_materialization_is_detected() -> None:
    sql = """
        WITH recent_orders AS MATERIALIZED (
            SELECT customer_id
            FROM orders
        )
        SELECT *
        FROM recent_orders
    """

    result = StructuralCTESemanticPreconditionAnalyzer().analyze(
        sql,
        CTEAlternativeType.CTE,
    )

    findings = {
        finding.name: finding
        for finding in result.findings
    }

    assert findings["MATERIALIZATION_BEHAVIOR"].detected is True


def test_recursive_cte_preconditions_are_detected() -> None:
    sql = """
        WITH RECURSIVE tree AS (
            SELECT id, parent_id
            FROM nodes
            WHERE parent_id IS NULL

            UNION ALL

            SELECT n.id, n.parent_id
            FROM nodes n
            JOIN tree t
                ON n.parent_id = t.id
            WHERE n.id < 100
        )
        SELECT *
        FROM tree
    """

    result = StructuralCTESemanticPreconditionAnalyzer().analyze(
        sql,
        CTEAlternativeType.RECURSIVE_CTE,
    )

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )

    findings = {
        finding.name: finding
        for finding in result.findings
    }

    assert findings["CTE_DEFINITION"].detected is True
    assert findings["RECURSIVE_CTE"].detected is True
    assert findings["RECURSIVE_ANCHOR"].detected is True
    assert findings["RECURSIVE_MEMBER"].detected is True
    assert findings["RECURSIVE_SET_OPERATION"].detected is True
    assert findings["RECURSIVE_REFERENCES"].detected is True
    assert findings["RECURSIVE_TERMINATION"].detected is True
    assert findings["CTE_OUTPUT_COLUMNS"].detected is True
    assert findings["QUERY_SCOPE"].detected is True


def test_non_recursive_query_is_not_assessed_as_recursive_cte() -> None:
    sql = """
        WITH recent_orders AS (
            SELECT customer_id
            FROM orders
        )
        SELECT *
        FROM recent_orders
    """

    result = StructuralCTESemanticPreconditionAnalyzer().analyze(
        sql,
        CTEAlternativeType.RECURSIVE_CTE,
    )

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert result.findings == ()


def test_missing_cte_is_not_assessed() -> None:
    sql = """
        SELECT customer_id
        FROM customers
    """

    result = StructuralCTESemanticPreconditionAnalyzer().analyze(
        sql,
        CTEAlternativeType.CTE,
    )

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert result.findings == ()


def test_recursive_cte_requires_all_recursive_conditions() -> None:
    engine = StructuralCTESemanticPreconditionRuleEngine()

    rule = engine.get_rule(
        CTEAlternativeType.RECURSIVE_CTE,
    )

    expected = {
        "CTE_DEFINITION",
        "RECURSIVE_CTE",
        "RECURSIVE_ANCHOR",
        "RECURSIVE_MEMBER",
        "RECURSIVE_SET_OPERATION",
        "RECURSIVE_REFERENCES",
        "RECURSIVE_TERMINATION",
        "CTE_OUTPUT_COLUMNS",
        "CTE_ALIASES",
        "QUERY_SCOPE",
        "MATERIALIZATION_BEHAVIOR",
    }

    assert set(rule.required_conditions) == expected


def test_precondition_analysis_does_not_declare_cte_safe() -> None:
    sql = """
        WITH recent_orders AS (
            SELECT customer_id
            FROM orders
        )
        SELECT *
        FROM recent_orders
    """

    result = StructuralCTESemanticPreconditionAnalyzer().analyze(
        sql,
        CTEAlternativeType.CTE,
    )

    assert (
        result.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )
    assert (
        result.semantic_safety
        != SemanticSafetyStatus.NOT_ASSESSED
    )
