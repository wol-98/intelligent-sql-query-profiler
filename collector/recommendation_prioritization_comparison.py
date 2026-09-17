"""
M14.3 Score-Only vs Workload-Aware Recommendation Prioritization
----------------------------------------------------------------
Compares two prioritization strategies using the same recommendation
evaluation dataset and the same experimentally observed outcomes.

Strategy A: score-only
    Sort by the existing recommendation_score.

Strategy B: workload-aware
    Sort by workload priority, execution-time share, then the original
    recommendation score.

This module is analytical only. It does not modify the database,
recommendation scores, benchmark results, or validation evidence.
"""

from collector.recommendation_quality_analyzer import (
    build_recommendation_evaluation_dataset,
    get_evaluation_improvement,
)
from collector.workload_cost_analyzer import analyze_workload_costs


# =========================================================
# CONSTANTS
# =========================================================

WORKLOAD_PRIORITY_VALUE = {
    "Critical": 4,
    "High": 3,
    "Moderate": 2,
    "Low": 1,
    "Unknown": 0,
}


# =========================================================
# BASIC HELPERS
# =========================================================

def _numeric(value, default=0.0):
    """Return a numeric value when possible."""
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _evaluated_records(dataset):
    """
    Keep only records with an experimentally observed improvement.

    Rows without benchmark evidence are retained in the source dataset
    but excluded from outcome-ranking evaluation.
    """
    return [
        record
        for record in dataset
        if get_evaluation_improvement(record) is not None
    ]


def _status_value(status):
    """
    Convert validation status into an outcome value.

    Retained for compatibility with existing analysis/tests. Validation
    status is not used to determine either ranking strategy because doing
    so would introduce outcome leakage.
    """
    return {
        "SUCCESSFUL": 3,
        "NEUTRAL": 2,
        "UNSUCCESSFUL": 1,
        "UNSAFE": 0,
    }.get(status, -1)


# =========================================================
# SCORE-ONLY RANKING
# =========================================================

def rank_score_only(records):
    """
    Rank evaluated records using only the existing recommendation score.

    Higher recommendation scores appear first.

    Validation status and observed improvement are deliberately excluded
    from ranking to avoid outcome leakage. Recommendation ID is used only
    as a deterministic tie-breaker.
    """
    ranked = list(records)

    ranked.sort(
        key=lambda record: (
            _numeric(
                record.get("recommendation_score")
            ),
            -_numeric(
                record.get("recommendation_id")
            ),
        ),
        reverse=True,
    )

    return _assign_rank(ranked, "score_only_rank")


# =========================================================
# WORKLOAD-AWARE RANKING
# =========================================================

def rank_workload_aware(records):
    """
    Rank evaluated records using workload-aware prioritization.

    Ordering:
        1. workload priority
        2. workload execution-time share
        3. original recommendation score
        4. recommendation ID

    Validation status and observed improvement are deliberately excluded
    from ranking to avoid outcome leakage.

    The original recommendation score is preserved as a secondary
    signal; it is not recalculated.
    """
    ranked = list(records)

    ranked.sort(
        key=lambda record: (
            WORKLOAD_PRIORITY_VALUE.get(
                record.get("workload_priority"),
                0,
            ),
            _numeric(
                record.get("execution_time_share")
            ),
            _numeric(
                record.get("recommendation_score")
            ),
            -_numeric(
                record.get("recommendation_id")
            ),
        ),
        reverse=True,
    )

    return _assign_rank(ranked, "workload_aware_rank")


def _assign_rank(records, rank_key):
    """Attach a one-based rank without modifying source records."""
    ranked = []

    for position, record in enumerate(records, start=1):
        copy = dict(record)
        copy[rank_key] = position
        ranked.append(copy)

    return ranked


# =========================================================
# RANK COMPARISON
# =========================================================

