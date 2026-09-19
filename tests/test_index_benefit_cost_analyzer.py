from collector.index_benefit_cost_analyzer import (
    validate_benefit_cost_record,
    calculate_read_benefit_per_storage,
    calculate_benefit_cost_difference,
    classify_read_benefit,
    classify_cost_impact,
    build_benefit_cost_record,
    build_read_benefit_summary,
    build_cost_evidence_summary,
    build_integrated_benefit_cost_analysis,
)


def test_validate_benefit_cost_record():
    assert validate_benefit_cost_record({
        "read_improvement_percentage": 50,
        "index_size_bytes": 1000,
        "table_size_bytes": 5000,
        "maintenance_overhead_percentage": 10,
    })


def test_invalid_negative_index_size():
    assert not validate_benefit_cost_record({
        "index_size_bytes": -1,
    })


def test_read_benefit_per_storage():
    value = calculate_read_benefit_per_storage(
        50,
        1024 * 1024,
    )

    assert value == 50


def test_missing_storage_returns_none():
    assert calculate_read_benefit_per_storage(
        50,
        None,
    ) is None


def test_benefit_cost_difference():
    assert (
        calculate_benefit_cost_difference(
            60,
            20,
        )
        == 40
    )


def test_read_benefit_classification():
    assert classify_read_benefit(75) == "HIGH_BENEFIT"
    assert classify_read_benefit(25) == "MODERATE_BENEFIT"
    assert classify_read_benefit(5) == "LOW_BENEFIT"
    assert classify_read_benefit(-2) == "NEGATIVE_BENEFIT"


def test_cost_classification():
    assert classify_cost_impact(0) == "NONE_OR_NEGATIVE"
    assert classify_cost_impact(5) == "LOW_COST"
    assert classify_cost_impact(25) == "MODERATE_COST"
    assert classify_cost_impact(75) == "HIGH_COST"


def test_build_benefit_cost_record():
    record = build_benefit_cost_record(
        60,
        1024 * 1024,
        10 * 1024 * 1024,
        20,
        5,
    )

    assert record[
        "read_benefit_class"
    ] == "HIGH_BENEFIT"

    assert record[
        "maintenance_cost_class"
    ] == "MODERATE_COST"

    assert record[
        "read_benefit_per_storage_mb"
    ] == 60


def test_build_read_benefit_summary():
    dataset = [
        {
            "evaluation_improvement_percentage": 50,
            "validation_status": "SUCCESSFUL",
            "index_used": True,
            "rows_preserved": True,
        },
        {
            "evaluation_improvement_percentage": 10,
            "validation_status": "NEUTRAL",
            "index_used": False,
            "rows_preserved": True,
        },
        {
            "evaluation_improvement_percentage": -5,
            "validation_status": "UNSUCCESSFUL",
            "index_used": True,
            "rows_preserved": True,
        },
    ]

    summary = build_read_benefit_summary(
        dataset
    )

    assert summary[
        "evaluated_observations"
    ] == 3

    assert summary[
        "successful"
    ] == 1

    assert summary[
        "positive_benefit_count"
    ] == 2

    assert summary[
        "negative_benefit_count"
    ] == 1


def test_build_cost_evidence_summary():
    summary = build_cost_evidence_summary(
        600000,
        3000000,
        20,
        75,
        3,
        10,
        -5,
        100,
    )

    assert summary[
        "index_table_ratio_percentage"
    ] == 20

    assert summary[
        "maintenance_mean_cost_class"
    ] == "HIGH_COST"

    assert summary[
        "maintenance_median_cost_class"
    ] == "LOW_COST"


def test_integrated_analysis_keeps_evidence_separate():
    dataset = [
        {
            "evaluation_improvement_percentage": 50,
            "validation_status": "SUCCESSFUL",
            "index_used": True,
            "rows_preserved": True,
        }
    ]

    cost = build_cost_evidence_summary(
        600000,
        3000000,
        20,
        75,
        3,
    )

    analysis = (
        build_integrated_benefit_cost_analysis(
            dataset,
            cost,
        )
    )

    assert (
        analysis["cost_benefit_linked"]
        is False
    )

    assert (
        analysis["read_benefit_evidence"]
        ["evaluated_observations"]
        == 1
    )

    assert (
        analysis["cost_evidence"]
        ["index_size_bytes"]
        == 600000
    )
