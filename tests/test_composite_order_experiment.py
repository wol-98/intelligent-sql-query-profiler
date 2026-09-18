"""
Unit tests for the Composite Index Column-Order Experiment.
"""

from collector.composite_order_experiment import (
    is_eligible_composite_candidate,
    build_alternative_column_order,
    build_order_experiment,
    build_order_experiments,
)


# =========================================================
# ELIGIBILITY
# =========================================================

def test_single_column_candidate_is_ineligible():

    candidate = {
        "table_name": "orders",
        "column_name": "customer_id",
        "candidate_type": "single",
        "column_count": 1,
    }

    assert (
        is_eligible_composite_candidate(candidate)
        is False
    )


def test_two_column_composite_is_eligible():

    candidate = {
        "table_name": "orders",
        "column_name": "customer_id, status",
        "candidate_type": "composite",
        "column_count": 2,
    }

    assert (
        is_eligible_composite_candidate(candidate)
        is True
    )


def test_three_column_composite_is_eligible():

    candidate = {
        "table_name": "orders",
        "column_name": (
            "customer_id, status, order_date"
        ),
        "candidate_type": "composite",
        "column_count": 3,
    }

    assert (
        is_eligible_composite_candidate(candidate)
        is True
    )


def test_four_column_composite_is_ineligible():

    candidate = {
        "table_name": "orders",
        "column_name": (
            "customer_id, status, "
            "order_date, total_amount"
        ),
        "candidate_type": "composite",
        "column_count": 4,
    }

    assert (
        is_eligible_composite_candidate(candidate)
        is False
    )


def test_inconsistent_column_count_is_ineligible():

    candidate = {
        "table_name": "orders",
        "column_name": "customer_id, status",
        "candidate_type": "composite",
        "column_count": 3,
    }

    assert (
        is_eligible_composite_candidate(candidate)
        is False
    )


# =========================================================
# ALTERNATIVE ORDER
# =========================================================

def test_two_column_order_is_reversed():

    result = build_alternative_column_order(
        "customer_id, status"
    )

    assert result == [
        "status",
        "customer_id",
    ]


def test_three_column_order_is_reversed():

    result = build_alternative_column_order(
        "customer_id, status, order_date"
    )

    assert result == [
        "order_date",
        "status",
        "customer_id",
    ]


def test_invalid_width_returns_empty_list():

    result = build_alternative_column_order(
        "a, b, c, d"
    )

    assert result == []


# =========================================================
# EXPERIMENT RECORD
# =========================================================

def test_experiment_record_preserves_original_candidate():

    candidate = {
        "recommendation_id": 10,
        "query_id": "Q001",
        "fingerprint": "abc123",
        "table_name": "orders",
        "column_name": "customer_id, status",
        "candidate_type": "composite",
        "source_type": "where",
        "column_count": 2,
    }

    result = build_order_experiment(
        candidate
    )

    assert result is not None

    assert result["recommendation_id"] == 10
    assert result["query_id"] == "Q001"
    assert result["fingerprint"] == "abc123"
    assert result["table_name"] == "orders"

    assert result["original_columns"] == [
        "customer_id",
        "status",
    ]

    assert result["alternative_columns"] == [
        "status",
        "customer_id",
    ]

    assert result["experiment_type"] == "column_order"


def test_ineligible_candidate_produces_no_experiment():

    candidate = {
        "table_name": "orders",
        "column_name": "customer_id",
        "candidate_type": "single",
        "column_count": 1,
    }

    assert (
        build_order_experiment(candidate)
        is None
    )


# =========================================================
# BATCH EXPERIMENT GENERATION
# =========================================================

def test_batch_generation_excludes_ineligible_candidates():

    candidates = [
        {
            "table_name": "orders",
            "column_name": "customer_id",
            "candidate_type": "single",
            "column_count": 1,
        },
        {
            "table_name": "orders",
            "column_name": "customer_id, status",
            "candidate_type": "composite",
            "column_count": 2,
        },
    ]

    results = build_order_experiments(
        candidates
    )

    assert len(results) == 1

    assert results[0]["original_columns"] == [
        "customer_id",
        "status",
    ]


def test_batch_generation_does_not_modify_input():

    candidates = [
        {
            "table_name": "orders",
            "column_name": "customer_id, status",
            "candidate_type": "composite",
            "column_count": 2,
        }
    ]

    original = candidates[0]["column_name"]

    build_order_experiments(
        candidates
    )

    assert (
        candidates[0]["column_name"]
        == original
    )
