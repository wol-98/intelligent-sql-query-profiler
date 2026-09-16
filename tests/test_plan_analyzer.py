from collector.plan_analyzer import analyze_plan


# ---------------------------------------------------------
# Sample PostgreSQL-style execution plan
# ---------------------------------------------------------

sample_plan = {

    "Node Type": "Hash Join",

    "Join Type": "Inner",

    "Actual Rows": 100,

    "Actual Loops": 1,

    "Startup Cost": 10.0,

    "Total Cost": 50.0,

    "Plan Rows": 100,

    "Plan Width": 50,

    "Plans": [

        {
            "Node Type": "Seq Scan",

            "Relation Name": "orders",

            "Actual Rows": 1000,

            "Actual Loops": 1,

            "Startup Cost": 0.0,

            "Total Cost": 20.0,

            "Plan Rows": 1000,

            "Plan Width": 30
        },

        {

            "Node Type": "Hash",

            "Actual Rows": 100,

            "Actual Loops": 1,

            "Startup Cost": 5.0,

            "Total Cost": 10.0,

            "Plan Rows": 100,

            "Plan Width": 20,

            "Plans": [

                {

                    "Node Type": "Seq Scan",

                    "Relation Name": "customers",

                    "Actual Rows": 100,

                    "Actual Loops": 1,

                    "Startup Cost": 0.0,

                    "Total Cost": 5.0,

                    "Plan Rows": 100,

                    "Plan Width": 20

                }

            ]
        }
    ]
}


# ---------------------------------------------------------
# Run test
# ---------------------------------------------------------

if __name__ == "__main__":

    nodes = analyze_plan(
        sample_plan
    )

    print()

    print("=" * 65)
    print("PLAN ANALYZER TEST")
    print("=" * 65)

    print()

    print(
        f"Total plan nodes: {len(nodes)}"
    )

    print()

    for node in nodes:

        indent = "  " * node["depth"]

        print(
            f"{indent}"
            f"{node['node_type']}"
            f" | relation="
            f"{node['relation_name']}"
            f" | rows="
            f"{node['actual_rows']}"
        )

    print()

    print("=" * 65)
