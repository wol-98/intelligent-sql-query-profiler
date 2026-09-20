"""
Tests for M21 schema introspection.
"""

from unittest.mock import MagicMock, patch

from api.services.schema_introspector import (
    ColumnMetadata,
    SchemaIntrospector,
    TableMetadata,
)


def make_connection(rows):
    """Create a mocked database connection."""

    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = rows

    return connection


def test_get_tables_returns_structured_metadata():
    rows = [
        ("public", "customers", "customer_id", "integer", 1),
        ("public", "customers", "name", "character varying", 2),
        ("public", "orders", "order_id", "integer", 1),
        ("public", "orders", "customer_id", "integer", 2),
        ("public", "orders", "status", "character varying", 4),
    ]

    connection = make_connection(rows)

    with patch(
        "api.services.schema_introspector.get_connection",
        return_value=connection,
    ):
        tables = SchemaIntrospector().get_tables()

    assert tables == (
        TableMetadata(
            schema="public",
            name="customers",
            columns=(
                ColumnMetadata(
                    name="customer_id",
                    data_type="integer",
                    ordinal_position=1,
                ),
                ColumnMetadata(
                    name="name",
                    data_type="character varying",
                    ordinal_position=2,
                ),
            ),
        ),
        TableMetadata(
            schema="public",
            name="orders",
            columns=(
                ColumnMetadata(
                    name="order_id",
                    data_type="integer",
                    ordinal_position=1,
                ),
                ColumnMetadata(
                    name="customer_id",
                    data_type="integer",
                    ordinal_position=2,
                ),
                ColumnMetadata(
                    name="status",
                    data_type="character varying",
                    ordinal_position=4,
                ),
            ),
        ),
    )


def test_table_exists_is_case_insensitive():
    rows = [
        ("public", "orders", "order_id", "integer", 1),
    ]

    connection = make_connection(rows)

    with patch(
        "api.services.schema_introspector.get_connection",
        return_value=connection,
    ):
        introspector = SchemaIntrospector()

        assert introspector.table_exists("orders") is True
        assert introspector.table_exists("ORDERS") is True
        assert introspector.table_exists("Orders") is True


def test_table_exists_returns_false_for_missing_table():
    rows = [
        ("public", "orders", "order_id", "integer", 1),
    ]

    connection = make_connection(rows)

    with patch(
        "api.services.schema_introspector.get_connection",
        return_value=connection,
    ):
        introspector = SchemaIntrospector()

        assert introspector.table_exists("products") is False


def test_column_exists_is_case_insensitive():
    rows = [
        ("public", "orders", "customer_id", "integer", 1),
        ("public", "orders", "status", "character varying", 2),
    ]

    connection = make_connection(rows)

    with patch(
        "api.services.schema_introspector.get_connection",
        return_value=connection,
    ):
        introspector = SchemaIntrospector()

        assert introspector.column_exists(
            "orders",
            "customer_id",
        ) is True

        assert introspector.column_exists(
            "ORDERS",
            "CUSTOMER_ID",
        ) is True


def test_column_exists_returns_false_for_missing_column():
    rows = [
        ("public", "orders", "customer_id", "integer", 1),
    ]

    connection = make_connection(rows)

    with patch(
        "api.services.schema_introspector.get_connection",
        return_value=connection,
    ):
        introspector = SchemaIntrospector()

        assert introspector.column_exists(
            "orders",
            "category",
        ) is False


def test_missing_table_returns_false_for_column_lookup():
    rows = [
        ("public", "orders", "customer_id", "integer", 1),
    ]

    connection = make_connection(rows)

    with patch(
        "api.services.schema_introspector.get_connection",
        return_value=connection,
    ):
        introspector = SchemaIntrospector()

        assert introspector.column_exists(
            "products",
            "category_id",
        ) is False
