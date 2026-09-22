from api.schemas.structural_optimization import (
    CandidateStatus,
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralLayer,
    StructuralViewRecommendation,
    StructuralViewRecommendationResult,
    ViewRecommendationType,
)


def make_recommendation(
    recommendation_type: ViewRecommendationType,
    *,
    source_layer: StructuralLayer | None = None,
    evidence_status: EvidenceStatus = EvidenceStatus.COMPLETE,
):
    return StructuralViewRecommendation(
        recommendation_id="VIEW-REC-0001",
        recommendation_type=recommendation_type,
        evidence_status=evidence_status,
        title="Architectural view recommendation",
        rationale="Eligible for later architectural validation.",
        source_layer=source_layer,
        original_sql="SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id",
    )


def test_view_recommendation_contract():
    recommendation = make_recommendation(ViewRecommendationType.VIEW)

    assert recommendation.recommendation_type == ViewRecommendationType.VIEW
    assert recommendation.status == CandidateStatus.CANDIDATE
    assert recommendation.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert recommendation.evidence_status == EvidenceStatus.COMPLETE
    assert recommendation.original_sql == (
        "SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id"
    )


def test_materialized_view_recommendation_contract():
    recommendation = make_recommendation(
        ViewRecommendationType.MATERIALIZED_VIEW
    )

    assert (
        recommendation.recommendation_type
        == ViewRecommendationType.MATERIALIZED_VIEW
    )
    assert recommendation.status == CandidateStatus.CANDIDATE
    assert recommendation.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED


def test_recommendation_status_can_be_explicitly_validated():
    recommendation = StructuralViewRecommendation(
        recommendation_id="VIEW-REC-0002",
        recommendation_type=ViewRecommendationType.VIEW,
        status=CandidateStatus.VALIDATED,
        evidence_status=EvidenceStatus.COMPLETE,
        title="Validated view recommendation",
        rationale="Validated by a later stage.",
        original_sql="SELECT * FROM customers",
    )

    assert recommendation.status == CandidateStatus.VALIDATED


def test_semantic_safety_can_require_validation():
    recommendation = StructuralViewRecommendation(
        recommendation_id="VIEW-REC-0003",
        recommendation_type=ViewRecommendationType.MATERIALIZED_VIEW,
        semantic_safety=SemanticSafetyStatus.REQUIRES_VALIDATION,
        evidence_status=EvidenceStatus.PARTIAL,
        title="Materialized-view candidate",
        rationale="Requires architectural validation.",
        original_sql="SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id",
    )

    assert recommendation.semantic_safety == SemanticSafetyStatus.REQUIRES_VALIDATION
    assert recommendation.evidence_status == EvidenceStatus.PARTIAL


def test_source_layer_is_optional():
    recommendation = make_recommendation(ViewRecommendationType.VIEW)

    assert recommendation.source_layer is None


def test_source_layer_is_preserved():
    recommendation = make_recommendation(
        ViewRecommendationType.VIEW,
        source_layer=StructuralLayer.GROUP_BY,
    )

    assert recommendation.source_layer == StructuralLayer.GROUP_BY


def test_original_sql_is_preserved_exactly():
    sql = """
SELECT
    customer_id,
    COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
ORDER BY order_count DESC
"""

    recommendation = StructuralViewRecommendation(
        recommendation_id="VIEW-REC-0004",
        recommendation_type=ViewRecommendationType.VIEW,
        evidence_status=EvidenceStatus.COMPLETE,
        title="View candidate",
        rationale="Eligible for later architectural validation.",
        original_sql=sql,
    )

    assert recommendation.original_sql == sql


def test_empty_recommendation_result_is_valid():
    result = StructuralViewRecommendationResult()

    assert result.recommendations == []


def test_recommendation_result_preserves_recommendations():
    first = make_recommendation(ViewRecommendationType.VIEW)
    second = make_recommendation(ViewRecommendationType.MATERIALIZED_VIEW)

    result = StructuralViewRecommendationResult(
        recommendations=[first, second]
    )

    assert len(result.recommendations) == 2
    assert result.recommendations[0].recommendation_type == (
        ViewRecommendationType.VIEW
    )
    assert result.recommendations[1].recommendation_type == (
        ViewRecommendationType.MATERIALIZED_VIEW
    )
