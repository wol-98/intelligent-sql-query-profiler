from config.database import get_connection


def fetch_overview_records() -> list[dict]:
    """
    Read recommendation, query-profile, and benchmark evidence
    for the M20 overview.

    This function is strictly read-only.
    It performs no INSERT, UPDATE, DELETE, index creation,
    index removal, or benchmark execution.
    """

    conn = get_connection()

    try:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                r.recommendation_id,
                r.recommendation_score,
                r.priority,

                qp.query_profile_id,
                qp.query_hash,
                qp.query_text,
                qp.query_type,
                qp.execution_count,
                qp.total_execution_time_ms,
                qp.average_execution_time_ms,
                qp.rows_processed,

                b.benchmark_id,
                b.improvement_percentage,
                b.median_improvement_percentage,
                b.rows_preserved,
                b.index_used,
                b.plan_changed,
                b.validation_status

            FROM index_recommendations r

            JOIN query_profiles qp
                ON r.query_profile_id = qp.query_profile_id

            LEFT JOIN benchmark_results b
                ON r.recommendation_id = b.recommendation_id

            ORDER BY
                r.recommendation_id,
                b.benchmark_id;
            """
        )

        columns = [
            description[0]
            for description in cur.description
        ]

        rows = cur.fetchall()

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        cur.close()
        conn.close()
def fetch_recommendation_records(
    recommendation_id: int | None = None,
) -> list[dict]:
    """
    Read recommendation records and their associated query and benchmark
    evidence for the M20 dashboard.

    This function is strictly read-only.
    It performs no INSERT, UPDATE, DELETE, index creation,
    index removal, or benchmark execution.
    """
    conn = get_connection()

    try:
        cur = conn.cursor()

        query = """
            SELECT
                r.recommendation_id,
                r.query_profile_id,
                r.table_name,
                r.column_name,
                r.index_type,
                r.recommendation_score,
                r.priority,
                r.reasoning,
                r.index_sql,
                r.created_at,

                qp.query_hash,
                qp.query_text,
                qp.query_type,
                qp.execution_count,
                qp.total_execution_time_ms,
                qp.average_execution_time_ms,
                qp.rows_processed,
                qp.captured_at,

                b.benchmark_id,
                b.improvement_percentage,
                b.median_improvement_percentage,
                b.execution_time_before_ms,
                b.execution_time_after_ms,
                b.rows_before,
                b.rows_after,
                b.rows_preserved,
                b.index_used,
                b.index_node_type,
                b.plan_changed,
                b.validation_status,
                b.validation_reason,
                b.benchmarked_at

            FROM index_recommendations r

            JOIN query_profiles qp
                ON r.query_profile_id = qp.query_profile_id

            LEFT JOIN benchmark_results b
                ON r.recommendation_id = b.recommendation_id
        """

        params: tuple[int, ...] = ()

        if recommendation_id is not None:
            query += """
                WHERE r.recommendation_id = %s
            """
            params = (recommendation_id,)

        query += """
            ORDER BY
                r.recommendation_id,
                b.benchmark_id;
        """

        cur.execute(query, params)

        columns = [description[0] for description in cur.description]
        rows = cur.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    finally:
        cur.close()
        conn.close()
