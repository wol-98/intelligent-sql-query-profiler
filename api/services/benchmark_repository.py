from __future__ import annotations

from config.database import get_connection


def fetch_benchmark_records(
    benchmark_id: int | None = None,
) -> list[dict]:
    """
    Read-only access to stored benchmark evidence.

    This repository:
    - reads benchmark_results only;
    - does not execute benchmark experiments;
    - does not create or remove indexes;
    - does not modify benchmark evidence.
    """

    conn = get_connection()

    try:
        cur = conn.cursor()

        query = """
            SELECT
                b.benchmark_id,
                b.recommendation_id,
                b.query_text,
                b.execution_time_before_ms,
                b.execution_time_after_ms,
                b.improvement_percentage,
                b.median_before_ms,
                b.median_after_ms,
                b.median_improvement_percentage,
                b.rows_before,
                b.rows_after,
                b.rows_preserved,
                b.index_used,
                b.index_node_type,
                b.plan_changed,
                b.before_plan,
                b.after_plan,
                b.validation_status,
                b.validation_reason,
                b.benchmarked_at
            FROM benchmark_results b
        """

        params: tuple[int, ...] = ()

        if benchmark_id is not None:
            query += """
                WHERE b.benchmark_id = %s
            """
            params = (benchmark_id,)

        query += """
            ORDER BY b.benchmark_id
        """

        cur.execute(query, params)

        columns = [description[0] for description in cur.description]

        return [
            dict(zip(columns, row))
            for row in cur.fetchall()
        ]

    finally:
        cur.close()
        conn.close()
