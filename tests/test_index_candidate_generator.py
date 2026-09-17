"""
Unit tests for the Index Candidate Generator.
"""

from unittest.mock import patch

from collector.index_candidate_generator import (
    resolve_column_reference,
    generate_index_candidates,
    get_indexed_columns,
    column_has_index,
)


# =========================================================
# RESOLVE COLUMN REFERENCE
# =========================================================

def test_resolve_qualified_column_reference():
    aliases = {
        "oi": "order_items",
        "p": "products",
    }

    table, column = resolve_column_reference(
        "p.category_id",
        aliases,
        ["order_items", "products"],
    )

    assert table == "products"
    assert column == "category_id"


def test_resolve_unqualified_column_single_table():
    aliases = {}

    table, column = resolve_column_reference(
        "customer_id",
        aliases,
        ["customers"],
    )

    assert table == "customers"
    assert column == "customer_id"


def test_resolve_ambiguous_unqualified_column():
    aliases = {
        "o": "orders",
        "c": "customers",
    }

    table, column = resolve_column_reference(
        "customer_id",
        aliases,
        ["orders", "customers"],
    )

    assert table is None
    assert column == "customer_id"


def test_resolve_unknown_alias():
    aliases = {
        "oi": "order_items",
    }

    table, column = resolve_column_reference(
        "p.category_id",
        aliases,
        ["order_items", "products"],
    )

    assert table is None
    assert column == "category_id"


# =========================================================
# CANDIDATE GENERATION
# =========================================================

