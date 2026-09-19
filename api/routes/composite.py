from fastapi import APIRouter, HTTPException

from api.schemas.composite import CompositeIndexResponse
from api.services.composite_service import (
    get_composite_index,
    get_composite_indexes,
)


router = APIRouter(
    prefix="/api/composite-indexes",
    tags=["Composite Indexes"],
)


@router.get("", response_model=list[CompositeIndexResponse])
def list_composite_indexes() -> list[CompositeIndexResponse]:
    return get_composite_indexes()


@router.get(
    "/{recommendation_id}",
    response_model=CompositeIndexResponse,
)
def retrieve_composite_index(
    recommendation_id: int,
) -> CompositeIndexResponse:
    try:
        return get_composite_index(recommendation_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
