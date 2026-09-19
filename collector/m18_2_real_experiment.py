import json

from collector.linked_cost_benefit_benchmark import (
    run_linked_cost_benefit_experiment,
)
from collector.linked_cost_benefit_experiment import (
    build_experiment_definition,
)


def main():
    experiment = build_experiment_definition(
        experiment_id="M18_001",
        index_name="m18_001_idx_orders_customer_id",
        table_name="orders",
        columns=["customer_id"],
        read_query="SELECT * FROM {table} WHERE customer_id = 845;",
        write_table="orders",
        read_iterations=10,
        read_warmup_runs=2,
        write_iterations=5,
        write_warmup_runs=2,
        index_type="BTREE",
        notes=(
            "Linked M18.2 read/storage/write experiment for "
            "orders.customer_id."
        ),
    )

    result = run_linked_cost_benefit_experiment(
        experiment,
        source_table="orders",
        write_batch_size=1000,
    )

    print("\n" + "=" * 70)
    print("M18.2 LINKED COST-BENEFIT EXPERIMENT")
    print("=" * 70)

    print(json.dumps(result, indent=2, default=str))

    print("=" * 70)
    print("Experiment completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()
