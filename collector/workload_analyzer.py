"""
SQL Workload Fingerprint Analyzer
---------------------------------
Analyzes the SQL workload using query fingerprints.

This module provides two analysis modes:

1. Static workload analysis
   - Reads the official SQL workload file.
   - Parses each query.
   - Generates query fingerprints.
   - Groups structurally similar queries.

2. Profiled workload analysis
   - Reads query execution profiles stored in PostgreSQL.
   - Reconstructs fingerprints from the stored SQL text.
   - Groups profiles by structural fingerprint.
   - Aggregates execution count, execution time,
     and rows processed.

This module does not modify the database.
"""

import re
from collections import defaultdict

from collector.query_parser import parse_query


# =========================================================
# STATIC WORKLOAD LOADING
# =========================================================

def load_workload(workload_path: str) -> list[dict]:
    """
    Load the official SQL workload file.

    The workload is expected to contain queries in the form:

        -- Q001: Description
        SELECT ...

    Returns
    -------
    list[dict]
        List containing query ID, description, and SQL text.
    """

    with open(
        workload_path,
        "r",
        encoding="utf-8",
    ) as file:
        sql_text = file.read()

    pattern = re.compile(
        r"--\s*(Q\d+):\s*(.*?)\n"
        r"(.*?)(?=\n\s*--\s*Q\d+:|\Z)",
        re.IGNORECASE | re.DOTALL,
    )

    workload = []

    for match in pattern.finditer(sql_text):
        query_id = match.group(1).upper()
        description = match.group(2).strip()
        query = match.group(3).strip()

        workload.append(
            {
                "query_id": query_id,
                "description": description,
                "query": query,
            }
        )

    return workload


# =========================================================
# STATIC WORKLOAD ANALYSIS
# =========================================================

def analyze_workload(
    workload_path: str,
) -> dict:
    """
    Analyze the official SQL workload using fingerprints.

    Returns
    -------
    dict
        Workload fingerprint analysis.
    """

    workload = load_workload(
        workload_path
    )

    fingerprint_groups = defaultdict(list)

    analyzed_queries = []

    for item in workload:
        metadata = parse_query(
            item["query"]
        )

        fingerprint = metadata[
            "fingerprint"
        ]

        analyzed_queries.append(
            {
                "query_id": item["query_id"],
                "description": item[
                    "description"
                ],
                "query": item["query"],
                "fingerprint": fingerprint,
                "normalized_template": metadata[
                    "normalized_template"
                ],
            }
        )

        fingerprint_groups[
            fingerprint
        ].append(
            item["query_id"]
        )

    groups = []

    for fingerprint, query_ids in (
        fingerprint_groups.items()
    ):
        matching_query = next(
            query
            for query in analyzed_queries
            if query["fingerprint"]
            == fingerprint
        )

        groups.append(
            {
                "fingerprint": fingerprint,
                "normalized_template":
                    matching_query[
                        "normalized_template"
                    ],
                "frequency": len(query_ids),
                "query_ids": query_ids,
            }
        )

    groups.sort(
        key=lambda group: (
            -group["frequency"],
            group["query_ids"][0],
        )
    )

    repeated_groups = [
        group
        for group in groups
        if group["frequency"] > 1
    ]

    largest_group_size = max(
        (
            group["frequency"]
            for group in groups
        ),
        default=0,
    )

    return {
        "total_queries": len(
            analyzed_queries
        ),
        "unique_fingerprints": len(
            groups
        ),
        "repeated_groups": len(
            repeated_groups
        ),
        "largest_group_size":
            largest_group_size,
        "queries": analyzed_queries,
        "groups": groups,
    }


# =========================================================
# STATIC WORKLOAD REPORTING
# =========================================================

def print_workload_analysis(
    analysis: dict,
) -> None:
    """
    Print a human-readable static workload
    fingerprint report.
    """

    print("\n" + "=" * 80)
    print(
        "SQL WORKLOAD FINGERPRINT ANALYSIS"
    )
    print("=" * 80)

    print(
        f"Total queries       : "
        f"{analysis['total_queries']}"
    )

    print(
        f"Unique fingerprints : "
        f"{analysis['unique_fingerprints']}"
    )

    print(
        f"Repeated groups     : "
        f"{analysis['repeated_groups']}"
    )

    print(
        f"Largest group size  : "
        f"{analysis['largest_group_size']}"
    )

    print("\n" + "-" * 80)
    print("FINGERPRINT GROUPS")
    print("-" * 80)

    for index, group in enumerate(
        analysis["groups"],
        start=1,
    ):
        print(
            f"\nGroup {index}"
        )

        print(
            f"Frequency : "
            f"{group['frequency']}"
        )

        print(
            f"Query IDs : "
            f"{', '.join(group['query_ids'])}"
        )

        print(
            f"Fingerprint : "
            f"{group['fingerprint']}"
        )

        print(
            f"Template : "
            f"{group['normalized_template']}"
        )


# =========================================================
# PROFILED WORKLOAD ANALYSIS
# =========================================================

