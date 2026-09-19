"""
Composite Index Column-Order Analysis
-------------------------------------
M16.2 analytical layer for evaluating controlled
composite-index column-order experiments.

This module is analytical only.

It does not:
    - generate recommendations;
    - generate composite candidates;
    - create database indexes;
    - execute queries;
    - read benchmark_results;
    - use recommendation scores;
    - modify recommendation priorities.

The analysis operates on controlled experimental
observations supplied by the caller.
"""

from statistics import mean, median


REQUIRED_FIELDS = {
    "recommendation_id",
    "original_columns",
    "alternative_columns",
    "original_improvement_percentage",
    "alternative_improvement_percentage",
    "improvement_difference_percentage_points",
    "original_index_used",
    "alternative_index_used",
    "original_rows_preserved",
    "alternative_rows_preserved",
}


def validate_experiment_result(result):
    """
    Validate the minimum structure required for analysis.
    """
    if not isinstance(result, dict):
        return False

    if not REQUIRED_FIELDS.issubset(result.keys()):
        return False

    if not result.get("original_columns"):
        return False

    if not result.get("alternative_columns"):
        return False

    return True


def classify_order_effect(effect):
    """
    Classify the observed difference between the original
    and alternative column ordering.

    Thresholds are intentionally descriptive rather than
    predictive.
    """
    if effect is None:
        return "unknown"

    absolute_effect = abs(effect)

    if absolute_effect < 1:
        return "negligible"

    if absolute_effect < 10:
        return "moderate"

    return "substantial"


def classify_experiment_result(result):
    """
    Classify one controlled experiment based on its
    observed improvement and order effect.
    """
    if not validate_experiment_result(result):
        raise ValueError("Invalid composite-order experiment result")

    effect = result["improvement_difference_percentage_points"]

    return {
        "recommendation_id": result["recommendation_id"],
        "original_columns": list(result["original_columns"]),
        "alternative_columns": list(result["alternative_columns"]),
        "original_improvement_percentage": (
            result["original_improvement_percentage"]
        ),
        "alternative_improvement_percentage": (
            result["alternative_improvement_percentage"]
        ),
        "order_effect_percentage_points": effect,
        "order_effect_class": classify_order_effect(effect),
        "original_index_used": result["original_index_used"],
        "alternative_index_used": result["alternative_index_used"],
        "rows_preserved": (
            result["original_rows_preserved"]
            and result["alternative_rows_preserved"]
        ),
    }


def calculate_order_effect_statistics(results):
    """
    Calculate descriptive statistics across controlled
    composite column-order experiments.
    """
    valid_results = [
        result
        for result in results or []
        if validate_experiment_result(result)
    ]

    if not valid_results:
        return {
            "experiment_count": 0,
            "mean_order_effect_percentage_points": None,
            "median_order_effect_percentage_points": None,
            "minimum_order_effect_percentage_points": None,
            "maximum_order_effect_percentage_points": None,
            "negligible_effect_count": 0,
            "moderate_effect_count": 0,
            "substantial_effect_count": 0,
        }

    effects = [
        result["improvement_difference_percentage_points"]
        for result in valid_results
    ]

    classifications = [
        classify_order_effect(effect)
        for effect in effects
    ]

    return {
        "experiment_count": len(valid_results),
        "mean_order_effect_percentage_points": mean(effects),
        "median_order_effect_percentage_points": median(effects),
        "minimum_order_effect_percentage_points": min(effects),
        "maximum_order_effect_percentage_points": max(effects),
        "negligible_effect_count": classifications.count("negligible"),
        "moderate_effect_count": classifications.count("moderate"),
        "substantial_effect_count": classifications.count("substantial"),
    }


