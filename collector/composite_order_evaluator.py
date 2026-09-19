"""
Composite Index Column-Order Evaluator
--------------------------------------
Evaluates M16.1 composite-index column-order experiments.

This module is experimental only.

It:
    - benchmarks one common baseline;
    - tests the original column ordering;
    - tests the alternative column ordering;
    - compares both against the same baseline;
    - records paired experimental evidence;
    - records row-preservation evidence;
    - records plan-change evidence;
    - records buffer-usage evidence.

It does not:
    - modify recommendation generation;
    - use recommendation scores;
    - use previous benchmark outcomes;
    - save results to benchmark_results.
"""

from collector.benchmark_runner import benchmark_query

from collector.index_validator import (
    analyze_table,
    calculate_improvement,
    create_composite_test_index,
    drop_test_index,
    find_index_usage,
)

from collector.composite_order_experiment import (
    is_eligible_composite_candidate,
)

from collector.index_candidate_generator import (
    normalize_candidate_columns,
)


DEFAULT_ITERATIONS = 10
DEFAULT_WARMUP_RUNS = 2


def calculate_order_effect(original_improvement, alternative_improvement):
    """
    Calculate the difference in improvement between the alternative
    and original column ordering.

    A positive value means the alternative ordering produced greater
    improvement than the original ordering.

    A negative value means the original ordering produced greater
    improvement than the alternative ordering.

    This is an observed experimental difference, not a claim that
    either ordering is universally optimal.
    """
    return alternative_improvement - original_improvement


def _get_average_rows(benchmark):
    """
    Return the average number of rows returned by a benchmark result.
    """
    return benchmark["average_rows"]


def _get_representative_plan(result):
    """
    Return the representative execution plan from a benchmark result.

    Supports both:
        - normalized experimental results using "plan";
        - raw benchmark results using "representative_plan".
    """
    if "plan" in result:
        return result["plan"]

    return result["representative_plan"]


def _normalize_benchmark_result(benchmark):
    """
    Normalize a raw benchmark result into the schema used by the
    column-order evaluator.

    benchmark_query() returns:
        average_execution_time_ms

    The evaluator uses:
        execution_time_ms

    This function keeps the benchmark evidence intact while adding
    the normalized execution-time field.
    """
    return {
        **benchmark,
        "execution_time_ms": benchmark["average_execution_time_ms"],
    }


def build_experiment_result(
    experiment,
    baseline,
    original,
    alternative,
):
    """
    Build a paired column-order experiment result.

    The function performs no database operations.

    Row preservation is evaluated against the common baseline.

    Plan change is evaluated by comparing the representative
    plan of each indexed variant with the common baseline plan.

    All three inputs are expected to use the normalized
    "execution_time_ms" field.
    """

    original_improvement = calculate_improvement(
        baseline["execution_time_ms"],
        original["execution_time_ms"],
    )

    alternative_improvement = calculate_improvement(
        baseline["execution_time_ms"],
        alternative["execution_time_ms"],
    )

    order_effect = calculate_order_effect(
        original_improvement,
        alternative_improvement,
    )

    baseline_rows = _get_average_rows(baseline)
    original_rows = _get_average_rows(original)
    alternative_rows = _get_average_rows(alternative)

    original_rows_preserved = (
        original_rows == baseline_rows
    )

    alternative_rows_preserved = (
        alternative_rows == baseline_rows
    )

    baseline_plan = _get_representative_plan(baseline)
    original_plan = _get_representative_plan(original)
    alternative_plan = _get_representative_plan(alternative)

    original_plan_changed = (
        original_plan != baseline_plan
    )

    alternative_plan_changed = (
        alternative_plan != baseline_plan
    )

    return {
        "recommendation_id": experiment.get("recommendation_id"),
        "query_id": experiment.get("query_id"),
        "fingerprint": experiment.get("fingerprint"),
        "table_name": experiment.get("table_name"),
        "candidate_type": experiment.get("candidate_type"),
        "source_type": experiment.get("source_type"),
        "column_count": experiment.get("column_count"),
        "original_columns": list(
            experiment["original_columns"]
        ),
        "alternative_columns": list(
            experiment["alternative_columns"]
        ),
        "experiment_type": experiment.get(
            "experiment_type",
            "column_order",
        ),
        "baseline": baseline,
        "original": original,
        "alternative": alternative,
        "original_improvement_percentage": (
            original_improvement
        ),
        "alternative_improvement_percentage": (
            alternative_improvement
        ),
        "improvement_difference_percentage_points": (
            order_effect
        ),
        "original_rows_preserved": (
            original_rows_preserved
        ),
        "alternative_rows_preserved": (
            alternative_rows_preserved
        ),
        "original_plan_changed": (
            original_plan_changed
        ),
        "alternative_plan_changed": (
            alternative_plan_changed
        ),
    }


