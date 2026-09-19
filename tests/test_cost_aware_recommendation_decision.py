import pytest

from collector.cost_aware_recommendation_decision import (
    build_decision_input,
    determine_evidence_status,
    evaluate_recommendation,
    evaluate_recommendations,
    link_recommendation_evidence,
    summarize_cost_aware_decisions,
)


def make_recommendation():
    return {
        "recommendation_id": 1,
        "score": 80,
        "priority": "High",
        "candidate_type": "single",
        "columns": ["customer_id"],
    }


def make_workload():
    return {
        "priority": "High",
        "execution_time_share": 20.0,
        "frequency_share": 10.0,
    }


def make_read():
    return {
        "available": True,
        "average_improvement_percentage": 96.25,
        "median_improvement_percentage": 96.38,
        "absolute_savings_ms": 3.95,
        "index_used": True,
        "plan_changed": True,
        "rows_preserved": True,
    }


def make_cost():
    return {
        "storage_available": True,
        "index_table_ratio_percentage": 16.52,
        "write_available": True,
        "average_overhead_percentage": 8.09,
        "median_overhead_percentage": 0.02,
    }


def make_linkage(
    recommendation_id=1,
    same_index=True,
):
    return {
        "recommendation_id": recommendation_id,
        "evidence_recommendation_id": recommendation_id,
        "same_recommendation": True,
        "same_index": same_index,
        "linked": same_index,
        "evidence_status": (
            "COMPLETE" if same_index else "INSUFFICIENT"
        ),
        "query_fingerprint": "abc123",
        "index_name": "idx_orders_customer_id",
        "experiment_id": "M18_004",
    }


def test_complete_evidence_status():
    assert determine_evidence_status(
        True,
        True,
        True,
        True,
    ) == "COMPLETE"


def test_partial_evidence_status():
    assert determine_evidence_status(
        True,
        True,
        False,
        True,
    ) == "PARTIAL"


def test_unlinked_evidence_is_insufficient():
    assert determine_evidence_status(
        True,
        True,
        True,
        False,
    ) == "INSUFFICIENT"


def test_no_evidence_is_insufficient():
    assert determine_evidence_status(
        False,
        False,
        False,
        False,
    ) == "INSUFFICIENT"


def test_same_recommendation_and_index_links():
    result = link_recommendation_evidence(
        make_recommendation(),
        {
            "recommendation_id": 1,
            "read": True,
            "storage": True,
            "write": True,
            "linked": True,
            "same_index": True,
        },
    )

    assert result["linked"] is True
    assert result["evidence_status"] == "COMPLETE"


def test_different_recommendation_does_not_link():
    result = link_recommendation_evidence(
        make_recommendation(),
        {
            "recommendation_id": 99,
            "read": True,
            "storage": True,
            "write": True,
            "linked": True,
            "same_index": True,
        },
    )

    assert result["linked"] is False
    assert result["evidence_status"] == "INSUFFICIENT"


def test_same_index_false_does_not_link():
    result = link_recommendation_evidence(
        make_recommendation(),
        {
            "recommendation_id": 1,
            "read": True,
            "storage": True,
            "write": True,
            "linked": True,
            "same_index": False,
        },
    )

    assert result["linked"] is False
    assert result["evidence_status"] == "INSUFFICIENT"


def test_build_decision_input_preserves_recommendation_score():
    result = build_decision_input(
        make_recommendation(),
        make_workload(),
        make_read(),
        make_cost(),
        make_linkage(),
    )

    assert result["recommendation"]["score"] == 80
    assert result["recommendation"]["priority"] == "High"

    assert result["evidence"]["read"] is True
    assert result["evidence"]["storage"] is True
    assert result["evidence"]["write"] is True
    assert result["evidence"]["linked"] is True


def test_complete_evidence_produces_recommendation():
    result = evaluate_recommendation(
        make_recommendation(),
        make_workload(),
        make_read(),
        make_cost(),
        make_linkage(),
    )

    assert result["decision"]["decision"] == "RECOMMEND"
    assert result["evidence"]["complete"] is True


def test_unlinked_evidence_cannot_produce_recommendation():
    result = evaluate_recommendation(
        make_recommendation(),
        make_workload(),
        make_read(),
        make_cost(),
        make_linkage(same_index=False),
    )

    assert (
        result["decision"]["decision"]
        == "INSUFFICIENT_EVIDENCE"
    )


def test_evaluate_multiple_recommendations():
    records = [
        {
            "recommendation": make_recommendation(),
            "workload": make_workload(),
            "read_evidence": make_read(),
            "cost_evidence": make_cost(),
            "linkage": make_linkage(),
        },
    ]

    results = evaluate_recommendations(records)

    assert len(results) == 1
    assert results[0]["recommendation_id"] == 1


def test_summary_counts_decisions():
    results = [
        evaluate_recommendation(
            make_recommendation(),
            make_workload(),
            make_read(),
            make_cost(),
            make_linkage(),
        )
    ]

    summary = summarize_cost_aware_decisions(
        results
    )

    assert summary["recommendation_count"] == 1
    assert summary["decision_counts"]["RECOMMEND"] == 1
    assert (
        summary["evidence_status_counts"]["COMPLETE"]
        == 1
    )


def test_invalid_recommendation_is_rejected():
    with pytest.raises(ValueError):
        link_recommendation_evidence(
            {},
            {
                "recommendation_id": 1,
                "read": True,
                "storage": True,
                "write": True,
                "linked": True,
                "same_index": True,
            },
        )


def test_invalid_evidence_is_rejected():
    with pytest.raises(ValueError):
        link_recommendation_evidence(
            make_recommendation(),
            {
                "recommendation_id": 1,
                "read": True,
            },
        )
