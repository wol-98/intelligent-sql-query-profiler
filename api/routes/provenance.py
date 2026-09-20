from fastapi import APIRouter, HTTPException

from api.schemas.provenance import ProvenanceResponse
from api.services.provenance_service import (
    get_provenance_record,
    get_provenance_records,
)


router = APIRouter(
    prefix="/api/provenance",
    tags=["Evidence & Provenance"],
)


@router.get("", response_model=list[ProvenanceResponse])
def list_provenance() -> list[ProvenanceResponse]:
    return get_provenance_records()


@router.get(
    "/{recommendation_id}",
    response_model=ProvenanceResponse,
)
def retrieve_provenance(
    recommendation_id: int,
) -> ProvenanceResponse:
    try:
        return get_provenance_record(recommendation_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
