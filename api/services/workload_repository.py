
from config.database import get_connection


def fetch_workload_records():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    query_profile_id,
                    query_hash,
                    query_text,
                    query_type,
                    execution_count,
                    total_execution_time_ms,
                    average_execution_time_ms
                FROM query_profiles
                ORDER BY query_profile_id
                """
            )

            profile_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    recommendation_id,
                    query_profile_id
                FROM index_recommendations
                ORDER BY recommendation_id
                """
            )

            recommendation_rows = cursor.fetchall()

        return profile_rows, recommendation_rows
    finally:
        connection.close()
