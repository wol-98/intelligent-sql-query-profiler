"""
M14.2 Recommendation Quality & Workload-Outcome Analysis
---------------------------------------------------------
Converts the M14.1 analytical dataset into research-oriented
descriptive statistics.

This module is analytical only. It does not:
    - modify recommendations
    - create or drop indexes
    - modify benchmark results
    - change validation decisions

M14.2 examines:
    1. Recommendation score vs measured improvement
    2. Workload execution-time share vs measured improvement
    3. Workload priority vs validation outcome
    4. Recommendation priority vs validation outcome
    5. Overall and grouped validation rates
    6. Low-benefit, negative-benefit and index-not-used outcomes

Important:
    The analysis reports associations in the experimental dataset.
    It does not claim causation or general predictive accuracy.
"""

from collections import Counter, defaultdict
from math import sqrt


# =========================================================
# BASIC HELPERS
# =========================================================

def _numeric_pairs(dataset, x_key, y_key):
    """Return finite numeric (x, y) pairs from dataset rows."""
    pairs = []

    for row in dataset:
        x = row.get(x_key)
        y = row.get(y_key)

        if isinstance(x, bool) or isinstance(y, bool):
            continue

        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            pairs.append((float(x), float(y)))

    return pairs


def _mean(values):
    if not values:
        return None
    return sum(values) / len(values)


def _median(values):
    if not values:
        return None

    ordered = sorted(values)
    n = len(ordered)
    middle = n // 2

    if n % 2:
        return ordered[middle]

    return (ordered[middle - 1] + ordered[middle]) / 2


def _pearson_correlation(pairs):
    """
    Calculate Pearson correlation without external dependencies.

    Returns None when fewer than two observations exist or when
    either variable has zero variance.
    """
    if len(pairs) < 2:
        return None

    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]

    mean_x = _mean(xs)
    mean_y = _mean(ys)

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in pairs
    )

    denominator_x = sum(
        (x - mean_x) ** 2
        for x in xs
    )

    denominator_y = sum(
        (y - mean_y) ** 2
        for y in ys
    )

    denominator = sqrt(
        denominator_x * denominator_y
    )

    if denominator == 0:
        return None

    return numerator / denominator


def _rank_values(values):
    """
    Average-rank values, including tied values.
    """
    indexed = sorted(
        enumerate(values),
        key=lambda item: item[1]
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

        for i in range(position, end + 1):
            original_index = indexed[i][0]
            ranks[original_index] = average_rank

        position = end + 1

    return ranks


def _spearman_correlation(pairs):
    """
    Calculate Spearman rank correlation using average ranks.
    """
    if len(pairs) < 2:
        return None

    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]

    ranked_x = _rank_values(xs)
    ranked_y = _rank_values(ys)

    return _pearson_correlation(
        list(zip(ranked_x, ranked_y))
    )


# =========================================================
# OUTCOME CLASSIFICATION
# =========================================================

def classify_improvement(improvement):
    """
    Classify measured improvement using the project's existing
    5% success threshold.

    Categories:
        SUCCESSFUL       >= 5%
        LOW_BENEFIT      >= 0% and < 5%
        NEGATIVE_BENEFIT < 0%
        UNKNOWN          no measurable improvement
    """
    if improvement is None:
        return "UNKNOWN"

    if improvement >= 5:
        return "SUCCESSFUL"

    if improvement >= 0:
        return "LOW_BENEFIT"

    return "NEGATIVE_BENEFIT"


# =========================================================
# CORRELATION ANALYSIS
# =========================================================

def analyze_score_vs_improvement(dataset):
    """
    Analyze recommendation score against measured improvement.
    """
    pairs = _numeric_pairs(
        dataset,
        "recommendation_score",
        "evaluation_improvement_percentage",
    )

    return {
        "metric": "recommendation_score_vs_improvement",
        "n": len(pairs),
        "pearson_correlation": _pearson_correlation(pairs),
        "spearman_correlation": _spearman_correlation(pairs),
    }


def analyze_workload_share_vs_improvement(dataset):
    """
    Analyze workload execution-time share against measured improvement.
    """
    pairs = _numeric_pairs(
        dataset,
        "execution_time_share",
        "evaluation_improvement_percentage",
    )

    return {
        "metric": "execution_time_share_vs_improvement",
        "n": len(pairs),
        "pearson_correlation": _pearson_correlation(pairs),
        "spearman_correlation": _spearman_correlation(pairs),
    }


