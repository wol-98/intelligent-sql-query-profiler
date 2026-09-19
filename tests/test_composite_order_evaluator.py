"""
Tests for composite index column-order evaluation.
"""

from copy import deepcopy

from collector.composite_order_evaluator import (
    build_experiment_result,
    calculate_order_effect,
)


def make_experiment():
    """
    Build a representative M16.1 experiment definition.
    """

    return {
        "recommendation_id": 10,
        "query_id": "Q001",
        "fingerprint": "abc123",
        "table_name": "orders",
        "candidate_type": "composite",
        "source_type": "mixed",
        "column_count": 2,
        "original_columns": [
            "status",
            "customer_id",
        ],
        "alternative_columns": [
            "customer_id",
            "status",
        ],
        "experiment_type": "column_order",
    }


def make_benchmark(execution_time):
    """
    Build a normalized benchmark/variant result fixture.

    The execution-time key matches the contract returned by
    _run_order_variant().

    The benchmark runner itself uses
    average_execution_time_ms internally, but the evaluator
    normalizes that value to execution_time_ms for each
    experimental variant.
    """

    return {
        "execution_time_ms": execution_time,
        "median_execution_time_ms": execution_time,
        "average_rows": 50,
        "average_shared_hit_blocks": 100,
        "average_shared_read_blocks": 10,
        "representative_plan": {
            "Node Type": "Seq Scan",
        },
    }


def test_build_result_calculates_original_improvement():
    """
    Verify that improvement for the original ordering is
    calculated against the common baseline.
    """

    result = build_experiment_result(
        make_experiment(),
        make_benchmark(100.0),
        make_benchmark(60.0),
        make_benchmark(80.0),
    )

    assert (
        result["original_improvement_percentage"]
        == 40.0
    )


def test_build_result_calculates_alternative_improvement():
    """
    Verify that improvement for the alternative ordering is
    calculated against the common baseline.
    """

    result = build_experiment_result(
        make_experiment(),
        make_benchmark(100.0),
        make_benchmark(60.0),
        make_benchmark(80.0),
    )

    assert (
        result["alternative_improvement_percentage"]
        == 20.0
    )


def test_build_result_calculates_order_effect():
    """
    Verify the difference between alternative and original
    improvement.
    """

    result = build_experiment_result(
        make_experiment(),
        make_benchmark(100.0),
        make_benchmark(60.0),
        make_benchmark(80.0),
    )

    assert (
        result[
            "improvement_difference_percentage_points"
        ]
        == -20.0
    )


def test_build_result_preserves_metadata():
    """
    Verify that experiment metadata is preserved.
    """

    experiment = make_experiment()

    result = build_experiment_result(
        experiment,
        make_benchmark(100.0),
        make_benchmark(60.0),
        make_benchmark(80.0),
    )

    assert result["recommendation_id"] == 10
    assert result["query_id"] == "Q001"
    assert result["fingerprint"] == "abc123"
    assert result["table_name"] == "orders"
    assert result["candidate_type"] == "composite"
    assert result["source_type"] == "mixed"
    assert result["column_count"] == 2
    assert result["experiment_type"] == "column_order"


def test_build_result_preserves_column_orders():
    """
    Verify that both column orderings are preserved.
    """

    result = build_experiment_result(
        make_experiment(),
        make_benchmark(100.0),
        make_benchmark(60.0),
        make_benchmark(80.0),
    )

    assert result["original_columns"] == [
        "status",
        "customer_id",
    ]

    assert result["alternative_columns"] == [
        "customer_id",
        "status",
    ]


def test_build_result_preserves_benchmark_evidence():
    """
    Verify that the complete benchmark evidence is retained.
    """

    baseline = make_benchmark(100.0)
    original = make_benchmark(60.0)
    alternative = make_benchmark(80.0)

    result = build_experiment_result(
        make_experiment(),
        baseline,
        original,
        alternative,
    )

    assert result["baseline"] is baseline
    assert result["original"] is original
    assert result["alternative"] is alternative

    assert (
        result["original"]["average_rows"]
        == 50
    )

    assert (
        result["original"][
            "average_shared_hit_blocks"
        ]
        == 100
    )

    assert (
        result["original"][
            "average_shared_read_blocks"
        ]
        == 10
    )


