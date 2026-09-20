from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas.query import QueryResponse
from api.services.query_service import (
    get_queries,
    get_query,
)


router = APIRouter(
    prefix="/api/queries",
    tags=["Queries"],
)


@router.get(
    "",
    response_model=list[QueryResponse],
)
def list_queries() -> list[QueryResponse]:
    """
    Return all profiled SQL queries.
    """

    return get_queries()


@router.get(
    "/{fingerprint}",
    response_model=QueryResponse,
)
def retrieve_query(
    fingerprint: str,
) -> QueryResponse:
    """
    Return one profiled SQL query by fingerprint.
    """

    try:
        return get_query(fingerprint)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