@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_generate_where_candidate(mock_column_has_index):
    query_metadata = {
        "tables": ["products"],
        "aliases": {"p": "products"},
        "where_columns": ["p.category_id"],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    assert len(candidates) == 1
    assert candidates[0]["table_name"] == "products"
    assert candidates[0]["column_name"] == "category_id"
    assert candidates[0]["index_type"] == "B-tree"
    assert candidates[0]["reason"] == "Filter condition"
    assert candidates[0]["source"] == "p.category_id"

    mock_column_has_index.assert_called_once_with(
        "products",
        "category_id",
    )


@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_generate_join_candidates(mock_column_has_index):
    query_metadata = {
        "tables": ["orders", "customers"],
        "aliases": {
            "o": "orders",
            "c": "customers",
        },
        "where_columns": [],
        "join_columns": [
            "o.customer_id",
            "c.customer_id",
        ],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    assert len(candidates) == 2

    assert candidates[0]["table_name"] == "orders"
    assert candidates[0]["column_name"] == "customer_id"
    assert candidates[0]["reason"] == "Join condition"

    assert candidates[1]["table_name"] == "customers"
    assert candidates[1]["column_name"] == "customer_id"
    assert candidates[1]["reason"] == "Join condition"


@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_generate_order_by_candidate(mock_column_has_index):
    query_metadata = {
        "tables": ["orders"],
        "aliases": {"o": "orders"},
        "where_columns": [],
        "join_columns": [],
        "order_by_columns": ["o.order_date"],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    assert len(candidates) == 1
    assert candidates[0]["table_name"] == "orders"
    assert candidates[0]["column_name"] == "order_date"
    assert candidates[0]["reason"] == "ORDER BY"


@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_generate_group_by_candidate(mock_column_has_index):
    query_metadata = {
        "tables": ["products"],
        "aliases": {"p": "products"},
        "where_columns": [],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": ["p.category_id"],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    assert len(candidates) == 1
    assert candidates[0]["table_name"] == "products"
    assert candidates[0]["column_name"] == "category_id"
    assert candidates[0]["reason"] == "GROUP BY"


# =========================================================
# DUPLICATE PREVENTION
# =========================================================

@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_duplicate_table_column_generates_one_candidate(
    mock_column_has_index,
):
    query_metadata = {
        "tables": ["orders"],
        "aliases": {"o": "orders"},
        "where_columns": ["o.customer_id"],
        "join_columns": ["o.customer_id"],
        "order_by_columns": ["o.customer_id"],
        "group_by_columns": ["o.customer_id"],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    assert len(candidates) == 1

    assert candidates[0]["table_name"] == "orders"
    assert candidates[0]["column_name"] == "customer_id"


# =========================================================
# EXISTING INDEX EXCLUSION
# =========================================================

@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=True,
)
def test_existing_index_excludes_candidate(
    mock_column_has_index,
):
    query_metadata = {
        "tables": ["products"],
        "aliases": {"p": "products"},
        "where_columns": ["p.category_id"],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    assert candidates == []

    mock_column_has_index.assert_called_once_with(
        "products",
        "category_id",
    )


# =========================================================
# INVALID REFERENCES
# =========================================================

@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_invalid_column_reference_is_not_added(
    mock_column_has_index,
):
    query_metadata = {
        "tables": ["orders", "customers"],
        "aliases": {
            "o": "orders",
            "c": "customers",
        },
        "where_columns": ["customer_id"],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    assert candidates == []
    mock_column_has_index.assert_not_called()


# =========================================================
# CANDIDATE STRUCTURE
# =========================================================

@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_candidate_contains_expected_fields(
    mock_column_has_index,
):
    query_metadata = {
        "tables": ["products"],
        "aliases": {"p": "products"},
        "where_columns": ["p.category_id"],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert set(candidate.keys()) == {
        "table_name",
        "column_name",
        "index_type",
        "reason",
        "source",
    }


# =========================================================
# INDEX DEFINITION PARSING
# =========================================================

def test_get_indexed_columns_single_column():
    definition = (
        "CREATE UNIQUE INDEX customers_pkey "
        "ON public.customers USING btree (customer_id)"
    )

    assert get_indexed_columns(definition) == [
        "customer_id"
    ]


def test_get_indexed_columns_composite_index():
    definition = (
        "CREATE INDEX idx_orders_customer_date "
        "ON public.orders USING btree "
        "(customer_id, order_date)"
    )

    assert get_indexed_columns(definition) == [
        "customer_id",
        "order_date",
    ]


def test_get_indexed_columns_preserves_column_order():
    definition = (
        "CREATE INDEX idx_orders_date_customer "
        "ON public.orders USING btree "
        "(order_date, customer_id)"
    )

    assert get_indexed_columns(definition) == [
        "order_date",
        "customer_id",
    ]


def test_get_indexed_columns_returns_empty_for_invalid_definition():
    assert get_indexed_columns("") == []


# =========================================================
# EXISTING INDEX COVERAGE
# =========================================================

@patch(
    "collector.index_candidate_generator.get_existing_indexes"
)
def test_column_has_index_single_column(
    mock_get_existing_indexes,
):
    mock_get_existing_indexes.return_value = [
        {
            "index_name": "customers_pkey",
            "index_definition": (
                "CREATE UNIQUE INDEX customers_pkey "
                "ON public.customers USING btree "
                "(customer_id)"
            ),
        }
    ]

    assert column_has_index(
        "customers",
        "customer_id",
    ) is True

    assert column_has_index(
        "customers",
        "city",
    ) is False


@patch(
    "collector.index_candidate_generator.get_existing_indexes"
)
def test_column_has_index_composite_leftmost_column(
    mock_get_existing_indexes,
):
    mock_get_existing_indexes.return_value = [
        {
            "index_name": "idx_orders_customer_date",
            "index_definition": (
                "CREATE INDEX idx_orders_customer_date "
                "ON public.orders USING btree "
                "(customer_id, order_date)"
            ),
        }
    ]

    assert column_has_index(
        "orders",
        "customer_id",
    ) is True


@patch(
    "collector.index_candidate_generator.get_existing_indexes"
)
def test_column_has_index_composite_non_leftmost_column(
    mock_get_existing_indexes,
):
    mock_get_existing_indexes.return_value = [
        {
            "index_name": "idx_orders_customer_date",
            "index_definition": (
                "CREATE INDEX idx_orders_customer_date "
                "ON public.orders USING btree "
                "(customer_id, order_date)"
            ),
        }
    ]

    assert column_has_index(
        "orders",
        "order_date",
    ) is False
