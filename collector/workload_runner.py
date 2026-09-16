import sqlparse

from collector.query_collector import (
    collect_query_profile,
    save_query_profile,
    print_profile
)


WORKLOAD_FILE = "database/workload.sql"


def load_workload(filename: str) -> list[str]:
    """
    Load SQL statements from the workload file.

    Comments are removed and each SQL statement is
    returned separately.
    """

    with open(filename, "r", encoding="utf-8") as file:
        sql_text = file.read()

    statements = sqlparse.split(
        sqlparse.format(
            sql_text,
            strip_comments=True
        )
    )

    queries = []

    for statement in statements:

        statement = statement.strip()

        if statement:
            queries.append(statement)

    return queries


def run_workload():
    """
    Execute every query in the workload through
    the query collector.
    """

    queries = load_workload(WORKLOAD_FILE)

    print()
    print("=" * 65)
    print("INTELLIGENT SQL QUERY PROFILER")
    print("BASELINE WORKLOAD")
    print("=" * 65)

    print(f"Workload file : {WORKLOAD_FILE}")
    print(f"Total queries : {len(queries)}")

    print("=" * 65)

    successful = 0
    failed = 0

    for number, query in enumerate(
        queries,
        start=1
    ):

        print()
        print("-" * 65)
        print(f"QUERY Q{number:03d}")
        print("-" * 65)

        print(query)

        try:

            profile = collect_query_profile(
                query
            )

            profile_id = save_query_profile(
                profile
            )

            print_profile(
                profile,
                profile_id
            )

            successful += 1

        except Exception as error:

            failed += 1

            print()
            print("ERROR")
            print(error)

    print()
    print("=" * 65)
    print("WORKLOAD COMPLETE")
    print("=" * 65)

    print(f"Successful : {successful}")
    print(f"Failed     : {failed}")
    print(f"Total      : {len(queries)}")

    print("=" * 65)


if __name__ == "__main__":
    run_workload()
