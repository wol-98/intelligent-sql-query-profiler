from fastapi import APIRouter, HTTPException

from api.schemas.recommendation import (
    RecommendationResponse,
)

from api.services.recommendation_service import (
    get_recommendation,
    get_recommendations,
)

router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"],
)


@router.get(
    "",
    response_model=list[RecommendationResponse],
)
def list_recommendations() -> list[RecommendationResponse]:
    """
    Return all recommendations through the
    read-only M20 reporting API.
    """

    return get_recommendations()


@router.get(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def retrieve_recommendation(
    recommendation_id: int,
) -> RecommendationResponse:
    """
    Return one recommendation by ID.
    """

    try:
        return get_recommendation(
            recommendation_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
