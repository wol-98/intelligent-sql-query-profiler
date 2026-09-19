"""
Tests for M18.1 - Linked Cost-Benefit Experiment Design.
"""

import pytest

from collector.linked_cost_benefit_experiment import (
    build_experiment_definition,
    build_measurement_contract,
    build_linked_result,
    render_read_query,
    validate_experiment_definition,
    validate_linked_result,
    verify_measurement_linkage,
)


# =========================================================
# TEST FIXTURE
# =========================================================

def make_experiment():
    return build_experiment_definition(
        experiment_id="M18_001",
        index_name="m18_idx_orders_customer_id",
        table_name="orders",
        columns=["customer_id"],
        read_query=(
            "SELECT * FROM {table} "
            "WHERE customer_id = 845;"
        ),
        write_table="orders",
        read_iterations=10,
        read_warmup_runs=2,
        write_iterations=5,
        write_warmup_runs=2,
        index_type="BTREE",
    )


# =========================================================
# EXPERIMENT DEFINITION
# =========================================================

def test_valid_experiment_definition():
    experiment = make_experiment()

    assert validate_experiment_definition(
        experiment
    )

    assert experiment["experiment_id"] == "M18_001"
    assert experiment["index_name"] == (
        "m18_idx_orders_customer_id"
    )
    assert experiment["columns"] == ["customer_id"]
    assert "{table}" in experiment["read_query"]


def test_invalid_empty_columns():
    with pytest.raises(ValueError):
        build_experiment_definition(
            experiment_id="M18_001",
            index_name="m18_idx_orders_customer_id",
            table_name="orders",
            columns=[],
            read_query=(
                "SELECT * FROM {table} "
                "WHERE customer_id = 845;"
            ),
        )


def test_invalid_missing_read_query_placeholder():
    with pytest.raises(ValueError):
        build_experiment_definition(
            experiment_id="M18_001",
            index_name="m18_idx_orders_customer_id",
            table_name="orders",
            columns=["customer_id"],
            read_query=(
                "SELECT * FROM orders "
                "WHERE customer_id = 845;"
            ),
        )


def test_invalid_zero_read_iterations():
    with pytest.raises(ValueError):
        build_experiment_definition(
            experiment_id="M18_001",
            index_name="m18_idx_orders_customer_id",
            table_name="orders",
            columns=["customer_id"],
            read_query=(
                "SELECT * FROM {table} "
                "WHERE customer_id = 845;"
            ),
            read_iterations=0,
        )


# =========================================================
# READ QUERY RENDERING
# =========================================================

def test_render_read_query():
    experiment = make_experiment()

    query = render_read_query(
        experiment,
        "m18_orders_test",
    )

    assert "FROM m18_orders_test" in query
    assert "{table}" not in query
    assert "customer_id = 845" in query


def test_render_read_query_rejects_invalid_table():
    experiment = make_experiment()

    with pytest.raises(ValueError):
        render_read_query(
            experiment,
            "orders; DROP TABLE orders;",
        )


# =========================================================
# MEASUREMENT CONTRACT
# =========================================================

def test_measurement_contract():
    experiment = make_experiment()

    contract = build_measurement_contract(
        experiment
    )

    assert contract["experiment_id"] == "M18_001"

    assert contract["index_name"] == (
        "m18_idx_orders_customer_id"
    )

    assert contract["table_name"] == "orders"

    assert contract["write_table"] == "orders"

    assert contract["read_query_template"] == (
        "SELECT * FROM {table} "
        "WHERE customer_id = 845;"
    )

    assert contract["read"]["required"] is True
    assert contract["read"]["baseline_required"] is True
    assert contract["read"]["indexed_required"] is True

    assert contract["storage"]["required"] is True
    assert contract["storage"]["index_size_required"] is True
    assert contract["storage"]["table_size_required"] is True

    assert contract["write"]["required"] is True
    assert contract["write"]["baseline_required"] is True
    assert contract["write"]["indexed_required"] is True

    assert contract["linkage"]["same_experiment_required"] is True
    assert contract["linkage"]["same_index_required"] is True


