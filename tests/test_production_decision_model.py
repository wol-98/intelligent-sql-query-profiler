import pytest

from collector.production_decision_model import (
    POLICY_VERSION,
    assess_evidence_completeness,
    build_production_decision,
    classify_read_benefit,
    classify_storage_cost,
    classify_write_cost,
    determine_production_decision,
)


def make_complete_input(
    improvement=60.0,
    storage_ratio=10.0,
    write_overhead=5.0,
    rows_preserved=True,
    index_used=True,
):
    return {
        "recommendation": {
            "recommendation_id": 1,
            "score": 80,
            "priority": "High",
        },
        "workload": {
            "priority": "High",
            "execution_time_share": 20.0,
            "frequency_share": 10.0,
        },
        "read_evidence": {
            "available": True,
            "average_improvement_percentage": improvement,
            "median_improvement_percentage": improvement,
            "absolute_savings_ms": 5.0,
            "index_used": index_used,
            "plan_changed": True,
            "rows_preserved": rows_preserved,
        },
        "cost_evidence": {
            "storage_available": True,
            "index_table_ratio_percentage": storage_ratio,
            "write_available": True,
            "average_overhead_percentage": write_overhead,
            "median_overhead_percentage": write_overhead,
        },
        "evidence": {
            "read": True,
            "storage": True,
            "write": True,
            "linked": True,
            "complete": True,
        },
    }


# ------------------------------------------------------------------
# Threshold tests
# ------------------------------------------------------------------


def test_read_thresholds():
    assert classify_read_benefit(-0.01) == "negative"
    assert classify_read_benefit(0.0) == "neutral"
    assert classify_read_benefit(9.99) == "neutral"
    assert classify_read_benefit(10.0) == "positive"
    assert classify_read_benefit(49.99) == "positive"
    assert classify_read_benefit(50.0) == "strong"


def test_storage_thresholds():
    assert classify_storage_cost(10.0) == "low"
    assert classify_storage_cost(10.01) == "moderate"
    assert classify_storage_cost(25.0) == "moderate"
    assert classify_storage_cost(25.01) == "high"


def test_write_thresholds():
    assert classify_write_cost(5.0) == "low"
    assert classify_write_cost(5.01) == "moderate"
    assert classify_write_cost(20.0) == "moderate"
    assert classify_write_cost(20.01) == "high"


# ------------------------------------------------------------------
# Evidence tests
# ------------------------------------------------------------------


def test_complete_evidence():
    result = assess_evidence_completeness(
        True,
        True,
        True,
        True,
    )

    assert result["complete"] is True


def test_incomplete_evidence():
    result = assess_evidence_completeness(
        True,
        False,
        True,
        True,
    )

    assert result["complete"] is False

def test_evidence_completeness_is_derived():
    data = make_complete_input()

    data["evidence"] = {
        "read": False,
        "storage": False,
        "write": False,
        "linked": False,
        "complete": True,
    }

    result = build_production_decision(data)

    assert result["evidence"]["complete"] is False
    assert result["decision"] == "INSUFFICIENT_EVIDENCE"

def test_missing_evidence_flag_is_rejected():
    data = make_complete_input()

    data["evidence"] = {
        "read": True,
        "storage": True,
        "write": True,
    }

    with pytest.raises(ValueError):
        build_production_decision(data)



# ------------------------------------------------------------------
# Decision matrix tests
# ------------------------------------------------------------------


def test_strong_benefit_low_cost_recommends():
    assert determine_production_decision(
        "strong",
        "low",
        "low",
        True,
        True,
        True,
    ) == "RECOMMEND"


def test_strong_benefit_moderate_cost_recommends():
    assert determine_production_decision(
        "strong",
        "moderate",
        "moderate",
        True,
        True,
        True,
    ) == "RECOMMEND"


def test_strong_benefit_high_cost_requires_review():
    assert determine_production_decision(
        "strong",
        "moderate",
        "high",
        True,
        True,
        True,
    ) == "REVIEW"


