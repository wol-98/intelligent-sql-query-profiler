from api.schemas.structural_optimization import (
    CandidateStatus,
    EvidenceStatus,
    OpportunityEvidenceScope,
    SemanticSafetyStatus,
    StructuralViewRecommendation,
    StructuralViewRecommendationResult,
    ViewRecommendationType,
)
from api.services.structural_view_recommendation_semantic_analyzer import (
    StructuralViewRecommendationSemanticAnalyzer,
)


SQL_VIEW = """
SELECT customer_id, order_count
FROM customer_order_summary
WHERE order_count > 5
"""

SQL_MATERIALIZED_VIEW = """
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
"""


def make_recommendation(
    recommendation_id: str,
    recommendation_type: ViewRecommendationType,
    original_sql: str,
) -> StructuralViewRecommendation:
    return StructuralViewRecommendation(
        recommendation_id=recommendation_id,
        recommendation_type=recommendation_type,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.COMPLETE,
        title=(
            f"{recommendation_type.value} architectural candidate"
        ),
        rationale="Structural architectural candidate.",
        original_sql=original_sql,
    )


def test_view_recommendation_is_analyzed():
    recommendation = make_recommendation(
        "VIEW-REC-0001",
        ViewRecommendationType.VIEW,
        SQL_VIEW,
    )

    result = StructuralViewRecommendationSemanticAnalyzer().analyze(
        recommendation
    )

    assert result.recommendation is recommendation

    assert (
        result.semantic_preconditions.recommendation_type
        == ViewRecommendationType.VIEW
    )

    assert (
        result.semantic_preconditions.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )


def test_materialized_view_recommendation_is_analyzed():
    recommendation = make_recommendation(
        "VIEW-REC-0001",
        ViewRecommendationType.MATERIALIZED_VIEW,
        SQL_MATERIALIZED_VIEW,
    )

    result = StructuralViewRecommendationSemanticAnalyzer().analyze(
        recommendation
    )

    assert result.recommendation is recommendation

    assert (
        result.semantic_preconditions.recommendation_type
        == ViewRecommendationType.MATERIALIZED_VIEW
    )

    assert (
        result.semantic_preconditions.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )


def test_recommendation_candidate_is_not_mutated():
    recommendation = make_recommendation(
        "VIEW-REC-0001",
        ViewRecommendationType.VIEW,
        SQL_VIEW,
    )

    original = recommendation.model_copy(deep=True)

    result = StructuralViewRecommendationSemanticAnalyzer().analyze(
        recommendation
    )

    assert result.recommendation == original

    assert result.recommendation.status == CandidateStatus.CANDIDATE

    assert (
        result.recommendation.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )


def test_original_sql_is_preserved_exactly():
    recommendation = make_recommendation(
        "VIEW-REC-0001",
        ViewRecommendationType.VIEW,
        SQL_VIEW,
    )

    result = StructuralViewRecommendationSemanticAnalyzer().analyze(
        recommendation
    )

    assert result.recommendation.original_sql == SQL_VIEW


def test_multiple_recommendations_preserve_order():
    first = make_recommendation(
        "VIEW-REC-0001",
        ViewRecommendationType.VIEW,
        SQL_VIEW,
    )

    second = make_recommendation(
        "VIEW-REC-0002",
        ViewRecommendationType.MATERIALIZED_VIEW,
        SQL_MATERIALIZED_VIEW,
    )

    third = make_recommendation(
        "VIEW-REC-0003",
        ViewRecommendationType.VIEW,
        SQL_VIEW,
    )

    recommendation_result = StructuralViewRecommendationResult(
        recommendations=[
            first,
            second,
            third,
        ]
    )

    analyzed = (
        StructuralViewRecommendationSemanticAnalyzer()
        .analyze_result(recommendation_result)
    )

    assert [item.recommendation.recommendation_id for item in analyzed] == [
        "VIEW-REC-0001",
        "VIEW-REC-0002",
        "VIEW-REC-0003",
    ]

    assert [
        item.semantic_preconditions.recommendation_type
        for item in analyzed
    ] == [
        ViewRecommendationType.VIEW,
        ViewRecommendationType.MATERIALIZED_VIEW,
        ViewRecommendationType.VIEW,
    ]


def test_empty_recommendation_result_returns_empty_tuple():
    result = StructuralViewRecommendationSemanticAnalyzer().analyze_result(
        StructuralViewRecommendationResult()
    )

    assert result == ()


def test_invalid_sql_does_not_mutate_candidate():
    recommendation = make_recommendation(
        "VIEW-REC-0001",
        ViewRecommendationType.VIEW,
        "SELECT FROM",
    )

    result = StructuralViewRecommendationSemanticAnalyzer().analyze(
        recommendation
    )

    assert (
        result.semantic_preconditions.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )

    assert result.recommendation is recommendation

    assert result.recommendation.status == CandidateStatus.CANDIDATE

    assert (
        result.recommendation.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )


def test_analysis_is_deterministic():
    recommendation = make_recommendation(
        "VIEW-REC-0001",
        ViewRecommendationType.VIEW,
        SQL_VIEW,
    )

    analyzer = StructuralViewRecommendationSemanticAnalyzer()

    first = analyzer.analyze(recommendation)
    second = analyzer.analyze(recommendation)

    assert first == second
