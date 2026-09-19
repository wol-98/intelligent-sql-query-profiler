"""
Index Cost Analyzer
-------------------

Provides PostgreSQL metadata describing the storage and
structural characteristics of indexes.

M17.1 — Index Cost Metadata

This module is analytical only.

It does NOT:
    - create indexes;
    - drop indexes;
    - execute benchmark workloads;
    - modify recommendation scores;
    - modify recommendation generation;
    - use benchmark outcomes.

The purpose is to measure the measurable cost characteristics
of existing indexes, particularly experimental indexes created
by the validation framework.
"""

from collector.index_validator import validate_identifier
from config.database import get_connection


# =========================================================
# TABLE SIZE
# =========================================================

def get_table_size(table_name):
    """
    Return PostgreSQL storage information for a table.

    Parameters
    ----------
    table_name : str
        PostgreSQL table name.

    Returns
    -------
    dict
        Table storage metadata.
    """

    if not validate_identifier(table_name):
        raise ValueError(
            f"Invalid table name: {table_name}"
        )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                pg_relation_size(%s) AS size_bytes,
                pg_size_pretty(
                    pg_relation_size(%s)
                ) AS size_pretty
            """,
            (
                table_name,
                table_name,
            )
        )

        row = cursor.fetchone()

        return {
            "table_name": table_name,
            "size_bytes": int(row[0]),
            "size_pretty": row[1],
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# INDEX SIZE
# =========================================================

def get_index_size(index_name):
    """
    Return PostgreSQL storage information for an index.

    Parameters
    ----------
    index_name : str
        PostgreSQL index name.

    Returns
    -------
    dict
        Index storage metadata.
    """

    if not validate_identifier(index_name):
        raise ValueError(
            f"Invalid index name: {index_name}"
        )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                pg_relation_size(%s) AS size_bytes,
                pg_size_pretty(
                    pg_relation_size(%s)
                ) AS size_pretty
            """,
            (
                index_name,
                index_name,
            )
        )

        row = cursor.fetchone()

        return {
            "index_name": index_name,
            "size_bytes": int(row[0]),
            "size_pretty": row[1],
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# INDEX METADATA
# =========================================================

def get_index_metadata(index_name):
    """
    Return structural metadata for a PostgreSQL index.

    The metadata includes:

        - index name;
        - table name;
        - index type;
        - indexed columns;
        - number of indexed columns;
        - uniqueness;
        - primary-key status;
        - validity;
        - index size.

    Parameters
    ----------
    index_name : str
        PostgreSQL index name.

    Returns
    -------
    dict
        Index metadata.
    """

    if not validate_identifier(index_name):
        raise ValueError(
            f"Invalid index name: {index_name}"
        )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                c.relname AS index_name,
                t.relname AS table_name,
                am.amname AS index_type,
                i.indisunique AS is_unique,
                i.indisprimary AS is_primary,
                i.indisvalid AS is_valid,
                COALESCE(
                    ARRAY_AGG(
                        a.attname
                        ORDER BY k.ordinality
                    ) FILTER (
                        WHERE a.attname IS NOT NULL
                    ),
                    ARRAY[]::text[]
                ) AS columns,
                COUNT(a.attname) AS column_count,
                pg_relation_size(c.oid) AS size_bytes,
                pg_size_pretty(
                    pg_relation_size(c.oid)
                ) AS size_pretty
            FROM pg_class c
            JOIN pg_index i
                ON i.indexrelid = c.oid
            JOIN pg_class t
                ON t.oid = i.indrelid
            JOIN pg_am am
                ON am.oid = c.relam
            LEFT JOIN LATERAL unnest(
                i.indkey
            ) WITH ORDINALITY AS k(attnum, ordinality)
                ON TRUE
            LEFT JOIN pg_attribute a
                ON a.attrelid = t.oid
               AND a.attnum = k.attnum
            WHERE c.relname = %s
            GROUP BY
                c.relname,
                t.relname,
                am.amname,
                i.indisunique,
                i.indisprimary,
                i.indisvalid,
                c.oid
            LIMIT 1
            """,
            (index_name,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "index_name": row[0],
            "table_name": row[1],
            "index_type": row[2],
            "is_unique": bool(row[3]),
            "is_primary": bool(row[4]),
            "is_valid": bool(row[5]),
            "columns": list(row[6] or []),
            "column_count": int(row[7]),
            "size_bytes": int(row[8]),
            "size_pretty": row[9],
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# TABLE / INDEX SIZE RATIO
# =========================================================

def calculate_index_table_ratio(
    index_size_bytes,
    table_size_bytes
):
    """
    Calculate index size as a percentage of table size.

    Positive value represents:

        index size / table size * 100

    Parameters
    ----------
    index_size_bytes : int
        Index size in bytes.

    table_size_bytes : int
        Table size in bytes.

    Returns
    -------
    float
        Index-to-table size percentage.
    """

    if table_size_bytes <= 0:
        return 0.0

    return (
        index_size_bytes
        / table_size_bytes
    ) * 100


# =========================================================
# COMPLETE COST METADATA
# =========================================================

def analyze_index_cost(index_name):
    """
    Build a complete storage-cost metadata record
    for an existing PostgreSQL index.

    The index must already exist.

    Returns
    -------
    dict or None
        Combined index and table storage metadata.
    """

    metadata = get_index_metadata(
        index_name
    )

    if metadata is None:
        return None

    table_size = get_table_size(
        metadata["table_name"]
    )

    index_size_bytes = metadata[
        "size_bytes"
    ]

    table_size_bytes = table_size[
        "size_bytes"
    ]

    ratio = calculate_index_table_ratio(
        index_size_bytes,
        table_size_bytes
    )

    return {
        **metadata,

        "table_size_bytes":
            table_size_bytes,

        "table_size_pretty":
            table_size["size_pretty"],

        "index_table_size_ratio_percent":
            ratio,
    }


# =========================================================
# MULTIPLE INDEXES
# =========================================================

def analyze_index_costs(index_names):
    """
    Analyze multiple existing indexes.

    Invalid or non-existent indexes are represented
    by None results and are not silently converted
    into fabricated metadata.

    Returns
    -------
    list of dict
        Index cost metadata records.
    """

    results = []

    for index_name in index_names or []:
        result = analyze_index_cost(
            index_name
        )

        if result is not None:
            results.append(result)

    return results


# =========================================================
# DISPLAY
# =========================================================

def print_index_cost_analysis(
    metadata
):
    """
    Print one index cost metadata record.
    """

    print("\n" + "=" * 70)
    print("INDEX COST METADATA")
    print("=" * 70)

    if not metadata:
        print("No index metadata available.")
        print("=" * 70)
        return

    print(
        f"Index name              : "
        f"{metadata['index_name']}"
    )

    print(
        f"Table                   : "
        f"{metadata['table_name']}"
    )

    print(
        f"Index type              : "
        f"{metadata['index_type']}"
    )

    print(
        f"Columns                 : "
        f"{', '.join(metadata['columns'])}"
    )

    print(
        f"Column count            : "
        f"{metadata['column_count']}"
    )

    print(
        f"Unique                  : "
        f"{metadata['is_unique']}"
    )

    print(
        f"Primary                 : "
        f"{metadata['is_primary']}"
    )

    print(
        f"Valid                   : "
        f"{metadata['is_valid']}"
    )

    print(
        f"Index size              : "
        f"{metadata['size_bytes']} bytes "
        f"({metadata['size_pretty']})"
    )

    print(
        f"Table size              : "
        f"{metadata['table_size_bytes']} bytes "
        f"({metadata['table_size_pretty']})"
    )

    print(
        f"Index/table ratio       : "
        f"{metadata['index_table_size_ratio_percent']:.4f}%"
    )

    print("=" * 70)
