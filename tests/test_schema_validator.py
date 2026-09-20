"""
Tests for M21 schema/table and column validation.
"""

from unittest.mock import patch

from sqlglot import parse_one

from api.services.schema_introspector import (
    SchemaIntrospector,
)
from api.services.schema_validator import (
    ColumnReference,
    TableReference,
    extract_column_references,
    extract_table_references,
    validate_columns,
    validate_tables,
)


def test_extract_single_table():
    expression = parse_one(
        "SELECT * FROM orders",
        dialect="postgres",
    )

    references = extract_table_references(expression)

    assert references == (
        TableReference(
            schema="public",
            table="orders",
            alias=None,
        ),
    )


def test_extract_table_with_alias():
    expression = parse_one(
        "SELECT * FROM orders o",
        dialect="postgres",
    )

    references = extract_table_references(expression)

    assert references == (
        TableReference(
            schema="public",
            table="orders",
            alias="o",
        ),
    )


def test_extract_multiple_tables():
    expression = parse_one(
        """
        SELECT *
        FROM orders o
        JOIN customers c
          ON o.customer_id = c.customer_id
        """,
        dialect="postgres",
    )

    references = extract_table_references(expression)

    assert references == (
        TableReference(
            schema="public",
            table="orders",
            alias="o",
        ),
        TableReference(
            schema="public",
            table="customers",
            alias="c",
        ),
    )


def test_cte_reference_is_not_treated_as_physical_table():
    expression = parse_one(
        """
        WITH recent AS (
            SELECT *
            FROM orders
        )
        SELECT *
        FROM recent;
        """,
        dialect="postgres",
    )

    references = extract_table_references(expression)

    assert references == (
        TableReference(
            schema="public",
            table="orders",
            alias=None,
        ),
    )


def test_schema_qualified_table_is_preserved():
    expression = parse_one(
        """
        SELECT *
        FROM public.orders;
        """,
        dialect="postgres",
    )

    references = extract_table_references(expression)

    assert references == (
        TableReference(
            schema="public",
            table="orders",
            alias=None,
        ),
    )


def test_duplicate_table_references_are_preserved_when_aliases_differ():
    expression = parse_one(
        """
        SELECT *
        FROM orders o
        JOIN orders o2
          ON o.customer_id = o2.customer_id;
        """,
        dialect="postgres",
    )

    references = extract_table_references(expression)

    assert len(references) == 2


def test_extract_unqualified_column():
    expression = parse_one(
        """
        SELECT customer_id
        FROM orders;
        """,
        dialect="postgres",
    )

    references = extract_column_references(expression)

    assert references == (
        ColumnReference(
            name="customer_id",
            table=None,
            schema=None,
        ),
    )


def test_extract_qualified_column():
    expression = parse_one(
        """
        SELECT orders.customer_id
        FROM orders;
        """,
        dialect="postgres",
    )

    references = extract_column_references(expression)

    assert references == (
        ColumnReference(
            name="customer_id",
            table="orders",
            schema=None,
        ),
    )


def test_extract_join_columns():
    expression = parse_one(
        """
        SELECT o.customer_id, c.name
        FROM orders o
        JOIN customers c
          ON o.customer_id = c.customer_id;
        """,
        dialect="postgres",
    )

    references = extract_column_references(expression)

    assert references == (
        ColumnReference(
            name="customer_id",
            table="o",
            schema=None,
        ),
        ColumnReference(
            name="name",
            table="c",
            schema=None,
        ),
        ColumnReference(
            name="customer_id",
            table="o",
            schema=None,
        ),
        ColumnReference(
            name="customer_id",
            table="c",
            schema=None,
        ),
    )


def test_existing_unqualified_column_is_valid():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT customer_id
        FROM orders;
        """,
        dialect="postgres",
    )

    with patch.object(
        introspector,
        "get_table",
        wraps=introspector.get_table,
    ):
        columns, missing, ambiguous = validate_columns(
            expression,
            introspector,
        )

    assert missing == ()
    assert ambiguous == ()
    assert columns[0].exists is True
    assert columns[0].resolved_table == "orders"


def test_missing_column_is_detected():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT category_id
        FROM orders;
        """,
        dialect="postgres",
    )

    columns, missing, ambiguous = validate_columns(
        expression,
        introspector,
    )

    assert columns[0].exists is False
    assert missing == ("category_id",)
    assert ambiguous == ()


