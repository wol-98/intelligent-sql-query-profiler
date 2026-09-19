"""
Tests for M18.2 - Linked Read/Write Benchmark.

These tests focus on deterministic analytical and validation
helpers. Database execution is reserved for the real M18.2
experiment runner.
"""

import pytest

from collector.linked_cost_benefit_benchmark import (
    build_experiment_table_name,
    calculate_write_overhead,
    validate_experiment_table_name,
    build_read_evidence,
    build_write_evidence,
)


# =========================================================
# EXPERIMENT TABLE NAME
# =========================================================

def test_build_experiment_table_name():
    name = build_experiment_table_name(
        "M18_001",
        "orders",
    )

    assert name == (
        "m18_m18_001_orders_test"
    )


def test_experiment_table_name_is_valid():
    name = build_experiment_table_name(
        "M18-001",
        "orders",
    )

    assert validate_experiment_table_name(
        name
    )


def test_invalid_experiment_table_name():
    with pytest.raises(ValueError):
        validate_experiment_table_name(
            "orders;DROP"
        )


# =========================================================
# WRITE OVERHEAD
# =========================================================

def test_write_overhead():
    overhead = calculate_write_overhead(
        100.0,
        120.0,
    )

    assert overhead == pytest.approx(
        20.0
    )


def test_negative_write_overhead():
    overhead = calculate_write_overhead(
        100.0,
        80.0,
    )

    assert overhead == pytest.approx(
        -20.0
    )


def test_zero_baseline_write_overhead():
    overhead = calculate_write_overhead(
        0.0,
        100.0,
    )

    assert overhead == 0.0


# =========================================================
# MOCK EXPERIMENT
# =========================================================

def make_experiment():
    return {
        "experiment_id": "M18_001",
        "index_name": "m18_idx_orders_customer_id",
        "read_query": (
            "SELECT * FROM {table} "
            "WHERE customer_id = 845;"
        ),
        "read_iterations": 2,
        "read_warmup_runs": 1,
        "write_iterations": 2,
        "write_warmup_runs": 1,
        "columns": ["customer_id"],
        "table_name": "orders",
        "index_type": "BTREE",
    }


def make_benchmark(
    average,
    median,
    rows=10,
    plan=None,
):
    if plan is None:
        plan = {
            "Node Type": "Seq Scan"
        }

    return {
        "iterations": 2,
        "warmup_runs": 1,
        "runs": [],
        "execution_times_ms": [
            average,
            average,
        ],
        "planning_times_ms": [
            0.1,
            0.1,
        ],
        "average_execution_time_ms":
            average,
        "median_execution_time_ms":
            median,
        "minimum_execution_time_ms":
            average,
        "maximum_execution_time_ms":
            average,
        "standard_deviation_ms":
            0.0,
        "average_planning_time_ms":
            0.1,
        "average_rows":
            rows,
        "average_shared_hit_blocks":
            10,
        "average_shared_read_blocks":
            0,
        "representative_plan":
            plan,
    }


# =========================================================
# READ EVIDENCE
# =========================================================

def test_build_read_evidence():
    experiment = make_experiment()

    baseline = make_benchmark(
        average=100.0,
        median=100.0,
        rows=10,
        plan={
            "Node Type": "Seq Scan"
        },
    )

    indexed = make_benchmark(
        average=50.0,
        median=50.0,
        rows=10,
        plan={
            "Node Type": "Index Scan",
            "Index Name":
                "m18_idx_orders_customer_id",
        },
    )

    # find_index_usage requires the actual recursive
    # plan structure and will identify the index.
    evidence = build_read_evidence(
        experiment,
        baseline,
        indexed,
        "m18_idx_orders_customer_id",
    )

    assert evidence["experiment_id"] == (
        "M18_001"
    )

    assert evidence["index_name"] == (
        "m18_idx_orders_customer_id"
    )

    assert evidence[
        "improvement_percentage"
    ] == pytest.approx(50.0)

    assert evidence[
        "median_improvement_percentage"
    ] == pytest.approx(50.0)

    assert evidence["rows_preserved"] is True
    assert evidence["index_used"] is True


def test_read_evidence_detects_row_change():
    experiment = make_experiment()

    baseline = make_benchmark(
        average=100.0,
        median=100.0,
        rows=10,
    )

    indexed = make_benchmark(
        average=50.0,
        median=50.0,
        rows=9,
        plan={
            "Node Type": "Index Scan",
            "Index Name":
                "m18_idx_orders_customer_id",
        },
    )

    evidence = build_read_evidence(
        experiment,
        baseline,
        indexed,
        "m18_idx_orders_customer_id",
    )

    assert evidence["rows_preserved"] is False


# =========================================================
# WRITE EVIDENCE
# =========================================================

def make_write_result(
    average,
    median,
):
    return {
        "iterations": 2,
        "warmup_runs": 1,
        "batch_size": 1000,
        "execution_times_ms": [
            average,
            average,
        ],
        "average_execution_time_ms":
            average,
        "median_execution_time_ms":
            median,
        "minimum_execution_time_ms":
            average,
        "maximum_execution_time_ms":
            average,
        "standard_deviation_ms":
            0.0,
    }


def test_build_write_evidence():
    experiment = make_experiment()

    baseline = make_write_result(
        100.0,
        100.0,
    )

    indexed = make_write_result(
        120.0,
        110.0,
    )

    evidence = build_write_evidence(
        experiment,
        baseline,
        indexed,
        "m18_idx_orders_customer_id",
    )

    assert evidence["experiment_id"] == (
        "M18_001"
    )

    assert evidence[
        "average_write_overhead_percentage"
    ] == pytest.approx(20.0)

    assert evidence[
        "median_write_overhead_percentage"
    ] == pytest.approx(10.0)

    assert evidence["batch_size"] == 1000
