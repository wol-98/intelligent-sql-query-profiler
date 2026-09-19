from config.database import get_connection
import pandas as pd


# ============================================================
# PROJECT EVALUATION METRICS
# ============================================================

conn = get_connection()


# ------------------------------------------------------------
# LOAD PROJECT DATA
# ------------------------------------------------------------

query_profiles = pd.read_sql(
    """
    SELECT *
    FROM query_profiles
    """,
    conn
)

recommendations = pd.read_sql(
    """
    SELECT *
    FROM index_recommendations
    """,
    conn
)

benchmarks = pd.read_sql(
    """
    SELECT *
    FROM benchmark_results
    """,
    conn
)

conn.close()


# ============================================================
# 1. QUERY EXECUTION TIME
# ============================================================

print("\n" + "=" * 60)
print("1. QUERY EXECUTION TIME")
print("=" * 60)

if {
    "execution_time_before_ms",
    "execution_time_after_ms"
}.issubset(benchmarks.columns):

    execution_data = benchmarks[
        [
            "benchmark_id",
            "execution_time_before_ms",
            "execution_time_after_ms"
        ]
    ].copy()

    print(execution_data.to_string(index=False))

else:

    print("Required benchmark execution-time fields are unavailable.")


# ============================================================
# 2. PERCENTAGE IMPROVEMENT
# ============================================================

print("\n" + "=" * 60)
print("2. PERCENTAGE IMPROVEMENT")
print("=" * 60)

if "improvement_percentage" in benchmarks.columns:

    improvement = benchmarks[
        "improvement_percentage"
    ].dropna()

    if not improvement.empty:

        print(
            f"Average improvement : {improvement.mean():.2f}%"
        )

        print(
            f"Maximum improvement : {improvement.max():.2f}%"
        )

        print(
            f"Minimum improvement : {improvement.min():.2f}%"
        )

    else:

        print("No improvement values available.")

else:

    print("Improvement percentage is unavailable.")


# ============================================================
# 3. RECOMMENDATION PRECISION
# ============================================================

print("\n" + "=" * 60)
print("3. RECOMMENDATION PRECISION")
print("=" * 60)

if (
    "recommendation_id" in benchmarks.columns
    and "validation_status" in benchmarks.columns
):

    validated = benchmarks[
        benchmarks["validation_status"].notna()
    ]

    successful = validated[
        validated["validation_status"]
        .astype(str)
        .str.upper()
        == "SUCCESSFUL"
    ]

    if len(validated) > 0:

        precision = (
            len(successful) / len(validated)
        ) * 100

        print(f"Validated recommendations : {len(validated)}")
        print(f"Successful recommendations : {len(successful)}")
        print(f"Recommendation precision : {precision:.2f}%")

    else:

        print("No validated recommendations available.")

else:

    print(
        "Required validation fields are unavailable."
    )


# ============================================================
# 4. RECOMMENDATION COVERAGE
# ============================================================

print("\n" + "=" * 60)
print("4. RECOMMENDATION COVERAGE")
print("=" * 60)

if (
    "query_profile_id" in recommendations.columns
    and "query_profile_id" in query_profiles.columns
):

    total_queries = query_profiles[
        "query_profile_id"
    ].nunique()

    covered_queries = recommendations[
        "query_profile_id"
    ].dropna().nunique()

    if total_queries > 0:

        coverage = (
            covered_queries / total_queries
        ) * 100

        print(f"Queries analyzed : {total_queries}")
        print(f"Queries with recommendations : {covered_queries}")
        print(f"Recommendation coverage : {coverage:.2f}%")

    else:

        print("No query profiles available.")

else:

    print(
        "Required query-profile fields are unavailable."
    )


# ============================================================
# 5. LOW-BENEFIT RECOMMENDATIONS
# ============================================================

print("\n" + "=" * 60)
print("5. LOW-BENEFIT RECOMMENDATIONS")
print("=" * 60)

if "improvement_percentage" in benchmarks.columns:

    low_benefit = benchmarks[
        benchmarks["improvement_percentage"].fillna(0) <= 5
    ]

    print(
        f"Recommendations with <= 5% improvement : "
        f"{len(low_benefit)}"
    )

    if not low_benefit.empty:

        print(
            low_benefit[
                [
                    column
                    for column in [
                        "benchmark_id",
                        "recommendation_id",
                        "improvement_percentage"
                    ]
                    if column in low_benefit.columns
                ]
            ].to_string(index=False)
        )

else:

    print("Improvement data is unavailable.")


# ============================================================
# 6. ANALYSIS LATENCY
# ============================================================

print("\n" + "=" * 60)
print("6. ANALYSIS LATENCY")
print("=" * 60)

latency_columns = [
    "analysis_latency_ms",
    "analysis_time_ms",
    "processing_time_ms"
]

available_latency = [
    column
    for column in latency_columns
    if column in query_profiles.columns
]

if available_latency:

    latency_column = available_latency[0]

    latency = query_profiles[
        latency_column
    ].dropna()

    if not latency.empty:

        print(
            f"Latency field : {latency_column}"
        )

        print(
            f"Average analysis latency : "
            f"{latency.mean():.2f} ms"
        )

        print(
            f"Maximum analysis latency : "
            f"{latency.max():.2f} ms"
        )

    else:

        print("No latency values available.")

else:

    print(
        "Analysis latency is not stored in the current "
        "query_profiles table."
    )


# ============================================================
# 7. INDEX OVERHEAD
# ============================================================

print("\n" + "=" * 60)
print("7. INDEX OVERHEAD")
print("=" * 60)

print(
    "Index overhead cannot be calculated from the current "
    "benchmark_results fields because the project data does "
    "not contain a dedicated index-storage/creation-cost "
    "measurement."
)

print(
    "No value is fabricated for this metric."
)


# ============================================================
# FINAL PROJECT SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("FINAL PROJECT SUMMARY")
print("=" * 60)

print(f"Queries analyzed       : {len(query_profiles)}")
print(f"Recommendations        : {len(recommendations)}")
print(f"Benchmarks performed   : {len(benchmarks)}")

if "validation_status" in benchmarks.columns:

    status_counts = (
        benchmarks["validation_status"]
        .value_counts()
    )

    for status, count in status_counts.items():

        print(
            f"{str(status).capitalize():<23}: {count}"
        )

print("\nEvaluation completed.")