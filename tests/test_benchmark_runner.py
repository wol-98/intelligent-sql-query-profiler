"""
Test PostgreSQL Benchmark Runner
--------------------------------
Tests Benchmark Runner v2 using Q009.
"""

from collector.benchmark_runner import (
    benchmark_query,
    print_benchmark,
)


def main():

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

    print("\n" + "=" * 70)
    print("POSTGRESQL BENCHMARK RUNNER TEST")
    print("=" * 70)

    benchmark = benchmark_query(
        query,
        iterations=5,
        warmup_runs=1
    )

    print_benchmark(
        benchmark
    )

    print(
        "\nPostgreSQL benchmark runner "
        "test completed successfully."
    )


if __name__ == "__main__":
    main()
