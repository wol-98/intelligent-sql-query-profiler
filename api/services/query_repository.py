from __future__ import annotations

from config.database import get_connection


def fetch_query_records(
    fingerprint: str | None = None,
) -> list[dict]:
    """
    Read query-profile records for the M20 dashboard.

    This repository is strictly read-only. It performs no INSERT,
    UPDATE, DELETE, index creation, index removal, or benchmark execution.

    Parameters
    ----------
    fingerprint:
        Optional query fingerprint. When supplied, only the matching
        query profile is returned.
    """

    conn = get_connection()

    try:
        cur = conn.cursor()

        query = """
            SELECT
                qp.query_profile_id,
                qp.query_hash,
                qp.query_text,
                qp.query_type,
                qp.execution_count,
                qp.total_execution_time_ms,
                qp.average_execution_time_ms,
                qp.rows_processed,
                qp.table_name,
                qp.captured_at,
                qp.execution_plan,
                qp.plan_node_type,

                ARRAY_REMOVE(
                    ARRAY_AGG(
                        DISTINCT r.recommendation_id
                    ),
                    NULL
                ) AS recommendation_ids

            FROM query_profiles qp

            LEFT JOIN index_recommendations r
                ON r.query_profile_id = qp.query_profile_id
        """

        params: tuple[str, ...] = ()

        if fingerprint is not None:
            query += """
                WHERE qp.query_hash = %s
            """
            params = (fingerprint,)

        query += """
            GROUP BY
                qp.query_profile_id,
                qp.query_hash,
                qp.query_text,
                qp.query_type,
                qp.execution_count,
                qp.total_execution_time_ms,
                qp.average_execution_time_ms,
                qp.rows_processed,
                qp.table_name,
                qp.captured_at,
                qp.execution_plan,
                qp.plan_node_type

            ORDER BY
                qp.query_profile_id;
        """

        cur.execute(query, params)

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
