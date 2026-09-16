"""
Candidate Generation Diagnostics
---------------------------------
Checks SQL parsing and index candidate generation
for every query profile.

This test does NOT create or modify indexes.
"""

from config.database import get_connection

from collector.plan_analyzer import analyze_plan
from collector.feature_extractor import extract_plan_features
from collector.query_parser import parse_query
from collector.index_candidate_generator import (
    generate_index_candidates
)


def get_root_plan(execution_plan):
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
            WHERE query_profile_id BETWEEN 2 AND 16
            ORDER BY query_profile_id;
        """)

        profiles = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    print("\n" + "=" * 100)
    print("CANDIDATE GENERATION DIAGNOSTICS")
    print("=" * 100)

    for profile_id, query_text, execution_plan in profiles:

        print("\n" + "-" * 100)
        print(f"PROFILE {profile_id}")
        print("-" * 100)

        print("\nSQL:")
        print(query_text.strip())

        # --------------------------------------------------
        # Execution plan
        # --------------------------------------------------

        root_plan = get_root_plan(execution_plan)

        plan_nodes = analyze_plan(root_plan)

        features = extract_plan_features(plan_nodes)

        # --------------------------------------------------
        # SQL parser
        # --------------------------------------------------

        metadata = parse_query(query_text)

        print("\nParsed metadata:")
        print(f"  Tables       : {metadata.get('tables')}")
        print(f"  Aliases      : {metadata.get('aliases')}")
        print(f"  WHERE        : {metadata.get('where_columns')}")
        print(f"  JOIN         : {metadata.get('join_columns')}")
        print(f"  ORDER BY     : {metadata.get('order_by_columns')}")
        print(f"  GROUP BY     : {metadata.get('group_by_columns')}")

        # --------------------------------------------------
        # Plan features
        # --------------------------------------------------

        print("\nPlan features:")
        print(f"  Tables       : {features.get('tables')}")
        print(f"  Seq scans    : {features.get('seq_scan_count')}")
        print(f"  Index scans  : {features.get('index_scan_count')}")
        print(f"  Bitmap scans : {features.get('bitmap_scan_count')}")
        print(f"  Has filter   : {features.get('has_filter')}")
        print(f"  Has join     : {features.get('has_join')}")
        print(f"  Has index condition: {features.get('has_index_condition')}")

        # --------------------------------------------------
        # Candidate generation
        # --------------------------------------------------

        candidates = generate_index_candidates(
            features,
            metadata
        )

        print("\nCandidates:")

        if not candidates:
            print("  *** NO CANDIDATES GENERATED ***")
        else:
            for candidate in candidates:
                print(
                    f"  - {candidate['table_name']}."
                    f"{candidate['column_name']} "
                    f"| Type: {candidate['index_type']} "
                    f"| Reason: {candidate['reason']} "
                    f"| Source: {candidate['source']}"
                )

    print("\n" + "=" * 100)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()
