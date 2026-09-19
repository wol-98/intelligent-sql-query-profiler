"""
M17.2 — Index Maintenance Experiment

Measures the write-side execution overhead associated with an index.

This module is experimental only.

It does NOT:
- modify recommendation scores
- modify candidate generation
- modify recommendation priorities
- use benchmark_results
- create permanent production indexes

The experiment compares the same write workload with:
1. No secondary index
2. An experimental secondary index
"""

from __future__ import annotations

from statistics import mean, median, stdev
from typing import Any, Callable


MIN_ROWS = 10
DEFAULT_ROWS = 1000
DEFAULT_ITERATIONS = 5


def validate_maintenance_result(result: dict[str, Any]) -> None:
    """Validate the structure of a maintenance experiment result."""

    required_keys = {
        "table_name",
        "indexed_columns",
        "row_count",
        "iterations",
        "baseline_times_ms",
        "indexed_times_ms",
        "baseline_average_ms",
        "indexed_average_ms",
        "maintenance_overhead_ms",
        "maintenance_overhead_percent",
        "baseline_median_ms",
        "indexed_median_ms",
        "median_overhead_ms",
        "median_overhead_percent",
        "baseline_stddev_ms",
        "indexed_stddev_ms",
        "baseline_min_ms",
        "baseline_max_ms",
        "indexed_min_ms",
        "indexed_max_ms",
    }

    missing = required_keys - result.keys()

    if missing:
        raise ValueError(
            f"Maintenance experiment result is missing keys: {sorted(missing)}"
        )

    if result["row_count"] < MIN_ROWS:
        raise ValueError("row_count is too small for a meaningful experiment")

    if result["iterations"] < 1:
        raise ValueError("iterations must be at least 1")


def calculate_average(values: list[float]) -> float:
    """Calculate the arithmetic mean."""

    if not values:
        raise ValueError("Cannot calculate average of an empty list")

    return mean(values)


def calculate_median(values: list[float]) -> float:
    """Calculate the median."""

    if not values:
        raise ValueError("Cannot calculate median of an empty list")

    return median(values)


def calculate_standard_deviation(values: list[float]) -> float:
    """Calculate sample standard deviation."""

    if len(values) < 2:
        return 0.0

    return stdev(values)


def calculate_maintenance_overhead(
    baseline_value_ms: float,
    indexed_value_ms: float,
) -> tuple[float, float]:
    """
    Calculate absolute and percentage maintenance overhead.

    Returns:
        (overhead_ms, overhead_percent)
    """

    if baseline_value_ms <= 0:
        raise ValueError("baseline value must be greater than zero")

    overhead_ms = indexed_value_ms - baseline_value_ms

    overhead_percent = (
        overhead_ms / baseline_value_ms
    ) * 100.0

    return overhead_ms, overhead_percent


def build_maintenance_result(
    table_name: str,
    indexed_columns: list[str],
    row_count: int,
    iterations: int,
    baseline_times_ms: list[float],
    indexed_times_ms: list[float],
) -> dict[str, Any]:
    """
    Build a normalized maintenance experiment result.

    Both mean and median measurements are retained so that
    timing outliers remain visible rather than being discarded.
    """

    if not baseline_times_ms:
        raise ValueError("baseline_times_ms cannot be empty")

    if not indexed_times_ms:
        raise ValueError("indexed_times_ms cannot be empty")

    if len(baseline_times_ms) != len(indexed_times_ms):
        raise ValueError(
            "Baseline and indexed observations must have equal length"
        )

    if iterations != len(baseline_times_ms):
        raise ValueError(
            "iterations must match the number of timing observations"
        )

    baseline_average_ms = calculate_average(baseline_times_ms)
    indexed_average_ms = calculate_average(indexed_times_ms)

    baseline_median_ms = calculate_median(baseline_times_ms)
    indexed_median_ms = calculate_median(indexed_times_ms)

    mean_overhead_ms, mean_overhead_percent = (
        calculate_maintenance_overhead(
            baseline_average_ms,
            indexed_average_ms,
        )
    )

    median_overhead_ms, median_overhead_percent = (
        calculate_maintenance_overhead(
            baseline_median_ms,
            indexed_median_ms,
        )
    )

    result = {
        "table_name": table_name,
        "indexed_columns": list(indexed_columns),
        "row_count": row_count,
        "iterations": iterations,
        "baseline_times_ms": list(baseline_times_ms),
        "indexed_times_ms": list(indexed_times_ms),

        # Mean
        "baseline_average_ms": baseline_average_ms,
        "indexed_average_ms": indexed_average_ms,
        "maintenance_overhead_ms": mean_overhead_ms,
        "maintenance_overhead_percent": mean_overhead_percent,

        # Median
        "baseline_median_ms": baseline_median_ms,
        "indexed_median_ms": indexed_median_ms,
        "median_overhead_ms": median_overhead_ms,
        "median_overhead_percent": median_overhead_percent,

        # Variability
        "baseline_stddev_ms": calculate_standard_deviation(
            baseline_times_ms
        ),
        "indexed_stddev_ms": calculate_standard_deviation(
            indexed_times_ms
        ),

        # Range
        "baseline_min_ms": min(baseline_times_ms),
        "baseline_max_ms": max(baseline_times_ms),
        "indexed_min_ms": min(indexed_times_ms),
        "indexed_max_ms": max(indexed_times_ms),
    }

    validate_maintenance_result(result)

    return result


