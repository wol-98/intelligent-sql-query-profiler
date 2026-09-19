"""
M17.1 — Real PostgreSQL Index Cost Metadata Experiment

Creates one controlled experimental index, measures its
storage metadata, and removes it afterward.

This runner does not modify recommendation scores or
candidate generation.
"""

from collector.index_validator import (
    create_test_index,
    drop_test_index,
)

from collector.index_cost_analyzer import (
    analyze_index_cost,
    print_index_cost_analysis,
)


TABLE_NAME = "orders"
COLUMN_NAME = "customer_id"
INDEX_NAME = "m17_1_idx_orders_customer_id"


def main():

    print("\n" + "=" * 70)
    print("M17.1 — REAL INDEX COST METADATA EXPERIMENT")
    print("=" * 70)

    created_index = None

    try:

        print("\nCreating experimental index...")

        created_index = create_test_index(
            table_name=TABLE_NAME,
            column_name=COLUMN_NAME,
            index_name=INDEX_NAME,
        )

        print(
            f"Created index: {created_index}"
        )

        print("\nCollecting index cost metadata...")

        metadata = analyze_index_cost(
            created_index
        )

        print_index_cost_analysis(
            metadata
        )

    finally:

        if created_index:

            print(
                "\nRemoving experimental index..."
            )

            drop_test_index(
                created_index
            )

            print(
                f"Removed index: {created_index}"
            )

    print("\nM17.1 experiment complete.")


if __name__ == "__main__":
    main()
