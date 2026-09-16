"""
Test SQL Query Metadata Extractor
---------------------------------
"""

from collector.query_parser import (
    parse_query,
    print_query_metadata,
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
    WHERE p.category_id = 1
    ORDER BY oi.order_id DESC
    LIMIT 20;
    """

    print("\n" + "=" * 65)
    print("SQL QUERY PARSER TEST")
    print("=" * 65)

    metadata = parse_query(query)

    print_query_metadata(
        metadata
    )

    print(
        "\nQuery parser test "
        "completed successfully."
    )


if __name__ == "__main__":
    main()
