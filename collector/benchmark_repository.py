"""
Benchmark Result Repository
---------------------------
Persists BEFORE/AFTER benchmark and validation evidence.
"""

from datetime import datetime

from config.database import get_connection


def save_benchmark_result(
    recommendation_id,
    query_text,
    validation_result
):
    """
    Save a benchmark and its validation evidence.
    """

    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO benchmark_results (
                recommendation_id,
                query_text,

                execution_time_before_ms,
                execution_time_after_ms,
                improvement_percentage,

                median_before_ms,
                median_after_ms,
                median_improvement_percentage,

                rows_before,
                rows_after,
                rows_preserved,

                index_used,
                index_node_type,
                plan_changed,

                before_plan,
                after_plan,

                validation_status,
                validation_reason,

                benchmarked_at
            )
            VALUES (
                %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s,
                %s
            )
            RETURNING benchmark_id;
        """, (
            recommendation_id,
            query_text,

            validation_result[
                "execution_time_before_ms"
            ],

            validation_result[
                "execution_time_after_ms"
            ],

            validation_result[
                "improvement_percentage"
            ],

            validation_result.get(
                "median_before_ms"
            ),

            validation_result.get(
                "median_after_ms"
            ),

            validation_result.get(
                "median_improvement_percentage"
            ),

            validation_result[
                "rows_before"
            ],

            validation_result[
                "rows_after"
            ],

            validation_result.get(
                "rows_preserved"
            ),

            validation_result.get(
                "index_used"
            ),

            validation_result.get(
                "index_node_type"
            ),

            validation_result.get(
                "plan_changed"
            ),

            str(
                validation_result[
                    "before_plan"
                ]
            ),

            str(
                validation_result[
                    "after_plan"
                ]
            ),

            validation_result.get(
                "validation_status"
            ),

            validation_result.get(
                "validation_reason"
            ),

            datetime.now()
        ))

        benchmark_id = cur.fetchone()[0]

        conn.commit()

        return benchmark_id

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


def update_validation_decision(
    benchmark_id,
    status,
    reason
):
    """
    Store the final validation decision.
    """

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


def print_saved_benchmark(benchmark_id):
    """
    Print one stored benchmark result.
    """

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
                plan_changed,
                validation_status,
                validation_reason,
                benchmarked_at
            FROM benchmark_results
            WHERE benchmark_id = %s;
        """, (benchmark_id,))

        row = cur.fetchone()

        if row is None:
            print(
                f"No benchmark found for ID {benchmark_id}."
            )
            return

        print("\n" + "=" * 90)
        print("STORED BENCHMARK")
        print("=" * 90)

        labels = [
            "Benchmark ID",
            "Recommendation ID",
            "Average before",
            "Average after",
            "Average improvement",
            "Median improvement",
            "Rows before",
            "Rows after",
            "Rows preserved",
            "Index used",
            "Index node",
            "Plan changed",
            "Validation status",
            "Validation reason",
            "Benchmarked at",
        ]

        for label, value in zip(labels, row):
            print(f"{label:<25}: {value}")

        print("=" * 90)

    finally:
        cur.close()
        conn.close()
