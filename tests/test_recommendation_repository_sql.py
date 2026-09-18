"""
Recommendation Repository SQL Tests
------------------------------------
Tests index-name generation and CREATE INDEX
SQL generation for single-column and composite
index candidates.
"""

import pytest

from collector.recommendation_repository import (
    generate_index_name,
    generate_index_sql,
    normalize_index_name_part,
)


# =========================================================
# NORMALIZATION TESTS
# =========================================================

def test_normalize_single_column_name():

    result = normalize_index_name_part(
        "customer_id"
    )

    assert result == "customer_id"


def test_normalize_composite_column_name():

    result = normalize_index_name_part(
        "customer_id, status"
    )

    assert result == "customer_id_status"


def test_normalize_multiple_composite_columns():

    result = normalize_index_name_part(
        "segment, customer_id, name"
    )

    assert result == (
        "segment_customer_id_name"
    )


# =========================================================
# INDEX NAME TESTS
# =========================================================

def test_generate_single_column_index_name():

    result = generate_index_name(
        "orders",
        "customer_id"
    )

    assert result == (
        "idx_orders_customer_id"
    )


def test_generate_two_column_index_name():

    result = generate_index_name(
        "orders",
        "customer_id, status"
    )

    assert result == (
        "idx_orders_customer_id_status"
    )


def test_generate_three_column_index_name():

    result = generate_index_name(
        "customers",
        "segment, customer_id, name"
    )

    assert result == (
        "idx_customers_segment_customer_id_name"
    )


def test_index_name_contains_no_spaces():

    result = generate_index_name(
        "orders",
        "customer_id, status"
    )

    assert " " not in result


def test_index_name_contains_no_commas():

    result = generate_index_name(
        "orders",
        "customer_id, status"
    )

    assert "," not in result


# =========================================================
# SQL GENERATION TESTS
# =========================================================

def test_generate_single_column_btree_sql():

    result = generate_index_sql(
        "orders",
        "customer_id"
    )

    assert result == (
        "CREATE INDEX idx_orders_customer_id "
        "ON orders USING BTREE "
        "(customer_id);"
    )


def test_generate_two_column_composite_btree_sql():

    result = generate_index_sql(
        "orders",
        "customer_id, status"
    )

    assert result == (
        "CREATE INDEX idx_orders_customer_id_status "
        "ON orders USING BTREE "
        "(customer_id, status);"
    )


def test_generate_three_column_composite_btree_sql():

    result = generate_index_sql(
        "customers",
        "segment, customer_id, name"
    )

    assert result == (
        "CREATE INDEX "
        "idx_customers_segment_customer_id_name "
        "ON customers USING BTREE "
        "(segment, customer_id, name);"
    )


def test_composite_sql_preserves_column_order():

    result = generate_index_sql(
        "orders",
        "status, customer_id"
    )

    assert result == (
        "CREATE INDEX idx_orders_status_customer_id "
        "ON orders USING BTREE "
        "(status, customer_id);"
    )


# =========================================================
# VALIDATION TESTS
# =========================================================

def test_unsupported_index_type_raises_error():

    with pytest.raises(
        ValueError,
        match="Unsupported index type"
    ):

        generate_index_sql(
            "orders",
            "customer_id",
            "Hash"
        )


def test_btree_variants_are_supported():

    expected = (
        "CREATE INDEX idx_orders_customer_id "
        "ON orders USING BTREE "
        "(customer_id);"
    )

    assert generate_index_sql(
        "orders",
        "customer_id",
        "B-tree"
    ) == expected

    assert generate_index_sql(
        "orders",
        "customer_id",
        "btree"
    ) == expected

    assert generate_index_sql(
        "orders",
        "customer_id",
        "B TREE"
    ) == expected


# =========================================================
# INDEX NAME LENGTH TEST
# =========================================================

def test_index_name_is_limited_to_postgresql_identifier_length():

    long_table_name = (
        "this_is_a_very_long_table_name_"
        "that_exceeds_normal_identifier_length"
    )

    long_column_name = (
        "this_is_a_very_long_column_name_"
        "that_exceeds_normal_identifier_length"
    )

    result = generate_index_name(
        long_table_name,
        long_column_name
    )

    assert len(result) <= 63
