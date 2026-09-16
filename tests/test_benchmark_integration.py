"""
Benchmark Integration Test
--------------------------
Tests the complete flow:

Recommendation
    ↓
Index Validator
    ↓
Before/After Benchmark
    ↓
Benchmark Repository
    ↓
benchmark_results
"""

from config.database import get_connection

from collector.index_validator import (
    validate_index,
    print_validation_result
)

from collector.benchmark_repository import (
    save_benchmark_result,
    print_saved_benchmark
)


def main():

    # -----------------------------------------------------
    # Q009
    # -----------------------------------------------------

    query = """
    SELECT
        oi.order_id,
        p.product_name,
        oi.quantity,
        oi.unit_price
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE p.category_id = 1;
    """

    # -----------------------------------------------------
    # Recommendation ID 8
    # products.category_id
    # -----------------------------------------------------

    recommendation_id = 8

    table_name = "products"
    column_name = "category_id"

    print("\n" + "=" * 70)
    print("BENCHMARK INTEGRATION TEST")
    print("=" * 70)

    print(
        f"Recommendation ID : {recommendation_id}"
    )

    print(
        f"Table             : {table_name}"
    )

    print(
        f"Column            : {column_name}"
    )

    # -----------------------------------------------------
    # Run controlled validation
    # -----------------------------------------------------

    validation_result = validate_index(
        query=query,
        table_name=table_name,
        column_name=column_name,
        iterations=10,
        warmup_runs=2
    )

    # -----------------------------------------------------
    # Display validation result
    # -----------------------------------------------------

    print_validation_result(
        validation_result
    )

    # -----------------------------------------------------
    # Save benchmark result
    # -----------------------------------------------------

    benchmark_id = save_benchmark_result(
        recommendation_id=recommendation_id,
        query_text=query,
        validation_result=validation_result
    )

    # -----------------------------------------------------
    # Display saved benchmark
    # -----------------------------------------------------

    print_saved_benchmark(
        benchmark_id
    )


if __name__ == "__main__":
    main()
