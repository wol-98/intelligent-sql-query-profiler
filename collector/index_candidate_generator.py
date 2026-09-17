"""
Index Candidate Generator
-------------------------
Generates possible indexes from query metadata
and execution-plan features.

Existing indexes are checked against PostgreSQL
before a candidate is returned.
"""

from config.database import get_connection


# =========================================================
# RESOLVE COLUMN REFERENCE
# =========================================================

def resolve_column_reference(
    column_reference,
    aliases,
    tables=None
):
    """
    Resolve a column reference such as:

        oi.product_id
        p.category_id
        customer_id

    into:

        (table_name, column_name)
    """

    # -----------------------------------------------------
    # Qualified column reference
    # Example:
    #     p.category_id
    #     oi.product_id
    # -----------------------------------------------------

    if "." in column_reference:

        alias, column = (
            column_reference.split(
                ".",
                1
            )
        )

        table = aliases.get(
            alias
        )

        if table:
            return table, column

        return None, column

    # -----------------------------------------------------
    # Unqualified column reference
    #
    # If exactly one table exists in the query,
    # the column can safely be resolved to that table.
    # -----------------------------------------------------

    if tables and len(tables) == 1:

        return tables[0], column_reference

    # -----------------------------------------------------
    # Backward compatibility:
    # If aliases contain exactly one table,
    # use that table.
    # -----------------------------------------------------

    if len(aliases) == 1:

        table = next(
            iter(aliases.values())
        )

        return table, column_reference

    # -----------------------------------------------------
    # Ambiguous column reference.
    # Do not guess the table.
    # -----------------------------------------------------

    return None, column_reference


# =========================================================
# GET EXISTING INDEXES
# =========================================================

def get_existing_indexes(
    table_name
):
    """
    Retrieve existing PostgreSQL indexes for a table.

    Returns
    -------
    list of dict
        Existing index information.
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND tablename = %s
            ORDER BY indexname;
            """,
            (table_name,)
        )

        indexes = []

        for index_name, index_definition in (
            cursor.fetchall()
        ):

            indexes.append(
                {
                    "index_name": index_name,
                    "index_definition":
                        index_definition,
                }
            )

        return indexes

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# PARSE INDEXED COLUMNS
# =========================================================

def get_indexed_columns(
    index_definition
):
    """
    Extract indexed column names from a PostgreSQL
    index definition.

    Examples
    --------
    CREATE UNIQUE INDEX customers_pkey
    ON public.customers USING btree (customer_id)

    -> ["customer_id"]

    CREATE INDEX idx_orders_customer_date
    ON public.orders USING btree (customer_id, order_date)

    -> ["customer_id", "order_date"]

    Returns
    -------
    list of str
        Indexed columns in their PostgreSQL index order.
    """

    if not index_definition:
        return []

    try:

        opening_parenthesis = (
            index_definition.rfind("(")
        )

        closing_parenthesis = (
            index_definition.rfind(")")
        )

        if (
            opening_parenthesis == -1
            or closing_parenthesis == -1
            or closing_parenthesis <= opening_parenthesis
        ):
            return []

        column_section = index_definition[
            opening_parenthesis + 1:
            closing_parenthesis
        ]

        columns = []

        for column in column_section.split(","):

            column = column.strip()

            if not column:
                continue

            # -------------------------------------------------
            # Remove optional PostgreSQL identifier quotes.
            # -------------------------------------------------

            if (
                len(column) >= 2
                and column[0] == '"'
                and column[-1] == '"'
            ):
                column = column[1:-1]

            columns.append(
                column
            )

        return columns

    except (AttributeError, TypeError):

        return []


# =========================================================
# CHECK WHETHER COLUMN IS ALREADY INDEXED
# =========================================================

def column_has_index(
    table_name,
    column_name
):
    """
    Check whether the specified column is already
    covered by an existing PostgreSQL B-tree index.

    For composite indexes, only the leftmost indexed
    column is treated as directly covered for a
    single-column candidate.

    Examples
    --------
    (customer_id)
        -> customer_id is covered

    (customer_id, order_date)
        -> customer_id is covered
        -> order_date is not treated as independently covered

    Parameters
    ----------
    table_name : str
        PostgreSQL table name.

    column_name : str
        Column to check.

    Returns
    -------
    bool
        True when the column is the leftmost column
        of an existing index.
    """

    indexes = get_existing_indexes(
        table_name
    )

    for index in indexes:

        definition = index.get(
            "index_definition",
            ""
        )

        indexed_columns = get_indexed_columns(
            definition
        )

        if not indexed_columns:
            continue

        if indexed_columns[0] == column_name:
            return True

    return False


