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
# CHECK WHETHER COLUMN IS ALREADY INDEXED
# =========================================================

def column_has_index(
    table_name,
    column_name
):
    """
    Check whether the specified column already
    appears in an existing PostgreSQL index.

    This intentionally checks the index definition
    rather than assuming a particular index name.
    """

    indexes = get_existing_indexes(
        table_name
    )

    search_pattern = (
        f"({column_name})"
    )

    for index in indexes:

        definition = (
            index[
                "index_definition"
            ]
        )

        if search_pattern in definition:

            return True

    return False


# =========================================================
# ADD CANDIDATE
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
    Add a candidate if:

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
