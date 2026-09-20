from fastapi import APIRouter, HTTPException

from api.schemas.decision import ProductionDecisionResponse
from api.services.decision_service import (
    get_production_decision,
    get_production_decisions,
)


router = APIRouter(
    prefix="/api/decisions",
    tags=["Production Decisions"],
)


@router.get(
    "",
    response_model=list[ProductionDecisionResponse],
)
def list_production_decisions() -> list[
    ProductionDecisionResponse
]:
    return get_production_decisions()


@router.get(
    "/{recommendation_id}",
    response_model=ProductionDecisionResponse,
)
def retrieve_production_decision(
    recommendation_id: int,
) -> ProductionDecisionResponse:
    try:
        return get_production_decision(
            recommendation_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
