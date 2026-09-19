import pytest

from collector.integrated_optimization_report import (
    DECISION_POLICY_VERSION,
    GUARDRAIL_POLICY_VERSION,
    REPORT_VERSION,
    build_integrated_record,
    validate_integrated_record,
)


def make_recommendation():
    return {
        "recommendation_id": 42,
        "score": 75,
        "priority": "High",
        "candidate_type": "single_column",
        "columns": ["customer_id"],
    }


def make_query():
    return {
        "fingerprint": "abc123",
        "template": (
            "SELECT * FROM orders WHERE customer_id = ?;"
        ),
        "query_type": "SELECT",
        "tables": ["orders"],
    }


def make_workload():
    return {
        "priority": "High",
        "execution_time_share": 15.5,
        "frequency_share": 12.0,
    }


def make_read_evidence():
    return {
        "available": True,
        "average_improvement_percentage": 96.25,
        "median_improvement_percentage": 96.38,
        "absolute_savings_ms": 3.95,
        "index_used": True,
        "plan_changed": True,
        "rows_preserved": True,
    }


def make_cost_evidence():
    return {
        "storage_available": True,
        "index_table_ratio_percentage": 16.52,
        "write_available": True,
        "average_overhead_percentage": 8.09,
        "median_overhead_percentage": 0.02,
    }


def make_linkage():
    return {
        "same_index": True,
        "index_name": "idx_orders_customer_id",
        "linked_experiment_id": "M18_004",
        "evidence_status": "COMPLETE",
    }


def make_decision():
    return {
        "decision": "RECOMMEND",
        "policy_version": "M19.1-v1",
        "explanation": "Read benefit is strong and costs are within policy.",
    }


def make_guardrails():
    return {
        "status": "PASS",
        "policy_version": "M19.3-v1",
        "checks": {
            "evidence_completeness": "PASS",
            "evidence_linkage": "PASS",
            "rows_preserved": "PASS",
            "index_usage": "PASS",
            "execution_evidence": "PASS",
            "experimental_scope": "PASS",
        },
        "blocking_reasons": [],
        "insufficient_evidence_reasons": [],
    }


def make_record():
    return build_integrated_record(
        recommendation=make_recommendation(),
        query=make_query(),
        workload=make_workload(),
        read_evidence=make_read_evidence(),
        cost_evidence=make_cost_evidence(),
        linkage=make_linkage(),
        decision=make_decision(),
        guardrails=make_guardrails(),
    )


def test_builds_complete_integrated_record():
    record = make_record()

    assert validate_integrated_record(record) is True
    assert record["recommendation"]["recommendation_id"] == 42
    assert record["decision"]["decision"] == "RECOMMEND"
    assert record["guardrails"]["status"] == "PASS"


def test_preserves_report_versions():
    record = make_record()

    assert record["report"]["report_version"] == REPORT_VERSION
    assert (
        record["report"]["decision_policy_version"]
        == DECISION_POLICY_VERSION
    )
    assert (
        record["report"]["guardrail_policy_version"]
        == GUARDRAIL_POLICY_VERSION
    )


def test_preserves_recommendation_score():
    recommendation = make_recommendation()

    record = build_integrated_record(
        recommendation,
        make_query(),
        make_workload(),
        make_read_evidence(),
        make_cost_evidence(),
        make_linkage(),
        make_decision(),
        make_guardrails(),
    )

    assert record["recommendation"]["score"] == 75


def test_preserves_recommendation_priority():
    record = make_record()

    assert record["recommendation"]["priority"] == "High"


def test_preserves_read_evidence():
    record = make_record()

    assert (
        record["read_evidence"]["average_improvement_percentage"]
        == 96.25
    )
    assert record["read_evidence"]["index_used"] is True
    assert record["read_evidence"]["rows_preserved"] is True


def test_preserves_cost_evidence():
    record = make_record()

    assert (
        record["cost_evidence"]["index_table_ratio_percentage"]
        == 16.52
    )
    assert (
        record["cost_evidence"]["average_overhead_percentage"]
        == 8.09
    )


