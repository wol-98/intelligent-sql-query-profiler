"""
Workload Cost Analyzer
----------------------
Analyzes profiled SQL workload groups and derives
workload-level cost and frequency metrics.

This module does not execute SQL workload queries
and does not modify the database.

It uses the query fingerprinting layer to group
structurally equivalent query profiles.
"""

from collector.workload_analyzer import (
    analyze_profiled_workload,
)


# =========================================================
# WORKLOAD COST ANALYSIS
# =========================================================

def analyze_workload_costs() -> dict:
    """
    Analyze workload groups using execution cost,
    execution frequency, and processed-row metrics.

    Returns
    -------
    dict
        Workload cost analysis containing group-level
        metrics and overall workload totals.
    """

    analysis = (
        analyze_profiled_workload()
    )

    groups = analysis[
        "groups"
    ]

    total_execution_time_ms = (
        analysis[
            "total_execution_time_ms"
        ]
    )

    total_executions = (
        analysis[
            "total_executions"
        ]
    )

    enriched_groups = []

    for rank, group in enumerate(
        groups,
        start=1,
    ):

        group_total_time = (
            group[
                "total_execution_time_ms"
            ]
        )

        group_executions = (
            group[
                "total_executions"
            ]
        )

        # -------------------------------------------------
        # Execution-time share
        # -------------------------------------------------

        if total_execution_time_ms > 0:

            execution_time_share = (
                group_total_time
                / total_execution_time_ms
                * 100.0
            )

        else:

            execution_time_share = 0.0

        # -------------------------------------------------
        # Execution-frequency share
        # -------------------------------------------------

        if total_executions > 0:

            execution_frequency_share = (
                group_executions
                / total_executions
                * 100.0
            )

        else:

            execution_frequency_share = 0.0

        enriched_groups.append(
            {
                **group,

                "workload_cost_rank":
                    rank,

                "execution_time_share":
                    execution_time_share,

                "execution_frequency_share":
                    execution_frequency_share,
            }
        )

    return {
        "total_profiles":
            analysis[
                "total_profiles"
            ],

        "unique_fingerprints":
            analysis[
                "unique_fingerprints"
            ],

        "total_executions":
            total_executions,

        "total_execution_time_ms":
            total_execution_time_ms,

        "total_rows_processed":
            analysis[
                "total_rows_processed"
            ],

        "groups":
            enriched_groups,
    }


# =========================================================
# REPORTING
# =========================================================

def print_workload_cost_analysis(
    analysis: dict,
) -> None:
    """
    Print a human-readable workload cost report.
    """

    print("\n" + "=" * 80)
    print(
        "M13 — WORKLOAD COST ANALYSIS"
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
        "WORKLOAD COST RANKING"
    )
    print("-" * 80)

    for group in analysis[
        "groups"
    ]:

        print(
            f"\nRank {group['workload_cost_rank']}"
        )

        print(
            f"Profiles              : "
            f"{', '.join(map(str, group['profile_ids']))}"
        )

        print(
            f"Executions            : "
            f"{group['total_executions']}"
        )

        print(
            f"Total time            : "
            f"{group['total_execution_time_ms']:.3f} ms"
        )

        print(
            f"Weighted average      : "
            f"{group['weighted_average_execution_time_ms']:.3f} ms"
        )

        print(
            f"Execution time share  : "
            f"{group['execution_time_share']:.2f}%"
        )

        print(
            f"Execution frequency   : "
            f"{group['execution_frequency_share']:.2f}%"
        )

        print(
            f"Rows processed        : "
            f"{group['total_rows_processed']}"
        )

        print(
            f"Template              : "
            f"{group['normalized_template']}"
        )


# =========================================================
# MAIN
# =========================================================

def main() -> None:
    """
    Run workload cost analysis.
    """

    analysis = (
        analyze_workload_costs()
    )

    print_workload_cost_analysis(
        analysis
    )


# =========================================================
# SCRIPT ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