def compare_rankings(records):
    """
    Compare score-only and workload-aware rankings.

    Returns:
        {
            "score_only": [...],
            "workload_aware": [...],
            "rank_comparison": [...],
            "rank_correlation": {...}
        }
    """
    evaluated = _evaluated_records(records)

    score_ranked = rank_score_only(evaluated)
    workload_ranked = rank_workload_aware(evaluated)

    score_by_key = {
        _record_key(record): record
        for record in score_ranked
    }

    workload_by_key = {
        _record_key(record): record
        for record in workload_ranked
    }

    keys = list(score_by_key.keys())

    comparison = []

    for key in keys:
        score_record = score_by_key[key]
        workload_record = workload_by_key[key]

        score_rank = score_record["score_only_rank"]
        workload_rank = workload_record["workload_aware_rank"]

        comparison.append({
            "record_key": key,
            "recommendation_id":
                score_record.get("recommendation_id"),
            "query_profile_id":
                score_record.get("query_profile_id"),
            "table_name":
                score_record.get("table_name"),
            "column_name":
                score_record.get("column_name"),
            "recommendation_score":
                score_record.get("recommendation_score"),
            "recommendation_priority":
                score_record.get("recommendation_priority"),
            "workload_priority":
                score_record.get("workload_priority"),
            "execution_time_share":
                score_record.get("execution_time_share"),
            "execution_frequency_share":
                score_record.get("execution_frequency_share"),
            "validation_status":
                score_record.get("validation_status"),
            "evaluation_improvement":
                get_evaluation_improvement(score_record),
            "score_only_rank": score_rank,
            "workload_aware_rank": workload_rank,
            "rank_shift":
                score_rank - workload_rank,
        })

    comparison.sort(
        key=lambda row: row["score_only_rank"]
    )

    return {
        "score_only": score_ranked,
        "workload_aware": workload_ranked,
        "rank_comparison": comparison,
        "rank_correlation": calculate_rank_correlation(
            comparison
        ),
    }


def _record_key(record):
    """
    Identify a benchmark observation.

    benchmark_id is preferred because one recommendation can have
    multiple experimental observations.
    """
    benchmark_id = record.get("benchmark_id")

    if benchmark_id is not None:
        return ("benchmark", benchmark_id)

    return (
        "recommendation",
        record.get("recommendation_id"),
        record.get("query_profile_id"),
        record.get("table_name"),
        record.get("column_name"),
    )


# =========================================================
# RANK CORRELATION
# =========================================================

def calculate_rank_correlation(comparison):
    """
    Calculate Pearson and Spearman-style correlation between the
    two ranking positions.

    No external statistical dependency is required.
    """
    pairs = [
        (
            row["score_only_rank"],
            row["workload_aware_rank"],
        )
        for row in comparison
        if row.get("score_only_rank") is not None
        and row.get("workload_aware_rank") is not None
    ]

    pearson = _pearson(pairs)

    score_ranks = [pair[0] for pair in pairs]
    workload_ranks = [pair[1] for pair in pairs]

    spearman_pairs = list(
        zip(
            _average_ranks(score_ranks),
            _average_ranks(workload_ranks),
        )
    )

    spearman = _pearson(spearman_pairs)

    return {
        "n": len(pairs),
        "pearson": pearson,
        "spearman": spearman,
    }


def _pearson(pairs):
    """Calculate Pearson correlation for numeric pairs."""
    if len(pairs) < 2:
        return None

    xs = [float(pair[0]) for pair in pairs]
    ys = [float(pair[1]) for pair in pairs]

    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in zip(xs, ys)
    )

    denominator_x = sum(
        (x - mean_x) ** 2
        for x in xs
    )

    denominator_y = sum(
        (y - mean_y) ** 2
        for y in ys
    )

    denominator = (
        denominator_x * denominator_y
    ) ** 0.5

    if denominator == 0:
        return 0.0

    return numerator / denominator


def _average_ranks(values):
    """
    Assign average ranks for ties.

    Values are ranked ascending, matching conventional Spearman
    rank-correlation calculation.
    """
    indexed = sorted(
        enumerate(values),
        key=lambda item: item[1],
    )

    ranks = [0.0] * len(values)

    position = 0

    while position < len(indexed):
        end = position

        while (
            end + 1 < len(indexed)
            and indexed[end + 1][1] == indexed[position][1]
        ):
            end += 1

        average_rank = (
            position + 1 + end + 1
        ) / 2.0

        for index in range(position, end + 1):
            original_index = indexed[index][0]
            ranks[original_index] = average_rank

        position = end + 1

    return ranks


# =========================================================
# TOP-N OUTCOME ANALYSIS
# =========================================================

def summarize_top_k(records, k_values=(3, 5, 10)):
    """
    Compare outcome composition in the top-k observations for both
    prioritization strategies.

    The same validation observations are used for both strategies.
    """
    comparison = compare_rankings(records)

    results = {}

    for k in k_values:
        results[k] = {
            "score_only": summarize_ranked_records(
                comparison["score_only"][:k]
            ),
            "workload_aware": summarize_ranked_records(
                comparison["workload_aware"][:k]
            ),
        }

    return results


