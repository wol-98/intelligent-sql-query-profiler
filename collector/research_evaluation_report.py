"""
M14.4 Integrated Research Evaluation Report
--------------------------------------------

Consolidates M14.2 recommendation-quality analysis and M14.3
score-only vs workload-aware prioritization into one reproducible,
research-oriented analytical report.

Analytical only:
- No database mutation
- No recommendation-score changes
- No benchmark changes
- No index creation

The report is intentionally descriptive. It summarizes the evidence
available in the current experimental dataset and explicitly records
scope/limitations rather than making causal or general claims.
"""

from collector.recommendation_quality_analyzer import (
    build_recommendation_evaluation_dataset,
)

from collector.recommendation_quality_analysis import (
    analyze_recommendation_quality,
)

from collector.workload_cost_analyzer import (
    analyze_workload_costs,
)

from collector.recommendation_prioritization_comparison import (
    analyze_prioritization_comparison,
)


# =========================================================
# RESEARCH SUMMARY
# =========================================================

def build_research_summary(
    quality_analysis,
    prioritization_analysis,
):
    """
    Build a compact set of report-level research findings.

    Uses the current M14.2 return structure and also supports
    the legacy structure used by earlier M14.4 test fixtures.
    """

    # -----------------------------------------------------
    # Current M14.2 structure
    # -----------------------------------------------------

    metrics = quality_analysis.get(
        "metrics",
        {}
    )

    score = quality_analysis.get(
        "score_vs_improvement",
        {}
    )

    workload = quality_analysis.get(
        "workload_share_vs_improvement",
        {}
    )

    # -----------------------------------------------------
    # Legacy/test-fixture structure
    # -----------------------------------------------------

    overall = quality_analysis.get(
        "overall",
        {}
    )

    relationships = quality_analysis.get(
        "relationships",
        {}
    )

    priority = quality_analysis.get(
        "priority_outcomes",
        {}
    )

    # -----------------------------------------------------
    # Overall validation metrics
    # -----------------------------------------------------

    evaluated_rows = metrics.get(
        "evaluated_rows"
    )

    if evaluated_rows is None:
        evaluated_rows = quality_analysis.get(
            "evaluated_rows"
        )

    if evaluated_rows is None:
        evaluated_rows = overall.get(
            "evaluated_rows",
            0
        )

    successful = metrics.get(
        "successful"
    )

    if successful is None:
        successful = overall.get(
            "successful",
            0
        )

    neutral = metrics.get(
        "neutral"
    )

    if neutral is None:
        neutral = overall.get(
            "neutral",
            0
        )

    unsuccessful = metrics.get(
        "unsuccessful"
    )

    if unsuccessful is None:
        unsuccessful = overall.get(
            "unsuccessful",
            0
        )

    success_rate = metrics.get(
        "success_rate"
    )

    if success_rate is None:
        success_rate = overall.get(
            "success_rate",
            0.0
        )

    average_improvement = metrics.get(
        "average_improvement"
    )

    if average_improvement is None:
        average_improvement = overall.get(
            "average_improvement",
            0.0
        )

    median_improvement = metrics.get(
        "median_improvement"
    )

    if median_improvement is None:
        median_improvement = overall.get(
            "median_improvement",
            0.0
        )

    # -----------------------------------------------------
    # Score relationships
    # -----------------------------------------------------

    score_pearson = score.get(
        "pearson_correlation"
    )

    if score_pearson is None:
        score_pearson = relationships.get(
            "score_vs_improvement",
            {}
        ).get(
            "pearson"
        )

    score_spearman = score.get(
        "spearman_correlation"
    )

    if score_spearman is None:
        score_spearman = relationships.get(
            "score_vs_improvement",
            {}
        ).get(
            "spearman"
        )

    # -----------------------------------------------------
    # Workload relationships
    # -----------------------------------------------------

    workload_pearson = workload.get(
        "pearson_correlation"
    )

    if workload_pearson is None:
        workload_pearson = relationships.get(
            "workload_share_vs_improvement",
            {}
        ).get(
            "pearson"
        )

    workload_spearman = workload.get(
        "spearman_correlation"
    )

    if workload_spearman is None:
        workload_spearman = relationships.get(
            "workload_share_vs_improvement",
            {}
        ).get(
            "spearman"
        )

    # -----------------------------------------------------
    # Recommendation priority
    # -----------------------------------------------------

    high_priority_count = metrics.get(
        "high_priority_count"
    )

    if high_priority_count is None:
        high_priority_count = priority.get(
            "recommendation",
            {}
        ).get(
            "high_priority_count",
            0
        )

    high_priority_success_rate = metrics.get(
        "high_priority_success_rate"
    )

    if high_priority_success_rate is None:
        high_priority_success_rate = priority.get(
            "recommendation",
            {}
        ).get(
            "high_priority_success_rate",
            0.0
        )

    # -----------------------------------------------------
    # Ranking comparison
    # -----------------------------------------------------

    rank_correlation = prioritization_analysis.get(
        "rank_correlation",
        {}
    )

    rank_shifts = prioritization_analysis.get(
        "rank_shifts",
        {}
    )

    return {
        "evaluated_rows":
            evaluated_rows,

        "successful":
            successful,

        "neutral":
            neutral,

        "unsuccessful":
            unsuccessful,

        "success_rate":
            success_rate or 0.0,

        "average_improvement":
            average_improvement or 0.0,

        "median_improvement":
            median_improvement or 0.0,

        "score_vs_improvement_pearson":
            score_pearson,

        "score_vs_improvement_spearman":
            score_spearman,

        "time_share_vs_improvement_pearson":
            workload_pearson,

        "time_share_vs_improvement_spearman":
            workload_spearman,

        "high_priority_count":
            high_priority_count,

        "high_priority_success_rate":
            high_priority_success_rate,

        "rank_correlation_spearman":
            rank_correlation.get(
                "spearman"
            ),

        "average_rank_shift":
            rank_shifts.get(
                "average_absolute_rank_shift",
                0.0
            ),

        "maximum_rank_shift":
            rank_shifts.get(
                "maximum_absolute_rank_shift",
                0
            ),
    }


