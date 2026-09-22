from api.schemas.structural_optimization import (
    ArchitecturalOpportunityStatus,
    ArchitecturalOpportunityType,
    CandidateStatus,
    EvidenceStatus,
    OpportunityEvidenceScope,
    SemanticSafetyStatus,
    StructuralArchitecturalOpportunity,
    StructuralArchitecturalOpportunityResult,
    StructuralLayer,
    ViewRecommendationType,
)
from api.services.structural_view_recommendation_generator import (
    StructuralViewRecommendationGenerator,
)


SQL = "SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id"


def make_opportunity(
    opportunity_type: ArchitecturalOpportunityType,
    *,
    finding_index: int = 0,
    status: ArchitecturalOpportunityStatus = (
        ArchitecturalOpportunityStatus.IDENTIFIED
    ),
    evidence_status: EvidenceStatus = EvidenceStatus.COMPLETE,
):
    return StructuralArchitecturalOpportunity(
        finding_index=finding_index,
        opportunity_type=opportunity_type,
        status=status,
        evidence_status=evidence_status,
        evidence_scope=OpportunityEvidenceScope.FINDING,
        rationale="Structural opportunity identified.",
    )


def make_result(*opportunities):
    return StructuralArchitecturalOpportunityResult(
        opportunities=list(opportunities)
    )


def test_reusable_cte_generates_view_candidate():
    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.REUSABLE_CTE,
                finding_index=2,
            )
        ),
        original_sql=SQL,
        source_layers={2: StructuralLayer.CTE},
    )

    assert len(result.recommendations) == 1

    recommendation = result.recommendations[0]

    assert recommendation.recommendation_id == "VIEW-REC-0001"
    assert recommendation.recommendation_type == ViewRecommendationType.VIEW
    assert recommendation.status == CandidateStatus.CANDIDATE
    assert (
        recommendation.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert recommendation.evidence_status == EvidenceStatus.COMPLETE
    assert recommendation.source_layer == StructuralLayer.CTE
    assert recommendation.original_sql == SQL


def test_aggregated_result_generates_materialized_view_candidate():
    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.AGGREGATED_RESULT
            )
        ),
        original_sql=SQL,
        source_layers={0: StructuralLayer.GROUP_BY},
    )

    recommendation = result.recommendations[0]

    assert (
        recommendation.recommendation_type
        == ViewRecommendationType.MATERIALIZED_VIEW
    )


def test_filtered_result_generates_view_candidate():
    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
            )
        ),
        original_sql=SQL,
    )

    assert (
        result.recommendations[0].recommendation_type
        == ViewRecommendationType.VIEW
    )


def test_analytical_result_generates_view_candidate():
    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.ANALYTICAL_RESULT
            )
        ),
        original_sql=SQL,
    )

    assert (
        result.recommendations[0].recommendation_type
        == ViewRecommendationType.VIEW
    )


def test_recursive_cte_generates_no_recommendation():
    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.RECURSIVE_CTE
            )
        ),
        original_sql=SQL,
    )

    assert result.recommendations == []


def test_partial_evidence_generates_no_recommendation():
    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.REUSABLE_CTE,
                evidence_status=EvidenceStatus.PARTIAL,
            )
        ),
        original_sql=SQL,
    )

    assert result.recommendations == []


def test_not_assessed_opportunity_generates_no_recommendation():
    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.ANALYTICAL_RESULT,
                status=ArchitecturalOpportunityStatus.NOT_ASSESSED,
            )
        ),
        original_sql=SQL,
    )

    assert result.recommendations == []


def test_recommendation_ids_are_deterministic():
    opportunities = make_result(
        make_opportunity(
            ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT,
            finding_index=1,
        ),
        make_opportunity(
            ArchitecturalOpportunityType.AGGREGATED_RESULT,
            finding_index=2,
        ),
    )

    first = StructuralViewRecommendationGenerator().generate(
        opportunities,
        original_sql=SQL,
    )
    second = StructuralViewRecommendationGenerator().generate(
        opportunities,
        original_sql=SQL,
    )

    assert [
        item.recommendation_id for item in first.recommendations
    ] == [
        item.recommendation_id for item in second.recommendations
    ]


def test_original_sql_is_preserved_exactly():
    sql = """
SELECT
    customer_id,
    COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
"""

    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.AGGREGATED_RESULT
            )
        ),
        original_sql=sql,
    )

    assert result.recommendations[0].original_sql == sql


def test_generation_does_not_validate_candidate():
    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.AGGREGATED_RESULT
            )
        ),
        original_sql=SQL,
    )

    recommendation = result.recommendations[0]

    assert recommendation.status == CandidateStatus.CANDIDATE
    assert (
        recommendation.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )


def test_multiple_eligible_opportunities_preserve_order():
    result = StructuralViewRecommendationGenerator().generate(
        make_result(
            make_opportunity(
                ArchitecturalOpportunityType.REUSABLE_CTE,
                finding_index=1,
            ),
            make_opportunity(
                ArchitecturalOpportunityType.AGGREGATED_RESULT,
                finding_index=2,
            ),
            make_opportunity(
                ArchitecturalOpportunityType.ANALYTICAL_RESULT,
                finding_index=3,
            ),
        ),
        original_sql=SQL,
    )

    assert len(result.recommendations) == 3

    assert [
        item.recommendation_type
        for item in result.recommendations
    ] == [
        ViewRecommendationType.VIEW,
        ViewRecommendationType.MATERIALIZED_VIEW,
        ViewRecommendationType.VIEW,
    ]
