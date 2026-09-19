import pytest

from collector.linked_cost_benefit_analyzer import (
    build_linked_cost_benefit_analysis,
    calculate_absolute_read_savings,
    calculate_read_improvement,
    calculate_storage_ratio,
    calculate_write_overhead,
    classify_effect,
    validate_linked_evidence,
)


def make_result():
    return {
        "experiment_id": "M18_001",
        "index_name": "m18_001_idx_orders_customer_id",
        "table_name": "orders",
        "columns": ["customer_id"],
        "index_type": "BTREE",
        "evidence_linked": True,
        "read_evidence": {
            "baseline": {
                "average_execution_time_ms": 4.1082,
                "median_execution_time_ms": 4.0885,
                "representative_plan": {
                    "Node Type": "Seq Scan"
                },
            },
            "indexed": {
                "average_execution_time_ms": 0.1541,
                "median_execution_time_ms": 0.148,
                "representative_plan": {
                    "Node Type": "Index Scan"
                },
            },
            "rows_preserved": True,
            "index_used": True,
            "plan_changed": True,
        },
        "storage_evidence": {
            "index_size_bytes": 606208,
            "index_size_pretty": "592 kB",
            "table_size_bytes": 3670016,
            "table_size_pretty": "3584 kB",
            "index_metadata": {
                "index_type": "btree",
                "column_count": 1,
                "columns": ["customer_id"],
                "is_valid": True,
            },
        },
        "write_evidence": {
            "baseline": {
                "average_execution_time_ms": 147.6142011990305,
                "median_execution_time_ms": 152.85346300152014,
                "standard_deviation_ms": 38.69725521844263,
            },
            "indexed": {
                "average_execution_time_ms": 159.5491302003211,
                "median_execution_time_ms": 152.8794410005503,
                "standard_deviation_ms": 29.41212895649738,
            },
            "batch_size": 1000,
        },
    }


def test_validate_linked_evidence():
    assert validate_linked_evidence(make_result()) is True


def test_validate_linked_evidence_rejects_invalid():
    assert validate_linked_evidence({}) is False


def test_absolute_read_savings():
    assert calculate_absolute_read_savings(4.1082, 0.1541) == pytest.approx(
        3.9541
    )


def test_read_improvement():
    assert calculate_read_improvement(4.1082, 0.1541) == pytest.approx(
        96.24896548
    )


def test_storage_ratio():
    assert calculate_storage_ratio(606208, 3670016) == pytest.approx(
        16.51785714
    )


def test_write_overhead():
    assert calculate_write_overhead(
        147.6142011990305,
        159.5491302003211,
    ) == pytest.approx(8.08521735)


def test_classify_positive():
    assert classify_effect(10) == "positive"


def test_classify_negative():
    assert classify_effect(-10) == "negative"


def test_classify_neutral():
    assert classify_effect(0) == "neutral"


def test_complete_analysis():
    result = build_linked_cost_benefit_analysis(make_result())

    assert result["experiment_id"] == "M18_001"
    assert result["index_name"] == "m18_001_idx_orders_customer_id"
    assert result["evidence_linked"] is True

    assert result["read_analysis"]["index_used"] is True
    assert result["read_analysis"]["rows_preserved"] is True
    assert result["read_analysis"]["plan_changed"] is True

    assert result["storage_analysis"]["index_size_bytes"] == 606208

    assert result["write_analysis"]["batch_size"] == 1000


def test_complete_analysis_preserves_linkage():
    result = build_linked_cost_benefit_analysis(make_result())

    assert result["experiment_id"] == "M18_001"
    assert result["index_name"] == "m18_001_idx_orders_customer_id"
