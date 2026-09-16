from config.database import get_connection

from collector.query_parser import parse_query
from collector.index_candidate_generator import (
    generate_index_candidates
)
from collector.recommendation_engine import (
    score_index_candidates,
    print_recommendations
)
from collector.recommendation_repository import (
    save_recommendations,
    print_saved_recommendations
)


def main():

    # -----------------------------------------------------
    # Q009
    # -----------------------------------------------------

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

    query_profile_id = 10

    # -----------------------------------------------------
    # Get the execution-plan features
    # -----------------------------------------------------

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT execution_plan
        FROM query_profiles
        WHERE query_profile_id = %s;
        """,
        (query_profile_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        raise ValueError(
            f"Query profile {query_profile_id} "
            "was not found."
        )

    execution_plan = row[0]

    # -----------------------------------------------------
    # Extract root plan
    # -----------------------------------------------------

    if isinstance(execution_plan, list):
        plan_data = execution_plan[0]
    else:
        plan_data = execution_plan

    root_plan = plan_data["Plan"]

    # -----------------------------------------------------
    # Import plan tools
    # -----------------------------------------------------

    from collector.plan_analyzer import (
        analyze_plan
    )

    from collector.feature_extractor import (
        extract_plan_features
    )

    plan_nodes = analyze_plan(
        root_plan
    )

    features = extract_plan_features(
        plan_nodes
    )

    # -----------------------------------------------------
    # Parse query
    # -----------------------------------------------------

    query_metadata = parse_query(
        query
    )

    # -----------------------------------------------------
    # Generate candidates
    # -----------------------------------------------------

    candidates = generate_index_candidates(
        features,
        query_metadata
    )

    # -----------------------------------------------------
    # Score candidates
    # -----------------------------------------------------

    recommendations = score_index_candidates(
        candidates,
        features,
        query_metadata
    )

    print_recommendations(
        recommendations
    )

    # -----------------------------------------------------
    # Save recommendations
    # -----------------------------------------------------

    recommendation_ids = save_recommendations(
        query_profile_id,
        recommendations
    )

    # -----------------------------------------------------
    # Display saved records
    # -----------------------------------------------------

    print_saved_recommendations(
        recommendation_ids
    )


if __name__ == "__main__":
    main()
