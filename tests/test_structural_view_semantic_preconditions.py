from api.schemas.structural_optimization import (
    SemanticSafetyStatus,
    ViewRecommendationType,
)
from api.services.structural_view_semantic_preconditions import (
    StructuralViewSemanticPreconditionRuleEngine,
    ViewSemanticPreconditionFinding,
    ViewSemanticPreconditionResult,
    ViewSemanticPreconditionRule,
)

from api.services.structural_view_semantic_preconditions import (
    DEFAULT_VIEW_SEMANTIC_PRECONDITION_RULES,
    MATERIALIZED_VIEW_REQUIRED_CONDITIONS,
    VIEW_REQUIRED_CONDITIONS,
)

def test_view_semantic_precondition_finding_contract():
    finding = ViewSemanticPreconditionFinding(
        name="PROJECTED_COLUMNS",
        detected=True,
        rationale="Projected columns must be preserved.",
    )

    assert finding.name == "PROJECTED_COLUMNS"
    assert finding.detected is True
    assert finding.rationale == "Projected columns must be preserved."


def test_materialized_view_semantic_precondition_finding_contract():
    finding = ViewSemanticPreconditionFinding(
        name="REFRESH_BEHAVIOR",
        detected=True,
        rationale="Refresh-related behavior requires validation.",
    )

    assert finding.name == "REFRESH_BEHAVIOR"
    assert finding.detected is True
    assert (
        finding.rationale
        == "Refresh-related behavior requires validation."
    )


def test_semantic_precondition_result_contract():
    finding = ViewSemanticPreconditionFinding(
        name="QUERY_SCOPE",
        detected=True,
        rationale="Query scope must be preserved.",
    )

    result = ViewSemanticPreconditionResult(
        recommendation_type=ViewRecommendationType.VIEW,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        findings=(finding,),
    )

    assert result.recommendation_type == ViewRecommendationType.VIEW
    assert result.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert len(result.findings) == 1
    assert result.findings[0] == finding


def test_semantic_precondition_result_defaults_to_no_findings():
    result = ViewSemanticPreconditionResult(
        recommendation_type=ViewRecommendationType.MATERIALIZED_VIEW,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
    )

    assert result.findings == ()


def test_semantic_precondition_rule_contract():
    rule = ViewSemanticPreconditionRule(
        recommendation_type=ViewRecommendationType.VIEW,
        required_conditions=(
            "PROJECTED_COLUMNS",
            "QUERY_SCOPE",
        ),
        rationale="View semantics must be preserved during validation.",
    )

    assert rule.recommendation_type == ViewRecommendationType.VIEW
    assert rule.required_conditions == (
        "PROJECTED_COLUMNS",
        "QUERY_SCOPE",
    )
    assert (
        rule.rationale
        == "View semantics must be preserved during validation."
    )


def test_rule_engine_resolves_registered_rule():
    rule = ViewSemanticPreconditionRule(
        recommendation_type=ViewRecommendationType.VIEW,
        required_conditions=("PROJECTED_COLUMNS",),
        rationale="Projected columns must be preserved.",
    )

    engine = StructuralViewSemanticPreconditionRuleEngine(
        rules=(rule,)
    )

    resolved = engine.get_rule(ViewRecommendationType.VIEW)

    assert resolved == rule


def test_rule_engine_resolves_materialized_view_rule():
    rule = ViewSemanticPreconditionRule(
        recommendation_type=ViewRecommendationType.MATERIALIZED_VIEW,
        required_conditions=("REFRESH_BEHAVIOR",),
        rationale="Refresh behavior must be validated.",
    )

    engine = StructuralViewSemanticPreconditionRuleEngine(
        rules=(rule,)
    )

    resolved = engine.get_rule(
        ViewRecommendationType.MATERIALIZED_VIEW
    )

    assert resolved == rule


def test_rule_engine_returns_none_for_unregistered_rule():
    engine = StructuralViewSemanticPreconditionRuleEngine()

    assert (
        engine.get_rule(ViewRecommendationType.VIEW)
        is None
    )


def test_rule_engine_rejects_duplicate_rules():
    rule_one = ViewSemanticPreconditionRule(
        recommendation_type=ViewRecommendationType.VIEW,
        required_conditions=("PROJECTED_COLUMNS",),
        rationale="First rule.",
    )

    rule_two = ViewSemanticPreconditionRule(
        recommendation_type=ViewRecommendationType.VIEW,
        required_conditions=("QUERY_SCOPE",),
        rationale="Second rule.",
    )

    try:
        StructuralViewSemanticPreconditionRuleEngine(
            rules=(rule_one, rule_two)
        )
    except ValueError as exc:
        assert str(exc) == (
            "Duplicate semantic-precondition rule for VIEW"
        )
    else:
        raise AssertionError(
            "Expected duplicate semantic-precondition rules "
            "to raise ValueError."
        )

def test_default_view_rule_contains_deterministic_conditions():
    engine = StructuralViewSemanticPreconditionRuleEngine.with_default_rules()

    rule = engine.get_rule(ViewRecommendationType.VIEW)

    assert rule is not None
    assert rule.required_conditions == VIEW_REQUIRED_CONDITIONS


def test_default_materialized_view_rule_contains_deterministic_conditions():
    engine = StructuralViewSemanticPreconditionRuleEngine.with_default_rules()

    rule = engine.get_rule(
        ViewRecommendationType.MATERIALIZED_VIEW
    )

    assert rule is not None
    assert (
        rule.required_conditions
        == MATERIALIZED_VIEW_REQUIRED_CONDITIONS
    )


def test_materialized_view_has_additional_materialization_conditions():
    assert (
        "MATERIALIZATION_BEHAVIOR"
        in MATERIALIZED_VIEW_REQUIRED_CONDITIONS
    )
    assert "REFRESH_BEHAVIOR" in MATERIALIZED_VIEW_REQUIRED_CONDITIONS
    assert (
        "DATA_FRESHNESS_REQUIREMENTS"
        in MATERIALIZED_VIEW_REQUIRED_CONDITIONS
    )


def test_view_rule_does_not_require_materialized_view_conditions():
    assert (
        "MATERIALIZATION_BEHAVIOR"
        not in VIEW_REQUIRED_CONDITIONS
    )
    assert "REFRESH_BEHAVIOR" not in VIEW_REQUIRED_CONDITIONS
    assert (
        "DATA_FRESHNESS_REQUIREMENTS"
        not in VIEW_REQUIRED_CONDITIONS
    )


def test_default_rules_are_registered_for_both_recommendation_types():
    assert len(DEFAULT_VIEW_SEMANTIC_PRECONDITION_RULES) == 2

    recommendation_types = {
        rule.recommendation_type
        for rule in DEFAULT_VIEW_SEMANTIC_PRECONDITION_RULES
    }

    assert recommendation_types == {
        ViewRecommendationType.VIEW,
        ViewRecommendationType.MATERIALIZED_VIEW,
    }


def test_default_rules_are_deterministic():
    first = StructuralViewSemanticPreconditionRuleEngine.with_default_rules()
    second = StructuralViewSemanticPreconditionRuleEngine.with_default_rules()

    first_view = first.get_rule(ViewRecommendationType.VIEW)
    second_view = second.get_rule(ViewRecommendationType.VIEW)

    first_mv = first.get_rule(
        ViewRecommendationType.MATERIALIZED_VIEW
    )
    second_mv = second.get_rule(
        ViewRecommendationType.MATERIALIZED_VIEW
    )

    assert first_view == second_view
    assert first_mv == second_mv
