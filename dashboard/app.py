import streamlit as st
import pandas as pd

from config.database import get_connection


st.set_page_config(
    page_title="Intelligent SQL Query Profiler",
    page_icon="📊",
    layout="wide"
)


def load_data(query):
    conn = get_connection()

    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📊 Intelligent SQL Query Profiler")
st.subheader("Benchmarking & Index Optimization Dashboard")

st.write(
    "Dashboard for analysing SQL query performance, "
    "index recommendations and benchmark validation results."
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:
    query_profiles = load_data("""
        SELECT *
        FROM query_profiles;
    """)

    recommendations = load_data("""
        SELECT *
        FROM index_recommendations
        ORDER BY recommendation_id;
    """)

    benchmarks = load_data("""
        SELECT *
        FROM benchmark_results
        ORDER BY benchmark_id;
    """)

except Exception as e:
    st.error("Could not load data from the database.")
    st.exception(e)
    st.stop()


# --------------------------------------------------
# OVERVIEW METRICS
# --------------------------------------------------

st.header(" Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Queries Analyzed",
        len(query_profiles)
    )

with col2:
    st.metric(
        "Recommendations",
        len(recommendations)
    )

with col3:
    st.metric(
        "Benchmarks",
        len(benchmarks)
    )

with col4:
    if "validation_status" in benchmarks.columns:
        successful = (
            benchmarks["validation_status"]
            .astype(str)
            .str.upper()
            .eq("SUCCESSFUL")
            .sum()
        )
    else:
        successful = 0

    st.metric(
        "Successful Validations",
        successful
    )


# --------------------------------------------------

# --------------------------------------------------
# SLOWEST QUERIES
# --------------------------------------------------

st.subheader("Slowest Queries")

if query_profiles.empty:

    st.info("No query profile data available.")

else:

    slowest_queries = (
        query_profiles[
            [
                "query_profile_id",
                "query_type",
                "table_name",
                "average_execution_time_ms",
                "execution_count",
                "rows_processed"
            ]
        ]
        .sort_values(
            "average_execution_time_ms",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        slowest_queries,
        use_container_width=True
    )     



# --------------------------------------------------
# QUERY EXPLORER
# --------------------------------------------------

# --------------------------------------------------
# QUERY EXPLORER
# --------------------------------------------------

st.header("Query Explorer")

if query_profiles.empty:

    st.info("No query profiles available.")

else:

    # --------------------------------------------------
    # SEARCH QUERY
    # --------------------------------------------------

    search_text = st.text_input(
        "Search query text",
        placeholder="Enter a keyword or SQL text..."
    )

    filtered_profiles = query_profiles.copy()

    if search_text:
        filtered_profiles = filtered_profiles[
            filtered_profiles["query_text"]
            .astype(str)
            .str.contains(
                search_text,
                case=False,
                na=False
            )
        ]

    # --------------------------------------------------
    # NO MATCHING QUERIES
    # --------------------------------------------------

    if filtered_profiles.empty:

        st.warning("No matching queries found.")

    else:

        # --------------------------------------------------
        # QUERY PROFILE SELECTION
        # --------------------------------------------------

        profile_options = ["Select a query profile..."] + (
            filtered_profiles["query_profile_id"]
            .astype(str)
            .tolist()
        )

        selected_profile_id = st.selectbox(
            "Select Query Profile",
            profile_options,
            index=0
        )

        # --------------------------------------------------
        # WAIT UNTIL USER SELECTS A PROFILE
        # --------------------------------------------------

        if selected_profile_id == "Select a query profile...":

            st.info(
                "Select a query profile to view its SQL query and features."
            )

        else:

            selected_profile_id = int(selected_profile_id)

            selected_profile = filtered_profiles[
                filtered_profiles["query_profile_id"]
                == selected_profile_id
            ].iloc[0]

            # --------------------------------------------------
            # SQL QUERY
            # --------------------------------------------------

            st.subheader("SQL Query")

            st.code(
                str(selected_profile["query_text"]),
                language="sql"
            )

            # --------------------------------------------------
            # QUERY FEATURES
            # --------------------------------------------------

            st.subheader("Query Features")

            feature_columns = [
                "query_profile_id",
                "query_hash",
                "query_type",
                "execution_count",
                "total_execution_time_ms",
                "average_execution_time_ms",
                "rows_processed",
                "table_name",
                "planning_time_ms",
                "shared_hit_blocks",
                "shared_read_blocks",
                "rows_removed_by_filter",
                "plan_node_type"
            ]

            available_features = [
                column
                for column in feature_columns
                if column in selected_profile.index
            ]

            feature_data = pd.DataFrame({
                "Feature": available_features,
                "Value": [
                    selected_profile[column]
                    for column in available_features
                ]
            })

            st.dataframe(
                feature_data,
                use_container_width=True
            )

# --------------------------------------------------
# 3. RECOMMENDATIONS
# --------------------------------------------------

st.header("3. Recommendations")

if recommendations.empty:

    st.info("No index recommendations available.")

else:

    # --------------------------------------------------
    # PREPARE RECOMMENDATION DATA
    # --------------------------------------------------

    recommendation_columns = [
        "recommendation_id",
        "query_profile_id",
        "table_name",
        "column_name",
        "index_type",
        "recommendation_score",
        "priority",
        "reasoning",
        "confidence"
    ]

    available_columns = [
        column
        for column in recommendation_columns
        if column in recommendations.columns
    ]

    recommendation_view = recommendations[
        available_columns
    ].copy()

    # --------------------------------------------------
    # ADD VALIDATION STATUS
    # --------------------------------------------------

    if (
        not benchmarks.empty
        and "recommendation_id" in benchmarks.columns
        and "validation_status" in benchmarks.columns
    ):

        validation_columns = [
            "recommendation_id",
            "validation_status"
        ]

        validation_data = benchmarks[
            validation_columns
        ].drop_duplicates(
            subset=["recommendation_id"],
            keep="last"
        )

        recommendation_view = recommendation_view.merge(
            validation_data,
            on="recommendation_id",
            how="left"
        )

    # --------------------------------------------------
    # FILTER BY PRIORITY
    # --------------------------------------------------

    if "priority" in recommendation_view.columns:

        priority_values = (
            recommendation_view["priority"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        priority_options = ["All"] + sorted(priority_values)

        selected_priority = st.selectbox(
            "Recommendation Priority",
            priority_options,
            index=0
        )

        if selected_priority != "All":

            recommendation_view = recommendation_view[
                recommendation_view["priority"]
                .astype(str)
                == selected_priority
            ]

    # --------------------------------------------------
    # DISPLAY RECOMMENDATIONS
    # --------------------------------------------------

    if recommendation_view.empty:

        st.warning(
            "No recommendations match the selected priority."
        )

    else:

        # Rename columns for clean dashboard display
        display_columns = {
            "recommendation_id": "Recommendation ID",
            "query_profile_id": "Query Profile ID",
            "table_name": "Table",
            "column_name": "Column",
            "index_type": "Index Type",
            "recommendation_score": "Score",
            "priority": "Priority",
            "reasoning": "Rationale",
            "confidence": "Confidence",
            "validation_status": "Validation Status"
        }

        recommendation_display = recommendation_view.rename(
            columns=display_columns
        )

        st.dataframe(
            recommendation_display,
            use_container_width=True,
            hide_index=True
        )
# --------------------------------------------------
# BENCHMARK SUMMARY
# --------------------------------------------------

st.subheader("Benchmark Summary")

if benchmarks.empty:

    st.info("No benchmark data available.")

else:

    avg_before = benchmarks["execution_time_before_ms"].mean()
    avg_after = benchmarks["execution_time_after_ms"].mean()
    avg_improvement = benchmarks["improvement_percentage"].mean()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Avg. Before (ms)",
            f"{avg_before:.2f}"
        )

    with col2:
        st.metric(
            "Avg. After (ms)",
            f"{avg_after:.2f}"
        )

    with col3:
        st.metric(
            "Avg. Improvement",
            f"{avg_improvement:.2f}%"
        )   


# --------------------------------------------------
# DATABASE INSIGHTS
# --------------------------------------------------

st.header("Database Insights")

if query_profiles.empty:

    st.info("No database insights available.")

else:

    # ----------------------------------------------
    # TABLE ACCESS
    # ----------------------------------------------

    st.subheader("Frequently Accessed Tables")

    table_access = (
        query_profiles
        .groupby("table_name")
        .agg(
            Queries=("query_profile_id", "count"),
            Total_Executions=("execution_count", "sum"),
            Total_Time_ms=("total_execution_time_ms", "sum")
        )
        .reset_index()
        .sort_values(
            "Total_Executions",
            ascending=False
        )
    )

    st.dataframe(
        table_access,
        use_container_width=True
    )

    st.bar_chart(
        table_access.set_index("table_name")["Total_Executions"]
    )


    # ----------------------------------------------
    # HIGH-COST QUERIES
    # ----------------------------------------------

    st.subheader("High-Cost Query Patterns")

    high_cost = (
        query_profiles[
            [
                "query_profile_id",
                "query_type",
                "table_name",
                "average_execution_time_ms",
                "total_execution_time_ms",
                "execution_count"
            ]
        ]
        .sort_values(
            "average_execution_time_ms",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        high_cost,
        use_container_width=True
    )


# --------------------------------------------------
# VALIDATION RESULTS
# --------------------------------------------------

st.header("Validation Results")

if benchmarks.empty or "validation_status" not in benchmarks.columns:

    st.info("No validation results available.")

else:

    validation_summary = (
        benchmarks["validation_status"]
        .astype(str)
        .str.upper()
        .value_counts()
        .rename_axis("Validation Status")
        .reset_index(name="Count")
    )

    total_validations = validation_summary["Count"].sum()

    validation_summary["Percentage"] = (
        validation_summary["Count"] / total_validations * 100
    ).round(2)

    st.dataframe(
        validation_summary,
        use_container_width=True
    )

    st.bar_chart(
        validation_summary.set_index("Validation Status")["Count"]
    )  

# --------------------------------------------------
# SUCCESSFUL VALIDATIONS
# --------------------------------------------------

st.subheader("Successful Validations")

if benchmarks.empty:

    st.info("No benchmark results available.")

else:

    successful_validations = benchmarks[
        benchmarks["validation_status"]
        .astype(str)
        .str.upper()
        == "SUCCESSFUL"
    ].copy()

    st.metric(
        "Successful Recommendations",
        len(successful_validations)
    )

    if successful_validations.empty:

        st.info("No successful validations found.")

    else:

        successful_validations = successful_validations[
            [
                "benchmark_id",
                "recommendation_id",
                "improvement_percentage",
                "index_used",
                "rows_preserved",
                "plan_changed",
                "validation_reason"
            ]
        ]

        st.dataframe(
            successful_validations,
            use_container_width=True
        ) 
                                                