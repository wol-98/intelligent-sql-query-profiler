from fastapi import APIRouter

from api.schemas.workload import WorkloadResponse
from api.services.workload_service import get_workloads


router = APIRouter(
    prefix="/api/workloads",
    tags=["Workloads"],
)


@router.get("", response_model=list[WorkloadResponse])
def list_workloads() -> list[WorkloadResponse]:
    return get_workloads()
