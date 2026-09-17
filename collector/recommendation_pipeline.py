"""
Recommendation Pipeline
-----------------------
Canonical orchestration layer for SQL index recommendations.

Pipeline:

    Query
      ↓
    Parse
      ↓
    Candidate Generation
      ↓
    Candidate Scoring
      ↓
    Workload-Aware Enrichment
      ↓
    Workload-Aware Ranking

This module does not create or modify indexes.
"""

from collector.query_parser import parse_query
from collector.index_candidate_generator import (
    generate_index_candidates,
)
from collector.recommendation_engine import (
    score_index_candidates,
)
from collector.workload_aware_recommendations import (
    integrate_workload_awareness,
)


def generate_recommendations(
    query_text,
    features,
):
    """
    Generate workload-aware index recommendations
    for a SQL query.

    Parameters
    ----------
    query_text : str
        SQL query to analyze.

    features : dict
        Execution-plan features extracted by the
        collector feature extractor.

    Returns
    -------
    list of dict
        Workload-aware ranked recommendations.
    """

    # -------------------------------------------------
    # 1. Parse query
    # -------------------------------------------------

    query_metadata = parse_query(
        query_text
    )

    # -------------------------------------------------
    # 2. Generate index candidates
    # -------------------------------------------------

    candidates = generate_index_candidates(
        query_text,
        query_metadata
    )

    if not candidates:
        return []

    # -------------------------------------------------
    # 3. Score candidates
    # -------------------------------------------------

    recommendations = score_index_candidates(
        candidates,
        features,
        query_metadata,
    )

    # -------------------------------------------------
    # 4. Attach query information
    # -------------------------------------------------

    for recommendation in recommendations:

        recommendation[
            "query_text"
        ] = query_text

        recommendation[
            "fingerprint"
        ] = query_metadata[
            "fingerprint"
        ]

        recommendation[
            "normalized_template"
        ] = query_metadata[
            "normalized_template"
        ]

    # -------------------------------------------------
    # 5. Apply workload awareness
    # -------------------------------------------------

    workload_aware_recommendations = (
        integrate_workload_awareness(
            recommendations
        )
    )

    return workload_aware_recommendations


def print_pipeline_summary(
    query_text,
    recommendations,
):
    """
    Print a concise recommendation pipeline summary.
    """

    print("\n" + "=" * 80)
    print("RECOMMENDATION PIPELINE")
    print("=" * 80)

    print(
        f"Query: {query_text}"
    )

    print(
        f"Recommendations generated: "
        f"{len(recommendations)}"
    )

    if not recommendations:

        print(
            "No recommendations generated."
        )

        print("=" * 80)

        return

    for number, recommendation in enumerate(
        recommendations,
        start=1,
    ):

        print(
            f"\nRecommendation {number}"
        )

        print(
            f"  Index candidate       : "
            f"{recommendation['table_name']}."
            f"{recommendation['column_name']}"
        )

        print(
            f"  Recommendation score  : "
            f"{recommendation['score']}/100"
        )

        print(
            f"  Recommendation priority: "
            f"{recommendation['priority']}"
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

    print("\n" + "=" * 80)
