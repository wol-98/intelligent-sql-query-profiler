from fastapi import APIRouter, HTTPException

from api.schemas.cost_benefit import CostBenefitResponse
from api.services.cost_benefit_service import (
    get_cost_benefit,
    get_cost_benefits,
)


router = APIRouter(
    prefix="/api/cost-benefit",
    tags=["Cost & Benefit"],
)


@router.get(
    "",
    response_model=list[CostBenefitResponse],
)
def list_cost_benefits() -> list[CostBenefitResponse]:
    """
    Return all available cost-benefit evidence
    through the read-only M20 reporting API.
    """

    return get_cost_benefits()


@router.get(
    "/{experiment_id}",
    response_model=CostBenefitResponse,
)
def retrieve_cost_benefit(
    experiment_id: str,
) -> CostBenefitResponse:
    """
    Return cost-benefit evidence for one experiment.
    """

    try:
        return get_cost_benefit(experiment_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