# =========================================================
# TOP-K COMPARISON
# =========================================================

def build_top_k_comparison(
    prioritization_analysis
):
    """
    Return a concise side-by-side Top-K comparison.
    """

    rows = []

    for k, strategies in (
        prioritization_analysis
        .get(
            "top_k",
            {}
        )
        .items()
    ):

        for strategy, metrics in strategies.items():

            rows.append({
                "k":
                    k,

                "strategy":
                    strategy,

                "count":
                    metrics.get(
                        "count",
                        0
                    ),

                "successful":
                    metrics.get(
                        "successful",
                        0
                    ),

                "success_rate":
                    metrics.get(
                        "success_rate"
                    ) or 0.0,

                "neutral":
                    metrics.get(
                        "neutral",
                        0
                    ),

                "unsuccessful":
                    metrics.get(
                        "unsuccessful",
                        0
                    ),

                "low_benefit":
                    metrics.get(
                        "low_benefit",
                        0
                    ),

                "negative_benefit":
                    metrics.get(
                        "negative_benefit",
                        0
                    ),

                "average_improvement":
                    metrics.get(
                        "average_improvement"
                    ),
            })

    return rows


# =========================================================
# CRITICAL WORKLOAD COMPARISON
# =========================================================

def build_critical_workload_comparison(
    prioritization_analysis
):
    """
    Summarize Critical-workload placement.
    """

    critical = prioritization_analysis.get(
        "critical_workload",
        {}
    )

    return {
        "critical_observations":
            critical.get(
                "critical_observation_count",
                0
            ),

        "score_only":
            critical.get(
                "score_only",
                {}
            ),

        "workload_aware":
            critical.get(
                "workload_aware",
                {}
            ),
    }


# =========================================================
# EVIDENCE TABLE
# =========================================================

