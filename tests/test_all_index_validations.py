"""
Batch Index Validation Test
---------------------------
Validates all recommendations belonging to the
official workload profiles 2-16.

Flow:

Query Profile
    ↓
Saved Recommendation
    ↓
Index Validator
    ↓
Before/After Benchmark
    ↓
Rows Preserved / Index Used
    ↓
Benchmark Repository
    ↓
benchmark_results
"""

from config.database import get_connection

from collector.index_validator import (
    validate_index,
    print_validation_result
)

from collector.benchmark_repository import (
    save_benchmark_result
)


# =========================================================
# GET OFFICIAL RECOMMENDATIONS
# =========================================================

def get_recommendations():

    conn = get_connection()

    try:

        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                ir.recommendation_id,
                ir.query_profile_id,
                qp.query_text,
                ir.table_name,
                ir.column_name,
                ir.index_type
            FROM index_recommendations ir
            JOIN query_profiles qp
                ON ir.query_profile_id =
                   qp.query_profile_id
            WHERE ir.query_profile_id BETWEEN 2 AND 16
            ORDER BY
                ir.query_profile_id,
                ir.recommendation_id;
            """
        )

        return cur.fetchall()

    finally:

        cur.close()
        conn.close()


# =========================================================
# MAIN
# =========================================================

def main():

    recommendations = get_recommendations()

    print("\n" + "=" * 90)
    print("BATCH INDEX VALIDATION")
    print("=" * 90)

    print(
        f"Recommendations found : {len(recommendations)}"
    )

    print(
        "Official profiles      : 2-16"
    )

    print(
        "Temporary indexes      : YES"
    )

    print(
        "Permanent indexes      : NO"
    )

    print("=" * 90)

    successful = 0
    failed = 0

    validation_results = []

    # -----------------------------------------------------
    # Validate each recommendation
    # -----------------------------------------------------

    for row in recommendations:

        (
            recommendation_id,
            query_profile_id,
            query,
            table_name,
            column_name,
            index_type
        ) = row

        print("\n" + "-" * 90)

        print(
            f"Query Profile ID : {query_profile_id}"
        )

        print(
            f"Recommendation ID: {recommendation_id}"
        )

        print(
            f"Table            : {table_name}"
        )

        print(
            f"Column           : {column_name}"
        )

        print(
            f"Index Type       : {index_type}"
        )

        try:

            # -------------------------------------------------
            # Controlled validation
            # -------------------------------------------------

            validation_result = validate_index(
                query=query,
                table_name=table_name,
                column_name=column_name,
                iterations=10,
                warmup_runs=2
            )

            # -------------------------------------------------
            # Display validation result
            # -------------------------------------------------

            print_validation_result(
                validation_result
            )

            # -------------------------------------------------
            # Save benchmark result
            # -------------------------------------------------

            benchmark_id = save_benchmark_result(
                recommendation_id=recommendation_id,
                query_text=query,
                validation_result=validation_result
            )

            print(
                f"Benchmark ID     : {benchmark_id}"
            )

            validation_results.append(
                (
                    recommendation_id,
                    query_profile_id,
                    table_name,
                    column_name,
                    validation_result
                )
            )

            successful += 1

        except Exception as error:

            failed += 1

            print(
                "\nVALIDATION FAILED"
            )

            print(
                f"Error: {error}"
            )

    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n" + "=" * 90)
    print("BATCH VALIDATION SUMMARY")
    print("=" * 90)

    print(
        f"Recommendations processed : "
        f"{len(recommendations)}"
    )

    print(
        f"Successful validations    : "
        f"{successful}"
    )

    print(
        f"Failed validations        : "
        f"{failed}"
    )

    # -----------------------------------------------------
    # Results summary
    # -----------------------------------------------------

    if validation_results:

        print("\n" + "-" * 90)
        print("PERFORMANCE RESULTS")
        print("-" * 90)

        for (
            recommendation_id,
            query_profile_id,
            table_name,
            column_name,
            result
        ) in validation_results:

            improvement = result.get(
                "improvement_percentage"
            )

            median_improvement = result.get(
                "median_improvement_percentage"
            )

            index_used = result.get(
                "index_used"
            )

            rows_preserved = result.get(
                "rows_preserved"
            )

            print(
                f"\nProfile {query_profile_id} | "
                f"Recommendation {recommendation_id}"
            )

            print(
                f"  Index       : "
                f"{table_name}.{column_name}"
            )

            print(
                f"  Avg improve : "
                f"{improvement:.2f}%"
            )

            print(
                f"  Median      : "
                f"{median_improvement:.2f}%"
            )

            print(
                f"  Index used  : "
                f"{index_used}"
            )

            print(
                f"  Rows same   : "
                f"{rows_preserved}"
            )

    print("\n" + "=" * 90)

    if failed == 0:

        print(
            "ALL INDEX VALIDATIONS COMPLETED SUCCESSFULLY."
        )

    else:

        print(
            "VALIDATION COMPLETED WITH ERRORS."
        )

    print("=" * 90)


if __name__ == "__main__":
    main()