def test_preserves_linkage():
    record = make_record()

    assert record["linkage"]["same_index"] is True
    assert record["linkage"]["index_name"] == "idx_orders_customer_id"
    assert record["linkage"]["linked_experiment_id"] == "M18_004"
    assert record["linkage"]["evidence_status"] == "COMPLETE"


def test_preserves_decision():
    record = make_record()

    assert record["decision"]["decision"] == "RECOMMEND"
    assert record["decision"]["policy_version"] == "M19.1-v1"


def test_preserves_guardrails():
    record = make_record()

    assert record["guardrails"]["status"] == "PASS"
    assert record["guardrails"]["policy_version"] == "M19.3-v1"


def test_missing_recommendation_is_rejected():
    record = make_record()
    del record["recommendation"]

    with pytest.raises(ValueError):
        validate_integrated_record(record)


def test_missing_query_is_rejected():
    record = make_record()
    del record["query"]

    with pytest.raises(ValueError):
        validate_integrated_record(record)


def test_missing_workload_is_rejected():
    record = make_record()
    del record["workload"]

    with pytest.raises(ValueError):
        validate_integrated_record(record)


def test_missing_read_evidence_is_rejected():
    record = make_record()
    del record["read_evidence"]

    with pytest.raises(ValueError):
        validate_integrated_record(record)


def test_missing_cost_evidence_is_rejected():
    record = make_record()
    del record["cost_evidence"]

    with pytest.raises(ValueError):
        validate_integrated_record(record)


def test_missing_linkage_is_rejected():
    record = make_record()
    del record["linkage"]

    with pytest.raises(ValueError):
        validate_integrated_record(record)


def test_missing_decision_is_rejected():
    record = make_record()
    del record["decision"]

    with pytest.raises(ValueError):
        validate_integrated_record(record)


def test_missing_guardrails_are_rejected():
    record = make_record()
    del record["guardrails"]

    with pytest.raises(ValueError):
        validate_integrated_record(record)


def test_incomplete_evidence_can_be_preserved():
    """
    M19.4 reports evidence state; it does not fabricate missing evidence.
    """
    linkage = make_linkage()
    linkage["evidence_status"] = "INSUFFICIENT"

    read_evidence = make_read_evidence()
    read_evidence["available"] = False
    read_evidence["average_improvement_percentage"] = None
    read_evidence["median_improvement_percentage"] = None
    read_evidence["absolute_savings_ms"] = None
    read_evidence["index_used"] = None
    read_evidence["plan_changed"] = None
    read_evidence["rows_preserved"] = None

    record = build_integrated_record(
        make_recommendation(),
        make_query(),
        make_workload(),
        read_evidence,
        make_cost_evidence(),
        linkage,
        {
            "decision": "INSUFFICIENT_EVIDENCE",
            "policy_version": "M19.1-v1",
            "explanation": "Required linked evidence is unavailable.",
        },
        {
            "status": "INSUFFICIENT_EVIDENCE",
            "policy_version": "M19.3-v1",
            "checks": {},
            "blocking_reasons": [],
            "insufficient_evidence_reasons": [
                "Read evidence unavailable."
            ],
        },
    )

    assert record["linkage"]["evidence_status"] == "INSUFFICIENT"
    assert record["read_evidence"]["available"] is False
    assert (
        record["read_evidence"]["average_improvement_percentage"]
        is None
    )


def test_invalid_decision_is_rejected():
    decision = make_decision()
    decision["decision"] = "APPROVE"

    with pytest.raises(ValueError):
        build_integrated_record(
            make_recommendation(),
            make_query(),
            make_workload(),
            make_read_evidence(),
            make_cost_evidence(),
            make_linkage(),
            decision,
            make_guardrails(),
        )


def test_invalid_guardrail_status_is_rejected():
    guardrails = make_guardrails()
    guardrails["status"] = "SAFE"

    with pytest.raises(ValueError):
        build_integrated_record(
            make_recommendation(),
            make_query(),
            make_workload(),
            make_read_evidence(),
            make_cost_evidence(),
            make_linkage(),
            make_decision(),
            guardrails,
        )


