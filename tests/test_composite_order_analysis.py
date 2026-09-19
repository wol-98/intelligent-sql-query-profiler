from collector.composite_order_analysis import (
    build_analysis_summary,
    calculate_order_effect_statistics,
    calculate_variant_statistics,
    classify_order_effect,
    classify_experiment_result,
    validate_experiment_result,
)


def make_result(
    recommendation_id,
    original_improvement,
    alternative_improvement,
    order_effect,
    original_used=True,
    alternative_used=True,
):
    return {
        "recommendation_id": recommendation_id,
        "original_columns": ["a", "b"],
        "alternative_columns": ["b", "a"],
        "original_improvement_percentage": original_improvement,
        "alternative_improvement_percentage": alternative_improvement,
        "improvement_difference_percentage_points": order_effect,
        "original_index_used": original_used,
        "alternative_index_used": alternative_used,
        "original_rows_preserved": True,
        "alternative_rows_preserved": True,
    }


def test_validate_experiment_result():
    result = make_result(1, 10.0, 9.0, -1.0)

    assert validate_experiment_result(result) is True
    assert validate_experiment_result({}) is False
    assert validate_experiment_result(None) is False


def test_classify_order_effect():
    assert classify_order_effect(0.5) == "negligible"
    assert classify_order_effect(-5.0) == "moderate"
    assert classify_order_effect(20.0) == "substantial"
    assert classify_order_effect(-20.0) == "substantial"


def test_classify_experiment_result():
    result = make_result(32, 97.16, 97.27, 0.10)

    classified = classify_experiment_result(result)

    assert classified["recommendation_id"] == 32
    assert classified["order_effect_class"] == "negligible"
    assert classified["rows_preserved"] is True


def test_order_effect_statistics():
    results = [
        make_result(
            32,
            97.16,
            97.27,
            0.10,
            original_used=True,
            alternative_used=True,
        ),
        make_result(
            33,
            80.13,
            -0.26,
            -80.39,
            original_used=True,
            alternative_used=False,
        ),
        make_result(
            34,
            16.88,
            -1.25,
            -18.13,
            original_used=True,
            alternative_used=False,
        ),
        make_result(
            35,
            -0.65,
            -2.35,
            -1.69,
            original_used=True,
            alternative_used=True,
        ),
    ]

    stats = calculate_order_effect_statistics(results)

    assert stats["experiment_count"] == 4
    assert round(stats["mean_order_effect_percentage_points"], 2) == -25.03
    assert round(stats["median_order_effect_percentage_points"], 2) == -9.91
    assert stats["minimum_order_effect_percentage_points"] == -80.39
    assert stats["maximum_order_effect_percentage_points"] == 0.10

    assert stats["negligible_effect_count"] == 1
    assert stats["moderate_effect_count"] == 1
    assert stats["substantial_effect_count"] == 2


def test_variant_statistics():
    results = [
        make_result(
            32,
            97.16,
            97.27,
            0.10,
            original_used=True,
            alternative_used=True,
        ),
        make_result(
            33,
            80.13,
            -0.26,
            -80.39,
            original_used=True,
            alternative_used=False,
        ),
        make_result(
            34,
            16.88,
            -1.25,
            -18.13,
            original_used=True,
            alternative_used=False,
        ),
        make_result(
            35,
            -0.65,
            -2.35,
            -1.69,
            original_used=True,
            alternative_used=True,
        ),
    ]

    stats = calculate_variant_statistics(results)

    assert stats["experiment_count"] == 4
    assert round(stats["original_average_improvement"], 2) == 48.38
    assert round(stats["alternative_average_improvement"], 2) == 23.35
    assert stats["original_index_usage_rate"] == 100.0
    assert stats["alternative_index_usage_rate"] == 50.0
    assert stats["rows_preserved_rate"] == 100.0


def test_build_analysis_summary():
    results = [
        make_result(
            32,
            97.16,
            97.27,
            0.10,
            original_used=True,
            alternative_used=True,
        ),
        make_result(
            33,
            80.13,
            -0.26,
            -80.39,
            original_used=True,
            alternative_used=False,
        ),
        make_result(
            34,
            16.88,
            -1.25,
            -18.13,
            original_used=True,
            alternative_used=False,
        ),
        make_result(
            35,
            -0.65,
            -2.35,
            -1.69,
            original_used=True,
            alternative_used=True,
        ),
    ]

    summary = build_analysis_summary(results)

    assert len(summary["experiment_results"]) == 4
    assert summary["order_effect_statistics"]["experiment_count"] == 4
    assert summary["variant_statistics"]["experiment_count"] == 4


def test_invalid_results_are_excluded_from_statistics():
    results = [
        make_result(32, 97.16, 97.27, 0.10),
        {},
        None,
    ]

    stats = calculate_order_effect_statistics(results)

    assert stats["experiment_count"] == 1
