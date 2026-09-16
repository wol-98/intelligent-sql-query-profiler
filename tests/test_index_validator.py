"""
Index Validator v2 Test
-----------------------
Tests products(category_id) against Q009.
"""

from collector.index_validator import (
    validate_index,
    print_validation_result,
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

    result = validate_index(
        query=query,
        table_name="products",
        column_name="category_id",
        iterations=10,
        warmup_runs=2
    )

    print_validation_result(
        result
    )

    print(
        "\nIndex validation v2 test "
        "completed successfully."
    )


if __name__ == "__main__":
    main()
