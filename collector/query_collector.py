import hashlib
import json
from datetime import datetime

from config.database import get_connection
from collector.plan_analyzer import analyze_plan
from collector.feature_extractor import (
    extract_plan_features,
    print_features,
)


# =========================================================
# QUERY NORMALIZATION
# =========================================================

def normalize_query(query: str) -> str:
    """
    Normalize whitespace in a SQL query.

    This allows logically identical queries with
    different formatting to receive the same hash.
    """

    return " ".join(
        query.strip().split()
    )


# =========================================================
# QUERY HASH
# =========================================================

def generate_query_hash(query: str) -> str:
    """
    Generate a SHA-256 hash for the normalized query.
    """

    normalized_query = normalize_query(
        query
    )

    return hashlib.sha256(
        normalized_query.encode(
            "utf-8"
        )
    ).hexdigest()


# =========================================================
# COLLECT QUERY PROFILE
# =========================================================

def collect_query_profile(query: str) -> dict:
    """
    Execute EXPLAIN ANALYZE against PostgreSQL
    and collect profiling information.
    """

    connection = None
    cursor = None

    try:

        # -------------------------------------------------
        # Connect to Supabase PostgreSQL
        # -------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()

        # -------------------------------------------------
        # Build EXPLAIN query
        # -------------------------------------------------

        explain_query = f"""
        EXPLAIN (
            ANALYZE,
            BUFFERS,
            FORMAT JSON
        )
        {query}
        """

        # -------------------------------------------------
        # Execute
        # -------------------------------------------------

        cursor.execute(
            explain_query
        )

        # -------------------------------------------------
        # Fetch JSON execution plan
        # -------------------------------------------------

        result = cursor.fetchone()[0]

        plan_data = result[0]

        root_plan = plan_data["Plan"]

        # -------------------------------------------------
        # Recursively analyze complete plan tree
        # -------------------------------------------------

        plan_nodes = analyze_plan(
            root_plan
        )

        # -------------------------------------------------
        # Extract structured features
        # -------------------------------------------------

        features = extract_plan_features(
            plan_nodes
        )

        # -------------------------------------------------
        # Build profile
        # -------------------------------------------------

        profile = {

            "query_hash":
                generate_query_hash(
                    query
                ),

            "query_text":
                normalize_query(
                    query
                ),

            "query_type":
                query.strip()
                .split()[0]
                .upper(),

            "execution_time_ms":
                plan_data.get(
                    "Execution Time",
                    0
                ),

            "planning_time_ms":
                plan_data.get(
                    "Planning Time",
                    0
                ),

            "actual_rows":
                root_plan.get(
                    "Actual Rows",
                    0
                ),

            "rows_removed_by_filter":
                root_plan.get(
                    "Rows Removed by Filter",
                    0
                ),

            "shared_hit_blocks":
                root_plan.get(
                    "Shared Hit Blocks",
                    0
                ),

            "shared_read_blocks":
                root_plan.get(
                    "Shared Read Blocks",
                    0
                ),

            "plan_node_type":
                root_plan.get(
                    "Node Type"
                ),

            "relation_name":
                root_plan.get(
                    "Relation Name"
                ),

            "execution_plan":
                plan_data,

            "plan_nodes":
                plan_nodes,

            "features":
                features,

            "captured_at":
                datetime.now()
        }

        return profile

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# SAVE QUERY PROFILE
# =========================================================

