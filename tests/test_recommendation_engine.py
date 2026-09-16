"""
Test Recommendation / Candidate Scoring Engine
----------------------------------------------
"""

from collector.recommendation_engine import (
    score_index_candidates,
    print_recommendations,
)


def main():

    # -----------------------------------------------------
    # Candidate indexes
    # -----------------------------------------------------

    candidates = [

        {
            "table": "products",
            "columns": ["category_id"],
            "reason": "Filter condition",
            "source": "p.category_id",
            "index_type": "B-tree",
        },

        {
            "table": "order_items",
            "columns": ["product_id"],
            "reason": "Join condition",
            "source": "oi.product_id",
            "index_type": "B-tree",
        },

        {
            "table": "products",
            "columns": ["product_id"],
            "reason": "Join condition",
            "source": "p.product_id",
            "index_type": "B-tree",
        },

        {
            "table": "order_items",
            "columns": ["order_id"],
            "reason": "ORDER BY",
            "source": "oi.order_id",
            "index_type": "B-tree",
        },

    ]

    # -----------------------------------------------------
    # Execution-plan features
    # -----------------------------------------------------

    features = {

        "filters": [
            {
                "table": "products",
                "condition": "(category_id = 1)",
                "rows_removed": 948,
            }
        ],

        "scan_nodes": [

            {
                "node_type": "Seq Scan",
                "table": "order_items",
            },

            {
                "node_type": "Seq Scan",
                "table": "products",
            },

        ],

        "has_index_condition": False,

    }

    # -----------------------------------------------------
    # SQL metadata
    # -----------------------------------------------------

    query_metadata = {

        "tables": [
            "order_items",
            "products"
        ],

        "aliases": {
            "oi": "order_items",
            "p": "products"
        },

        "where_columns": [
            "p.category_id"
        ],

        "join_columns": [
            "oi.product_id",
            "p.product_id"
        ],

        "order_by_columns": [
            "oi.order_id"
        ],

        "group_by_columns": [],

    }

    print("\n" + "=" * 70)
    print("RECOMMENDATION ENGINE TEST")
    print("=" * 70)

    recommendations = score_index_candidates(
        candidates,
        features,
        query_metadata
    )

    print_recommendations(
        recommendations
    )

    print(
        "\nRecommendation engine test "
        "completed successfully."
    )


if __name__ == "__main__":
    main()
