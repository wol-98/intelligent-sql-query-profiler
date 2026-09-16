from config.database import get_connection


def main():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                current_database(),
                current_user,
                version();
            """
        )

        database, user, version = cursor.fetchone()

        print()
        print("=" * 50)
        print("   SUPABASE CONNECTION SUCCESSFUL")
        print("=" * 50)
        print(f"Database : {database}")
        print(f"User     : {user}")
        print(f"Postgres : {version}")
        print("=" * 50)
        print()

    except Exception as error:
        print()
        print("DATABASE CONNECTION FAILED")
        print(error)
        print()

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    main()