# =========================================================
# GROUPED OUTCOME ANALYSIS
# =========================================================

def summarize_by_category(
    dataset,
    category_key,
    categories=None,
):
    """
    Summarize validation outcomes for a categorical field.

    Only rows with a measurable evaluation improvement are included
    in outcome-rate calculations.
    """
    grouped = defaultdict(list)

    for row in dataset:
        category = row.get(category_key)

        if category is None:
            continue

        grouped[category].append(row)

    if categories is not None:
        ordered_categories = list(categories)
    else:
        ordered_categories = sorted(
            grouped.keys(),
            key=lambda value: str(value)
        )

    results = []

    for category in ordered_categories:
        rows = grouped.get(category, [])

        evaluated = [
            row
            for row in rows
            if row.get(
                "evaluation_improvement_percentage"
            ) is not None
        ]

        improvements = [
            row["evaluation_improvement_percentage"]
            for row in evaluated
        ]

        statuses = Counter(
            row.get("validation_status")
            for row in evaluated
        )

        successful = sum(
            1
            for row in evaluated
            if row.get("validation_status")
            == "SUCCESSFUL"
        )

        low_benefit = sum(
            1
            for row in evaluated
            if classify_improvement(
                row.get(
                    "evaluation_improvement_percentage"
                )
            ) == "LOW_BENEFIT"
        )

        negative = sum(
            1
            for row in evaluated
            if classify_improvement(
                row.get(
                    "evaluation_improvement_percentage"
                )
            ) == "NEGATIVE_BENEFIT"
        )

        results.append({
            "category": category,
            "rows": len(rows),
            "evaluated_rows": len(evaluated),
            "successful": successful,
            "neutral": statuses.get("NEUTRAL", 0),
            "unsuccessful": statuses.get(
                "UNSUCCESSFUL",
                0
            ),
            "unsafe": statuses.get("UNSAFE", 0),
            "success_rate": (
                successful / len(evaluated) * 100
                if evaluated
                else None
            ),
            "low_benefit": low_benefit,
            "negative_benefit": negative,
            "average_improvement": _mean(
                improvements
            ),
            "median_improvement": _median(
                improvements
            ),
        })

    return results


def analyze_workload_priority_outcomes(dataset):
    return summarize_by_category(
        dataset,
        "workload_priority",
        categories=[
            "Critical",
            "High",
            "Moderate",
            "Low",
            "Unknown",
        ],
    )


def analyze_recommendation_priority_outcomes(dataset):
    return summarize_by_category(
        dataset,
        "recommendation_priority",
        categories=[
            "High",
            "Medium",
            "Low",
            "Unknown",
        ],
    )


# =========================================================
# OVERALL RESEARCH METRICS
# =========================================================