def test_positive_benefit_low_cost_recommends():
    assert determine_production_decision(
        "positive",
        "low",
        "low",
        True,
        True,
        True,
    ) == "RECOMMEND"


def test_positive_benefit_moderate_cost_requires_review():
    assert determine_production_decision(
        "positive",
        "moderate",
        "low",
        True,
        True,
        True,
    ) == "REVIEW"


def test_positive_benefit_high_cost_rejects():
    assert determine_production_decision(
        "positive",
        "low",
        "high",
        True,
        True,
        True,
    ) == "REJECT"


def test_neutral_benefit_rejects():
    assert determine_production_decision(
        "neutral",
        "low",
        "low",
        True,
        True,
        True,
    ) == "REJECT"


def test_negative_benefit_rejects():
    assert determine_production_decision(
        "negative",
        "low",
        "low",
        True,
        True,
        True,
    ) == "REJECT"


# ------------------------------------------------------------------
# Safety gates
# ------------------------------------------------------------------


def test_rows_not_preserved_rejects():
    assert determine_production_decision(
        "strong",
        "low",
        "low",
        True,
        False,
        True,
    ) == "REJECT"


def test_index_not_used_requires_more_evidence():
    assert determine_production_decision(
        "strong",
        "low",
        "low",
        True,
        True,
        False,
    ) == "INSUFFICIENT_EVIDENCE"


def test_incomplete_evidence_requires_more_evidence():
    assert determine_production_decision(
        "strong",
        "low",
        "low",
        False,
        True,
        True,
    ) == "INSUFFICIENT_EVIDENCE"


# ------------------------------------------------------------------
# Integrated output tests
# ------------------------------------------------------------------


def test_build_recommendation_output():
    result = build_production_decision(
        make_complete_input(
            improvement=96.25,
            storage_ratio=16.52,
            write_overhead=8.09,
        )
    )

    assert result["decision_policy_version"] == POLICY_VERSION
    assert result["decision"] == "RECOMMEND"

    assert (
        result["read_evidence"]["classification"]
        == "strong"
    )

    assert (
        result["cost_evidence"]["storage_classification"]
        == "moderate"
    )

    assert (
        result["cost_evidence"]["write_classification"]
        == "moderate"
    )

    assert result["evidence"]["complete"] is True
    assert result["explanation"]


def test_build_neutral_result():
    result = build_production_decision(
        make_complete_input(
            improvement=0.83,
            storage_ratio=25.0,
            write_overhead=17.49,
        )
    )

    assert result["decision"] == "REJECT"
    assert (
        result["read_evidence"]["classification"]
        == "neutral"
    )


def test_build_high_cost_strong_result():
    result = build_production_decision(
        make_complete_input(
            improvement=97.8,
            storage_ratio=16.52,
            write_overhead=88.67,
        )
    )

    assert result["decision"] == "REVIEW"
    assert (
        result["read_evidence"]["classification"]
        == "strong"
    )
    assert (
        result["cost_evidence"]["write_classification"]
        == "high"
    )


def test_rows_not_preserved_overrides_other_evidence():
    result = build_production_decision(
        make_complete_input(
            improvement=96.25,
            storage_ratio=10.0,
            write_overhead=5.0,
            rows_preserved=False,
        )
    )

    assert result["decision"] == "REJECT"


def test_index_not_used_produces_insufficient_evidence():
    result = build_production_decision(
        make_complete_input(
            improvement=96.25,
            index_used=False,
        )
    )

    assert result["decision"] == "INSUFFICIENT_EVIDENCE"


# ------------------------------------------------------------------
# Validation tests
# ------------------------------------------------------------------


def test_invalid_storage_is_rejected():
    with pytest.raises(ValueError):
        classify_storage_cost(-1)


def test_negative_write_overhead_is_low():
    assert classify_write_cost(-1.0) == "low"


def test_missing_required_input_section_is_rejected():
    data = make_complete_input()
    del data["cost_evidence"]

    with pytest.raises(ValueError):
        build_production_decision(data)
