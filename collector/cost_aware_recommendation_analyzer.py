"""
M17.4 - Cost-Aware Recommendation Analysis

Analytical layer for examining recommendation effectiveness
alongside index cost evidence.

This module does NOT:
- create indexes
- drop indexes
- execute queries
- modify recommendation scores
- generate candidates
- change recommendation priorities
- write benchmark_results

Important methodological rule:
Historical recommendation observations must not be assigned
M17.1/M17.2 cost measurements unless the cost measurements
refer to the same experimental index.
"""


# =========================================================
# VALIDATION
# =========================================================

def validate_cost_aware_record(record):
    """
    Validate a cost-aware recommendation record.

    Missing evidence is allowed. Invalid supplied values
    are rejected.
    """

    if not isinstance(record, dict):
        return False

    numeric_fields = [
        "read_improvement_percentage",
        "index_size_bytes",
        "table_size_bytes",
        "maintenance_overhead_percentage",
        "workload_time_share_percentage",
        "recommendation_score",
    ]

    for field in numeric_fields:
        value = record.get(field)

        if value is not None and not isinstance(
            value,
            (int, float)
        ):
            return False

    for field in (
        "index_size_bytes",
        "table_size_bytes",
    ):
        value = record.get(field)

        if value is not None and value < 0:
            return False

    return True


# =========================================================
# EVIDENCE AVAILABILITY
# =========================================================

def determine_evidence_completeness(
    read_benefit_available,
    storage_cost_available,
    maintenance_cost_available,
):
    """
    Determine which evidence streams are available.

    Returns a descriptive evidence category.
    """

    available = sum(
        bool(value)
        for value in (
            read_benefit_available,
            storage_cost_available,
            maintenance_cost_available,
        )
    )

    if available == 3:
        return "COMPLETE"

    if available == 2:
        return "PARTIAL"

    if available == 1:
        return "LIMITED"

    return "INSUFFICIENT"


# =========================================================
# COST-AWARE CLASSIFICATION
# =========================================================

def classify_cost_aware_evidence(
    read_benefit_class,
    maintenance_cost_class,
    evidence_completeness,
):
    """
    Classify the observed evidence.

    These are descriptive research categories.
    They are not recommendation scores or decisions.
    """

    if evidence_completeness != "COMPLETE":
        return "INSUFFICIENT_EVIDENCE"

    if (
        read_benefit_class == "NEGATIVE_BENEFIT"
        and maintenance_cost_class
        in {
            "MODERATE_COST",
            "HIGH_COST",
        }
    ):
        return "NEGATIVE_BENEFIT_WITH_COST"

    if (
        read_benefit_class == "LOW_BENEFIT"
        and maintenance_cost_class
        in {
            "MODERATE_COST",
            "HIGH_COST",
        }
    ):
        return "LOW_BENEFIT_WITH_COST"

    if (
        read_benefit_class
        in {
            "HIGH_BENEFIT",
            "MODERATE_BENEFIT",
        }
        and maintenance_cost_class == "LOW_COST"
    ):
        return "BENEFIT_WITH_LOW_COST"

    if (
        read_benefit_class
        in {
            "HIGH_BENEFIT",
            "MODERATE_BENEFIT",
        }
        and maintenance_cost_class
        in {
            "MODERATE_COST",
            "HIGH_COST",
        }
    ):
        return "BENEFIT_WITH_MEASURABLE_COST"

    return "MIXED_EVIDENCE"


# =========================================================
# RECORD CONSTRUCTION
# =========================================================

def build_cost_aware_record(
    read_improvement_percentage=None,
    read_benefit_class="UNKNOWN",
    index_size_bytes=None,
    table_size_bytes=None,
    maintenance_overhead_percentage=None,
    maintenance_cost_class="UNKNOWN",
    workload_time_share_percentage=None,
    recommendation_score=None,
    evidence_linked_to_same_index=False,
):
    """
    Build one cost-aware analytical record.

    Cost evidence is considered linked to the read evidence
    only when explicitly marked as belonging to the same
    experimental index.
    """

    if not evidence_linked_to_same_index:
        storage_available = False
        maintenance_available = False
    else:
        storage_available = (
            index_size_bytes is not None
        )

        maintenance_available = (
            maintenance_overhead_percentage
            is not None
        )

    read_available = (
        read_improvement_percentage is not None
    )

    completeness = determine_evidence_completeness(
        read_available,
        storage_available,
        maintenance_available,
    )

    classification = classify_cost_aware_evidence(
        read_benefit_class,
        maintenance_cost_class,
        completeness,
    )

    return {
        "read_improvement_percentage":
            read_improvement_percentage,

        "read_benefit_class":
            read_benefit_class,

        "index_size_bytes":
            index_size_bytes,

        "table_size_bytes":
            table_size_bytes,

        "maintenance_overhead_percentage":
            maintenance_overhead_percentage,

        "maintenance_cost_class":
            maintenance_cost_class,

        "workload_time_share_percentage":
            workload_time_share_percentage,

        "recommendation_score":
            recommendation_score,

        "evidence_linked_to_same_index":
            evidence_linked_to_same_index,

        "evidence_completeness":
            completeness,

        "cost_aware_class":
            classification,
    }


# =========================================================
# HISTORICAL RECOMMENDATION ANALYSIS
# =========================================================