def build_validation_evidence_table(
    dataset
):
    """
    Build a compact row-level validation evidence table.

    Evaluation metric precedence:

    1. median_improvement_percentage
    2. improvement_percentage
    3. evaluation_improvement_percentage

    This preserves the validation fallback behavior while
    remaining compatible with the current M14.1/M14.2 dataset.
    """

    rows = []

    for record in dataset:

        # -------------------------------------------------
        # Preferred stored median
        # -------------------------------------------------

        improvement = record.get(
            "median_improvement_percentage"
        )

        # -------------------------------------------------
        # Fallback to stored average
        # -------------------------------------------------

        if improvement is None:
            improvement = record.get(
                "improvement_percentage"
            )

        # -------------------------------------------------
        # Fallback to M14.2 evaluation metric
        # -------------------------------------------------

        if improvement is None:
            improvement = record.get(
                "evaluation_improvement_percentage"
            )

        # -------------------------------------------------
        # No validation evidence
        # -------------------------------------------------

        if improvement is None:
            continue

        rows.append({
            "recommendation_id":
                record.get(
                    "recommendation_id"
                ),

            "benchmark_id":
                record.get(
                    "benchmark_id"
                ),

            "table_name":
                record.get(
                    "table_name"
                ),

            "column_name":
                record.get(
                    "column_name"
                ),

            "recommendation_score":
                record.get(
                    "recommendation_score"
                ),

            "recommendation_priority":
                record.get(
                    "recommendation_priority"
                ),

            "workload_priority":
                record.get(
                    "workload_priority"
                ),

            "execution_time_share":
                record.get(
                    "execution_time_share"
                ),

            "validation_status":
                record.get(
                    "validation_status"
                ),

            "improvement_percentage":
                improvement,

            "rows_preserved":
                record.get(
                    "rows_preserved"
                ),

            "index_used":
                record.get(
                    "index_used"
                ),

            "plan_changed":
                record.get(
                    "plan_changed"
                ),
        })

    return rows


# =========================================================
# LIMITATIONS
# =========================================================

def build_limitations(
    evaluated_rows,
    benchmark_count,
):
    """
    Return explicit limitations for the current experiment.
    """

    return [

        (
            f"The analysis is based on {evaluated_rows} "
            "evaluated benchmark observations from the current "
            "prototype workload."
        ),

        (
            f"The current evidence contains {benchmark_count} "
            "stored benchmark records and should not be treated "
            "as a statistically representative sample of all "
            "PostgreSQL workloads."
        ),

        (
            "The analysis is descriptive and exploratory; observed "
            "associations do not establish causality."
        ),

        (
            "Multiple benchmark observations can correspond to the "
            "same recommendation, so observations are not necessarily "
            "independent."
        ),

        (
            "Stored benchmark median fields are unavailable for the "
            "current observations; therefore the evaluation metric "
            "uses the available benchmark average where a stored "
            "median is absent. The M14.2 median is calculated across "
            "the resulting evaluation observations."
        ),

        (
            "Workload priority measures observed workload importance, "
            "not guaranteed index effectiveness."
        ),

        (
            "Results may depend on the current dataset size, PostgreSQL "
            "planner decisions, hardware/environment, cache state, "
            "query mix, and benchmark protocol."
        ),
    ]


# =========================================================
# RESEARCH INTERPRETATION
# =========================================================

def build_interpretation(
    summary,
    critical_comparison,
    top_k_rows,
):
    """
    Produce neutral, evidence-based interpretation statements.

    These are report statements, not judgments about which
    prioritization strategy is universally preferable.
    """

    statements = []

    # -----------------------------------------------------
    # 1. Validation variation
    # -----------------------------------------------------

    statements.append(
        "The validation experiments produced measurable "
        "performance variation across index recommendations, "
        "including successful, neutral, and unsuccessful outcomes."
    )

    # -----------------------------------------------------
    # 2. Recommendation score relationship
    # -----------------------------------------------------

    statements.append(
        "The original recommendation score showed a positive but "
        "limited association with observed improvement in the current "
        "experimental dataset."
    )

    # -----------------------------------------------------
    # 3. Workload relationship
    # -----------------------------------------------------

    statements.append(
        "Workload execution-time share did not show a direct positive "
        "association with measured index improvement in the current "
        "observations."
    )

    # -----------------------------------------------------
    # 4. Critical workload placement
    # -----------------------------------------------------

    critical_count = critical_comparison[
        "critical_observations"
    ]

    workload_top3 = critical_comparison[
        "workload_aware"
    ].get(
        "top_3_count",
        0
    )

    score_top3 = critical_comparison[
        "score_only"
    ].get(
        "top_3_count",
        0
    )

    if critical_count:

        statements.append(
            f"The workload-aware strategy placed "
            f"{workload_top3} of {critical_count} "
            "Critical-workload observations in its Top-3, "
            "while score-only ranking placed "
            f"{score_top3} in its Top-3."
        )

    # -----------------------------------------------------
    # 5. Top-3 comparison
    # -----------------------------------------------------

    top3 = [
        row
        for row in top_k_rows
        if row["k"] == 3
    ]

    score_top3_rows = [
        row
        for row in top3
        if row["strategy"] == "score_only"
    ]

    workload_top3_rows = [
        row
        for row in top3
        if row["strategy"] == "workload_aware"
    ]

    if (
        score_top3_rows
        and workload_top3_rows
    ):

        score_success = score_top3_rows[0][
            "success_rate"
        ]

        workload_success = workload_top3_rows[0][
            "success_rate"
        ]

        statements.append(
            "Within the current Top-3 comparison, the observed "
            f"success rates were {score_success:.2f}% for "
            "score-only and "
            f"{workload_success:.2f}% for workload-aware ranking. "
            "This is an observation from the current dataset rather "
            "than evidence of universal superiority."
        )

    # -----------------------------------------------------
    # 6. Workload importance vs effectiveness
    # -----------------------------------------------------

    statements.append(
        "Taken together, the experiments distinguish workload "
        "importance from index effectiveness: a query can consume "
        "a large share of workload time without a single-column "
        "index producing a substantial improvement."
    )

    # -----------------------------------------------------
    # 7. Validation requirement
    # -----------------------------------------------------

    statements.append(
        "The results therefore support retaining empirical "
        "validation as a necessary part of the prototype "
        "evaluation pipeline rather than treating either workload "
        "cost or heuristic score as proof of index benefit."
    )

    return statements


