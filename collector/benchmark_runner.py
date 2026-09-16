"""
Benchmark Runner v2
-------------------
PostgreSQL-aware query benchmarking.

Uses EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
to capture PostgreSQL execution metrics over
multiple runs.

This module does NOT create indexes.
"""

import statistics
import json

from config.database import get_connection


# =========================================================
# RUN ONE QUERY WITH POSTGRESQL ANALYSIS
# =========================================================

def run_single_benchmark(query):
    """
    Execute EXPLAIN ANALYZE for one query and extract
    PostgreSQL performance metrics.

    Returns
    -------
    dict
        PostgreSQL execution metrics.
    """

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        explain_query = f"""
        EXPLAIN (
            ANALYZE,
            BUFFERS,
            FORMAT JSON
        )
        {query}
        """

        cursor.execute(explain_query)

        result = cursor.fetchone()[0]

        # PostgreSQL returns the JSON plan as a list.
        plan_data = result[0]

        execution_time_ms = plan_data.get(
            "Execution Time",
            0
        )

        planning_time_ms = plan_data.get(
            "Planning Time",
            0
        )

        root_plan = plan_data.get(
            "Plan",
            {}
        )

        actual_rows = root_plan.get(
            "Actual Rows",
            0
        )

        shared_hit_blocks = root_plan.get(
            "Shared Hit Blocks",
            0
        )

        shared_read_blocks = root_plan.get(
            "Shared Read Blocks",
            0
        )

        return {
            "execution_time_ms": execution_time_ms,
            "planning_time_ms": planning_time_ms,
            "actual_rows": actual_rows,
            "shared_hit_blocks": shared_hit_blocks,
            "shared_read_blocks": shared_read_blocks,
            "plan": root_plan,
            "raw_plan": plan_data,
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# BENCHMARK QUERY
# =========================================================

def benchmark_query(
    query,
    iterations=5,
    warmup_runs=1
):
    """
    Run a PostgreSQL query repeatedly and calculate
    benchmark statistics.

    Parameters
    ----------
    query : str
        SQL query.

    iterations : int
        Number of measured runs.

    warmup_runs : int
        Number of warm-up executions.

    Returns
    -------
    dict
        Benchmark results.
    """

    if iterations <= 0:
        raise ValueError(
            "iterations must be greater than 0"
        )

    if warmup_runs < 0:
        raise ValueError(
            "warmup_runs cannot be negative"
        )

    # -----------------------------------------------------
    # Warm-up
    # -----------------------------------------------------

    for _ in range(warmup_runs):

        run_single_benchmark(
            query
        )

    # -----------------------------------------------------
    # Measured runs
    # -----------------------------------------------------

    runs = []

    for _ in range(iterations):

        result = run_single_benchmark(
            query
        )

        runs.append(
            result
        )

    # -----------------------------------------------------
    # Extract execution times
    # -----------------------------------------------------

    execution_times = [
        run["execution_time_ms"]
        for run in runs
    ]

    planning_times = [
        run["planning_time_ms"]
        for run in runs
    ]

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    average_execution_time = (
        statistics.mean(
            execution_times
        )
    )

    median_execution_time = (
        statistics.median(
            execution_times
        )
    )

    minimum_execution_time = (
        min(execution_times)
    )

    maximum_execution_time = (
        max(execution_times)
    )

    standard_deviation = (
        statistics.stdev(
            execution_times
        )
        if len(execution_times) > 1
        else 0
    )

    average_planning_time = (
        statistics.mean(
            planning_times
        )
    )

    average_rows = statistics.mean([
        run["actual_rows"]
        for run in runs
    ])

    average_shared_hits = statistics.mean([
        run["shared_hit_blocks"]
        for run in runs
    ])

    average_shared_reads = statistics.mean([
        run["shared_read_blocks"]
        for run in runs
    ])

    # Use the first plan as the representative plan.
    representative_plan = runs[0]["plan"]

    return {
        "iterations": iterations,
        "warmup_runs": warmup_runs,

        "runs": runs,

        "execution_times_ms":
            execution_times,

        "planning_times_ms":
            planning_times,

        "average_execution_time_ms":
            average_execution_time,

        "median_execution_time_ms":
            median_execution_time,

        "minimum_execution_time_ms":
            minimum_execution_time,

        "maximum_execution_time_ms":
            maximum_execution_time,

        "standard_deviation_ms":
            standard_deviation,

        "average_planning_time_ms":
            average_planning_time,

        "average_rows":
            average_rows,

        "average_shared_hit_blocks":
            average_shared_hits,

        "average_shared_read_blocks":
            average_shared_reads,

        "representative_plan":
            representative_plan,
    }


# =========================================================
# PRINT BENCHMARK
# =========================================================

def print_benchmark(
    benchmark
):
    """
    Print PostgreSQL benchmark results.
    """

    print("\n" + "=" * 70)
    print("POSTGRESQL QUERY BENCHMARK")
    print("=" * 70)

    print(
        f"Iterations              : "
        f"{benchmark['iterations']}"
    )

    print(
        f"Warm-up runs            : "
        f"{benchmark['warmup_runs']}"
    )

    print("\nExecution Time per Run:")

    for number, execution_time in enumerate(
        benchmark["execution_times_ms"],
        start=1
    ):

        planning_time = (
            benchmark[
                "planning_times_ms"
            ][number - 1]
        )

        print(
            f"  Run {number:<2} : "
            f"Execution = "
            f"{execution_time:.3f} ms | "
            f"Planning = "
            f"{planning_time:.3f} ms"
        )

    print("\nExecution Statistics:")

    print(
        f"  Average               : "
        f"{benchmark['average_execution_time_ms']:.3f} ms"
    )

    print(
        f"  Median                : "
        f"{benchmark['median_execution_time_ms']:.3f} ms"
    )

    print(
        f"  Minimum               : "
        f"{benchmark['minimum_execution_time_ms']:.3f} ms"
    )

    print(
        f"  Maximum               : "
        f"{benchmark['maximum_execution_time_ms']:.3f} ms"
    )

    print(
        f"  Standard deviation    : "
        f"{benchmark['standard_deviation_ms']:.3f} ms"
    )

    print("\nOther PostgreSQL Metrics:")

    print(
        f"  Avg planning time     : "
        f"{benchmark['average_planning_time_ms']:.3f} ms"
    )

    print(
        f"  Avg actual rows       : "
        f"{benchmark['average_rows']:.0f}"
    )

    print(
        f"  Avg shared hits       : "
        f"{benchmark['average_shared_hit_blocks']:.0f}"
    )

    print(
        f"  Avg shared reads      : "
        f"{benchmark['average_shared_read_blocks']:.0f}"
    )

    print("\nRepresentative execution plan:")

    print(
        json.dumps(
            benchmark["representative_plan"],
            indent=2
        )
    )

    print("=" * 70)
