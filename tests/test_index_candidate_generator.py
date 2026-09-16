"""
Test Index Candidate Generator
------------------------------
Tests candidate generation using SQL metadata
and execution-plan features.
"""

from collector.index_candidate_generator import (
    generate_index_candidates,
    print_candidates,
)


def main():

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

        "join_nodes": [
            {
                "node_type": "Hash Join",
                "join_type": "Inner",
                "join_filter": None,
                "hash_condition":
                    "(oi.product_id = p.product_id)",
            }
        ],

        "index_names": [],

    }

    print("\n" + "=" * 65)
    print("INDEX CANDIDATE GENERATOR TEST")
    print("=" * 65)

    candidates = generate_index_candidates(
        features,
        query_metadata
    )

    print_candidates(
        candidates
    )

    print(
        "\nCandidate generator test "
        "completed successfully."
    )


if __name__ == "__main__":
    main()
