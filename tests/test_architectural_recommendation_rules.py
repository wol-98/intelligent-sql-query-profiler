from api.schemas.structural_optimization import (
    ArchitecturalOpportunityType,
    EvidenceStatus,
    ViewRecommendationType,
)
from api.services.architectural_recommendation_rules import (
    ArchitecturalRecommendationRuleEngine,
)


def test_reusable_cte_maps_to_view():
    rule = ArchitecturalRecommendationRuleEngine().get_rule(
        ArchitecturalOpportunityType.REUSABLE_CTE
    )

    assert rule.recommendation_type == ViewRecommendationType.VIEW
    assert rule.required_evidence_status == EvidenceStatus.COMPLETE
    assert rule.requires_semantic_validation is True


def test_aggregated_result_maps_to_materialized_view():
    rule = ArchitecturalRecommendationRuleEngine().get_rule(
        ArchitecturalOpportunityType.AGGREGATED_RESULT
    )

    assert (
        rule.recommendation_type
        == ViewRecommendationType.MATERIALIZED_VIEW
    )
    assert rule.required_evidence_status == EvidenceStatus.COMPLETE
    assert rule.requires_semantic_validation is True


def test_filtered_relational_result_maps_to_view():
    rule = ArchitecturalRecommendationRuleEngine().get_rule(
        ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
    )

    assert rule.recommendation_type == ViewRecommendationType.VIEW
    assert rule.required_evidence_status == EvidenceStatus.COMPLETE
    assert rule.requires_semantic_validation is True


def test_analytical_result_maps_to_view():
    rule = ArchitecturalRecommendationRuleEngine().get_rule(
        ArchitecturalOpportunityType.ANALYTICAL_RESULT
    )

    assert rule.recommendation_type == ViewRecommendationType.VIEW
    assert rule.required_evidence_status == EvidenceStatus.COMPLETE
    assert rule.requires_semantic_validation is True


def test_recursive_cte_has_no_automatic_recommendation():
    rule = ArchitecturalRecommendationRuleEngine().get_rule(
        ArchitecturalOpportunityType.RECURSIVE_CTE
    )

    assert rule.recommendation_type is None
    assert rule.required_evidence_status == EvidenceStatus.COMPLETE
    assert rule.requires_semantic_validation is True


def test_rules_are_deterministic():
    engine = ArchitecturalRecommendationRuleEngine()

    first = engine.get_rule(
        ArchitecturalOpportunityType.AGGREGATED_RESULT
    )
    second = engine.get_rule(
        ArchitecturalOpportunityType.AGGREGATED_RESULT
    )

    assert first == second


def test_rule_rationale_is_non_performance_claiming():
    engine = ArchitecturalRecommendationRuleEngine()

    for opportunity_type in ArchitecturalOpportunityType:
        rule = engine.get_rule(opportunity_type)

        assert "benchmark" not in rule.rationale.lower()
        assert "performance improvement" not in rule.rationale.lower()


def test_unknown_opportunity_type_is_rejected():
    engine = ArchitecturalRecommendationRuleEngine()

    try:
        engine.get_rule("UNKNOWN")
    except ValueError as exc:
        assert "No architectural recommendation rule exists" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown opportunity")