def calculate_research_metrics(dataset):
    """
    Calculate M14.2 project-level descriptive metrics.
    """
    evaluated = [
        row
        for row in dataset
        if row.get(
            "evaluation_improvement_percentage"
        ) is not None
    ]

    successful = [
        row
        for row in evaluated
        if row.get("validation_status")
        == "SUCCESSFUL"
    ]

    neutral = [
        row
        for row in evaluated
        if row.get("validation_status")
        == "NEUTRAL"
    ]

    unsuccessful = [
        row
        for row in evaluated
        if row.get("validation_status")
        == "UNSUCCESSFUL"
    ]

    unsafe = [
        row
        for row in evaluated
        if row.get("validation_status")
        == "UNSAFE"
    ]

    low_benefit = [
        row
        for row in evaluated
        if classify_improvement(
            row.get(
                "evaluation_improvement_percentage"
            )
        ) == "LOW_BENEFIT"
    ]

    negative_benefit = [
        row
        for row in evaluated
        if classify_improvement(
            row.get(
                "evaluation_improvement_percentage"
            )
        ) == "NEGATIVE_BENEFIT"
    ]

    index_used = [
        row
        for row in evaluated
        if row.get("index_used") is True
    ]

    index_not_used = [
        row
        for row in evaluated
        if row.get("index_used") is False
    ]

    rows_preserved = [
        row
        for row in evaluated
        if row.get("rows_preserved") is True
    ]

    high_priority = [
        row
        for row in evaluated
        if row.get("recommendation_priority")
        == "High"
    ]

    high_priority_successful = [
        row
        for row in high_priority
        if row.get("validation_status")
        == "SUCCESSFUL"
    ]

    workload_critical = [
        row
        for row in evaluated
        if row.get("workload_priority")
        == "Critical"
    ]

    workload_critical_successful = [
        row
        for row in workload_critical
        if row.get("validation_status")
        == "SUCCESSFUL"
    ]

    improvements = [
        row["evaluation_improvement_percentage"]
        for row in evaluated
    ]

    return {
        "dataset_rows": len(dataset),
        "evaluated_rows": len(evaluated),
        "successful": len(successful),
        "neutral": len(neutral),
        "unsuccessful": len(unsuccessful),
        "unsafe": len(unsafe),
        "success_rate": (
            len(successful) / len(evaluated) * 100
            if evaluated
            else None
        ),
        "neutral_rate": (
            len(neutral) / len(evaluated) * 100
            if evaluated
            else None
        ),
        "unsuccessful_rate": (
            len(unsuccessful) / len(evaluated) * 100
            if evaluated
            else None
        ),
        "unsafe_rate": (
            len(unsafe) / len(evaluated) * 100
            if evaluated
            else None
        ),
        "average_improvement": _mean(
            improvements
        ),
        "median_improvement": _median(
            improvements
        ),
        "low_benefit_count": len(low_benefit),
        "low_benefit_rate": (
            len(low_benefit) / len(evaluated) * 100
            if evaluated
            else None
        ),
        "negative_benefit_count": len(
            negative_benefit
        ),
        "negative_benefit_rate": (
            len(negative_benefit) / len(evaluated) * 100
            if evaluated
            else None
        ),
        "index_used_count": len(index_used),
        "index_used_rate": (
            len(index_used) / len(evaluated) * 100
            if evaluated
            else None
        ),
        "index_not_used_count": len(index_not_used),
        "index_not_used_rate": (
            len(index_not_used) / len(evaluated) * 100
            if evaluated
            else None
        ),
        "rows_preserved_count": len(rows_preserved),
        "rows_preserved_rate": (
            len(rows_preserved) / len(evaluated) * 100
            if evaluated
            else None
        ),
        "high_priority_count": len(high_priority),
        "high_priority_successful": len(
            high_priority_successful
        ),
        "high_priority_success_rate": (
            len(high_priority_successful)
            / len(high_priority)
            * 100
            if high_priority
            else None
        ),
        "workload_critical_count": len(
            workload_critical
        ),
        "workload_critical_successful": len(
            workload_critical_successful
        ),
        "workload_critical_success_rate": (
            len(workload_critical_successful)
            / len(workload_critical)
            * 100
            if workload_critical
            else None
        ),
    }


# =========================================================
# FULL M14.2 ANALYSIS
# =========================================================

def analyze_recommendation_quality(dataset):
    """
    Run the complete M14.2 analysis.

    Returns a dictionary suitable for reporting, testing,
    dashboard integration and later statistical analysis.
    """
    return {
        "metrics": calculate_research_metrics(dataset),
        "score_vs_improvement": (
            analyze_score_vs_improvement(dataset)
        ),
        "workload_share_vs_improvement": (
            analyze_workload_share_vs_improvement(
                dataset
            )
        ),
        "workload_priority_outcomes": (
            analyze_workload_priority_outcomes(
                dataset
            )
        ),
        "recommendation_priority_outcomes": (
            analyze_recommendation_priority_outcomes(
                dataset
            )
        ),
    }


# =========================================================
# DISPLAY
# =========================================================

def _format(value, decimals=2):
    if value is None:
        return "N/A"

    if isinstance(value, float):
        return f"{value:.{decimals}f}"

    return str(value)


