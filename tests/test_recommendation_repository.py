from collector.recommendation_repository import save_recommendation


def main():

    recommendation_id = save_recommendation(
        query_profile_id=10,
        table_name="products",
        column_name="category_id",
        index_type="B-tree",
        recommendation_score=60,
        priority="Medium",
        reasoning=(
            "Filter condition on products.category_id; "
            "sequential scan detected; "
            "rows removed by filter."
        ),
    )

    print("\n" + "=" * 70)
    print("RECOMMENDATION SAVED")
    print("=" * 70)

    print(f"Recommendation ID: {recommendation_id}")


if __name__ == "__main__":
    main()
