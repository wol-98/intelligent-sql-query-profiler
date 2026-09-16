"""
Validation Decision Layer Test
------------------------------
Reads existing benchmark evidence and assigns
SUCCESSFUL, NEUTRAL, UNSUCCESSFUL, or UNSAFE.

No benchmarks are executed.
No indexes are created.
"""

from config.database import get_connection
from collector.validation_decision import evaluate_validation


def get_benchmark_results():

    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                benchmark_id,
                recommendation_id,
                execution_time_before_ms,
                execution_time_after_ms,
                improvement_percentage,
                median_improvement_percentage,
                rows_before,
                rows_after,
                rows_preserved,
                index_used,
                index_node_type,
                plan_changed
            FROM benchmark_results
            ORDER BY benchmark_id;
        """)

        return cur.fetchall()

    finally:
        cur.close()
        conn.close()


def save_decision(
    benchmark_id,
    status,
    reason
):

    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            UPDATE benchmark_results
            SET
                validation_status = %s,
                validation_reason = %s
            WHERE benchmark_id = %s;
        """, (
            status,
            reason,
            benchmark_id,
        ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


def main():

    rows = get_benchmark_results()

    print("\n" + "=" * 110)
    print("M10 — VALIDATION DECISION LAYER")
    print("=" * 110)

    print(
        f"Benchmark records found : {len(rows)}"
    )

    print(
        "Benchmarks executed     : NO"
    )

    print(
        "Indexes created         : NO"
    )

    print("=" * 110)

    counts = {
        "SUCCESSFUL": 0,
        "NEUTRAL": 0,
        "UNSUCCESSFUL": 0,
        "UNSAFE": 0,
    }

    for row in rows:

        (
            benchmark_id,
            recommendation_id,
            before_ms,
            after_ms,
            improvement,
            median_improvement,
            rows_before,
            rows_after,
            rows_preserved,
            index_used,
            index_node_type,
            plan_changed,
        ) = row

        result = {
            "improvement_percentage": improvement,
            "median_improvement_percentage":
                median_improvement,
            "rows_before": rows_before,
            "rows_after": rows_after,
            "rows_preserved": rows_preserved,
            "index_used": index_used,
            "index_node_type": index_node_type,
            "plan_changed": plan_changed,
        }

        decision = evaluate_validation(
            result
        )

        save_decision(
            benchmark_id,
            decision["status"],
            decision["reason"],
        )

        counts[
            decision["status"]
        ] += 1

        metric = decision[
            "improvement_percentage"
        ]

        print(
            f"Benchmark {benchmark_id:>2} | "
            f"Recommendation {recommendation_id:>2} | "
            f"{decision['status']:<13} | "
            f"{metric:>8.2f}% | "
            f"Index used: "
            f"{str(index_used):<5} | "
            f"Rows preserved: "
            f"{str(rows_preserved):<5}"
        )

    print("\n" + "=" * 110)
    print("DECISION SUMMARY")
    print("=" * 110)

    for status, count in counts.items():
        print(
            f"{status:<15}: {count}"
        )

    print("=" * 110)


if __name__ == "__main__":
    main()