def measure_write_operation(
    operation: Callable[[], None],
) -> float:
    """
    Measure one write-operation execution.
    """

    import time

    start = time.perf_counter()

    operation()

    end = time.perf_counter()

    return (end - start) * 1000.0


def summarize_maintenance_result(
    result: dict[str, Any],
) -> dict[str, Any]:
    """
    Produce a concise analytical summary.

    No recommendation score or priority is modified.
    """

    mean_overhead = result["maintenance_overhead_percent"]
    median_overhead = result["median_overhead_percent"]

    if median_overhead > 0:
        interpretation = (
            "indexed writes had higher median execution time"
        )
    elif median_overhead < 0:
        interpretation = (
            "indexed writes had lower median execution time "
            "in this observation"
        )
    else:
        interpretation = (
            "no median write-time difference was measured"
        )

    return {
        "table_name": result["table_name"],
        "indexed_columns": result["indexed_columns"],
        "row_count": result["row_count"],
        "iterations": result["iterations"],

        "baseline_average_ms": result["baseline_average_ms"],
        "indexed_average_ms": result["indexed_average_ms"],
        "maintenance_overhead_ms": result["maintenance_overhead_ms"],
        "maintenance_overhead_percent": mean_overhead,

        "baseline_median_ms": result["baseline_median_ms"],
        "indexed_median_ms": result["indexed_median_ms"],
        "median_overhead_ms": result["median_overhead_ms"],
        "median_overhead_percent": median_overhead,

        "baseline_stddev_ms": result["baseline_stddev_ms"],
        "indexed_stddev_ms": result["indexed_stddev_ms"],

        "baseline_min_ms": result["baseline_min_ms"],
        "baseline_max_ms": result["baseline_max_ms"],
        "indexed_min_ms": result["indexed_min_ms"],
        "indexed_max_ms": result["indexed_max_ms"],

        "interpretation": interpretation,
    }


def print_maintenance_result(result: dict[str, Any]) -> None:
    """Print the maintenance experiment result."""

    summary = summarize_maintenance_result(result)

    print()
    print("=" * 70)
    print("INDEX MAINTENANCE EXPERIMENT")
    print("=" * 70)

    print(f"Table                  : {summary['table_name']}")
    print(
        "Indexed columns        : "
        f"{', '.join(summary['indexed_columns'])}"
    )
    print(f"Rows per iteration     : {summary['row_count']}")
    print(f"Iterations             : {summary['iterations']}")

    print()
    print("MEAN")
    print(
        f"Baseline average       : "
        f"{summary['baseline_average_ms']:.4f} ms"
    )
    print(
        f"Indexed average        : "
        f"{summary['indexed_average_ms']:.4f} ms"
    )
    print(
        f"Mean overhead          : "
        f"{summary['maintenance_overhead_ms']:.4f} ms"
    )
    print(
        f"Mean overhead %        : "
        f"{summary['maintenance_overhead_percent']:.4f}%"
    )

    print()
    print("MEDIAN")
    print(
        f"Baseline median        : "
        f"{summary['baseline_median_ms']:.4f} ms"
    )
    print(
        f"Indexed median         : "
        f"{summary['indexed_median_ms']:.4f} ms"
    )
    print(
        f"Median overhead        : "
        f"{summary['median_overhead_ms']:.4f} ms"
    )
    print(
        f"Median overhead %      : "
        f"{summary['median_overhead_percent']:.4f}%"
    )

    print()
    print("VARIABILITY")
    print(
        f"Baseline std deviation : "
        f"{summary['baseline_stddev_ms']:.4f} ms"
    )
    print(
        f"Indexed std deviation  : "
        f"{summary['indexed_stddev_ms']:.4f} ms"
    )

    print()
    print("RANGE")
    print(
        f"Baseline min/max       : "
        f"{summary['baseline_min_ms']:.4f} / "
        f"{summary['baseline_max_ms']:.4f} ms"
    )
    print(
        f"Indexed min/max        : "
        f"{summary['indexed_min_ms']:.4f} / "
        f"{summary['indexed_max_ms']:.4f} ms"
    )

    print()
    print(f"Interpretation         : {summary['interpretation']}")
    print("=" * 70)