def test_invalid_evidence_status_is_rejected():
    linkage = make_linkage()
    linkage["evidence_status"] = "UNKNOWN"

    with pytest.raises(ValueError):
        build_integrated_record(
            make_recommendation(),
            make_query(),
            make_workload(),
            make_read_evidence(),
            make_cost_evidence(),
            linkage,
            make_decision(),
            make_guardrails(),
        )


def test_build_does_not_mutate_input_records():
    recommendation = make_recommendation()
    query = make_query()
    workload = make_workload()
    read_evidence = make_read_evidence()
    cost_evidence = make_cost_evidence()
    linkage = make_linkage()
    decision = make_decision()
    guardrails = make_guardrails()

    build_integrated_record(
        recommendation,
        query,
        workload,
        read_evidence,
        cost_evidence,
        linkage,
        decision,
        guardrails,
    )

    assert recommendation["score"] == 75
    assert read_evidence["average_improvement_percentage"] == 96.25
    assert linkage["evidence_status"] == "COMPLETE"
    assert decision["decision"] == "RECOMMEND"
    assert guardrails["status"] == "PASS"


def test_build_recommendation_outcome():
    from collector.integrated_optimization_report import (
        build_recommendation_outcome,
    )

    record = make_record()

    outcome = build_recommendation_outcome(record)

    assert outcome["recommendation_id"] == 42
    assert outcome["index_name"] == "idx_orders_customer_id"
    assert outcome["query_fingerprint"] == "abc123"
    assert outcome["experiment_id"] == "M18_004"

    assert outcome["outcome"]["decision"] == "RECOMMEND"
    assert outcome["outcome"]["guardrail_status"] == "PASS"
    assert outcome["outcome"]["evidence_status"] == "COMPLETE"

    assert outcome["read"]["improvement"] == 96.25
    assert outcome["read"]["median_improvement"] == 96.38
    assert outcome["read"]["savings_ms"] == 3.95

    assert outcome["cost"]["storage_ratio"] == 16.52
    assert outcome["cost"]["write_overhead"] == 8.09
    assert outcome["cost"]["median_write_overhead"] == 0.02


def test_outcome_preserves_decision_without_recalculation():
    from collector.integrated_optimization_report import (
        build_recommendation_outcome,
    )

    record = make_record()
    record["decision"]["decision"] = "REVIEW"

    outcome = build_recommendation_outcome(record)

    assert outcome["outcome"]["decision"] == "REVIEW"


def test_outcome_preserves_guardrail_status_without_recalculation():
    from collector.integrated_optimization_report import (
        build_recommendation_outcome,
    )

    record = make_record()
    record["guardrails"]["status"] = "INSUFFICIENT_EVIDENCE"

    outcome = build_recommendation_outcome(record)

    assert (
        outcome["outcome"]["guardrail_status"]
        == "INSUFFICIENT_EVIDENCE"
    )


def test_outcome_preserves_incomplete_evidence():
    from collector.integrated_optimization_report import (
        build_recommendation_outcome,
    )

    record = make_record()

    record["linkage"]["evidence_status"] = "INSUFFICIENT"
    record["read_evidence"]["available"] = False
    record["read_evidence"]["average_improvement_percentage"] = None
    record["read_evidence"]["median_improvement_percentage"] = None
    record["read_evidence"]["absolute_savings_ms"] = None

    outcome = build_recommendation_outcome(record)

    assert outcome["outcome"]["evidence_status"] == "INSUFFICIENT"
    assert outcome["read"]["improvement"] is None
    assert outcome["read"]["median_improvement"] is None
    assert outcome["read"]["savings_ms"] is None


def test_outcome_does_not_include_a_new_score():
    from collector.integrated_optimization_report import (
        build_recommendation_outcome,
    )

    outcome = build_recommendation_outcome(make_record())

    assert "score" not in outcome
    assert "priority" not in outcome
    assert "new_score" not in outcome


