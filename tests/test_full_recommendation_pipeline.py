"""
Full Recommendation Pipeline Test
----------------------------------
Processes the 15 official workload queries:

query_profiles
      ↓
plan_analyzer
      ↓
feature_extractor
      ↓
query_parser
      ↓
index_candidate_generator
      ↓
recommendation_engine
      ↓
recommendation_repository
"""

from config.database import get_connection

from collector.plan_analyzer import analyze_plan
from collector.feature_extractor import extract_plan_features
from collector.query_parser import parse_query
from collector.index_candidate_generator import (
    generate_index_candidates
)
from collector.recommendation_engine import (
    score_index_candidates
)
from collector.recommendation_repository import (
    save_recommendations
)


def get_root_plan(execution_plan):
    """
    Extract the root plan from PostgreSQL's
    EXPLAIN JSON structure.
    """
    if isinstance(execution_plan, list):
        execution_plan = execution_plan[0]

    return execution_plan["Plan"]


def main():

    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                query_profile_id,
                query_text,
                execution_plan
            FROM query_profiles
            ORDER BY query_profile_id;
        """)

        profiles = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    print("\n" + "=" * 80)
    print("FULL RECOMMENDATION PIPELINE")
    print("=" * 80)

    print(f"\nQuery profiles found: {len(profiles)}")

    total_candidates = 0
    total_recommendations = 0

    for (
        query_profile_id,
        query_text,
        execution_plan
    ) in profiles:

        print("\n" + "-" * 80)
        print(f"Query Profile ID : {query_profile_id}")

        # --------------------------------------------------
        # 1. Extract root execution plan
        # --------------------------------------------------

        root_plan = get_root_plan(execution_plan)

        # --------------------------------------------------
        # 2. Analyze execution plan
        # --------------------------------------------------

        plan_nodes = analyze_plan(root_plan)

        # --------------------------------------------------
        # 3. Extract plan features
        # --------------------------------------------------

        features = extract_plan_features(plan_nodes)

        # --------------------------------------------------
        # 4. Parse SQL query
        # --------------------------------------------------

        query_metadata = parse_query(query_text)

        # --------------------------------------------------
        # 5. Generate index candidates
        # --------------------------------------------------

        candidates = generate_index_candidates(
            features,
            query_metadata
        )

        total_candidates += len(candidates)

        # --------------------------------------------------
        # 6. Score candidates
        # --------------------------------------------------

        recommendations = score_index_candidates(
            candidates,
            features,
            query_metadata
        )

        total_recommendations += len(recommendations)

        # --------------------------------------------------
        # 7. Persist recommendations
        # --------------------------------------------------

        saved_ids = save_recommendations(
            query_profile_id,
            recommendations
        )

        print(f"Candidates generated : {len(candidates)}")
        print(f"Recommendations      : {len(recommendations)}")
        print(f"Saved recommendation IDs: {saved_ids}")

        for i, recommendation in enumerate(
            recommendations,
            start=1
        ):

            print(
                f"  {i}. "
                f"{recommendation['table_name']}."
                f"{recommendation['column_name']} "
                f"| Score: {recommendation['score']:.0f} "
                f"| Priority: {recommendation['priority']}"
            )

    print("\n" + "=" * 80)
    print("RECOMMENDATION PIPELINE SUMMARY")
    print("=" * 80)

    print(f"Queries processed       : {len(profiles)}")
    print(f"Total candidates        : {total_candidates}")
    print(f"Total recommendations   : {total_recommendations}")

    print("\nRecommendation generation completed successfully.")


if __name__ == "__main__":
    main()
