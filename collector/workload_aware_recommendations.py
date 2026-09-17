"""
Workload-Aware Recommendation Integration
------------------------------------------
Combines the existing index recommendation engine
with workload-level cost information.

This module DOES NOT change the original
recommendation score or recommendation priority.

It adds workload context so that recommendations
can be prioritized using observed workload importance.
"""

from collector.query_parser import parse_query
from collector.workload_cost_analyzer import analyze_workload_costs
from collector.workload_recommendation_prioritizer import (
    build_workload_lookup,
    calculate_workload_priority,
)


def enrich_recommendations_with_workload(
    recommendations,
    workload_analysis=None,
):
    """
    Add workload-level information to existing
    recommendations.

    Parameters
    ----------
    recommendations : list of dict
        Recommendations produced by the existing
        recommendation engine.

    workload_analysis : dict, optional
        Output from analyze_workload_costs().

    Returns
    -------
    list of dict
        Recommendations enriched with workload metrics.
    """

    if workload_analysis is None:
        workload_analysis = analyze_workload_costs()

    workload_lookup = build_workload_lookup(
        workload_analysis
    )

    enriched_recommendations = []

    for recommendation in recommendations:

        enriched = recommendation.copy()

        query_text = recommendation.get(
            "query_text",
            ""
        )

        if not query_text:

            enriched.update({
                "workload_cost_rank": None,
                "execution_time_share": 0.0,
                "execution_frequency_share": 0.0,
                "total_executions": 0,
                "total_execution_time_ms": 0.0,
                "weighted_average_execution_time_ms": 0.0,
                "total_rows_processed": 0,
                "workload_priority": "Unknown",
            })

            enriched_recommendations.append(
                enriched
            )

            continue

        parsed_query = parse_query(
            query_text
        )

        fingerprint = parsed_query[
            "fingerprint"
        ]

        workload_metrics = workload_lookup.get(
            fingerprint
        )

        if workload_metrics is None:

            enriched.update({
                "workload_cost_rank": None,
                "execution_time_share": 0.0,
                "execution_frequency_share": 0.0,
                "total_executions": 0,
                "total_execution_time_ms": 0.0,
                "weighted_average_execution_time_ms": 0.0,
                "total_rows_processed": 0,
                "workload_priority": "Unknown",
            })

        else:

            workload_priority = calculate_workload_priority(
                workload_metrics[
                    "execution_time_share"
                ],
                workload_metrics[
                    "execution_frequency_share"
                ],
            )

            enriched.update(
                workload_metrics
            )

            enriched[
                "workload_priority"
            ] = workload_priority

        enriched_recommendations.append(
            enriched
        )

    return enriched_recommendations


def workload_priority_value(
    workload_priority
):
    """
    Convert workload priority to a sortable value.

    This does not alter the original recommendation score.
    """

    priority_values = {
        "Critical": 4,
        "High": 3,
        "Moderate": 2,
        "Low": 1,
        "Unknown": 0,
    }

    return priority_values.get(
        workload_priority,
        0
    )


def rank_workload_aware_recommendations(
    recommendations
):
    """
    Rank recommendations using workload importance first,
    followed by the original recommendation score.

    Workload priority is used only as a prioritization
    dimension. The original score remains unchanged.
    """

    ranked = list(
        recommendations
    )

    ranked.sort(
        key=lambda recommendation: (
            workload_priority_value(
                recommendation.get(
                    "workload_priority",
                    "Unknown"
                )
            ),
            recommendation.get(
                "execution_time_share",
                0.0
            ),
            recommendation.get(
                "score",
                0
            ),
        ),
        reverse=True,
    )

    return ranked


def integrate_workload_awareness(
    recommendations,
    workload_analysis=None,
):
    """
    Complete M13.4 integration.

    Steps:
        1. Enrich recommendations with workload data.
        2. Rank using workload importance.
        3. Preserve the original recommendation score.
    """

    enriched = enrich_recommendations_with_workload(
        recommendations,
        workload_analysis,
    )

    ranked = rank_workload_aware_recommendations(
        enriched
    )

    return ranked


def print_workload_aware_recommendations(
    recommendations
):
    """
    Display workload-aware recommendation results.
    """

    print("\n" + "=" * 80)
    print("M13 — WORKLOAD-AWARE INDEX RECOMMENDATIONS")
    print("=" * 80)

    if not recommendations:

        print(
            "No recommendations available."
        )

        print("=" * 80)

        return

    for number, recommendation in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"\nRecommendation {number}"
        )

        print(
            f"  Table                 : "
            f"{recommendation.get('table_name', 'N/A')}"
        )

        print(
            f"  Column                : "
            f"{recommendation.get('column_name', 'N/A')}"
        )

        print(
            f"  Recommendation score  : "
            f"{recommendation.get('score', 'N/A')}/100"
        )

        print(
            f"  Recommendation priority: "
            f"{recommendation.get('priority', 'N/A')}"
        )

        print(
            f"  Workload rank         : "
            f"{recommendation.get('workload_cost_rank', 'N/A')}"
        )

        print(
            f"  Workload priority     : "
            f"{recommendation.get('workload_priority', 'Unknown')}"
        )

        print(
            f"  Execution time share  : "
            f"{recommendation.get('execution_time_share', 0.0):.2f}%"
        )

        print(
            f"  Frequency share       : "
            f"{recommendation.get('execution_frequency_share', 0.0):.2f}%"
        )

        print(
            f"  Total executions      : "
            f"{recommendation.get('total_executions', 0)}"
        )

        print(
            f"  Total execution time  : "
            f"{recommendation.get('total_execution_time_ms', 0.0):.3f} ms"
        )

        print(
            f"  Weighted average      : "
            f"{recommendation.get('weighted_average_execution_time_ms', 0.0):.3f} ms"
        )

        print(
            f"  Original score preserved: "
            f"{recommendation.get('score', 'N/A')}/100"
        )

    print("\n" + "=" * 80)


def main():
    """
    Standalone module check.

    Full recommendation integration requires
    recommendation objects produced by the
    recommendation engine.
    """

    workload_analysis = analyze_workload_costs()

    print(
        "\nWorkload-aware recommendation integration "
        "initialized successfully."
    )

    print(
        f"Workload fingerprints available: "
        f"{workload_analysis['unique_fingerprints']}"
    )


if __name__ == "__main__":
    main()
