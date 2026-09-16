"""
Test Feature Extractor
----------------------
Tests feature extraction using a sample execution-plan tree.
"""

from collector.plan_analyzer import analyze_plan
from collector.feature_extractor import (
    extract_plan_features,
    print_features,
)


def main():

    sample_plan = {
        "Node Type": "Hash Join",
        "Join Type": "Inner",
        "Actual Rows": 100,
        "Plan Rows": 120,
        "Hash Cond": "(orders.customer_id = customers.customer_id)",

        "Plans": [

            {
                "Node Type": "Seq Scan",
                "Relation Name": "orders",
                "Alias": "orders",
                "Actual Rows": 1000,
                "Plan Rows": 1100,
                "Rows Removed by Filter": 900,
                "Filter": "(status = 'Completed')",
                "Shared Hit Blocks": 200,
                "Shared Read Blocks": 10,
            },

            {
                "Node Type": "Hash",
                "Actual Rows": 100,
                "Plan Rows": 120,

                "Plans": [

                    {
                        "Node Type": "Seq Scan",
                        "Relation Name": "customers",
                        "Alias": "customers",
                        "Actual Rows": 100,
                        "Plan Rows": 120,
                        "Shared Hit Blocks": 50,
                        "Shared Read Blocks": 5,
                    }

                ],
            },

        ],
    }

    print("\n" + "=" * 65)
    print("FEATURE EXTRACTOR TEST")
    print("=" * 65)

    # First flatten the plan
    plan_nodes = analyze_plan(sample_plan)

    print(f"\nPlan nodes received: {len(plan_nodes)}")

    # Then extract features
    features = extract_plan_features(plan_nodes)

    # Display results
    print_features(features)

    print("\nFeature extractor test completed successfully.")


if __name__ == "__main__":
    main()