def _build_experimental_index_name(
    table_name,
    columns,
    variant,
):
    """
    Build a PostgreSQL-compatible experimental index name.

    PostgreSQL identifiers are limited to 63 bytes.
    """
    normalized_columns = normalize_candidate_columns(
        columns
    )

    column_part = "_".join(normalized_columns)

    base_name = (
        f"idx_{table_name}_{column_part}_{variant}"
    )

    return base_name[:63]


def _run_order_variant(
    query,
    table_name,
    columns,
    index_name,
    iterations,
    warmup_runs,
):
    """
    Create one experimental composite index, benchmark the query,
    collect evidence, and always remove the experimental index.
    """
    created_index = None

    try:
        created_index = create_composite_test_index(
            table_name=table_name,
            columns=columns,
            index_name=index_name,
        )

        analyze_table(table_name)

        benchmark = benchmark_query(
            query,
            iterations=iterations,
            warmup_runs=warmup_runs,
        )

        usage = find_index_usage(
            benchmark["representative_plan"],
            created_index,
        )

        return {
            "index_name": created_index,
            "columns": list(columns),
            "benchmark": benchmark,
            "execution_time_ms": (
                benchmark["average_execution_time_ms"]
            ),
            "median_execution_time_ms": (
                benchmark["median_execution_time_ms"]
            ),
            "average_rows": benchmark["average_rows"],
            "average_shared_hit_blocks": (
                benchmark["average_shared_hit_blocks"]
            ),
            "average_shared_read_blocks": (
                benchmark["average_shared_read_blocks"]
            ),
            "index_used": usage["used"],
            "index_node_type": usage["node_type"],
            "plan": benchmark["representative_plan"],
        }

    finally:
        if created_index:
            drop_test_index(created_index)


def evaluate_order_experiment(
    experiment,
    query,
    iterations=DEFAULT_ITERATIONS,
    warmup_runs=DEFAULT_WARMUP_RUNS,
):
    """
    Execute a complete paired column-order experiment.

    Experimental sequence:

        1. Common baseline
        2. Original column ordering
        3. Alternative column ordering
        4. Compare both variants against the same baseline

    The experimental indexes are always removed after each variant.

    No results are written to benchmark_results.
    """

    if not is_eligible_composite_candidate(
        {
            "candidate_type": experiment.get(
                "candidate_type"
            ),
            "table_name": experiment.get(
                "table_name"
            ),
            "column_name": ", ".join(
                experiment.get(
                    "original_columns",
                    [],
                )
            ),
            "column_count": experiment.get(
                "column_count"
            ),
        }
    ):
        raise ValueError(
            "Experiment does not contain an "
            "eligible composite candidate."
        )

    if not query or not query.strip():
        raise ValueError(
            "query must not be empty."
        )

    if iterations <= 0:
        raise ValueError(
            "iterations must be greater than 0."
        )

    if warmup_runs < 0:
        raise ValueError(
            "warmup_runs cannot be negative."
        )

    # ---------------------------------------------------------
    # 1. Common baseline
    # ---------------------------------------------------------

    baseline_raw = benchmark_query(
        query,
        iterations=iterations,
        warmup_runs=warmup_runs,
    )

    # Normalize the raw benchmark result so that the baseline
    # follows the same contract as the experimental variants.
    baseline = _normalize_benchmark_result(
        baseline_raw
    )

    # ---------------------------------------------------------
    # 2. Prepare experimental variants
    # ---------------------------------------------------------

    table_name = experiment["table_name"]

    original_columns = list(
        experiment["original_columns"]
    )

    alternative_columns = list(
        experiment["alternative_columns"]
    )

    original_name = _build_experimental_index_name(
        table_name,
        original_columns,
        "original",
    )

    alternative_name = _build_experimental_index_name(
        table_name,
        alternative_columns,
        "alternative",
    )

    # ---------------------------------------------------------
    # 3. Original ordering
    # ---------------------------------------------------------

    original = _run_order_variant(
        query=query,
        table_name=table_name,
        columns=original_columns,
        index_name=original_name,
        iterations=iterations,
        warmup_runs=warmup_runs,
    )

    # ---------------------------------------------------------
    # 4. Alternative ordering
    # ---------------------------------------------------------

    alternative = _run_order_variant(
        query=query,
        table_name=table_name,
        columns=alternative_columns,
        index_name=alternative_name,
        iterations=iterations,
        warmup_runs=warmup_runs,
    )

    # ---------------------------------------------------------
    # 5. Build paired experimental result
    # ---------------------------------------------------------

    return build_experiment_result(
        experiment=experiment,
        baseline=baseline,
        original=original,
        alternative=alternative,
    )
