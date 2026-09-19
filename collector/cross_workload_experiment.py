"""M18.4 cross-workload experiment definitions.

Defines the controlled workload set used to evaluate linked
index cost-benefit behavior across different query patterns.

This module is design-only:
- no database access
- no index creation
- no benchmarking
- no recommendation scoring
- no benchmark_results changes
"""

from collector.linked_cost_benefit_experiment import (
    build_experiment_definition,
)


def build_m18_4_experiment_set():
    """Build the controlled M18.4 experiment definitions."""

    return [
        build_experiment_definition(
            experiment_id="M18_001",
            index_name="m18_001_idx_orders_customer_id",
            table_name="orders",
            columns=["customer_id"],
            read_query=(
                "SELECT * FROM {table} "
                "WHERE customer_id = 845;"
            ),
            write_table="orders",
            read_iterations=10,
            read_warmup_runs=2,
            write_iterations=5,
            write_warmup_runs=2,
            index_type="BTREE",
            notes="Q001 - selective equality lookup",
        ),

        build_experiment_definition(
            experiment_id="M18_002",
            index_name="m18_002_idx_products_category_id",
            table_name="products",
            columns=["category_id"],
            read_query=(
                "SELECT oi.order_id, oi.product_id, oi.quantity, "
                "p.product_name "
                "FROM order_items oi "
                "JOIN {table} p ON oi.product_id = p.product_id "
                "WHERE p.category_id = 1;"
            ),
            write_table="products",
            read_iterations=10,
            read_warmup_runs=2,
            write_iterations=5,
            write_warmup_runs=2,
            index_type="BTREE",
            notes="Q009 - join plus category filter",
        ),

        build_experiment_definition(
            experiment_id="M18_003",
            index_name="m18_003_idx_orders_customer_id",
            table_name="orders",
            columns=["customer_id"],
            read_query=(
                "SELECT customer_id, COUNT(*) AS order_count "
                "FROM {table} "
                "GROUP BY customer_id "
                "ORDER BY customer_id "
                "LIMIT 20;"
            ),
            write_table="orders",
            read_iterations=10,
            read_warmup_runs=2,
            write_iterations=5,
            write_warmup_runs=2,
            index_type="BTREE",
            notes="Q015 pattern - grouping and ordering by customer",
        ),
    ]
