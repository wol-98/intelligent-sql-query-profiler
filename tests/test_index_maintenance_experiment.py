import pytest

from collector.index_maintenance_experiment import (
    build_maintenance_result,
    calculate_average,
    calculate_median,
    calculate_maintenance_overhead,
    calculate_standard_deviation,
    summarize_maintenance_result,
    validate_maintenance_result,
)


def test_calculate_average():
    assert calculate_average([10.0, 20.0, 30.0]) == 20.0


def test_calculate_average_empty():
    with pytest.raises(ValueError):
        calculate_average([])


def test_calculate_median():
    assert calculate_median([10.0, 20.0, 30.0]) == 20.0


def test_calculate_median_even_values():
    assert calculate_median([10.0, 20.0, 30.0, 40.0]) == 25.0


def test_calculate_median_empty():
    with pytest.raises(ValueError):
        calculate_median([])


def test_standard_deviation():
    result = calculate_standard_deviation(
        [10.0, 20.0, 30.0]
    )

    assert result == pytest.approx(10.0)


def test_standard_deviation_single_value():
    assert calculate_standard_deviation([10.0]) == 0.0


def test_calculate_maintenance_overhead():
    overhead_ms, overhead_percent = calculate_maintenance_overhead(
        10.0,
        12.0,
    )

    assert overhead_ms == pytest.approx(2.0)
    assert overhead_percent == pytest.approx(20.0)


def test_negative_maintenance_overhead():
    overhead_ms, overhead_percent = calculate_maintenance_overhead(
        10.0,
        8.0,
    )

    assert overhead_ms == pytest.approx(-2.0)
    assert overhead_percent == pytest.approx(-20.0)


def test_zero_baseline_rejected():
    with pytest.raises(ValueError):
        calculate_maintenance_overhead(0.0, 10.0)


def test_build_maintenance_result():
    result = build_maintenance_result(
        table_name="orders",
        indexed_columns=["customer_id"],
        row_count=100,
        iterations=5,
        baseline_times_ms=[
            10.0,
            11.0,
            9.0,
            10.0,
            10.0,
        ],
        indexed_times_ms=[
            12.0,
            13.0,
            11.0,
            12.0,
            12.0,
        ],
    )

    assert result["table_name"] == "orders"
    assert result["indexed_columns"] == ["customer_id"]
    assert result["row_count"] == 100
    assert result["iterations"] == 5

    assert result["baseline_average_ms"] == pytest.approx(10.0)
    assert result["indexed_average_ms"] == pytest.approx(12.0)

    assert result["baseline_median_ms"] == pytest.approx(10.0)
    assert result["indexed_median_ms"] == pytest.approx(12.0)

    assert result["maintenance_overhead_ms"] == pytest.approx(2.0)
    assert result["maintenance_overhead_percent"] == pytest.approx(20.0)

    assert result["median_overhead_ms"] == pytest.approx(2.0)
    assert result["median_overhead_percent"] == pytest.approx(20.0)

    assert "baseline_stddev_ms" in result
    assert "indexed_stddev_ms" in result

    assert result["baseline_min_ms"] == 9.0
    assert result["baseline_max_ms"] == 11.0

    assert result["indexed_min_ms"] == 11.0
    assert result["indexed_max_ms"] == 13.0


def test_invalid_result_missing_key():
    with pytest.raises(ValueError):
        validate_maintenance_result(
            {
                "table_name": "orders",
            }
        )


def test_invalid_row_count():
    with pytest.raises(ValueError):
        build_maintenance_result(
            table_name="orders",
            indexed_columns=["customer_id"],
            row_count=1,
            iterations=3,
            baseline_times_ms=[10.0, 11.0, 9.0],
            indexed_times_ms=[12.0, 13.0, 11.0],
        )


def test_invalid_iterations():
    with pytest.raises(ValueError):
        build_maintenance_result(
            table_name="orders",
            indexed_columns=["customer_id"],
            row_count=100,
            iterations=3,
            baseline_times_ms=[10.0, 11.0],
            indexed_times_ms=[12.0, 13.0, 11.0],
        )


def test_empty_baseline_rejected():
    with pytest.raises(ValueError):
        build_maintenance_result(
            table_name="orders",
            indexed_columns=["customer_id"],
            row_count=100,
            iterations=0,
            baseline_times_ms=[],
            indexed_times_ms=[],
        )


def test_summary_positive_median_overhead():
    result = build_maintenance_result(
        table_name="orders",
        indexed_columns=["customer_id"],
        row_count=100,
        iterations=5,
        baseline_times_ms=[
            10.0,
            10.0,
            10.0,
            10.0,
            10.0,
        ],
        indexed_times_ms=[
            12.0,
            12.0,
            12.0,
            12.0,
            12.0,
        ],
    )

    summary = summarize_maintenance_result(result)

    assert (
        summary["interpretation"]
        == "indexed writes had higher median execution time"
    )


def test_summary_negative_median_overhead():
    result = build_maintenance_result(
        table_name="orders",
        indexed_columns=["customer_id"],
        row_count=100,
        iterations=5,
        baseline_times_ms=[
            10.0,
            10.0,
            10.0,
            10.0,
            10.0,
        ],
        indexed_times_ms=[
            8.0,
            8.0,
            8.0,
            8.0,
            8.0,
        ],
    )

    summary = summarize_maintenance_result(result)

    assert (
        summary["interpretation"]
        == "indexed writes had lower median execution time "
        "in this observation"
    )


def test_summary_zero_median_overhead():
    result = build_maintenance_result(
        table_name="orders",
        indexed_columns=["customer_id"],
        row_count=100,
        iterations=5,
        baseline_times_ms=[
            10.0,
            10.0,
            10.0,
            10.0,
            10.0,
        ],
        indexed_times_ms=[
            10.0,
            10.0,
            10.0,
            10.0,
            10.0,
        ],
    )

    summary = summarize_maintenance_result(result)

    assert (
        summary["interpretation"]
        == "no median write-time difference was measured"
    )
