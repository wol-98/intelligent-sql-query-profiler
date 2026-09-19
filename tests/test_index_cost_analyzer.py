"""
Tests for M17.1 — Index Cost Metadata.
"""

from unittest.mock import MagicMock, patch

import pytest

from collector.index_cost_analyzer import (
    calculate_index_table_ratio,
    get_index_metadata,
    get_index_size,
    get_table_size,
)


# =========================================================
# RATIO
# =========================================================

def test_calculate_index_table_ratio():
    ratio = calculate_index_table_ratio(
        50,
        1000,
    )

    assert ratio == pytest.approx(5.0)


def test_calculate_index_table_ratio_zero_table():
    ratio = calculate_index_table_ratio(
        50,
        0,
    )

    assert ratio == 0.0


# =========================================================
# TABLE SIZE
# =========================================================

@patch(
    "collector.index_cost_analyzer.get_connection"
)
def test_get_table_size(mock_get_connection):

    connection = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = (
        102400,
        "100 kB",
    )

    connection.cursor.return_value = cursor
    mock_get_connection.return_value = connection

    result = get_table_size(
        "orders"
    )

    assert result["table_name"] == "orders"
    assert result["size_bytes"] == 102400
    assert result["size_pretty"] == "100 kB"

    cursor.close.assert_called_once()
    connection.close.assert_called_once()


# =========================================================
# INDEX SIZE
# =========================================================

@patch(
    "collector.index_cost_analyzer.get_connection"
)
def test_get_index_size(mock_get_connection):

    connection = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = (
        8192,
        "8192 bytes",
    )

    connection.cursor.return_value = cursor
    mock_get_connection.return_value = connection

    result = get_index_size(
        "idx_orders_customer_id"
    )

    assert result["index_name"] == (
        "idx_orders_customer_id"
    )

    assert result["size_bytes"] == 8192
    assert result["size_pretty"] == "8192 bytes"


# =========================================================
# INDEX METADATA
# =========================================================

@patch(
    "collector.index_cost_analyzer.get_connection"
)
def test_get_index_metadata(mock_get_connection):

    connection = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = (
        "idx_orders_customer_status",
        "orders",
        "btree",
        False,
        False,
        True,
        [
            "customer_id",
            "status",
        ],
        2,
        16384,
        "16 kB",
    )

    connection.cursor.return_value = cursor
    mock_get_connection.return_value = connection

    result = get_index_metadata(
        "idx_orders_customer_status"
    )

    assert result["index_name"] == (
        "idx_orders_customer_status"
    )

    assert result["table_name"] == "orders"

    assert result["index_type"] == "btree"

    assert result["columns"] == [
        "customer_id",
        "status",
    ]

    assert result["column_count"] == 2

    assert result["is_unique"] is False
    assert result["is_primary"] is False
    assert result["is_valid"] is True

    assert result["size_bytes"] == 16384
    assert result["size_pretty"] == "16 kB"


@patch(
    "collector.index_cost_analyzer.get_connection"
)
def test_get_index_metadata_not_found(
    mock_get_connection
):

    connection = MagicMock()
    cursor = MagicMock()

    cursor.fetchone.return_value = None

    connection.cursor.return_value = cursor
    mock_get_connection.return_value = connection

    result = get_index_metadata(
        "missing_index"
    )

    assert result is None


# =========================================================
# VALIDATION
# =========================================================

def test_get_table_size_rejects_invalid_identifier():

    with pytest.raises(ValueError):
        get_table_size(
            "orders; DROP TABLE customers"
        )


def test_get_index_size_rejects_invalid_identifier():

    with pytest.raises(ValueError):
        get_index_size(
            "index; DROP TABLE orders"
        )


def test_get_index_metadata_rejects_invalid_identifier():

    with pytest.raises(ValueError):
        get_index_metadata(
            "index-name"
        )