def calculate_variant_statistics(results):
    """
    Calculate descriptive statistics for the original and
    alternative column-order variants.
    """
    valid_results = [
        result
        for result in results or []
        if validate_experiment_result(result)
    ]

    if not valid_results:
        return {
            "experiment_count": 0,
            "original_average_improvement": None,
            "alternative_average_improvement": None,
            "original_median_improvement": None,
            "alternative_median_improvement": None,
            "original_index_usage_rate": None,
            "alternative_index_usage_rate": None,
            "rows_preserved_rate": None,
        }

    original_improvements = [
        result["original_improvement_percentage"]
        for result in valid_results
    ]

    alternative_improvements = [
        result["alternative_improvement_percentage"]
        for result in valid_results
    ]

    original_usage = [
        result["original_index_used"]
        for result in valid_results
    ]

    alternative_usage = [
        result["alternative_index_used"]
        for result in valid_results
    ]

    rows_preserved = [
        (
            result["original_rows_preserved"]
            and result["alternative_rows_preserved"]
        )
        for result in valid_results
    ]

    count = len(valid_results)

    return {
        "experiment_count": count,
        "original_average_improvement": mean(original_improvements),
        "alternative_average_improvement": mean(alternative_improvements),
        "original_median_improvement": median(original_improvements),
        "alternative_median_improvement": median(alternative_improvements),
        "original_index_usage_rate": (
            sum(original_usage) / count * 100
        ),
        "alternative_index_usage_rate": (
            sum(alternative_usage) / count * 100
        ),
        "rows_preserved_rate": (
            sum(rows_preserved) / count * 100
        ),
    }


def build_analysis_summary(results):
    """
    Build the complete descriptive M16.2 analysis summary.
    """
    classified_results = [
        classify_experiment_result(result)
        for result in results or []
        if validate_experiment_result(result)
    ]

    order_effects = calculate_order_effect_statistics(results)
    variant_statistics = calculate_variant_statistics(results)

    return {
        "experiment_results": classified_results,
        "order_effect_statistics": order_effects,
        "variant_statistics": variant_statistics,
    }


def print_analysis_summary(summary):
    """
    Print a human-readable M16.2 analysis summary.
    """
    order_stats = summary["order_effect_statistics"]
    variant_stats = summary["variant_statistics"]

    print("\n" + "=" * 72)
    print("M16.2 — COMPOSITE INDEX COLUMN-ORDER ANALYSIS")
    print("=" * 72)

    print("\nExperiment Count")
    print("-" * 72)
    print(order_stats["experiment_count"])

    print("\nOrder Effect (percentage points)")
    print("-" * 72)
    print(
        f"Mean:     "
        f"{order_stats['mean_order_effect_percentage_points']:.2f}"
    )
    print(
        f"Median:   "
        f"{order_stats['median_order_effect_percentage_points']:.2f}"
    )
    print(
        f"Minimum:  "
        f"{order_stats['minimum_order_effect_percentage_points']:.2f}"
    )
    print(
        f"Maximum:  "
        f"{order_stats['maximum_order_effect_percentage_points']:.2f}"
    )

    print("\nOrder Effect Classification")
    print("-" * 72)
    print(f"Negligible:   {order_stats['negligible_effect_count']}")
    print(f"Moderate:     {order_stats['moderate_effect_count']}")
    print(f"Substantial:  {order_stats['substantial_effect_count']}")

    print("\nVariant Improvement")
    print("-" * 72)
    print(
        f"Original average:     "
        f"{variant_stats['original_average_improvement']:.2f}%"
    )
    print(
        f"Alternative average:  "
        f"{variant_stats['alternative_average_improvement']:.2f}%"
    )
    print(
        f"Original median:      "
        f"{variant_stats['original_median_improvement']:.2f}%"
    )
    print(
        f"Alternative median:   "
        f"{variant_stats['alternative_median_improvement']:.2f}%"
    )

    print("\nIndex Usage")
    print("-" * 72)
    print(
        f"Original:     "
        f"{variant_stats['original_index_usage_rate']:.2f}%"
    )
    print(
        f"Alternative:  "
        f"{variant_stats['alternative_index_usage_rate']:.2f}%"
    )

    print("\nRows Preserved")
    print("-" * 72)
    print(
        f"Both variants preserved rows in "
        f"{variant_stats['rows_preserved_rate']:.2f}% "
        f"of experiments."
    )

    print("\nPer-Experiment Classification")
    print("-" * 72)

    for result in summary["experiment_results"]:
        print(
            f"Rec {result['recommendation_id']}: "
            f"{result['order_effect_percentage_points']:.2f} pp "
            f"({result['order_effect_class']})"
        )

    print("\n" + "=" * 72)
