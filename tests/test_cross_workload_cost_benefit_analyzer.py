from collector.cross_workload_cost_benefit_analyzer import (
    validate_cross_workload_results,
    extract_read_improvements,
    extract_read_savings,
    extract_storage_ratios,
    extract_write_overheads,
    summarize_values,
    build_cross_workload_summary,
)


def make_result(
    experiment_id,
    read_improvement,
    read_savings,
    storage_ratio,
    write_overhead,
):
    return {
        "experiment_id": experiment_id,
        "index_name": f"{experiment_id}_idx",
        "read_analysis": {
            "average_improvement_percentage": read_improvement,
            "median_improvement_percentage": read_improvement,
            "absolute_average_savings_ms": read_savings,
            "index_used": True,
            "plan_changed": True,
            "rows_preserved": True,
        },
        "storage_analysis": {
            "index_table_ratio_percentage": storage_ratio,
        },
        "write_analysis": {
            "average_overhead_percentage": write_overhead,
            "median_overhead_percentage": write_overhead,
        },
    }


def test_valid_cross_workload_results():
    results = [
        make_result("M18_001", 96.2, 3.95, 16.5, 8.0),
        make_result("M18_002", 40.0, 1.20, 10.0, 5.0),
    ]

    assert validate_cross_workload_results(results)


def test_invalid_cross_workload_results():
    assert not validate_cross_workload_results([])
    assert not validate_cross_workload_results(None)


def test_extract_read_improvements():
    results = [
        make_result("M18_001", 96.2, 3.95, 16.5, 8.0),
        make_result("M18_002", 40.0, 1.20, 10.0, 5.0),
    ]

    assert extract_read_improvements(results) == [96.2, 40.0]


def test_extract_read_savings():
    results = [
        make_result("M18_001", 96.2, 3.95, 16.5, 8.0),
        make_result("M18_002", 40.0, 1.20, 10.0, 5.0),
    ]

    assert extract_read_savings(results) == [3.95, 1.20]


def test_extract_storage_ratios():
    results = [
        make_result("M18_001", 96.2, 3.95, 16.5, 8.0),
        make_result("M18_002", 40.0, 1.20, 10.0, 5.0),
    ]

    assert extract_storage_ratios(results) == [16.5, 10.0]


def test_extract_write_overheads():
    results = [
        make_result("M18_001", 96.2, 3.95, 16.5, 8.0),
        make_result("M18_002", 40.0, 1.20, 10.0, 5.0),
    ]

    assert extract_write_overheads(results) == [8.0, 5.0]


def test_summarize_values():
    result = summarize_values([10, 20, 30])

    assert result["count"] == 3
    assert result["mean"] == 20
    assert result["median"] == 20
    assert result["minimum"] == 10
    assert result["maximum"] == 30


def test_summarize_empty_values():
    result = summarize_values([])

    assert result["count"] == 0
    assert result["mean"] is None
    assert result["median"] is None


def test_build_cross_workload_summary():
    results = [
        make_result("M18_001", 96.2, 3.95, 16.5, 8.0),
        make_result("M18_002", 40.0, 1.20, 10.0, 5.0),
    ]

    summary = build_cross_workload_summary(results)

    assert summary["experiment_count"] == 2
    assert len(summary["workloads"]) == 2

    assert (
        summary["aggregate"]
        ["read_improvement_percent"]["mean"]
        == 68.1
    )