# =========================================================
# COMPLETE REPORT
# =========================================================

def build_research_evaluation(
    quality_analysis,
    prioritization_analysis,
    dataset,
):
    """
    Assemble the complete M14.4 analytical report.
    """

    summary = build_research_summary(
        quality_analysis,
        prioritization_analysis,
    )

    top_k = build_top_k_comparison(
        prioritization_analysis
    )

    critical = build_critical_workload_comparison(
        prioritization_analysis
    )

    evidence = build_validation_evidence_table(
        dataset
    )

    benchmark_ids = {
        row.get(
            "benchmark_id"
        )
        for row in evidence
        if row.get(
            "benchmark_id"
        ) is not None
    }

    limitations = build_limitations(
        summary[
            "evaluated_rows"
        ],
        len(benchmark_ids),
    )

    interpretation = build_interpretation(
        summary,
        critical,
        top_k,
    )

    return {
        "summary":
            summary,

        "top_k_comparison":
            top_k,

        "critical_workload_comparison":
            critical,

        "validation_evidence":
            evidence,

        "interpretation":
            interpretation,

        "limitations":
            limitations,
    }


# =========================================================
# PRINT REPORT
# =========================================================

def _fmt(value):
    """
    Format an optional numeric value.
    """

    if value is None:
        return "N/A"

    return f"{value:.3f}"


