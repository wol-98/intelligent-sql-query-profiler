"""
Backfill Validation Evidence
----------------------------
Backfills validation metadata for existing benchmark_results
without rerunning benchmark experiments.

Recovered fields:
- rows_preserved
- index_used
- index_node_type
- plan_changed

Median metrics are not reconstructed because the original
benchmark_results table did not store individual run timings.
"""

import ast
import json

from config.database import get_connection


def parse_plan(value):
    """
    Convert the stored textual Python-dict representation
    back into a dictionary.
    """

    if isinstance(value, dict):
        return value

    if not value:
        return None

    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return None


def find_index_usage(plan, index_name):
    """
    Recursively search an execution plan for an index name.
    """

    if not isinstance(plan, dict):
        return {
            "used": False,
            "node_type": None,
        }

    if plan.get("Index Name") == index_name:
        return {
            "used": True,
            "node_type": plan.get("Node Type"),
        }

    for child in plan.get("Plans", []):
        result = find_index_usage(child, index_name)

        if result["used"]:
            return result

    return {
        "used": False,
        "node_type": None,
    }


def plans_are_different(before_plan, after_plan):
    """
    Compare execution plans structurally.
    """

    return (
        json.dumps(before_plan, sort_keys=True)
        !=
        json.dumps(after_plan, sort_keys=True)
    )


def get_benchmark_records():
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                benchmark_id,
                recommendation_id,
                rows_before,
                rows_after,
                before_plan,
                after_plan
            FROM benchmark_results
            ORDER BY benchmark_id;
        """)

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()


def get_recommendation_details(recommendation_id):
    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                table_name,
                column_name
            FROM index_recommendations
            WHERE recommendation_id = %s;
        """, (recommendation_id,))

        return cur.fetchone()

    finally:
        cur.close()
        conn.close()


def backfill():
    records = get_benchmark_records()

    print("\n" + "=" * 90)
    print("BACKFILL VALIDATION EVIDENCE")
    print("=" * 90)

    conn = get_connection()

    try:
        cur = conn.cursor()

        updated = 0

        for row in records:

            (
                benchmark_id,
                recommendation_id,
                rows_before,
                rows_after,
                before_plan_text,
                after_plan_text,
            ) = row

            recommendation = get_recommendation_details(
                recommendation_id
            )

            if recommendation is None:
                print(
                    f"Skipping Benchmark {benchmark_id}: "
                    f"Recommendation {recommendation_id} not found."
                )
                continue

            table_name, column_name = recommendation

            index_name = (
                f"idx_{table_name}_{column_name}"
            )

            before_plan = parse_plan(
                before_plan_text
            )

            after_plan = parse_plan(
                after_plan_text
            )

            index_usage = find_index_usage(
                after_plan,
                index_name
            )

            rows_preserved = (
                rows_before == rows_after
            )

            plan_changed = plans_are_different(
                before_plan,
                after_plan
            )

            cur.execute("""
                UPDATE benchmark_results
                SET
                    rows_preserved = %s,
                    index_used = %s,
                    index_node_type = %s,
                    plan_changed = %s
                WHERE benchmark_id = %s;
            """, (
                rows_preserved,
                index_usage["used"],
                index_usage["node_type"],
                plan_changed,
                benchmark_id,
            ))

            updated += 1

            print(
                f"Benchmark {benchmark_id:>2} | "
                f"Recommendation {recommendation_id:>2} | "
                f"{table_name}.{column_name:<25} | "
                f"Index used: {str(index_usage['used']):<5} | "
                f"Rows preserved: {str(rows_preserved):<5} | "
                f"Plan changed: {str(plan_changed):<5}"
            )

        conn.commit()

        print("\n" + "-" * 90)
        print(f"Records updated: {updated}")
        print("-" * 90)

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    backfill()