# =========================================================
# LINKAGE
# =========================================================

def test_valid_measurement_linkage():
    records = [
        {
            "experiment_id": "M18_001",
            "index_name": "m18_idx_orders_customer_id",
        },
        {
            "experiment_id": "M18_001",
            "index_name": "m18_idx_orders_customer_id",
        },
        {
            "experiment_id": "M18_001",
            "index_name": "m18_idx_orders_customer_id",
        },
    ]

    assert verify_measurement_linkage(
        "M18_001",
        "m18_idx_orders_customer_id",
        records,
    )


def test_invalid_experiment_linkage():
    records = [
        {
            "experiment_id": "M18_001",
            "index_name": "m18_idx_orders_customer_id",
        },
        {
            "experiment_id": "M18_002",
            "index_name": "m18_idx_orders_customer_id",
        },
    ]

    assert not verify_measurement_linkage(
        "M18_001",
        "m18_idx_orders_customer_id",
        records,
    )


def test_invalid_index_linkage():
    records = [
        {
            "experiment_id": "M18_001",
            "index_name": "m18_idx_orders_customer_id",
        },
        {
            "experiment_id": "M18_001",
            "index_name": "different_index",
        },
    ]

    assert not verify_measurement_linkage(
        "M18_001",
        "m18_idx_orders_customer_id",
        records,
    )


# =========================================================
# LINKED RESULT
# =========================================================

def test_build_linked_result():
    experiment = make_experiment()

    read_evidence = {
        "experiment_id": "M18_001",
        "index_name": "m18_idx_orders_customer_id",
        "baseline": {
            "average_execution_time_ms": 10.0,
        },
        "indexed": {
            "average_execution_time_ms": 5.0,
        },
    }

    storage_evidence = {
        "experiment_id": "M18_001",
        "index_name": "m18_idx_orders_customer_id",
        "index_size_bytes": 100000,
        "table_size_bytes": 1000000,
        "index_table_ratio_percent": 10.0,
    }

    write_evidence = {
        "experiment_id": "M18_001",
        "index_name": "m18_idx_orders_customer_id",
        "baseline": {
            "average_execution_time_ms": 20.0,
        },
        "indexed": {
            "average_execution_time_ms": 22.0,
        },
    }

    result = build_linked_result(
        experiment,
        read_evidence,
        storage_evidence,
        write_evidence,
    )

    assert validate_linked_result(result)

    assert result["experiment_id"] == "M18_001"

    assert result["index_name"] == (
        "m18_idx_orders_customer_id"
    )

    assert result["table_name"] == "orders"

    assert result["columns"] == ["customer_id"]

    assert result["index_type"] == "BTREE"

    assert result["evidence_linked"] is True


def test_linked_result_rejects_mismatched_index():
    experiment = make_experiment()

    read_evidence = {
        "experiment_id": "M18_001",
        "index_name": "m18_idx_orders_customer_id",
    }

    storage_evidence = {
        "experiment_id": "M18_001",
        "index_name": "m18_idx_orders_customer_id",
    }

    write_evidence = {
        "experiment_id": "M18_001",
        "index_name": "wrong_index",
    }

    with pytest.raises(ValueError):
        build_linked_result(
            experiment,
            read_evidence,
            storage_evidence,
            write_evidence,
        )


def test_linked_result_preserves_identity():
    experiment = make_experiment()

    read_evidence = {
        "experiment_id": "M18_001",
        "index_name": "m18_idx_orders_customer_id",
    }

    storage_evidence = {
        "experiment_id": "M18_001",
        "index_name": "m18_idx_orders_customer_id",
    }

    write_evidence = {
        "experiment_id": "M18_001",
        "index_name": "m18_idx_orders_customer_id",
    }

    result = build_linked_result(
        experiment,
        read_evidence,
        storage_evidence,
        write_evidence,
    )

    assert result["experiment_id"] == (
        experiment["experiment_id"]
    )

    assert result["index_name"] == (
        experiment["index_name"]
    )

    assert result["table_name"] == (
        experiment["table_name"]
    )

    assert result["columns"] == (
        experiment["columns"]
    )
