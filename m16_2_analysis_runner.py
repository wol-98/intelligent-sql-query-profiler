from collector.composite_order_analysis import (
    build_analysis_summary,
    print_analysis_summary,
)


results = [
    {
        "recommendation_id": 32,
        "original_columns": [
            "customer_id",
            "status",
        ],
        "alternative_columns": [
            "status",
            "customer_id",
        ],
        "original_improvement_percentage": 97.16,
        "alternative_improvement_percentage": 97.27,
        "improvement_difference_percentage_points": 0.10,
        "original_index_used": True,
        "alternative_index_used": True,
        "original_rows_preserved": True,
        "alternative_rows_preserved": True,
    },
    {
        "recommendation_id": 33,
        "original_columns": [
            "order_date",
            "total_amount",
        ],
        "alternative_columns": [
            "total_amount",
            "order_date",
        ],
        "original_improvement_percentage": 80.13,
        "alternative_improvement_percentage": -0.26,
        "improvement_difference_percentage_points": -80.39,
        "original_index_used": True,
        "alternative_index_used": False,
        "original_rows_preserved": True,
        "alternative_rows_preserved": True,
    },
    {
        "recommendation_id": 34,
        "original_columns": [
            "status",
            "customer_id",
        ],
        "alternative_columns": [
            "customer_id",
            "status",
        ],
        "original_improvement_percentage": 16.88,
        "alternative_improvement_percentage": -1.25,
        "improvement_difference_percentage_points": -18.13,
        "original_index_used": True,
        "alternative_index_used": False,
        "original_rows_preserved": True,
        "alternative_rows_preserved": True,
    },
    {
        "recommendation_id": 35,
        "original_columns": [
            "segment",
            "customer_id",
            "name",
        ],
        "alternative_columns": [
            "name",
            "customer_id",
            "segment",
        ],
        "original_improvement_percentage": -0.65,
        "alternative_improvement_percentage": -2.35,
        "improvement_difference_percentage_points": -1.69,
        "original_index_used": True,
        "alternative_index_used": True,
        "original_rows_preserved": True,
        "alternative_rows_preserved": True,
    },
]


summary = build_analysis_summary(results)

print_analysis_summary(summary)