def test_outcome_does_not_mutate_integrated_record():
    from collector.integrated_optimization_report import (
        build_recommendation_outcome,
    )

    record = make_record()

    original_decision = record["decision"]["decision"]
    original_improvement = (
        record["read_evidence"]["average_improvement_percentage"]
    )

    build_recommendation_outcome(record)

    assert record["decision"]["decision"] == original_decision
    assert (
        record["read_evidence"]["average_improvement_percentage"]
        == original_improvement
    )


def test_empty_portfolio_summary():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    summary = summarize_integrated_decisions([])

    assert summary["total_recommendations"] == 0

    assert summary["decision_counts"] == {
        "RECOMMEND": 0,
        "REVIEW": 0,
        "REJECT": 0,
        "INSUFFICIENT_EVIDENCE": 0,
    }

    assert summary["guardrail_counts"] == {
        "PASS": 0,
        "BLOCK": 0,
        "INSUFFICIENT_EVIDENCE": 0,
    }

    assert summary["evidence_counts"] == {
        "COMPLETE": 0,
        "PARTIAL": 0,
        "INSUFFICIENT": 0,
    }

    assert summary["read_summary"]["observations"] == 0
    assert (
        summary["read_summary"]["average_improvement_percentage"]
        is None
    )

    assert summary["cost_summary"]["storage_observations"] == 0
    assert (
        summary["cost_summary"]["average_storage_ratio_percentage"]
        is None
    )


def test_portfolio_summary_counts_states():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    record1 = make_record()

    record2 = make_record()
    record2["recommendation"]["recommendation_id"] = 43
    record2["decision"]["decision"] = "REVIEW"
    record2["guardrails"]["status"] = "INSUFFICIENT_EVIDENCE"
    record2["linkage"]["evidence_status"] = "PARTIAL"

    record3 = make_record()
    record3["recommendation"]["recommendation_id"] = 44
    record3["decision"]["decision"] = "REJECT"
    record3["guardrails"]["status"] = "BLOCK"
    record3["linkage"]["evidence_status"] = "INSUFFICIENT"

    summary = summarize_integrated_decisions(
        [record1, record2, record3]
    )

    assert summary["total_recommendations"] == 3

    assert summary["decision_counts"] == {
        "RECOMMEND": 1,
        "REVIEW": 1,
        "REJECT": 1,
        "INSUFFICIENT_EVIDENCE": 0,
    }

    assert summary["guardrail_counts"] == {
        "PASS": 1,
        "BLOCK": 1,
        "INSUFFICIENT_EVIDENCE": 1,
    }

    assert summary["evidence_counts"] == {
        "COMPLETE": 1,
        "PARTIAL": 1,
        "INSUFFICIENT": 1,
    }


def test_portfolio_summary_aggregates_available_read_evidence():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    record1 = make_record()

    record2 = make_record()
    record2["recommendation"]["recommendation_id"] = 43
    record2["read_evidence"]["average_improvement_percentage"] = 20.0
    record2["read_evidence"]["median_improvement_percentage"] = 18.0
    record2["read_evidence"]["absolute_savings_ms"] = 2.0

    summary = summarize_integrated_decisions(
        [record1, record2]
    )

    assert summary["read_summary"]["observations"] == 2

    assert (
        summary["read_summary"]["average_improvement_percentage"]
        == pytest.approx(58.125)
    )

    assert (
        summary["read_summary"]["median_improvement_percentage"]
        == pytest.approx(57.19)
    )

    assert (
        summary["read_summary"]["average_savings_ms"]
        == pytest.approx(2.975)
    )


def test_portfolio_summary_aggregates_available_cost_evidence():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    record1 = make_record()

    record2 = make_record()
    record2["recommendation"]["recommendation_id"] = 43
    record2["cost_evidence"]["index_table_ratio_percentage"] = 25.0
    record2["cost_evidence"]["average_overhead_percentage"] = 17.0
    record2["cost_evidence"]["median_overhead_percentage"] = 15.0

    summary = summarize_integrated_decisions(
        [record1, record2]
    )

    assert summary["cost_summary"]["storage_observations"] == 2

    assert (
        summary["cost_summary"]["average_storage_ratio_percentage"]
        == pytest.approx(20.76)
    )

    assert summary["cost_summary"]["write_observations"] == 2

    assert (
        summary["cost_summary"]["average_write_overhead_percentage"]
        == pytest.approx(12.545)
    )

    assert (
        summary["cost_summary"]["median_write_overhead_percentage"]
        == pytest.approx(7.51)
    )