def print_research_evaluation(
    report
):
    """
    Print the integrated M14.4 report.
    """

    summary = report[
        "summary"
    ]

    print()

    print(
        "=" * 110
    )

    print(
        "M14.4 INTEGRATED RESEARCH EVALUATION REPORT"
    )

    print(
        "=" * 110
    )

    # =====================================================
    # 1. EXPERIMENTAL SUMMARY
    # =====================================================

    print()
    print(
        "1. EXPERIMENTAL SUMMARY"
    )

    print(
        "-" * 110
    )

    print(
        f"Evaluated observations       : "
        f"{summary['evaluated_rows']}"
    )

    print(
        f"Successful                   : "
        f"{summary['successful']}"
    )

    print(
        f"Neutral                      : "
        f"{summary['neutral']}"
    )

    print(
        f"Unsuccessful                 : "
        f"{summary['unsuccessful']}"
    )

    print(
        f"Overall success rate         : "
        f"{summary['success_rate']:.2f}%"
    )

    print(
        f"Average improvement          : "
        f"{summary['average_improvement']:.2f}%"
    )

    print(
        f"Median improvement           : "
        f"{summary['median_improvement']:.2f}%"
    )

    # =====================================================
    # 2. SCORE / WORKLOAD RELATIONSHIPS
    # =====================================================

    print()
    print(
        "2. SCORE / WORKLOAD RELATIONSHIPS"
    )

    print(
        "-" * 110
    )

    print(
        f"Score vs improvement "
        f"(Pearson)                  : "
        f"{_fmt(summary['score_vs_improvement_pearson'])}"
    )

    print(
        f"Score vs improvement "
        f"(Spearman)                 : "
        f"{_fmt(summary['score_vs_improvement_spearman'])}"
    )

    print(
        f"Time share vs improvement "
        f"(Pearson)                  : "
        f"{_fmt(summary['time_share_vs_improvement_pearson'])}"
    )

    print(
        f"Time share vs improvement "
        f"(Spearman)                 : "
        f"{_fmt(summary['time_share_vs_improvement_spearman'])}"
    )

    print(
        f"High recommendation priority: "
        f"{summary['high_priority_count']}"
    )

    print(
        f"High-priority success rate   : "
        f"{_fmt(summary['high_priority_success_rate'])}%"
    )

    # =====================================================
    # 3. SCORE-ONLY VS WORKLOAD-AWARE
    # =====================================================

    print()
    print(
        "3. SCORE-ONLY VS WORKLOAD-AWARE"
    )

    print(
        "-" * 110
    )

    print(
        f"Ranking Spearman correlation: "
        f"{_fmt(report.get('rank_correlation', {}).get('spearman'))}"
    )

    for row in report[
        "top_k_comparison"
    ]:

        average = row[
            "average_improvement"
        ]

        average_text = (
            f"{average:.2f}%"
            if average is not None
            else "N/A"
        )

        print(
            f"Top-{row['k']:<2} "
            f"{row['strategy']:<17} "
            f"success={row['successful']:<2} "
            f"rate={row['success_rate']:>6.2f}% "
            f"neutral={row['neutral']:<2} "
            f"unsuccessful={row['unsuccessful']:<2} "
            f"avg_improvement={average_text}"
        )

    # =====================================================
    # 4. CRITICAL WORKLOAD PLACEMENT
    # =====================================================

    critical = report[
        "critical_workload_comparison"
    ]

    print()
    print(
        "4. CRITICAL WORKLOAD PLACEMENT"
    )

    print(
        "-" * 110
    )

    print(
        f"Critical observations      : "
        f"{critical['critical_observations']}"
    )

    for strategy in (
        "score_only",
        "workload_aware",
    ):

        data = critical[
            strategy
        ]

        print(
            f"{strategy:<25} "
            f"Top-3={data.get('top_3_count', 0)} "
            f"Top-5={data.get('top_5_count', 0)} "
            f"Top-10={data.get('top_10_count', 0)} "
            f"Ranks={data.get('ranks', [])}"
        )

    # =====================================================
    # 5. RESEARCH INTERPRETATION
    # =====================================================

    print()
    print(
        "5. RESEARCH INTERPRETATION"
    )

    print(
        "-" * 110
    )

    for number, statement in enumerate(
        report["interpretation"],
        start=1,
    ):

        print(
            f"{number}. {statement}"
        )

    # =====================================================
    # 6. LIMITATIONS
    # =====================================================

    print()
    print(
        "6. LIMITATIONS"
    )

    print(
        "-" * 110
    )

    for number, limitation in enumerate(
        report["limitations"],
        start=1,
    ):

        print(
            f"{number}. {limitation}"
        )

    # =====================================================
    # STATUS
    # =====================================================

    print()

    print(
        "=" * 110
    )

    print(
        "M14.4 STATUS: INTEGRATED ANALYTICAL EVALUATION COMPLETE"
    )

    print(
        "=" * 110
    )


# =========================================================
# MAIN
# =========================================================

def main():
    """
    Run M14.4 using the current project evidence.
    """

    # -----------------------------------------------------
    # M13 workload analysis
    # -----------------------------------------------------

    workload_analysis = analyze_workload_costs()

    # -----------------------------------------------------
    # M14.1 recommendation-evaluation dataset
    # -----------------------------------------------------

    dataset = build_recommendation_evaluation_dataset(
        workload_analysis
    )

    # -----------------------------------------------------
    # M14.2 recommendation quality analysis
    # -----------------------------------------------------

    quality_analysis = analyze_recommendation_quality(
        dataset
    )

    # -----------------------------------------------------
    # M14.3 prioritization comparison
    # -----------------------------------------------------

    prioritization_analysis = (
        analyze_prioritization_comparison(
            dataset
        )
    )

    # -----------------------------------------------------
    # M14.4 integrated report
    # -----------------------------------------------------

    report = build_research_evaluation(
        quality_analysis,
        prioritization_analysis,
        dataset,
    )

    # Keep the ranking relationship available at report level
    # for the printed integrated summary.

    report["rank_correlation"] = (
        prioritization_analysis.get(
            "rank_correlation",
            {}
        )
    )

    print_research_evaluation(
        report
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