def analyze_profiled_workload() -> dict:
    """
    Analyze query profiles stored in PostgreSQL
    using the M12 query fingerprinting layer.

    This function performs a read-only analysis.

    Returns
    -------
    dict
        Profile-level workload aggregation grouped
        by query fingerprint.
    """

    from config.database import get_connection

    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                query_profile_id,
                query_text,
                execution_count,
                total_execution_time_ms,
                average_execution_time_ms,
                rows_processed
            FROM query_profiles
            ORDER BY query_profile_id;
            """
        )

        rows = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    fingerprint_groups = defaultdict(
        lambda: {
            "fingerprint": None,
            "normalized_template": None,
            "profile_ids": [],
            "profile_count": 0,
            "total_executions": 0,
            "total_execution_time_ms": 0.0,
            "total_rows_processed": 0,
        }
    )

    for row in rows:
        (
            profile_id,
            query_text,
            execution_count,
            total_execution_time_ms,
            average_execution_time_ms,
            rows_processed,
        ) = row

        metadata = parse_query(
            query_text
        )

        fingerprint = metadata[
            "fingerprint"
        ]

        group = fingerprint_groups[
            fingerprint
        ]

        group["fingerprint"] = fingerprint

        group["normalized_template"] = (
            metadata[
                "normalized_template"
            ]
        )

        group["profile_ids"].append(
            profile_id
        )

        group["profile_count"] += 1

        group["total_executions"] += (
            execution_count or 0
        )

        group[
            "total_execution_time_ms"
        ] += (
            total_execution_time_ms
            or 0.0
        )

        group[
            "total_rows_processed"
        ] += (
            rows_processed
            or 0
        )

    groups = []

    for group in fingerprint_groups.values():

        total_executions = (
            group["total_executions"]
        )

        if total_executions > 0:
            weighted_average = (
                group[
                    "total_execution_time_ms"
                ]
                / total_executions
            )
        else:
            weighted_average = 0.0

        groups.append(
            {
                **group,
                "weighted_average_execution_time_ms":
                    weighted_average,
            }
        )

    groups.sort(
        key=lambda item: item[
            "total_execution_time_ms"
        ],
        reverse=True,
    )

    total_profiles = len(rows)

    unique_fingerprints = len(
        groups
    )

    total_executions = sum(
        group["total_executions"]
        for group in groups
    )

    total_execution_time_ms = sum(
        group[
            "total_execution_time_ms"
        ]
        for group in groups
    )

    total_rows_processed = sum(
        group[
            "total_rows_processed"
        ]
        for group in groups
    )

    return {
        "total_profiles":
            total_profiles,

        "unique_fingerprints":
            unique_fingerprints,

        "total_executions":
            total_executions,

        "total_execution_time_ms":
            total_execution_time_ms,

        "total_rows_processed":
            total_rows_processed,

        "groups":
            groups,
    }


# =========================================================
# PROFILED WORKLOAD REPORTING
# =========================================================

def print_profiled_workload_analysis(
    analysis: dict,
) -> None:
    """
    Print a human-readable profile-level
    workload fingerprint report.
    """

    print("\n" + "=" * 80)
    print(
        "PROFILED WORKLOAD FINGERPRINT ANALYSIS"
    )
    print("=" * 80)

    print(
        f"Total profiles        : "
        f"{analysis['total_profiles']}"
    )

    print(
        f"Unique fingerprints   : "
        f"{analysis['unique_fingerprints']}"
    )

    print(
        f"Total executions      : "
        f"{analysis['total_executions']}"
    )

    print(
        f"Total execution time  : "
        f"{analysis['total_execution_time_ms']:.3f} ms"
    )

    print(
        f"Total rows processed  : "
        f"{analysis['total_rows_processed']}"
    )

    print("\n" + "-" * 80)
    print(
        "FINGERPRINT COST GROUPS"
    )
    print("-" * 80)

    for index, group in enumerate(
        analysis["groups"],
        start=1,
    ):
        print(
            f"\nGroup {index}"
        )

        print(
            f"Profiles       : "
            f"{', '.join(map(str, group['profile_ids']))}"
        )

        print(
            f"Executions     : "
            f"{group['total_executions']}"
        )

        print(
            f"Total time     : "
            f"{group['total_execution_time_ms']:.3f} ms"
        )

        print(
            f"Weighted avg   : "
            f"{group['weighted_average_execution_time_ms']:.3f} ms"
        )

        print(
            f"Rows processed : "
            f"{group['total_rows_processed']}"
        )

        print(
            f"Template       : "
            f"{group['normalized_template']}"
        )


# =========================================================
# MAIN
# =========================================================

def main() -> None:
    """
    Run workload fingerprint analysis.
    """

    workload_path = (
        "database/workload.sql"
    )

    # -----------------------------------------------------
    # Static workload analysis
    # -----------------------------------------------------

    static_analysis = analyze_workload(
        workload_path
    )

    print_workload_analysis(
        static_analysis
    )

    # -----------------------------------------------------
    # Profiled workload analysis
    # -----------------------------------------------------

    profiled_analysis = (
        analyze_profiled_workload()
    )

    print_profiled_workload_analysis(
        profiled_analysis
    )


# =========================================================
# SCRIPT ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