def summarize_ranked_records(records):
    """Summarize validation outcomes for a ranked subset."""
    total = len(records)

    successful = sum(
        1
        for record in records
        if record.get("validation_status")
        == "SUCCESSFUL"
    )

    neutral = sum(
        1
        for record in records
        if record.get("validation_status")
        == "NEUTRAL"
    )

    unsuccessful = sum(
        1
        for record in records
        if record.get("validation_status")
        == "UNSUCCESSFUL"
    )

    unsafe = sum(
        1
        for record in records
        if record.get("validation_status")
        == "UNSAFE"
    )

    improvements = [
        get_evaluation_improvement(record)
        for record in records
        if get_evaluation_improvement(record) is not None
    ]

    low_benefit = sum(
        1
        for improvement in improvements
        if 0 <= improvement < 5
    )

    negative_benefit = sum(
        1
        for improvement in improvements
        if improvement < 0
    )

    return {
        "count": total,
        "successful": successful,
        "neutral": neutral,
        "unsuccessful": unsuccessful,
        "unsafe": unsafe,
        "success_rate": (
            successful / total * 100
            if total
            else 0.0
        ),
        "low_benefit": low_benefit,
        "negative_benefit": negative_benefit,
        "average_improvement": (
            sum(improvements) / len(improvements)
            if improvements
            else None
        ),
    }


# =========================================================
# RANK-SHIFT ANALYSIS
# =========================================================

def summarize_rank_shifts(comparison):
    """Summarize how much the workload-aware ranking moves records."""
    shifts = [
        row["rank_shift"]
        for row in comparison
        if row.get("rank_shift") is not None
    ]

    upward = [
        shift for shift in shifts
        if shift > 0
    ]

    downward = [
        shift for shift in shifts
        if shift < 0
    ]

    unchanged = [
        shift for shift in shifts
        if shift == 0
    ]

    absolute_shifts = [
        abs(shift)
        for shift in shifts
    ]

    return {
        "n": len(shifts),
        "upward": len(upward),
        "downward": len(downward),
        "unchanged": len(unchanged),
        "average_absolute_rank_shift": (
            sum(absolute_shifts) / len(absolute_shifts)
            if absolute_shifts
            else 0.0
        ),
        "maximum_absolute_rank_shift": (
            max(absolute_shifts)
            if absolute_shifts
            else 0
        ),
    }


# =========================================================
# CRITICAL WORKLOAD ANALYSIS
# =========================================================

def summarize_critical_workload(records):
    """
    Measure where Critical workload observations appear under each
    prioritization strategy.
    """
    comparison = compare_rankings(records)

    critical = [
        row
        for row in comparison["rank_comparison"]
        if row.get("workload_priority") == "Critical"
    ]

    def rank_stats(rank_key):
        ranks = [
            row[rank_key]
            for row in critical
            if row.get(rank_key) is not None
        ]

        return {
            "count": len(ranks),
            "ranks": sorted(ranks),
            "top_3_count": sum(
                1 for rank in ranks if rank <= 3
            ),
            "top_5_count": sum(
                1 for rank in ranks if rank <= 5
            ),
            "top_10_count": sum(
                1 for rank in ranks if rank <= 10
            ),
        }

    return {
        "critical_observation_count": len(critical),
        "score_only": rank_stats("score_only_rank"),
        "workload_aware": rank_stats("workload_aware_rank"),
    }


# =========================================================
# COMPLETE M14.3 ANALYSIS
# =========================================================

def analyze_prioritization_comparison(
    dataset,
    k_values=(3, 5, 10),
):
    """
    Run the complete M14.3 comparison.
    """
    evaluated = _evaluated_records(dataset)

    ranking = compare_rankings(evaluated)

    return {
        "evaluated_rows": len(evaluated),
        "score_only_count": len(
            ranking["score_only"]
        ),
        "workload_aware_count": len(
            ranking["workload_aware"]
        ),
        "rank_correlation":
            ranking["rank_correlation"],
        "rank_shifts":
            summarize_rank_shifts(
                ranking["rank_comparison"]
            ),
        "top_k":
            summarize_top_k(
                evaluated,
                k_values=k_values,
            ),
        "critical_workload":
            summarize_critical_workload(
                evaluated
            ),
        "rank_comparison":
            ranking["rank_comparison"],
        "score_only":
            ranking["score_only"],
        "workload_aware":
            ranking["workload_aware"],
    }


