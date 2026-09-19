from collector.cost_aware_recommendation_analyzer import (
    validate_cost_aware_record,
    determine_evidence_completeness,
    classify_cost_aware_evidence,
    build_cost_aware_record,
    analyze_historical_recommendations,
    build_cost_aware_summary,
)


def test_valid_record():
    assert validate_cost_aware_record({
        "read_improvement_percentage": 50,
        "index_size_bytes": 1000,
        "table_size_bytes": 5000,
        "maintenance_overhead_percentage": 5,
        "recommendation_score": 70,
    })


def test_invalid_record():
    assert not validate_cost_aware_record({
        "index_size_bytes": -1,
    })


def test_complete_evidence():
    assert (
        determine_evidence_completeness(
            True, True, True
        )
        == "COMPLETE"
    )


def test_partial_evidence():
    assert (
        determine_evidence_completeness(
            True, True, False
        )
        == "PARTIAL"
    )


def test_insufficient_evidence():
    assert (
        determine_evidence_completeness(
            False, False, False
        )
        == "INSUFFICIENT"
    )


def test_benefit_low_cost():
    assert (
        classify_cost_aware_evidence(
            "HIGH_BENEFIT",
            "LOW_COST",
            "COMPLETE",
        )
        == "BENEFIT_WITH_LOW_COST"
    )


def test_benefit_measurable_cost():
    assert (
        classify_cost_aware_evidence(
            "HIGH_BENEFIT",
            "HIGH_COST",
            "COMPLETE",
        )
        == "BENEFIT_WITH_MEASURABLE_COST"
    )


def test_negative_benefit_with_cost():
    assert (
        classify_cost_aware_evidence(
            "NEGATIVE_BENEFIT",
            "HIGH_COST",
            "COMPLETE",
        )
        == "NEGATIVE_BENEFIT_WITH_COST"
    )


def test_incomplete_evidence():
    assert (
        classify_cost_aware_evidence(
            "HIGH_BENEFIT",
            "LOW_COST",
            "PARTIAL",
        )
        == "INSUFFICIENT_EVIDENCE"
    )


def test_unlinked_cost_evidence():
    record = build_cost_aware_record(
        read_improvement_percentage=80,
        read_benefit_class="HIGH_BENEFIT",
        index_size_bytes=600000,
        table_size_bytes=3000000,
        maintenance_overhead_percentage=5,
        maintenance_cost_class="LOW_COST",
        evidence_linked_to_same_index=False,
    )

    assert (
        record["evidence_completeness"]
        == "LIMITED"
    )

    assert (
        record["cost_aware_class"]
        == "INSUFFICIENT_EVIDENCE"
    )


def test_historical_analysis_does_not_inherit_cost():
    dataset = [
        {
            "evaluation_improvement_percentage": 80,
            "recommendation_score": 70,
        }
    ]

    records = analyze_historical_recommendations(
        dataset
    )

    assert len(records) == 1
    assert (
        records[0]["evidence_linked_to_same_index"]
        is False
    )


def test_summary():
    records = [
        build_cost_aware_record(
            read_improvement_percentage=80,
            read_benefit_class="HIGH_BENEFIT",
            evidence_linked_to_same_index=False,
        )
    ]

    summary = build_cost_aware_summary(records)

    assert summary["total_records"] == 1
    assert summary["limited_evidence"] == 1
def test_summary_tracks_read_and_cost_linkage():
    records = [
        build_cost_aware_record(
            read_improvement_percentage=80,
            read_benefit_class="HIGH_BENEFIT",
            evidence_linked_to_same_index=False,
        ),
        build_cost_aware_record(
            read_improvement_percentage=None,
            read_benefit_class="UNKNOWN",
            evidence_linked_to_same_index=False,
        ),
    ]

    summary = build_cost_aware_summary(records)

    assert summary["read_evidence_records"] == 1
    assert summary["no_read_evidence_records"] == 1
    assert summary["cost_linked_records"] == 0
