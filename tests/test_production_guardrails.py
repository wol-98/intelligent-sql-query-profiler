import pytest

from collector.production_guardrails import (
    BLOCK,
    INSUFFICIENT_EVIDENCE,
    PASS,
    POLICY_VERSION,
    check_evidence_completeness,
    check_evidence_linkage,
    check_experimental_scope,
    check_execution_evidence,
    check_index_usage,
    check_rows_preserved,
    evaluate_production_guardrails,
)


def make_read_evidence():
    return {
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


def make_evidence():
    return {
        "evidence_completeness": {
            "read": True,
            "storage": True,
            "write": True,
        },
        "evidence_linkage": {
            "linked": True,
        },
        "read_evidence": make_read_evidence(),
        "cost_evidence": make_cost_evidence(),
        "experimental_scope": "PROJECT_VALIDATED",
    }


def test_complete_evidence_passes():
    evidence = make_evidence()

    result = evaluate_production_guardrails(
        evidence
    )

    assert result["status"] == PASS


def test_missing_evidence_is_insufficient():
    evidence = make_evidence()
    evidence["evidence_completeness"]["write"] = False

    result = evaluate_production_guardrails(
        evidence
    )

    assert result["status"] == INSUFFICIENT_EVIDENCE


def test_unlinked_evidence_is_insufficient():
    evidence = make_evidence()
    evidence["evidence_linkage"]["linked"] = False

    result = evaluate_production_guardrails(
        evidence
    )

    assert result["status"] == INSUFFICIENT_EVIDENCE


def test_rows_not_preserved_blocks():
    evidence = make_evidence()
    evidence["read_evidence"]["rows_preserved"] = False

    result = evaluate_production_guardrails(
        evidence
    )

    assert result["status"] == BLOCK
    assert (
        "Query result rows were not preserved."
        in result["blocking_reasons"]
    )


def test_correctness_failure_overrides_missing_evidence():
    evidence = make_evidence()

    evidence["read_evidence"]["rows_preserved"] = False
    evidence["evidence_completeness"]["write"] = False

    result = evaluate_production_guardrails(
        evidence
    )

    assert result["status"] == BLOCK


def test_index_not_used_is_insufficient():
    evidence = make_evidence()
    evidence["read_evidence"]["index_used"] = False

    result = evaluate_production_guardrails(
        evidence
    )

    assert result["status"] == INSUFFICIENT_EVIDENCE


def test_missing_index_usage_is_insufficient():
    read = make_read_evidence()
    del read["index_used"]

    assert (
        check_index_usage(read)
        == INSUFFICIENT_EVIDENCE
    )


def test_missing_rows_preserved_is_insufficient():
    read = make_read_evidence()
    del read["rows_preserved"]

    assert (
        check_rows_preserved(read)
        == INSUFFICIENT_EVIDENCE
    )


def test_invalid_rows_preserved_value_is_insufficient():
    read = make_read_evidence()
    read["rows_preserved"] = None

    assert (
        check_rows_preserved(read)
        == INSUFFICIENT_EVIDENCE
    )


def test_missing_execution_evidence_is_insufficient():
    read = make_read_evidence()
    cost = make_cost_evidence()

    del read["median_improvement_percentage"]

    assert (
        check_execution_evidence(read, cost)
        == INSUFFICIENT_EVIDENCE
    )


def test_unknown_experimental_scope_is_insufficient():
    assert (
        check_experimental_scope("UNKNOWN")
        == INSUFFICIENT_EVIDENCE
    )


def test_project_validated_scope_passes():
    assert (
        check_experimental_scope(
            "PROJECT_VALIDATED"
        )
        == PASS
    )


def test_complete_evidence_completeness_passes():
    assert (
        check_evidence_completeness(
            {
                "read": True,
                "storage": True,
                "write": True,
            }
        )
        == PASS
    )


def test_partial_evidence_completeness_is_insufficient():
    assert (
        check_evidence_completeness(
            {
                "read": True,
                "storage": True,
                "write": False,
            }
        )
        == INSUFFICIENT_EVIDENCE
    )


def test_linked_evidence_passes():
    assert (
        check_evidence_linkage(
            {"linked": True}
        )
        == PASS
    )


def test_unlinked_evidence_is_insufficient_directly():
    assert (
        check_evidence_linkage(
            {"linked": False}
        )
        == INSUFFICIENT_EVIDENCE
    )


def test_missing_read_execution_field_is_insufficient():
    read = make_read_evidence()
    cost = make_cost_evidence()

    del read["absolute_savings_ms"]

    assert (
        check_execution_evidence(read, cost)
        == INSUFFICIENT_EVIDENCE
    )


def test_missing_cost_execution_field_is_insufficient():
    read = make_read_evidence()
    cost = make_cost_evidence()

    del cost["average_overhead_percentage"]

    assert (
        check_execution_evidence(read, cost)
        == INSUFFICIENT_EVIDENCE
    )


def test_policy_version_is_returned():
    result = evaluate_production_guardrails(
        make_evidence()
    )

    assert result["policy_version"] == POLICY_VERSION
    assert result["policy_version"] == "M19.3-v1"


def test_invalid_top_level_input_is_rejected():
    with pytest.raises(ValueError):
        evaluate_production_guardrails({})


def test_invalid_read_evidence_is_rejected():
    evidence = make_evidence()
    evidence["read_evidence"] = None

    with pytest.raises(ValueError):
        evaluate_production_guardrails(
            evidence
        )
