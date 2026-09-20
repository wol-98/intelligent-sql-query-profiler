from __future__ import annotations

from api.schemas.benchmark import BenchmarkResponse
from api.services.benchmark_repository import (
    fetch_benchmark_records,
)


def _calculate_savings(
    baseline_time_ms: float | None,
    indexed_time_ms: float | None,
) -> float | None:
    """
    Calculate absolute execution-time savings only when both
    stored execution measurements are available.

    This is descriptive reporting, not a production decision.
    """

    if baseline_time_ms is None or indexed_time_ms is None:
        return None

    return baseline_time_ms - indexed_time_ms


def _normalize_outcome(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.upper()

    status_map = {
        "SUCCESSFUL": "SUCCESS",
        "SUCCESS": "SUCCESS",
        "NEUTRAL": "NEUTRAL",
        "UNSUCCESSFUL": "UNSUCCESSFUL",
        "UNSAFE": "UNSAFE",
    }

    return status_map.get(normalized)

def _build_benchmark_response(
    record: dict,
) -> BenchmarkResponse:
    baseline_time_ms = record.get(
        "execution_time_before_ms"
    )

    indexed_time_ms = record.get(
        "execution_time_after_ms"
    )

    return BenchmarkResponse(
        benchmark_id=record.get("benchmark_id"),
        recommendation_id=record.get("recommendation_id"),
        experiment_id=None,

        baseline_time_ms=baseline_time_ms,
        indexed_time_ms=indexed_time_ms,
        improvement_percent=record.get(
            "improvement_percentage"
        ),
        median_improvement_percent=record.get(
            "median_improvement_percentage"
        ),
        savings_ms=_calculate_savings(
            baseline_time_ms,
            indexed_time_ms,
        ),

        rows_preserved=record.get("rows_preserved"),
        index_used=record.get("index_used"),
        plan_changed=record.get("plan_changed"),

        outcome=_normalize_outcome(
            record.get("validation_status")
        ),
        scope="STORED_BENCHMARK",
    )


def get_benchmarks() -> list[BenchmarkResponse]:
    records = fetch_benchmark_records()

    return [
        _build_benchmark_response(record)
        for record in records
    ]


def get_benchmark(
    benchmark_id: int,
) -> BenchmarkResponse:
    records = fetch_benchmark_records(
        benchmark_id=benchmark_id
    )

    if not records:
        raise ValueError(
            f"Benchmark {benchmark_id} not found."
        )

    return _build_benchmark_response(records[0])