# =========================================================
# PRINT REPORT
# =========================================================

def print_prioritization_comparison(analysis):
    """Print the M14.3 research comparison."""
    print()
    print("=" * 100)
    print(
        "M14.3 SCORE-ONLY VS WORKLOAD-AWARE "
        "RECOMMENDATION PRIORITIZATION"
    )
    print("=" * 100)

    print()
    print("EXPERIMENT SET")
    print("-" * 100)
    print(
        f"Evaluated observations     : "
        f"{analysis['evaluated_rows']}"
    )
    print(
        "Strategy A                 : "
        "Existing recommendation score only"
    )
    print(
        "Strategy B                 : "
        "Workload priority + time share + original score"
    )
    print(
        "Validation evidence        : "
        "Same observations for both strategies"
    )

    correlation = analysis["rank_correlation"]

    print()
    print("RANK RELATIONSHIP")
    print("-" * 100)
    print(
        f"Pearson rank correlation   : "
        f"{correlation['pearson']:.3f}"
    )
    print(
        f"Spearman rank correlation  : "
        f"{correlation['spearman']:.3f}"
    )

    shifts = analysis["rank_shifts"]

    print()
    print("RANK SHIFTS")
    print("-" * 100)
    print(
        f"Moved upward               : "
        f"{shifts['upward']}"
    )
    print(
        f"Moved downward             : "
        f"{shifts['downward']}"
    )
    print(
        f"Unchanged                  : "
        f"{shifts['unchanged']}"
    )
    print(
        f"Average absolute shift    : "
        f"{shifts['average_absolute_rank_shift']:.2f}"
    )
    print(
        f"Maximum absolute shift    : "
        f"{shifts['maximum_absolute_rank_shift']}"
    )

    print()
    print("TOP-K OUTCOME COMPARISON")
    print("-" * 100)

    print(
        f"{'K':<6}"
        f"{'Strategy':<22}"
        f"{'Success':>10}"
        f"{'Success %':>12}"
        f"{'Neutral':>10}"
        f"{'Unsuccessful':>15}"
        f"{'Avg Improvement':>18}"
    )

    print("-" * 100)

    for k, strategies in analysis["top_k"].items():
        for strategy_name, metrics in strategies.items():
            display_name = (
                "Score-only"
                if strategy_name == "score_only"
                else "Workload-aware"
            )

            average = metrics["average_improvement"]

            average_text = (
                f"{average:.2f}%"
                if average is not None
                else "N/A"
            )

            print(
                f"{k:<6}"
                f"{display_name:<22}"
                f"{metrics['successful']:>10}"
                f"{metrics['success_rate']:>11.2f}%"
                f"{metrics['neutral']:>10}"
                f"{metrics['unsuccessful']:>15}"
                f"{average_text:>18}"
            )

    critical = analysis["critical_workload"]

    print()
    print("CRITICAL WORKLOAD PLACEMENT")
    print("-" * 100)
    print(
        f"Critical observations      : "
        f"{critical['critical_observation_count']}"
    )

    for strategy_name in (
        "score_only",
        "workload_aware",
    ):
        display_name = (
            "Score-only"
            if strategy_name == "score_only"
            else "Workload-aware"
        )

        stats = critical[strategy_name]

        print(
            f"{display_name:<26}"
            f"Top-3: {stats['top_3_count']}   "
            f"Top-5: {stats['top_5_count']}   "
            f"Top-10: {stats['top_10_count']}   "
            f"Ranks: {stats['ranks']}"
        )

    print()
    print(
        "Note: M14.3 is a descriptive comparison of the current "
        "experimental dataset. It does not establish causality or "
        "general performance across other workloads or databases."
    )

    print("=" * 100)


# =========================================================
# MAIN
# =========================================================

def main():
    """
    Load the current M14.1 dataset and run M14.3.
    """
    workload_analysis = analyze_workload_costs()

    dataset = build_recommendation_evaluation_dataset(
        workload_analysis
    )

    analysis = analyze_prioritization_comparison(
        dataset
    )

    print_prioritization_comparison(
        analysis
    )


if __name__ == "__main__":
    main()