def analyze_historical_recommendations(
    dataset,
):
    """
    Analyze historical recommendation observations.

    Historical recommendations do not inherit M17.1/M17.2
    cost measurements unless explicitly linked to the same
    experimental index.
    """

    records = []

    for row in dataset:
        read_improvement = row.get(
            "evaluation_improvement_percentage"
        )

        read_class = row.get(
            "evaluation_classification"
        )

        if read_class is None:
            if read_improvement is None:
                read_class = "UNKNOWN"
            elif read_improvement >= 50:
                read_class = "HIGH_BENEFIT"
            elif read_improvement >= 10:
                read_class = "MODERATE_BENEFIT"
            elif read_improvement > 0:
                read_class = "LOW_BENEFIT"
            else:
                read_class = "NEGATIVE_BENEFIT"

        records.append(
            build_cost_aware_record(
                read_improvement_percentage=(
                    read_improvement
                ),
                read_benefit_class=read_class,
                workload_time_share_percentage=(
                    row.get(
                        "execution_time_share_percentage"
                    )
                ),
                recommendation_score=(
                    row.get("recommendation_score")
                ),
                evidence_linked_to_same_index=False,
            )
        )

    return records


# =========================================================
# SUMMARY
# =========================================================

def build_cost_aware_summary(records):
    """
    Summarize cost-aware classifications.
    """

    summary = {
        "total_records": len(records),
        "read_evidence_records": 0,
        "no_read_evidence_records": 0,
        "cost_linked_records": 0,
        "complete_evidence": 0,
        "partial_evidence": 0,
        "limited_evidence": 0,
        "insufficient_evidence": 0,
        "benefit_with_low_cost": 0,
        "benefit_with_measurable_cost": 0,
        "low_benefit_with_cost": 0,
        "negative_benefit_with_cost": 0,
        "mixed_evidence": 0,
    }

    for record in records:
        completeness = record[
            "evidence_completeness"
        ]

        classification = record[
            "cost_aware_class"
        ]
        if (
            record.get(
                "read_improvement_percentage"
            )
            is not None
        ):
            summary[
                "read_evidence_records"
            ] += 1
        else:
            summary[
                "no_read_evidence_records"
            ] += 1

        if record.get(
            "evidence_linked_to_same_index"
        ):
            summary[
                "cost_linked_records"
            ] += 1

        if completeness == "COMPLETE":
            summary["complete_evidence"] += 1
        elif completeness == "PARTIAL":
            summary["partial_evidence"] += 1
        elif completeness == "LIMITED":
            summary["limited_evidence"] += 1
        else:
            summary["insufficient_evidence"] += 1

        if classification == "BENEFIT_WITH_LOW_COST":
            summary["benefit_with_low_cost"] += 1

        elif classification == (
            "BENEFIT_WITH_MEASURABLE_COST"
        ):
            summary[
                "benefit_with_measurable_cost"
            ] += 1

        elif classification == "LOW_BENEFIT_WITH_COST":
            summary["low_benefit_with_cost"] += 1

        elif classification == "NEGATIVE_BENEFIT_WITH_COST":
            summary[
                "negative_benefit_with_cost"
            ] += 1

        elif classification == "MIXED_EVIDENCE":
            summary["mixed_evidence"] += 1

    return summary


# =========================================================
# REPORT
# =========================================================

def print_cost_aware_analysis(
    records,
    summary,
    ):
    """
    Print the M17.4 analytical summary.
    """

    print()
    print("=" * 70)
    print(
        "M17.4 — COST-AWARE RECOMMENDATION ANALYSIS"
    )
    print("=" * 70)

    print()
    print("EVIDENCE COVERAGE")
    print("-" * 70)

    print(
    f"Recommendation observations : "
    f"{summary['total_records']}"
    )

    print(
    f"Read evidence available     : "
    f"{summary['read_evidence_records']}"
    )

    print(
    f"No read evidence            : "
    f"{summary['no_read_evidence_records']}"
    )

    print(
    f"Same-index cost linked      : "
    f"{summary['cost_linked_records']}"
    )

    print(
    f"Complete evidence           : "
    f"{summary['complete_evidence']}"
    )

    print(
        f"Partial evidence            : "
        f"{summary['partial_evidence']}"
    )

    print(
        f"Limited evidence            : "
        f"{summary['limited_evidence']}"
    )

    print(
        f"Insufficient evidence       : "
        f"{summary['insufficient_evidence']}"
    )

    print()
    print("COST-AWARE CLASSIFICATIONS")
    print("-" * 70)

    print(
        f"Benefit with low cost       : "
        f"{summary['benefit_with_low_cost']}"
    )

    print(
        f"Benefit with measurable cost: "
        f"{summary['benefit_with_measurable_cost']}"
    )

    print(
        f"Low benefit with cost       : "
        f"{summary['low_benefit_with_cost']}"
    )

    print(
        f"Negative benefit with cost  : "
        f"{summary['negative_benefit_with_cost']}"
    )

    print(
        f"Mixed evidence              : "
        f"{summary['mixed_evidence']}"
    )
    print()
    print("M17.4 RESEARCH FINDING")
    print("-" * 70)

    if summary["cost_linked_records"] == 0:
        print(
            "No recommendation observations have "
            "same-index linked storage and maintenance "
            "cost evidence."
        )

        print(
            "Therefore, no complete cost-aware "
            "classification is assigned to the "
            "historical recommendation set."
        )
    else:
        print(
            f"Cost-linked observations: "
            f"{summary['cost_linked_records']}"
        )
    print()
    print("METHODOLOGICAL BOUNDARY")
    print("-" * 70)

    print(
        "Historical recommendation observations are not "
        "assigned M17.1/M17.2 cost measurements unless "
        "the cost evidence belongs to the same "
        "experimental index."
    )

    print(
        "M17.4 does not modify recommendation scores, "
        "candidate generation, priorities, or "
        "benchmark_results."
    )