def test_build_result_does_not_modify_experiment():
    """
    Verify that building a result does not mutate the
    original experiment definition.
    """

    experiment = make_experiment()

    experiment_before = deepcopy(
        experiment
    )

    build_experiment_result(
        experiment,
        make_benchmark(100.0),
        make_benchmark(60.0),
        make_benchmark(80.0),
    )

    assert experiment == experiment_before


def test_improvement_difference_uses_percentage_points():
    """
    Verify that order effect is expressed as a difference
    in percentage points.
    """

    result = build_experiment_result(
        make_experiment(),
        make_benchmark(200.0),
        make_benchmark(100.0),
        make_benchmark(150.0),
    )

    assert (
        result[
            "original_improvement_percentage"
        ]
        == 50.0
    )

    assert (
        result[
            "alternative_improvement_percentage"
        ]
        == 25.0
    )

    assert (
        result[
            "improvement_difference_percentage_points"
        ]
        == -25.0
    )


def test_original_rows_preserved_is_recorded():
    """
    Verify that the original ordering is marked as
    preserving rows when its output matches the baseline.
    """

    baseline = make_benchmark(100.0)
    original = make_benchmark(60.0)
    alternative = make_benchmark(80.0)

    result = build_experiment_result(
        make_experiment(),
        baseline,
        original,
        alternative,
    )

    assert result["original_rows_preserved"] is True


def test_alternative_rows_preserved_is_recorded():
    """
    Verify that the alternative ordering is marked as
    preserving rows when its output matches the baseline.
    """

    baseline = make_benchmark(100.0)
    original = make_benchmark(60.0)
    alternative = make_benchmark(80.0)

    result = build_experiment_result(
        make_experiment(),
        baseline,
        original,
        alternative,
    )

    assert result["alternative_rows_preserved"] is True


def test_row_difference_is_detected():
    """
    Verify that a difference in returned rows is detected.
    """

    baseline = make_benchmark(100.0)

    original = make_benchmark(60.0)
    original["average_rows"] = 45

    alternative = make_benchmark(80.0)

    result = build_experiment_result(
        make_experiment(),
        baseline,
        original,
        alternative,
    )

    assert result["original_rows_preserved"] is False
    assert result["alternative_rows_preserved"] is True


def test_original_plan_change_is_recorded():
    """
    Verify that a plan change for the original ordering
    is detected against the common baseline.
    """

    baseline = make_benchmark(100.0)

    original = make_benchmark(60.0)
    original["representative_plan"] = {
        "Node Type": "Index Scan",
    }

    alternative = make_benchmark(80.0)

    result = build_experiment_result(
        make_experiment(),
        baseline,
        original,
        alternative,
    )

    assert result["original_plan_changed"] is True
    assert result["alternative_plan_changed"] is False


def test_alternative_plan_change_is_recorded():
    """
    Verify that a plan change for the alternative ordering
    is detected against the common baseline.
    """

    baseline = make_benchmark(100.0)

    original = make_benchmark(60.0)

    alternative = make_benchmark(80.0)
    alternative["representative_plan"] = {
        "Node Type": "Index Scan",
    }

    result = build_experiment_result(
        make_experiment(),
        baseline,
        original,
        alternative,
    )

    assert result["original_plan_changed"] is False
    assert result["alternative_plan_changed"] is True


def test_calculate_order_effect_positive():
    """
    Verify positive order effect when the alternative ordering
    produces greater improvement.
    """

    effect = calculate_order_effect(
        20.0,
        35.0,
    )

    assert effect == 15.0


def test_calculate_order_effect_negative():
    """
    Verify negative order effect when the original ordering
    produces greater improvement.
    """

    effect = calculate_order_effect(
        35.0,
        20.0,
    )

    assert effect == -15.0


def test_calculate_order_effect_zero():
    """
    Verify zero order effect when both orderings produce
    the same improvement.
    """

    effect = calculate_order_effect(
        25.0,
        25.0,
    )

    assert effect == 0.0
