"""
Full Workload Benchmark
-----------------------
Benchmarks all queries from database/workload.sql.

No indexes are created or modified.
This establishes the performance baseline.
"""

import re
import statistics

from collector.benchmark_runner import benchmark_query


# =========================================================
# LOAD WORKLOAD
# =========================================================

def load_workload(filepath):
    """
    Load and parse Q001-Q015 from workload.sql.

    Expected format:

    -- Q001
    SELECT ...

    -- Q002
    SELECT ...
    """

    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    pattern = re.compile(
    r"--\s*(Q\d+)\s*:?.*?\n(.*?)(?=\n--\s*Q\d+\s*:?.*?\n|\Z)",
    re.IGNORECASE | re.DOTALL
)

    queries = {}

    for match in pattern.finditer(content):

        query_id = match.group(1).upper()

        query = match.group(2).strip()

        if query:
            queries[query_id] = query

    return queries


# =========================================================
# PRINT SUMMARY
# =========================================================

def print_summary(results):
    """
    Print compact benchmark summary.
    """

    print("\n" + "=" * 110)
    print("FULL WORKLOAD BASELINE")
    print("=" * 110)

    header = (
        f"{'Query':<8}"
        f"{'Avg(ms)':>12}"
        f"{'Median':>12}"
        f"{'Min':>12}"
        f"{'Max':>12}"
        f"{'Std Dev':>12}"
        f"{'Plan(ms)':>12}"
        f"{'Rows':>12}"
    )

    print(header)
    print("-" * 110)

    for query_id, benchmark in results.items():

        print(
            f"{query_id:<8}"
            f"{benchmark['average_execution_time_ms']:>12.3f}"
            f"{benchmark['median_execution_time_ms']:>12.3f}"
            f"{benchmark['minimum_execution_time_ms']:>12.3f}"
            f"{benchmark['maximum_execution_time_ms']:>12.3f}"
            f"{benchmark['standard_deviation_ms']:>12.3f}"
            f"{benchmark['average_planning_time_ms']:>12.3f}"
            f"{benchmark['average_rows']:>12.0f}"
        )

    print("=" * 110)


# =========================================================
# MAIN
# =========================================================

def main():

    workload_path = (
        "database/workload.sql"
    )

    print("\n" + "=" * 70)
    print("FULL WORKLOAD BENCHMARK")
    print("=" * 70)

    queries = load_workload(
        workload_path
    )

    print(
        f"\nQueries loaded: "
        f"{len(queries)}"
    )

    if not queries:
        raise RuntimeError(
            "No queries were found in workload.sql"
        )

    results = {}

    # -----------------------------------------------------
    # Benchmark each query
    # -----------------------------------------------------

    for query_id, query in queries.items():

        print(
            f"\nBenchmarking {query_id}..."
        )

        benchmark = benchmark_query(
            query,
            iterations=5,
            warmup_runs=1
        )

        results[
            query_id
        ] = benchmark

        print(
            f"  Average execution: "
            f"{benchmark['average_execution_time_ms']:.3f} ms"
        )

        print(
            f"  Median: "
            f"{benchmark['median_execution_time_ms']:.3f} ms"
        )

    # -----------------------------------------------------
    # Final summary
    # -----------------------------------------------------

    print_summary(
        results
    )

    print(
        "\nFull workload benchmark "
        "completed successfully."
    )


if __name__ == "__main__":
    main()
