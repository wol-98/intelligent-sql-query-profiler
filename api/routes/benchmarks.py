from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas.benchmark import BenchmarkResponse
from api.services.benchmark_service import (
    get_benchmark,
    get_benchmarks,
)


router = APIRouter(
    prefix="/api/benchmarks",
    tags=["Benchmarks"],
)


@router.get(
    "",
    response_model=list[BenchmarkResponse],
)
def list_benchmarks() -> list[BenchmarkResponse]:
    return get_benchmarks()


@router.get(
    "/{benchmark_id}",
    response_model=BenchmarkResponse,
)
def retrieve_benchmark(
    benchmark_id: int,
) -> BenchmarkResponse:
    try:
        return get_benchmark(benchmark_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