# =========================================================
# ADD SINGLE-COLUMN CANDIDATE
# =========================================================

def add_candidate_if_new(
    candidates,
    table_name,
    column_name,
    index_type,
    reason,
    source
):
    """
    Add a single-column candidate if:

    1. table/column is valid
    2. it isn't already present in candidates
    3. it isn't already indexed
    """

    if not table_name:
        return

    if not column_name:
        return

    # -----------------------------------------------------
    # Avoid duplicate candidates generated from
    # multiple query features.
    # -----------------------------------------------------

    for candidate in candidates:

        if (
            candidate["table_name"]
            == table_name
            and candidate["column_name"]
            == column_name
        ):
            return

    # -----------------------------------------------------
    # Check PostgreSQL for an existing index.
    # -----------------------------------------------------

    if column_has_index(
        table_name,
        column_name
    ):
        return

    candidates.append(
        {
            "table_name": table_name,
            "column_name": column_name,
            "index_type": index_type,
            "reason": reason,
            "source": source,
        }
    )


# =========================================================
# ADD COMPOSITE CANDIDATE
# =========================================================

def add_composite_candidate_if_new(
    candidates,
    table_name,
    column_names,
    index_type,
    reason,
    source
):
    """
    Add a composite index candidate when:

    1. table is valid
    2. at least two distinct columns are provided
    3. it isn't already present in candidates
    4. it isn't already covered by an existing index

    Existing composite indexes are considered covering when
    the candidate columns match the leftmost columns of the
    existing B-tree index.
    """

    if not table_name:
        return

    if not column_names:
        return

    # -----------------------------------------------------
    # Remove duplicate columns while preserving order.
    # -----------------------------------------------------

    unique_columns = []

    for column_name in column_names:

        if (
            column_name
            and column_name not in unique_columns
        ):
            unique_columns.append(
                column_name
            )

    # -----------------------------------------------------
    # A composite index requires at least two columns.
    # -----------------------------------------------------

    if len(unique_columns) < 2:
        return

    # -----------------------------------------------------
    # Avoid duplicate composite candidates.
    # -----------------------------------------------------

    composite_column_name = ", ".join(
        unique_columns
    )

    for candidate in candidates:

        if (
            candidate["table_name"]
            == table_name
            and candidate["column_name"]
            == composite_column_name
        ):
            return

    # -----------------------------------------------------
    # Check existing PostgreSQL indexes.
    # -----------------------------------------------------

    existing_indexes = get_existing_indexes(
        table_name
    )

    for index in existing_indexes:

        definition = index.get(
            "index_definition",
            ""
        )

        indexed_columns = get_indexed_columns(
            definition
        )

        if not indexed_columns:
            continue

        # -------------------------------------------------
        # Existing index covers the candidate when the
        # candidate columns form its leftmost prefix.
        #
        # Example:
        #
        # Existing:
        #     (customer_id, order_date, status)
        #
        # Candidate:
        #     (customer_id, order_date)
        #
        # The candidate is already covered.
        # -------------------------------------------------

        if indexed_columns[
            :len(unique_columns)
        ] == unique_columns:
            return

    candidates.append(
        {
            "table_name": table_name,
            "column_name": composite_column_name,
            "index_type": index_type,
            "reason": reason,
            "source": source,
        }
    )


# =========================================================
# BUILD COMPOSITE COLUMN GROUPS
# =========================================================

def generate_composite_candidates(
    query_metadata,
    aliases,
    tables
):
    """
    Identify columns that can participate in a composite
    index candidate.

    Column priority:

    1. WHERE columns
    2. ORDER BY columns
    3. GROUP BY columns

    Only columns belonging to the same table are combined.

    JOIN columns are intentionally handled separately because
    JOIN conditions may involve different tables.
    """

    table_columns = {}

    def collect_columns(
        column_references
    ):
        for column_reference in column_references:

            table_name, column_name = (
                resolve_column_reference(
                    column_reference,
                    aliases,
                    tables
                )
            )

            # -------------------------------------------------
            # Do not guess when the table cannot be resolved.
            # -------------------------------------------------

            if not table_name or not column_name:
                continue

            if table_name not in table_columns:
                table_columns[table_name] = []

            if column_name not in (
                table_columns[table_name]
            ):
                table_columns[table_name].append(
                    column_name
                )

    # -----------------------------------------------------
    # Filtering columns have highest priority.
    # -----------------------------------------------------

    collect_columns(
        query_metadata.get(
            "where_columns",
            []
        )
    )

    # -----------------------------------------------------
    # ORDER BY columns come next.
    # -----------------------------------------------------

    collect_columns(
        query_metadata.get(
            "order_by_columns",
            []
        )
    )

    # -----------------------------------------------------
    # GROUP BY columns come last.
    # -----------------------------------------------------

    collect_columns(
        query_metadata.get(
            "group_by_columns",
            []
        )
    )

    return table_columns


