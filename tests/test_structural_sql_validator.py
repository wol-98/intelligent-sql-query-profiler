"""
Tests for M21 dynamic SQL validation.
"""

from api.schemas.structural_optimization import (
    QueryValidationStatus,
)
from api.services.structural_sql_validator import (
    validate_sql,
)


# =========================================================
# INVALID INPUT
# =========================================================

def test_empty_sql_is_invalid():
    result = validate_sql("")

    assert result.status == QueryValidationStatus.INVALID


def test_whitespace_sql_is_invalid():
    result = validate_sql("   \n\t  ")

    assert result.status == QueryValidationStatus.INVALID


def test_malformed_sql_is_invalid():
    result = validate_sql(
        "THIS IS NOT SQL"
    )

    assert result.status == QueryValidationStatus.INVALID


# =========================================================
# VALID SUPPORTED SQL
# =========================================================

def test_simple_select_is_valid():
    result = validate_sql(
        "SELECT * FROM orders;"
    )

    assert result.status == QueryValidationStatus.VALID
    assert result.query_type == "SELECT"
    assert result.normalized_query is not None


def test_select_with_where_is_valid():
    result = validate_sql(
        """
        SELECT *
        FROM orders
        WHERE customer_id = 10;
        """
    )

    assert result.status == QueryValidationStatus.VALID
    assert result.query_type == "SELECT"


def test_cte_select_is_valid():
    result = validate_sql(
        """
        WITH recent_orders AS (
            SELECT *
            FROM orders
        )
        SELECT *
        FROM recent_orders;
        """
    )

    assert result.status == QueryValidationStatus.VALID
    assert result.query_type == "SELECT"


# =========================================================
# VALID BUT UNSUPPORTED SQL
# =========================================================

def test_insert_is_unsupported():
    result = validate_sql(
        """
        INSERT INTO orders
        (customer_id)
        VALUES (10);
        """
    )

    assert result.status == QueryValidationStatus.UNSUPPORTED
    assert result.query_type == "INSERT"


def test_update_is_unsupported():
    result = validate_sql(
        """
        UPDATE orders
        SET status = 'Completed'
        WHERE order_id = 1;
        """
    )

    assert result.status == QueryValidationStatus.UNSUPPORTED
    assert result.query_type == "UPDATE"


def test_delete_is_unsupported():
    result = validate_sql(
        """
        DELETE FROM orders
        WHERE order_id = 1;
        """
    )

    assert result.status == QueryValidationStatus.UNSUPPORTED
    assert result.query_type == "DELETE"


def test_create_table_is_unsupported():
    result = validate_sql(
        """
        CREATE TABLE test_table (
            id INTEGER
        );
        """
    )

    assert result.status == QueryValidationStatus.UNSUPPORTED


# =========================================================
# MULTIPLE STATEMENTS
# =========================================================

def test_multiple_statements_are_unsupported():
    result = validate_sql(
        """
        SELECT * FROM orders;
        SELECT * FROM customers;
        """
    )

    assert result.status == QueryValidationStatus.UNSUPPORTED
    assert result.query_type is None


# =========================================================
# COMMENTS
# =========================================================

def test_comments_around_select_are_supported():
    result = validate_sql(
        """
        -- Read recent orders
        SELECT *
        FROM orders;
        """
    )

    assert result.status == QueryValidationStatus.VALID
    assert result.query_type == "SELECT"
