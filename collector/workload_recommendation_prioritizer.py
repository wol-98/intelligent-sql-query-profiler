"""
Workload-Aware Recommendation Prioritizer
-----------------------------------------
Enriches index recommendations with workload-level
importance derived from profiled query fingerprints.

This module does not modify the database and does not
change the original recommendation score.

The purpose is to distinguish:
    1. Query-level optimization relevance
    2. Workload-level importance

The existing recommendation score remains untouched.
"""

from collector.query_parser import parse_query
from collector.workload_cost_analyzer import analyze_workload_costs


def build_workload_lookup(workload_analysis: dict) -> dict:
    """
    Build a fingerprint -> workload metrics lookup.
    """

    lookup = {}

    for group in workload_analysis["groups"]:
        lookup[group["fingerprint"]] = {
            "workload_cost_rank": group["workload_cost_rank"],
            "execution_time_share": group["execution_time_share"],
            "execution_frequency_share": group["execution_frequency_share"],
            "total_executions": group["total_executions"],
            "total_execution_time_ms": group["total_execution_time_ms"],
            "weighted_average_execution_time_ms": (
                group["weighted_average_execution_time_ms"]
            ),
            "total_rows_processed": group["total_rows_processed"],
        }

    return lookup


def calculate_workload_priority(
    execution_time_share: float,
    execution_frequency_share: float,
) -> str:
    """
    Classify workload importance using observed
    execution-time and execution-frequency shares.

    The classification is intentionally separate from
    the existing recommendation score.
    """

    if execution_time_share >= 50:
        return "Critical"

    if execution_time_share >= 10:
        return "High"

    if execution_time_share >= 5:
        return "Moderate"

    if execution_frequency_share >= 10:
        return "Moderate"

    return "Low"


def enrich_recommendations(
    recommendations: list,
    workload_analysis: dict | None = None,
) -> list:
    """
    Add workload-aware metrics to recommendations.

    Each recommendation is matched to its SQL query
    fingerprint using query_parser.parse_query().
    """

    if workload_analysis is None:
        workload_analysis = analyze_workload_costs()

    workload_lookup = build_workload_lookup(workload_analysis)

    enriched = []

    for recommendation in recommendations:

        query_text = recommendation.get("query_text", "")

        if not query_text:
            enriched.append({
                **recommendation,
                "workload_cost_rank": None,
                "execution_time_share": 0.0,
                "execution_frequency_share": 0.0,
                "total_executions": 0,
                "total_execution_time_ms": 0.0,
                "weighted_average_execution_time_ms": 0.0,
                "total_rows_processed": 0,
                "workload_priority": "Unknown",
            })
            continue

        parsed = parse_query(query_text)

        fingerprint = parsed["fingerprint"]

        workload_metrics = workload_lookup.get(fingerprint)

        if workload_metrics is None:
            enriched.append({
                **recommendation,
                "workload_cost_rank": None,
                "execution_time_share": 0.0,
                "execution_frequency_share": 0.0,
                "total_executions": 0,
                "total_execution_time_ms": 0.0,
                "weighted_average_execution_time_ms": 0.0,
                "total_rows_processed": 0,
                "workload_priority": "Unknown",
            })
            continue

        workload_priority = calculate_workload_priority(
            workload_metrics["execution_time_share"],
            workload_metrics["execution_frequency_share"],
        )

        enriched.append({
            **recommendation,
            **workload_metrics,
            "workload_priority": workload_priority,
        })

    return enriched


def print_workload_recommendations(
    recommendations: list,
) -> None:
    """
    Display workload-aware recommendation information.
    """

    print("\n" + "=" * 80)
    print("M13 — WORKLOAD-AWARE RECOMMENDATION PRIORITIZATION")
    print("=" * 80)

    for recommendation in recommendations:

        print("\n" + "-" * 80)

        print(
            f"Profile ID            : "
            f"{recommendation.get('query_profile_id', 'N/A')}"
        )

        print(
            f"Recommendation        : "
            f"{recommendation.get('table_name', 'N/A')}."
            f"{recommendation.get('column_name', 'N/A')}"
        )

        print(
            f"Recommendation score  : "
            f"{recommendation.get('score', 'N/A')}"
        )

        print(
            f"Workload rank         : "
            f"{recommendation.get('workload_cost_rank', 'N/A')}"
        )

        print(
            f"Execution time share  : "
            f"{recommendation.get('execution_time_share', 0.0):.2f}%"
        )

        print(
            f"Frequency share       : "
            f"{recommendation.get('execution_frequency_share', 0.0):.2f}%"
        )

        print(
            f"Total executions      : "
            f"{recommendation.get('total_executions', 0)}"
        )

        print(
            f"Total execution time  : "
            f"{recommendation.get('total_execution_time_ms', 0.0):.3f} ms"
        )

        print(
            f"Weighted average      : "
            f"{recommendation.get('weighted_average_execution_time_ms', 0.0):.3f} ms"
        )

        print(
            f"Workload priority     : "
            f"{recommendation.get('workload_priority', 'Unknown')}"
        )


def main() -> None:
    """
    Standalone demonstration.
    """

    workload_analysis = analyze_workload_costs()

    print(
        "\nWorkload prioritization module initialized successfully."
    )

    print(
        f"Available fingerprints: "
        f"{workload_analysis['unique_fingerprints']}"
    )


if __name__ == "__main__":
    main()