def test_missing_read_evidence_is_not_treated_as_zero():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    record1 = make_record()

    record2 = make_record()
    record2["recommendation"]["recommendation_id"] = 43
    record2["read_evidence"]["average_improvement_percentage"] = None
    record2["read_evidence"]["median_improvement_percentage"] = None
    record2["read_evidence"]["absolute_savings_ms"] = None

    summary = summarize_integrated_decisions(
        [record1, record2]
    )

    assert summary["read_summary"]["observations"] == 1

    assert (
        summary["read_summary"]["average_improvement_percentage"]
        == pytest.approx(96.25)
    )

    assert (
        summary["read_summary"]["average_savings_ms"]
        == pytest.approx(3.95)
    )


def test_missing_cost_evidence_is_not_treated_as_zero():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    record1 = make_record()

    record2 = make_record()
    record2["recommendation"]["recommendation_id"] = 43
    record2["cost_evidence"]["index_table_ratio_percentage"] = None
    record2["cost_evidence"]["average_overhead_percentage"] = None
    record2["cost_evidence"]["median_overhead_percentage"] = None

    summary = summarize_integrated_decisions(
        [record1, record2]
    )

    assert summary["cost_summary"]["storage_observations"] == 1

    assert (
        summary["cost_summary"]["average_storage_ratio_percentage"]
        == pytest.approx(16.52)
    )

    assert summary["cost_summary"]["write_observations"] == 1

    assert (
        summary["cost_summary"]["average_write_overhead_percentage"]
        == pytest.approx(8.09)
    )


def test_portfolio_summary_does_not_rank_recommendations():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    summary = summarize_integrated_decisions([make_record()])

    assert "ranking" not in summary
    assert "ranked_recommendations" not in summary
    assert "winner" not in summary


def test_portfolio_summary_does_not_recalculate_decisions():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    record = make_record()
    record["decision"]["decision"] = "REVIEW"

    summary = summarize_integrated_decisions([record])

    assert summary["decision_counts"]["REVIEW"] == 1
    assert summary["decision_counts"]["RECOMMEND"] == 0


def test_portfolio_summary_does_not_recalculate_guardrails():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    record = make_record()
    record["guardrails"]["status"] = "BLOCK"

    summary = summarize_integrated_decisions([record])

    assert summary["guardrail_counts"]["BLOCK"] == 1
    assert summary["guardrail_counts"]["PASS"] == 0


def test_portfolio_summary_rejects_invalid_record():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    record = make_record()
    del record["decision"]

    with pytest.raises(ValueError):
        summarize_integrated_decisions([record])


def test_portfolio_summary_rejects_invalid_input_type():
    from collector.integrated_optimization_report import (
        summarize_integrated_decisions,
    )

    with pytest.raises(ValueError):
        summarize_integrated_decisions(None)
def test_build_integrated_report_with_single_record():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    record = make_record()

    report = build_integrated_report([record])

    assert report["report"]["report_version"] == "M19.4-v1"
    assert (
        report["report"]["decision_policy_version"]
        == "M19.1-v1"
    )
    assert (
        report["report"]["guardrail_policy_version"]
        == "M19.3-v1"
    )

    assert report["summary"]["total_recommendations"] == 1

    assert len(report["recommendations"]) == 1

    recommendation = report["recommendations"][0]

    assert recommendation["record"]["recommendation"] == (
        record["recommendation"]
    )

    assert recommendation["outcome"]["recommendation_id"] == 42
    assert recommendation["outcome"]["outcome"]["decision"] == (
        "RECOMMEND"
    )