def print_research_analysis(analysis):
    """
    Print the M14.2 research-oriented analysis.
    """
    metrics = analysis["metrics"]
    score = analysis["score_vs_improvement"]
    workload = analysis[
        "workload_share_vs_improvement"
    ]

    print("\n" + "=" * 80)
    print(
        "M14.2 RECOMMENDATION QUALITY & "
        "WORKLOAD-OUTCOME ANALYSIS"
    )
    print("=" * 80)

    print("\nOVERALL VALIDATION")
    print("-" * 80)
    print(
        f"Evaluated rows             : "
        f"{metrics['evaluated_rows']}"
    )
    print(
        f"Successful                 : "
        f"{metrics['successful']} "
        f"({_format(metrics['success_rate'])}%)"
    )
    print(
        f"Neutral                    : "
        f"{metrics['neutral']} "
        f"({_format(metrics['neutral_rate'])}%)"
    )
    print(
        f"Unsuccessful               : "
        f"{metrics['unsuccessful']} "
        f"({_format(metrics['unsuccessful_rate'])}%)"
    )
    print(
        f"Unsafe                     : "
        f"{metrics['unsafe']} "
        f"({_format(metrics['unsafe_rate'])}%)"
    )
    print(
        f"Average improvement        : "
        f"{_format(metrics['average_improvement'])}%"
    )
    print(
        f"Median improvement         : "
        f"{_format(metrics['median_improvement'])}%"
    )

    print("\nOUTCOME QUALITY")
    print("-" * 80)
    print(
        f"Low-benefit outcomes       : "
        f"{metrics['low_benefit_count']} "
        f"({_format(metrics['low_benefit_rate'])}%)"
    )
    print(
        f"Negative-benefit outcomes  : "
        f"{metrics['negative_benefit_count']} "
        f"({_format(metrics['negative_benefit_rate'])}%)"
    )
    print(
        f"Index used                 : "
        f"{metrics['index_used_count']} "
        f"({_format(metrics['index_used_rate'])}%)"
    )
    print(
        f"Index not used             : "
        f"{metrics['index_not_used_count']} "
        f"({_format(metrics['index_not_used_rate'])}%)"
    )
    print(
        f"Rows preserved             : "
        f"{metrics['rows_preserved_count']} "
        f"({_format(metrics['rows_preserved_rate'])}%)"
    )

    print("\nRELATIONSHIPS")
    print("-" * 80)
    print(
        f"Score vs improvement       : "
        f"n={score['n']}, "
        f"Pearson={_format(score['pearson_correlation'])}, "
        f"Spearman={_format(score['spearman_correlation'])}"
    )
    print(
        f"Time share vs improvement  : "
        f"n={workload['n']}, "
        f"Pearson={_format(workload['pearson_correlation'])}, "
        f"Spearman={_format(workload['spearman_correlation'])}"
    )

    print("\nPRIORITY OUTCOMES")
    print("-" * 80)
    print(
        f"High recommendation priority: "
        f"{metrics['high_priority_count']}"
    )
    print(
        f"High-priority successful    : "
        f"{metrics['high_priority_successful']}"
    )
    print(
        f"High-priority success rate  : "
        f"{_format(metrics['high_priority_success_rate'])}%"
    )
    print(
        f"Critical workload rows      : "
        f"{metrics['workload_critical_count']}"
    )
    print(
        f"Critical workload successful: "
        f"{metrics['workload_critical_successful']}"
    )
    print(
        f"Critical workload success rate: "
        f"{_format(metrics['workload_critical_success_rate'])}%"
    )

    print("\nWORKLOAD PRIORITY OUTCOMES")
    print("-" * 80)
    print(
        "Priority | Evaluated | Successful | "
        "Neutral | Unsuccessful | Success %"
    )

    for row in analysis[
        "workload_priority_outcomes"
    ]:
        if row["evaluated_rows"] == 0:
            continue

        print(
            f"{str(row['category']):<8} | "
            f"{row['evaluated_rows']:>9} | "
            f"{row['successful']:>10} | "
            f"{row['neutral']:>7} | "
            f"{row['unsuccessful']:>12} | "
            f"{_format(row['success_rate']):>8}"
        )

    print("\nRECOMMENDATION PRIORITY OUTCOMES")
    print("-" * 80)
    print(
        "Priority | Evaluated | Successful | "
        "Neutral | Unsuccessful | Success %"
    )

    for row in analysis[
        "recommendation_priority_outcomes"
    ]:
        if row["evaluated_rows"] == 0:
            continue

        print(
            f"{str(row['category']):<8} | "
            f"{row['evaluated_rows']:>9} | "
            f"{row['successful']:>10} | "
            f"{row['neutral']:>7} | "
            f"{row['unsuccessful']:>12} | "
            f"{_format(row['success_rate']):>8}"
        )

    print("=" * 80)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    from collector.workload_cost_analyzer import (
        analyze_workload_costs
    )
    from collector.recommendation_quality_analyzer import (
        build_recommendation_evaluation_dataset
    )

    workload_analysis = analyze_workload_costs()

    dataset = build_recommendation_evaluation_dataset(
        workload_analysis
    )

    analysis = analyze_recommendation_quality(
        dataset
    )

    print_research_analysis(analysis)
