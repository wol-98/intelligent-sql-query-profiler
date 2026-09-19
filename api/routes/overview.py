from fastapi import APIRouter

from api.schemas.overview import OverviewResponse
from api.services.overview_service import build_overview

router = APIRouter(
    prefix="/api/overview",
    tags=["Overview"],
)


@router.get("", response_model=OverviewResponse)
def get_overview() -> OverviewResponse:
    """Return the read-only dashboard overview."""
    return build_overview()