def save_query_profile(
    profile: dict
) -> int:

    """
    Insert a new query profile.

    If the query already exists, update the existing
    profile instead of creating a duplicate.

    Returns
    -------
    int
        query_profile_id
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        # -------------------------------------------------
        # Check whether query already exists
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                query_profile_id,
                execution_count,
                total_execution_time_ms
            FROM query_profiles
            WHERE query_hash = %s;
            """,
            (
                profile["query_hash"],
            )
        )

        existing = cursor.fetchone()

        # =================================================
        # EXISTING QUERY
        # =================================================

        if existing:

            query_profile_id = existing[0]

            old_count = (
                existing[1] or 0
            )

            old_total = (
                existing[2] or 0
            )

            new_count = (
                old_count + 1
            )

            new_total = (
                old_total
                + profile[
                    "execution_time_ms"
                ]
            )

            new_average = (
                new_total
                / new_count
            )

            cursor.execute(
                """
                UPDATE query_profiles
                SET
                    execution_count = %s,

                    total_execution_time_ms = %s,

                    average_execution_time_ms = %s,

                    rows_processed = %s,

                    table_name = %s,

                    planning_time_ms = %s,

                    shared_hit_blocks = %s,

                    shared_read_blocks = %s,

                    rows_removed_by_filter = %s,

                    plan_node_type = %s,

                    execution_plan = %s,

                    captured_at = %s

                WHERE query_profile_id = %s;
                """,

                (
                    new_count,

                    new_total,

                    new_average,

                    profile[
                        "actual_rows"
                    ],

                    profile[
                        "relation_name"
                    ],

                    profile[
                        "planning_time_ms"
                    ],

                    profile[
                        "shared_hit_blocks"
                    ],

                    profile[
                        "shared_read_blocks"
                    ],

                    profile[
                        "rows_removed_by_filter"
                    ],

                    profile[
                        "plan_node_type"
                    ],

                    json.dumps(
                        profile[
                            "execution_plan"
                        ]
                    ),

                    profile[
                        "captured_at"
                    ],

                    query_profile_id
                )
            )

        # =================================================
        # NEW QUERY
        # =================================================

        else:

            cursor.execute(
                """
                INSERT INTO query_profiles
                (
                    query_hash,

                    query_text,

                    query_type,

                    execution_count,

                    total_execution_time_ms,

                    average_execution_time_ms,

                    rows_processed,

                    table_name,

                    captured_at,

                    planning_time_ms,

                    shared_hit_blocks,

                    shared_read_blocks,

                    rows_removed_by_filter,

                    plan_node_type,

                    execution_plan
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )

                RETURNING query_profile_id;
                """,

                (
                    profile[
                        "query_hash"
                    ],

                    profile[
                        "query_text"
                    ],

                    profile[
                        "query_type"
                    ],

                    1,

                    profile[
                        "execution_time_ms"
                    ],

                    profile[
                        "execution_time_ms"
                    ],

                    profile[
                        "actual_rows"
                    ],

                    profile[
                        "relation_name"
                    ],

                    profile[
                        "captured_at"
                    ],

                    profile[
                        "planning_time_ms"
                    ],

                    profile[
                        "shared_hit_blocks"
                    ],

                    profile[
                        "shared_read_blocks"
                    ],

                    profile[
                        "rows_removed_by_filter"
                    ],

                    profile[
                        "plan_node_type"
                    ],

                    json.dumps(
                        profile[
                            "execution_plan"
                        ]
                    )
                )
            )

            query_profile_id = (
                cursor.fetchone()[0]
            )

        # -------------------------------------------------
        # Commit
        # -------------------------------------------------

        connection.commit()

        return query_profile_id

    except Exception:

        if connection:
            connection.rollback()

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# PRINT PROFILE
# =========================================================

def print_profile(
    profile: dict,
    profile_id: int
):
    """
    Print the collected query profile.
    """

    print()

    print("=" * 65)

    print("QUERY PROFILE")

    print("=" * 65)

    print(
        f"Profile ID     : "
        f"{profile_id}"
    )

    print(
        f"Query type     : "
        f"{profile['query_type']}"
    )

    print(
        f"Table          : "
        f"{profile['relation_name']}"
    )

    print(
        f"Plan node      : "
        f"{profile['plan_node_type']}"
    )

    print(
        f"Execution time : "
        f"{profile['execution_time_ms']} ms"
    )

    print(
        f"Planning time  : "
        f"{profile['planning_time_ms']} ms"
    )

    print(
        f"Actual rows    : "
        f"{profile['actual_rows']}"
    )

    print(
        f"Rows filtered  : "
        f"{profile['rows_removed_by_filter']}"
    )

    print(
        f"Buffer hits    : "
        f"{profile['shared_hit_blocks']}"
    )

    print(
        f"Buffer reads   : "
        f"{profile['shared_read_blocks']}"
    )

    print(
        f"Plan nodes     : "
        f"{len(profile['plan_nodes'])}"
    )

    print_features(
        profile["features"]
    )

    print("=" * 65)


# =========================================================
# TEST RUN
# =========================================================

if __name__ == "__main__":

    test_query = """
    SELECT
        oi.order_id,
        p.product_name,
        oi.quantity,
        oi.unit_price
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE p.category_id = 1;
    """

    profile = collect_query_profile(
        test_query
    )

    profile_id = save_query_profile(
        profile
    )

    print_profile(
        profile,
        profile_id
    )
