from __future__ import annotations

import statistics
import time

from config.database import get_connection
from collector.index_validator import validate_identifier
from collector.index_maintenance_experiment import (
    build_maintenance_result,
)


TABLE_NAME = "m17_2_orders_write_test"
INDEX_NAME = "m17_2_idx_customer_id"

SOURCE_TABLE = "orders"
INDEXED_COLUMN = "customer_id"

ROWS_PER_ITERATION = 10_000
WARMUP_ITERATIONS = 2
MEASURED_ITERATIONS = 5


def execute_write_batch(connection, start_id: int, row_count: int) -> float:
    """Insert a controlled batch and measure execution time."""

    cursor = connection.cursor()

    start = time.perf_counter()

    cursor.execute(
        f"""
        INSERT INTO {TABLE_NAME}
        (
            customer_id,
            order_date,
            status,
            total_amount
        )
        SELECT
            customer_id,
            order_date,
            status,
            total_amount
        FROM {SOURCE_TABLE}
        ORDER BY order_id
        OFFSET %s
        LIMIT %s
        """,
        (start_id, row_count),
    )

    connection.commit()

    end = time.perf_counter()

    cursor.close()

    return (end - start) * 1000.0


def create_experiment_table(connection) -> None:
    cursor = connection.cursor()

    cursor.execute(
        f"""
        DROP TABLE IF EXISTS {TABLE_NAME}
        """
    )

    cursor.execute(
        f"""
        CREATE TABLE {TABLE_NAME} AS
        SELECT
            customer_id,
            order_date,
            status,
            total_amount
        FROM {SOURCE_TABLE}
        WHERE FALSE
        """
    )

    connection.commit()
    cursor.close()


def clear_experiment_table(connection) -> None:
    cursor = connection.cursor()

    cursor.execute(
        f"""
        TRUNCATE TABLE {TABLE_NAME}
        """
    )

    connection.commit()
    cursor.close()


def create_experiment_index(connection) -> None:
    cursor = connection.cursor()

    cursor.execute(
        f"""
        CREATE INDEX {INDEX_NAME}
        ON {TABLE_NAME} USING BTREE ({INDEXED_COLUMN})
        """
    )

    connection.commit()
    cursor.close()


def drop_experiment_index(connection) -> None:
    cursor = connection.cursor()

    cursor.execute(
        f"""
        DROP INDEX IF EXISTS {INDEX_NAME}
        """
    )

    connection.commit()
    cursor.close()


def drop_experiment_table(connection) -> None:
    cursor = connection.cursor()

    cursor.execute(
        f"""
        DROP TABLE IF EXISTS {TABLE_NAME}
        """
    )

    connection.commit()
    cursor.close()


def run_condition(
    connection,
    condition_name: str,
    indexed: bool,
) -> list[float]:
    """
    Run warm-ups followed by measured write iterations.
    """

    print()
    print(f"{condition_name} condition")

    if indexed:
        print("Experimental index is present.")
    else:
        print("No secondary index is present.")

    # --------------------------------------------------------------
    # Warm-up
    # --------------------------------------------------------------

    print()
    print("Warm-up iterations:")

    for iteration in range(WARMUP_ITERATIONS):
        clear_experiment_table(connection)

        elapsed = execute_write_batch(
            connection,
            0,
            ROWS_PER_ITERATION,
        )

        print(
            f"  Warm-up {iteration + 1}: "
            f"{elapsed:.4f} ms"
        )

    # --------------------------------------------------------------
    # Measured iterations
    # --------------------------------------------------------------

    measured_times = []

    print()
    print("Measured iterations:")

    for iteration in range(MEASURED_ITERATIONS):
        clear_experiment_table(connection)

        elapsed = execute_write_batch(
            connection,
            0,
            ROWS_PER_ITERATION,
        )

        measured_times.append(elapsed)

        print(
            f"  Measurement {iteration + 1}: "
            f"{elapsed:.4f} ms"
        )

    return measured_times


def print_statistics(label: str, values: list[float]) -> None:
    print()
    print(f"{label} statistics")
    print(f"  Average      : {statistics.mean(values):.4f} ms")
    print(f"  Median       : {statistics.median(values):.4f} ms")
    print(f"  Minimum      : {min(values):.4f} ms")
    print(f"  Maximum      : {max(values):.4f} ms")

    if len(values) > 1:
        print(
            f"  Std deviation: "
            f"{statistics.stdev(values):.4f} ms"
        )
    else:
        print("  Std deviation: 0.0000 ms")


def main():
    print()
    print("=" * 70)
    print("M17.2 — REVISED REAL INDEX MAINTENANCE EXPERIMENT")
    print("=" * 70)

    print()
    print(f"Rows per iteration : {ROWS_PER_ITERATION}")
    print(f"Warm-up iterations : {WARMUP_ITERATIONS}")
    print(f"Measured iterations: {MEASURED_ITERATIONS}")

    validate_identifier(TABLE_NAME)
    validate_identifier(INDEX_NAME)
    validate_identifier(SOURCE_TABLE)
    validate_identifier(INDEXED_COLUMN)

    connection = get_connection()

    baseline_times = []
    indexed_times = []

    try:
        print()
        print("Creating temporary experiment table...")
        create_experiment_table(connection)

        # ==========================================================
        # BASELINE
        # ==========================================================

        baseline_times = run_condition(
            connection,
            "BASELINE",
            indexed=False,
        )

        # ==========================================================
        # INDEXED
        # ==========================================================

        print()
        print("Creating experimental index...")
        create_experiment_index(connection)

        print(f"Created index: {INDEX_NAME}")

        indexed_times = run_condition(
            connection,
            "INDEXED",
            indexed=True,
        )

        # ==========================================================
        # STATISTICS
        # ==========================================================

        print_statistics(
            "BASELINE",
            baseline_times,
        )

        print_statistics(
            "INDEXED",
            indexed_times,
        )

        result = build_maintenance_result(
            table_name=TABLE_NAME,
            indexed_columns=[INDEXED_COLUMN],
            row_count=ROWS_PER_ITERATION,
            iterations=MEASURED_ITERATIONS,
            baseline_times_ms=baseline_times,
            indexed_times_ms=indexed_times,
        )

        print()
        print("=" * 70)
        print("M17.2 MAINTENANCE COST RESULT")
        print("=" * 70)

        print(
            f"Baseline average       : "
            f"{result['baseline_average_ms']:.4f} ms"
        )

        print(
            f"Indexed average        : "
            f"{result['indexed_average_ms']:.4f} ms"
        )

        print(
            f"Maintenance overhead   : "
            f"{result['maintenance_overhead_ms']:.4f} ms"
        )

        print(
            f"Maintenance overhead % : "
            f"{result['maintenance_overhead_percent']:.4f}%"
        )

        print("=" * 70)

    finally:
        print()
        print("Cleaning up experimental objects...")

        try:
            drop_experiment_index(connection)
            print("Experimental index removed.")
        except Exception as exc:
            print(f"Index cleanup warning: {exc}")

        try:
            drop_experiment_table(connection)
            print("Experimental table removed.")
        except Exception as exc:
            print(f"Table cleanup warning: {exc}")

        connection.close()

        print("Cleanup complete.")

    print()
    print("M17.2 revised experiment complete.")


if __name__ == "__main__":
    main()