# =========================================================
# GENERATE CANDIDATES
# =========================================================

def generate_index_candidates(
    features,
    query_metadata
):
    """
    Generate index candidates using query metadata
    and execution-plan features.

    Candidate sources:

    - WHERE filters
    - JOIN conditions
    - ORDER BY columns
    - GROUP BY columns
    - Composite filter/order patterns
    """

    candidates = []

    aliases = query_metadata.get(
        "aliases",
        {}
    )

    tables = query_metadata.get(
        "tables",
        []
    )

    # -----------------------------------------------------
    # WHERE columns
    # -----------------------------------------------------

    for column_reference in (
        query_metadata.get(
            "where_columns",
            []
        )
    ):

        table_name, column_name = (
            resolve_column_reference(
                column_reference,
                aliases,
                tables
            )
        )

        add_candidate_if_new(
            candidates,
            table_name,
            column_name,
            "B-tree",
            "Filter condition",
            column_reference
        )

    # -----------------------------------------------------
    # JOIN columns
    # -----------------------------------------------------

    for column_reference in (
        query_metadata.get(
            "join_columns",
            []
        )
    ):

        table_name, column_name = (
            resolve_column_reference(
                column_reference,
                aliases,
                tables
            )
        )

        add_candidate_if_new(
            candidates,
            table_name,
            column_name,
            "B-tree",
            "Join condition",
            column_reference
        )

    # -----------------------------------------------------
    # ORDER BY columns
    # -----------------------------------------------------

    for column_reference in (
        query_metadata.get(
            "order_by_columns",
            []
        )
    ):

        table_name, column_name = (
            resolve_column_reference(
                column_reference,
                aliases,
                tables
            )
        )

        add_candidate_if_new(
            candidates,
            table_name,
            column_name,
            "B-tree",
            "ORDER BY",
            column_reference
        )

    # -----------------------------------------------------
    # GROUP BY columns
    # -----------------------------------------------------

    for column_reference in (
        query_metadata.get(
            "group_by_columns",
            []
        )
    ):

        table_name, column_name = (
            resolve_column_reference(
                column_reference,
                aliases,
                tables
            )
        )

        add_candidate_if_new(
            candidates,
            table_name,
            column_name,
            "B-tree",
            "GROUP BY",
            column_reference
        )

    # -----------------------------------------------------
    # COMPOSITE INDEX CANDIDATES
    # -----------------------------------------------------

    composite_columns = generate_composite_candidates(
        query_metadata,
        aliases,
        tables
    )

    for table_name, column_names in (
        composite_columns.items()
    ):

        source = ", ".join(
            column_names
        )

        add_composite_candidate_if_new(
            candidates,
            table_name,
            column_names,
            "B-tree",
            "Composite filter/order pattern",
            source
        )

    return candidates


# =========================================================
# PRINT CANDIDATES
# =========================================================

def print_candidates(
    candidates
):
    """
    Print generated index candidates.
    """

    print("\n" + "=" * 70)
    print("INDEX CANDIDATES")
    print("=" * 70)

    if not candidates:

        print(
            "No new index candidates found."
        )

        return

    for number, candidate in enumerate(
        candidates,
        start=1
    ):

        print(
            f"\nCandidate {number}"
        )

        print(
            f"  Table       : "
            f"{candidate['table_name']}"
        )

        print(
            f"  Column      : "
            f"{candidate['column_name']}"
        )

        print(
            f"  Type        : "
            f"{candidate['index_type']}"
        )

        print(
            f"  Reason      : "
            f"{candidate['reason']}"
        )

        print(
            f"  Source      : "
            f"{candidate['source']}"
        )

    print("=" * 70)
