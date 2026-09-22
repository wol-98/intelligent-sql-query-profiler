from api.schemas.structural_optimization import (
    ArchitecturalOpportunityStatus,
    ArchitecturalOpportunityType,
    EvidenceStatus,
    OpportunityEvidenceScope,
    StructuralArchitecturalOpportunity,
    ViewRecommendationType,
)
from api.services.architectural_recommendation_evaluator import (
    ArchitecturalRecommendationEvaluator,
)


def make_opportunity(
    opportunity_type: ArchitecturalOpportunityType,
    *,
    status: ArchitecturalOpportunityStatus = (
        ArchitecturalOpportunityStatus.IDENTIFIED
    ),
    evidence_status: EvidenceStatus = EvidenceStatus.COMPLETE,
):
    return StructuralArchitecturalOpportunity(
        finding_index=0,
        opportunity_type=opportunity_type,
        status=status,
        evidence_status=evidence_status,
        evidence_scope=OpportunityEvidenceScope.FINDING,
        rationale="Structural opportunity identified.",
    )


def test_complete_reusable_cte_is_eligible():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(ArchitecturalOpportunityType.REUSABLE_CTE)
    )

    assert result.eligible is True
    assert result.rule.recommendation_type == ViewRecommendationType.VIEW


def test_complete_aggregated_result_is_eligible():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(ArchitecturalOpportunityType.AGGREGATED_RESULT)
    )

    assert result.eligible is True
    assert (
        result.rule.recommendation_type
        == ViewRecommendationType.MATERIALIZED_VIEW
    )


def test_complete_filtered_result_is_eligible():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(
            ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
        )
    )

    assert result.eligible is True
    assert result.rule.recommendation_type == ViewRecommendationType.VIEW


def test_complete_analytical_result_is_eligible():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(ArchitecturalOpportunityType.ANALYTICAL_RESULT)
    )

    assert result.eligible is True
    assert result.rule.recommendation_type == ViewRecommendationType.VIEW


def test_recursive_cte_is_not_eligible():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(ArchitecturalOpportunityType.RECURSIVE_CTE)
    )

    assert result.eligible is False
    assert result.rule.recommendation_type is None


def test_partial_evidence_is_not_eligible():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(
            ArchitecturalOpportunityType.REUSABLE_CTE,
            evidence_status=EvidenceStatus.PARTIAL,
        )
    )

    assert result.eligible is False


def test_insufficient_evidence_is_not_eligible():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(
            ArchitecturalOpportunityType.AGGREGATED_RESULT,
            evidence_status=EvidenceStatus.INSUFFICIENT,
        )
    )

    assert result.eligible is False


def test_not_assessed_opportunity_is_not_eligible():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(
            ArchitecturalOpportunityType.ANALYTICAL_RESULT,
            status=ArchitecturalOpportunityStatus.NOT_ASSESSED,
        )
    )

    assert result.eligible is False


def test_structurally_neutral_opportunity_is_not_eligible():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(
            ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT,
            status=ArchitecturalOpportunityStatus.STRUCTURALLY_NEUTRAL,
        )
    )

    assert result.eligible is False


def test_evaluation_is_deterministic():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.AGGREGATED_RESULT
    )
    evaluator = ArchitecturalRecommendationEvaluator()

    first = evaluator.evaluate(opportunity)
    second = evaluator.evaluate(opportunity)

    assert first == second


def test_evaluation_does_not_change_opportunity():
    opportunity = make_opportunity(
        ArchitecturalOpportunityType.REUSABLE_CTE
    )

    before = opportunity.model_copy(deep=True)

    ArchitecturalRecommendationEvaluator().evaluate(opportunity)

    assert opportunity == before


def test_eligibility_does_not_mean_validation():
    result = ArchitecturalRecommendationEvaluator().evaluate(
        make_opportunity(ArchitecturalOpportunityType.ANALYTICAL_RESULT)
    )

    assert result.eligible is True
    assert result.rule.requires_semantic_validation is True