def test_qualified_column_is_resolved_through_alias():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT o.customer_id
        FROM orders o;
        """,
        dialect="postgres",
    )

    columns, missing, ambiguous = validate_columns(
        expression,
        introspector,
    )

    assert columns[0].exists is True
    assert columns[0].resolved_table == "o"
    assert missing == ()
    assert ambiguous == ()


def test_qualified_missing_column_is_detected():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT o.category_id
        FROM orders o;
        """,
        dialect="postgres",
    )

    columns, missing, ambiguous = validate_columns(
        expression,
        introspector,
    )

    assert columns[0].exists is False
    assert missing == ("o.category_id",)
    assert ambiguous == ()


def test_join_columns_resolve_through_aliases():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT o.customer_id, c.name
        FROM orders o
        JOIN customers c
          ON o.customer_id = c.customer_id;
        """,
        dialect="postgres",
    )

    columns, missing, ambiguous = validate_columns(
        expression,
        introspector,
    )

    assert all(column.exists for column in columns)
    assert missing == ()
    assert ambiguous == ()


def test_ambiguous_unqualified_column_is_detected():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT customer_id
        FROM orders o
        JOIN customers c
          ON o.customer_id = c.customer_id;
        """,
        dialect="postgres",
    )

    columns, missing, ambiguous = validate_columns(
        expression,
        introspector,
    )

    assert columns[0].ambiguous is True
    assert columns[0].exists is False
    assert missing == ()
    assert ambiguous == ("customer_id",)


def test_cte_output_column_is_resolved():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        WITH recent AS (
            SELECT customer_id, order_date
            FROM orders
        )
        SELECT customer_id, order_date
        FROM recent;
        """,
        dialect="postgres",
    )

    columns, missing, ambiguous = validate_columns(
        expression,
        introspector,
    )

    assert all(column.exists for column in columns)
    assert missing == ()
    assert ambiguous == ()


def test_wildcard_is_not_treated_as_missing_column():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT *
        FROM orders;
        """,
        dialect="postgres",
    )

    columns, missing, ambiguous = validate_columns(
        expression,
        introspector,
    )

    assert columns == ()
    assert missing == ()
    assert ambiguous == ()


def test_count_star_is_not_treated_as_missing_column():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT COUNT(*)
        FROM orders;
        """,
        dialect="postgres",
    )

    columns, missing, ambiguous = validate_columns(
        expression,
        introspector,
    )

    assert columns == ()
    assert missing == ()
    assert ambiguous == ()


def test_full_schema_validation_is_valid():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT o.customer_id, c.name
        FROM orders o
        JOIN customers c
          ON o.customer_id = c.customer_id;
        """,
        dialect="postgres",
    )

    with patch.object(
        introspector,
        "table_exists",
        return_value=True,
    ):
        result = validate_tables(
            expression,
            introspector=introspector,
        )

    assert result.valid is True
    assert result.missing_tables == ()
    assert result.missing_columns == ()
    assert result.ambiguous_columns == ()


def test_full_schema_validation_detects_missing_table():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT *
        FROM completely_fake_table;
        """,
        dialect="postgres",
    )

    with patch.object(
        introspector,
        "table_exists",
        return_value=False,
    ):
        result = validate_tables(
            expression,
            introspector=introspector,
        )

    assert result.valid is False
    assert result.missing_tables == (
        "public.completely_fake_table",
    )


def test_full_schema_validation_detects_missing_column():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT category_id
        FROM orders;
        """,
        dialect="postgres",
    )

    with patch.object(
        introspector,
        "table_exists",
        return_value=True,
    ):
        result = validate_tables(
            expression,
            introspector=introspector,
        )

    assert result.valid is False
    assert result.missing_tables == ()
    assert result.missing_columns == (
        "category_id",
    )


def test_full_schema_validation_detects_ambiguous_column():
    introspector = SchemaIntrospector()

    expression = parse_one(
        """
        SELECT customer_id
        FROM orders o
        JOIN customers c
          ON o.customer_id = c.customer_id;
        """,
        dialect="postgres",
    )

    with patch.object(
        introspector,
        "table_exists",
        return_value=True,
    ):
        result = validate_tables(
            expression,
            introspector=introspector,
        )

    assert result.valid is False
    assert result.missing_tables == ()
    assert result.ambiguous_columns == (
        "customer_id",
    )