def test_build_integrated_report_preserves_multiple_records():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    record1 = make_record()

    record2 = make_record()
    record2["recommendation"]["recommendation_id"] = 43
    record2["decision"]["decision"] = "REVIEW"

    report = build_integrated_report([record1, record2])

    assert report["summary"]["total_recommendations"] == 2
    assert len(report["recommendations"]) == 2

    assert (
        report["recommendations"][0]["record"]["recommendation"][
            "recommendation_id"
        ]
        == 42
    )

    assert (
        report["recommendations"][1]["record"]["recommendation"][
            "recommendation_id"
        ]
        == 43
    )

    assert (
        report["recommendations"][1]["outcome"]["outcome"]["decision"]
        == "REVIEW"
    )


def test_build_integrated_report_preserves_portfolio_summary():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    record1 = make_record()

    record2 = make_record()
    record2["recommendation"]["recommendation_id"] = 43
    record2["decision"]["decision"] = "REJECT"

    report = build_integrated_report([record1, record2])

    assert report["summary"]["decision_counts"] == {
        "RECOMMEND": 1,
        "REVIEW": 0,
        "REJECT": 1,
        "INSUFFICIENT_EVIDENCE": 0,
    }


def test_build_integrated_report_preserves_existing_decisions():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    record = make_record()
    record["decision"]["decision"] = "REVIEW"

    report = build_integrated_report([record])

    assert (
        report["recommendations"][0]["outcome"]["outcome"]["decision"]
        == "REVIEW"
    )


def test_build_integrated_report_preserves_guardrails():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    record = make_record()
    record["guardrails"]["status"] = "BLOCK"

    report = build_integrated_report([record])

    assert (
        report["recommendations"][0]["outcome"]["outcome"][
            "guardrail_status"
        ]
        == "BLOCK"
    )


def test_build_integrated_report_preserves_incomplete_evidence():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    record = make_record()

    record["linkage"]["evidence_status"] = "INSUFFICIENT"
    record["read_evidence"]["available"] = False
    record["read_evidence"]["average_improvement_percentage"] = None
    record["read_evidence"]["median_improvement_percentage"] = None
    record["read_evidence"]["absolute_savings_ms"] = None

    report = build_integrated_report([record])

    recommendation = report["recommendations"][0]

    assert (
        recommendation["outcome"]["outcome"]["evidence_status"]
        == "INSUFFICIENT"
    )

    assert recommendation["outcome"]["read"]["improvement"] is None


def test_build_integrated_report_handles_empty_records():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    report = build_integrated_report([])

    assert report["summary"]["total_recommendations"] == 0
    assert report["recommendations"] == []


def test_build_integrated_report_rejects_invalid_record():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    record = make_record()
    del record["decision"]

    with pytest.raises(ValueError):
        build_integrated_report([record])


def test_build_integrated_report_rejects_invalid_input_type():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    with pytest.raises(ValueError):
        build_integrated_report(None)


def test_build_integrated_report_does_not_mutate_inputs():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    record = make_record()

    original = {
        "score": record["recommendation"]["score"],
        "decision": record["decision"]["decision"],
        "guardrails": record["guardrails"]["status"],
        "evidence_status": record["linkage"]["evidence_status"],
    }

    build_integrated_report([record])

    assert record["recommendation"]["score"] == original["score"]
    assert record["decision"]["decision"] == original["decision"]
    assert record["guardrails"]["status"] == original["guardrails"]
    assert (
        record["linkage"]["evidence_status"]
        == original["evidence_status"]
    )


def test_build_integrated_report_does_not_create_new_score():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    report = build_integrated_report([make_record()])

    outcome = report["recommendations"][0]["outcome"]

    assert "score" not in outcome
    assert "new_score" not in outcome


def test_build_integrated_report_keeps_recommendation_order():
    from collector.integrated_optimization_report import (
        build_integrated_report,
    )

    records = []

    for recommendation_id in [100, 50, 75]:
        record = make_record()
        record["recommendation"]["recommendation_id"] = (
            recommendation_id
        )
        records.append(record)

    report = build_integrated_report(records)

    ids = [
        item["outcome"]["recommendation_id"]
        for item in report["recommendations"]
    ]

    assert ids == [100, 50, 75]
