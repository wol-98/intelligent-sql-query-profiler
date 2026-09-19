import json

from collector.linked_cost_benefit_analyzer import (
    build_linked_cost_benefit_analysis,
)


M18_2_RESULT = {
    "experiment_id": "M18_001",
    "index_name": "m18_001_idx_orders_customer_id",
    "table_name": "orders",
    "columns": ["customer_id"],
    "index_type": "BTREE",
    "evidence_linked": True,

    "read_evidence": {
        "baseline": {
            "average_execution_time_ms": 4.1082,
            "median_execution_time_ms": 4.0885,
            "representative_plan": {
                "Node Type": "Seq Scan"
            },
        },
        "indexed": {
            "average_execution_time_ms": 0.1541,
            "median_execution_time_ms": 0.148,
            "representative_plan": {
                "Node Type": "Index Scan"
            },
        },
        "rows_preserved": True,
        "index_used": True,
        "plan_changed": True,
    },

    "storage_evidence": {
        "index_size_bytes": 606208,
        "index_size_pretty": "592 kB",
        "table_size_bytes": 3670016,
        "table_size_pretty": "3584 kB",
        "index_metadata": {
            "index_type": "btree",
            "column_count": 1,
            "columns": ["customer_id"],
            "is_valid": True,
        },
    },

    "write_evidence": {
        "baseline": {
            "average_execution_time_ms": 147.6142011990305,
            "median_execution_time_ms": 152.85346300152014,
            "standard_deviation_ms": 38.69725521844263,
        },
        "indexed": {
            "average_execution_time_ms": 159.5491302003211,
            "median_execution_time_ms": 152.8794410005503,
            "standard_deviation_ms": 29.41212895649738,
        },
        "batch_size": 1000,
    },
}


def print_section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():
    analysis = build_linked_cost_benefit_analysis(M18_2_RESULT)

    print_section("M18.3 LINKED COST-BENEFIT ANALYSIS")

    print(json.dumps(analysis, indent=2))

    read = analysis["read_analysis"]
    storage = analysis["storage_analysis"]
    write = analysis["write_analysis"]

    print_section("M18.3 SUMMARY")

    print(f"Experiment: {analysis['experiment_id']}")
    print(f"Index:      {analysis['index_name']}")
    print(f"Table:      {analysis['table_name']}")
    print(f"Columns:    {', '.join(analysis['columns'])}")

    print()
    print("READ BENEFIT")
    print(f"  Baseline average:       {read['baseline_average_ms']:.4f} ms")
    print(f"  Indexed average:        {read['indexed_average_ms']:.4f} ms")
    print(
        f"  Average savings:        "
        f"{read['absolute_average_savings_ms']:.4f} ms"
    )
    print(
        f"  Average improvement:    "
        f"{read['average_improvement_percentage']:.2f}%"
    )
    print(
        f"  Median improvement:     "
        f"{read['median_improvement_percentage']:.2f}%"
    )
    print(f"  Rows preserved:         {read['rows_preserved']}")
    print(f"  Index used:             {read['index_used']}")
    print(f"  Plan changed:           {read['plan_changed']}")
    print(
        f"  Plan:                   "
        f"{read['baseline_plan_node']} -> {read['indexed_plan_node']}"
    )

    print()
    print("STORAGE COST")
    print(
        f"  Index size:             "
        f"{storage['index_size_bytes']} bytes "
        f"({storage['index_size_pretty']})"
    )
    print(
        f"  Table size:             "
        f"{storage['table_size_bytes']} bytes "
        f"({storage['table_size_pretty']})"
    )
    print(
        f"  Index/table ratio:      "
        f"{storage['index_table_ratio_percentage']:.2f}%"
    )
    print(f"  Index type:             {storage['index_type']}")
    print(f"  Indexed columns:        {', '.join(storage['columns'])}")

    print()
    print("WRITE COST")
    print(
        f"  Baseline average:       "
        f"{write['baseline_average_ms']:.4f} ms"
    )
    print(
        f"  Indexed average:        "
        f"{write['indexed_average_ms']:.4f} ms"
    )
    print(
        f"  Average overhead:       "
        f"{write['average_overhead_percentage']:.2f}%"
    )
    print(
        f"  Median overhead:        "
        f"{write['median_overhead_percentage']:.4f}%"
    )
    print(
        f"  Batch size:             "
        f"{write['batch_size']}"
    )

    print()
    print("LINKAGE")
    print(f"  Evidence linked:        {analysis['evidence_linked']}")
    print("  Same experiment/index:  verified by M18.2 contract")

    print_section("M18.3 COMPLETE")


if __name__ == "__main__":
    main()
