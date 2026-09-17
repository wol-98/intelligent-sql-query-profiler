"""
Unit tests for the Index Candidate Generator.
"""


from unittest.mock import patch


from collector.index_candidate_generator import (
    resolve_column_reference,
    generate_index_candidates,
    get_indexed_columns,
    column_has_index,
    normalize_candidate_columns,
    classify_candidate_relationship,
    candidate_is_redundant,
    determine_candidate_type,
    determine_source_type,
    build_candidate_metadata,
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


def test_resolve_empty_reference():

    table, column = resolve_column_reference(
        "",
        {},
        [],
    )

    assert table is None
    assert column is None


# =========================================================
# CANDIDATE GENERATION
# =========================================================

@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_generate_where_candidate(
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

    assert candidates[0]["table_name"] == "products"
    assert candidates[0]["column_name"] == "category_id"
    assert candidates[0]["index_type"] == "B-tree"
    assert candidates[0]["reason"] == "Filter condition"
    assert candidates[0]["source"] == "p.category_id"

    assert candidates[0]["candidate_type"] == "single"
    assert candidates[0]["source_type"] == "where"
    assert candidates[0]["column_count"] == 1

    mock_column_has_index.assert_called_once_with(
        "products",
        "category_id",
    )


@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_generate_join_candidates(
    mock_column_has_index,
):

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
    assert candidates[0]["candidate_type"] == "single"
    assert candidates[0]["source_type"] == "join"

    assert candidates[1]["table_name"] == "customers"
    assert candidates[1]["column_name"] == "customer_id"
    assert candidates[1]["reason"] == "Join condition"
    assert candidates[1]["candidate_type"] == "single"
    assert candidates[1]["source_type"] == "join"


@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_generate_order_by_candidate(
    mock_column_has_index,
):

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
    assert candidates[0]["source_type"] == "order_by"


@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_generate_group_by_candidate(
    mock_column_has_index,
):

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
    assert candidates[0]["source_type"] == "group_by"


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
        "candidate_type",
        "source_type",
        "column_count",
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


# =========================================================
# COMPOSITE INDEX CANDIDATES
# =========================================================

@patch(
    "collector.index_candidate_generator.get_existing_indexes",
    return_value=[],
)
@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_generate_composite_where_candidate(
    mock_column_has_index,
    mock_get_existing_indexes,
):

    query_metadata = {
        "tables": ["orders"],
        "aliases": {
            "o": "orders",
        },
        "where_columns": [
            "o.customer_id",
            "o.order_date",
        ],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    composite_candidates = [
        candidate
        for candidate in candidates
        if "," in candidate["column_name"]
    ]

    assert len(composite_candidates) == 1

    candidate = composite_candidates[0]

    assert candidate["table_name"] == "orders"
    assert candidate["column_name"] == (
        "customer_id, order_date"
    )
    assert candidate["index_type"] == "B-tree"
    assert candidate["reason"] == (
        "Composite filter/order pattern"
    )
    assert candidate["source"] == (
        "customer_id, order_date"
    )

    assert candidate["candidate_type"] == "composite"
    assert candidate["source_type"] == "where"
    assert candidate["column_count"] == 2


@patch(
    "collector.index_candidate_generator.get_existing_indexes",
    return_value=[],
)
@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_composite_candidate_preserves_column_order(
    mock_column_has_index,
    mock_get_existing_indexes,
):

    query_metadata = {
        "tables": ["orders"],
        "aliases": {
            "o": "orders",
        },
        "where_columns": [
            "o.customer_id",
            "o.order_date",
        ],
        "join_columns": [],
        "order_by_columns": [
            "o.order_id",
        ],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    composite_candidates = [
        candidate
        for candidate in candidates
        if "," in candidate["column_name"]
    ]

    assert len(composite_candidates) == 1

    assert composite_candidates[0]["column_name"] == (
        "customer_id, order_date, order_id"
    )

    assert composite_candidates[0]["candidate_type"] == (
        "composite"
    )

    assert composite_candidates[0]["source_type"] == (
        "mixed"
    )

    assert composite_candidates[0]["column_count"] == 3


@patch(
    "collector.index_candidate_generator.get_existing_indexes",
    return_value=[],
)
@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_composite_candidate_does_not_mix_tables(
    mock_column_has_index,
    mock_get_existing_indexes,
):

    query_metadata = {
        "tables": [
            "orders",
            "customers",
        ],
        "aliases": {
            "o": "orders",
            "c": "customers",
        },
        "where_columns": [
            "o.order_date",
            "c.city",
        ],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    composite_candidates = [
        candidate
        for candidate in candidates
        if "," in candidate["column_name"]
    ]

    assert composite_candidates == []


@patch(
    "collector.index_candidate_generator.get_existing_indexes",
    return_value=[],
)
@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_single_column_pattern_does_not_create_composite(
    mock_column_has_index,
    mock_get_existing_indexes,
):

    query_metadata = {
        "tables": ["orders"],
        "aliases": {
            "o": "orders",
        },
        "where_columns": [
            "o.customer_id",
        ],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    composite_candidates = [
        candidate
        for candidate in candidates
        if "," in candidate["column_name"]
    ]

    assert composite_candidates == []


@patch(
    "collector.index_candidate_generator.get_existing_indexes"
)
@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_existing_composite_prefix_prevents_candidate(
    mock_column_has_index,
    mock_get_existing_indexes,
):

    mock_get_existing_indexes.return_value = [
        {
            "index_name": (
                "idx_orders_customer_date_status"
            ),
            "index_definition": (
                "CREATE INDEX "
                "idx_orders_customer_date_status "
                "ON public.orders USING btree "
                "(customer_id, order_date, status)"
            ),
        }
    ]

    query_metadata = {
        "tables": ["orders"],
        "aliases": {
            "o": "orders",
        },
        "where_columns": [
            "o.customer_id",
            "o.order_date",
        ],
        "join_columns": [],
        "order_by_columns": [],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    composite_candidates = [
        candidate
        for candidate in candidates
        if "," in candidate["column_name"]
    ]

    assert composite_candidates == []


@patch(
    "collector.index_candidate_generator.get_existing_indexes",
    return_value=[],
)
@patch(
    "collector.index_candidate_generator.column_has_index",
    return_value=False,
)
def test_composite_candidate_removes_duplicate_columns(
    mock_column_has_index,
    mock_get_existing_indexes,
):

    query_metadata = {
        "tables": ["orders"],
        "aliases": {
            "o": "orders",
        },
        "where_columns": [
            "o.customer_id",
            "o.order_date",
        ],
        "join_columns": [],
        "order_by_columns": [
            "o.customer_id",
        ],
        "group_by_columns": [],
    }

    candidates = generate_index_candidates(
        {},
        query_metadata,
    )

    composite_candidates = [
        candidate
        for candidate in candidates
        if "," in candidate["column_name"]
    ]

    assert len(composite_candidates) == 1

    assert composite_candidates[0]["column_name"] == (
        "customer_id, order_date"
    )


# =========================================================
# NORMALIZATION
# =========================================================

def test_normalize_single_column():

    assert normalize_candidate_columns(
        "customer_id"
    ) == [
        "customer_id"
    ]


def test_normalize_comma_separated_columns():

    assert normalize_candidate_columns(
        "customer_id, order_date"
    ) == [
        "customer_id",
        "order_date",
    ]


def test_normalize_list_columns():

    assert normalize_candidate_columns(
        ["customer_id", "order_date"]
    ) == [
        "customer_id",
        "order_date",
    ]


def test_normalize_tuple_columns():

    assert normalize_candidate_columns(
        ("customer_id", "order_date")
    ) == [
        "customer_id",
        "order_date",
    ]


def test_normalize_removes_duplicates_preserving_order():

    assert normalize_candidate_columns(
        [
            "customer_id",
            "order_date",
            "customer_id",
            "status",
        ]
    ) == [
        "customer_id",
        "order_date",
        "status",
    ]


def test_normalize_invalid_value_returns_empty():

    assert normalize_candidate_columns(
        123
    ) == []


# =========================================================
# CANDIDATE RELATIONSHIPS
# =========================================================

def test_candidate_relationship_exact_duplicate():

    assert classify_candidate_relationship(
        ["customer_id", "order_date"],
        ["customer_id", "order_date"],
    ) == "exact_duplicate"


def test_candidate_relationship_candidate_prefix():

    assert classify_candidate_relationship(
        ["customer_id", "order_date"],
        [
            "customer_id",
            "order_date",
            "status",
        ],
    ) == "candidate_prefix"


def test_candidate_relationship_existing_prefix():

    assert classify_candidate_relationship(
        [
            "customer_id",
            "order_date",
            "status",
        ],
        ["customer_id", "order_date"],
    ) == "existing_prefix"


def test_candidate_relationship_different_order():

    assert classify_candidate_relationship(
        ["customer_id", "order_date"],
        ["order_date", "customer_id"],
    ) == "different"


# =========================================================
# CANDIDATE REDUNDANCY
# =========================================================

def test_exact_duplicate_candidate_is_redundant():

    candidates = [
        {
            "table_name": "orders",
            "column_name": "customer_id, order_date",
        }
    ]

    assert candidate_is_redundant(
        "orders",
        [
            "customer_id",
            "order_date",
        ],
        candidates,
    ) is True


def test_prefix_candidate_is_not_automatically_redundant():

    candidates = [
        {
            "table_name": "orders",
            "column_name": "customer_id, order_date",
        }
    ]

    assert candidate_is_redundant(
        "orders",
        [
            "customer_id",
            "order_date",
            "status",
        ],
        candidates,
    ) is False


def test_different_table_candidate_is_not_redundant():

    candidates = [
        {
            "table_name": "orders",
            "column_name": "customer_id, order_date",
        }
    ]

    assert candidate_is_redundant(
        "customers",
        [
            "customer_id",
            "order_date",
        ],
        candidates,
    ) is False


# =========================================================
# CANDIDATE METADATA
# =========================================================

def test_determine_single_candidate_type():

    assert determine_candidate_type(
        "customer_id"
    ) == "single"


def test_determine_composite_candidate_type():

    assert determine_candidate_type(
        "customer_id, order_date"
    ) == "composite"


def test_determine_unknown_candidate_type():

    assert determine_candidate_type(
        ""
    ) == "unknown"


def test_determine_where_source_type():

    assert determine_source_type(
        "Filter condition"
    ) == "where"


def test_determine_join_source_type():

    assert determine_source_type(
        "Join condition"
    ) == "join"


def test_determine_order_source_type():

    assert determine_source_type(
        "ORDER BY"
    ) == "order_by"


def test_determine_group_source_type():

    assert determine_source_type(
        "GROUP BY"
    ) == "group_by"


def test_determine_mixed_source_type():

    assert determine_source_type(
        "Filter condition ORDER BY"
    ) == "mixed"


def test_determine_unknown_source_type():

    assert determine_source_type(
        "something else"
    ) == "unknown"


def test_build_single_candidate_metadata():

    metadata = build_candidate_metadata(
        "customer_id",
        "where",
    )

    assert metadata == {
        "candidate_type": "single",
        "source_type": "where",
        "column_count": 1,
    }


def test_build_composite_candidate_metadata():

    metadata = build_candidate_metadata(
        [
            "customer_id",
            "order_date",
        ],
        "where",
    )

    assert metadata == {
        "candidate_type": "composite",
        "source_type": "where",
        "column_count": 2,
    }
