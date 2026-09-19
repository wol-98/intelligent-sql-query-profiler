"""M19.1 production-oriented index decision model.

Analytical only.

This module:
- does not access the database,
- does not create/drop indexes,
- does not modify benchmark_results,
- does not modify recommendation scores,
- does not generate candidates,
- does not change recommendation priorities.

It converts existing recommendation, workload, validation,
and linked cost-benefit evidence into a transparent decision.
"""

from typing import Any, Dict


POLICY_VERSION = "M19.1-v1"

# Read-benefit thresholds (% improvement)
READ_NEUTRAL_MAX = 10.0
READ_POSITIVE_MAX = 50.0

# Storage thresholds (% of table size)
STORAGE_LOW_MAX = 10.0
STORAGE_MODERATE_MAX = 25.0

# Write-overhead thresholds (%)
WRITE_LOW_MAX = 5.0
WRITE_MODERATE_MAX = 20.0

VALID_DECISIONS = {
    "RECOMMEND",
    "REVIEW",
    "REJECT",
    "INSUFFICIENT_EVIDENCE",
}

VALID_READ_CLASSIFICATIONS = {
    "negative",
    "neutral",
    "positive",
    "strong",
}

VALID_COST_CLASSIFICATIONS = {
    "low",
    "moderate",
    "high",
}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require_number(
    value: Any,
    field_name: str,
    minimum: float | None = None,
) -> None:
    if not _is_number(value):
        raise ValueError(f"{field_name} must be numeric.")

    if minimum is not None and value < minimum:
        raise ValueError(
            f"{field_name} must be >= {minimum}."
        )


def classify_read_benefit(improvement_percentage: float) -> str:
    """Classify measured read improvement."""
    _require_number(improvement_percentage, "improvement_percentage")

    if improvement_percentage < 0:
        return "negative"

    if improvement_percentage < READ_NEUTRAL_MAX:
        return "neutral"

    if improvement_percentage < READ_POSITIVE_MAX:
        return "positive"

    return "strong"


def classify_storage_cost(index_table_ratio_percentage: float) -> str:
    """Classify index storage footprint relative to table size."""
    _require_number(
        index_table_ratio_percentage,
        "index_table_ratio_percentage",
        minimum=0,
    )

    if index_table_ratio_percentage <= STORAGE_LOW_MAX:
        return "low"

    if index_table_ratio_percentage <= STORAGE_MODERATE_MAX:
        return "moderate"

    return "high"


def classify_write_cost(average_overhead_percentage: float) -> str:
    """Classify average measured write overhead."""
    _require_number(
        average_overhead_percentage,
        "average_overhead_percentage",
    )

    if average_overhead_percentage <= WRITE_LOW_MAX:
        return "low"

    if average_overhead_percentage <= WRITE_MODERATE_MAX:
        return "moderate"

    return "high"


def assess_evidence_completeness(
    read_available: bool,
    storage_available: bool,
    write_available: bool,
    linked: bool,
) -> Dict[str, Any]:
    """Assess whether linked cost-benefit evidence is complete."""
    values = {
        "read": bool(read_available),
        "storage": bool(storage_available),
        "write": bool(write_available),
        "linked": bool(linked),
    }

    values["complete"] = all(values.values())

    return values


def _validate_decision_input(data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("Decision input must be a dictionary.")

    required = {
        "recommendation",
        "workload",
        "read_evidence",
        "cost_evidence",
        "evidence",
    }

    missing = required - set(data)

    if missing:
        raise ValueError(
            f"Missing required decision input fields: "
            f"{sorted(missing)}"
        )


def determine_production_decision(
    read_classification: str | None,
    storage_classification: str | None,
    write_classification: str | None,
    evidence_complete: bool,
    rows_preserved: bool | None,
    index_used: bool | None,
) -> str:
    """Determine the production-oriented decision.

    Safety and evidence gates are evaluated before the
    benefit/cost decision matrix.
    """
    if rows_preserved is False:
        return "REJECT"

    if not evidence_complete:
        return "INSUFFICIENT_EVIDENCE"

    if index_used is False:
        return "INSUFFICIENT_EVIDENCE"

    if read_classification not in VALID_READ_CLASSIFICATIONS:
        return "INSUFFICIENT_EVIDENCE"

    if storage_classification not in VALID_COST_CLASSIFICATIONS:
        return "INSUFFICIENT_EVIDENCE"

    if write_classification not in VALID_COST_CLASSIFICATIONS:
        return "INSUFFICIENT_EVIDENCE"

    if read_classification in {"negative", "neutral"}:
        return "REJECT"

    has_high_cost = (
        storage_classification == "high"
        or write_classification == "high"
    )

    if read_classification == "strong":
        if has_high_cost:
            return "REVIEW"
        return "RECOMMEND"

    # Remaining valid positive case.
    if has_high_cost:
        return "REJECT"

    if (
        storage_classification == "moderate"
        or write_classification == "moderate"
    ):
        return "REVIEW"

    return "RECOMMEND"


def build_decision_explanation(
    decision: str,
    read_classification: str | None,
    storage_classification: str | None,
    write_classification: str | None,
    evidence_complete: bool,
    rows_preserved: bool | None,
    index_used: bool | None,
) -> str:
    """Build a human-readable explanation for the decision."""
    if rows_preserved is False:
        return (
            "REJECT: benchmark evidence did not preserve the query "
            "result rows."
        )

    if not evidence_complete:
        return (
            "INSUFFICIENT_EVIDENCE: linked read, storage, write, and "
            "same-index evidence is incomplete."
        )

    if index_used is False:
        return (
            "INSUFFICIENT_EVIDENCE: the benchmark did not use the "
            "proposed index, so the measured read effect cannot be "
            "attributed safely to this index."
        )

    if decision == "REJECT":
        if read_classification in {"negative", "neutral"}:
            return (
                f"REJECT: measured read benefit is {read_classification}, "
                "which does not provide sufficient observed performance "
                "benefit for production deployment."
            )

        return (
            "REJECT: the measured read benefit does not justify the "
            "observed index cost under the M19.1 decision policy."
        )

    if decision == "REVIEW":
        if read_classification == "strong":
            return (
                "REVIEW: the index provides strong measured read "
                "benefit, but at least one measured cost dimension is "
                "high and therefore requires engineering review."
            )

        return (
            "REVIEW: the index provides positive measured read benefit, "
            "but at least one cost dimension is moderate and requires "
            "review before production deployment."
        )

    if decision == "RECOMMEND":
        return (
            "RECOMMEND: measured read benefit is positive, correctness "
            "was preserved, the proposed index was used, and the "
            "observed storage and write costs remain within the "
            "M19.1 recommendation policy."
        )

    return (
        "INSUFFICIENT_EVIDENCE: the available evidence does not "
        "support a production-oriented decision."
    )


def build_production_decision(data: Dict[str, Any]) -> Dict[str, Any]:
    """Build the complete M19.1 production decision."""
    _validate_decision_input(data)

    recommendation = data["recommendation"]
    workload = data["workload"]
    read = data["read_evidence"]
    cost = data["cost_evidence"]

    evidence = data["evidence"]

    required_evidence_flags = {
        "read",
        "storage",
        "write",
        "linked",
    }

    missing_evidence_flags = (
        required_evidence_flags - set(evidence)
    )

    if missing_evidence_flags:
        raise ValueError(
            f"Missing evidence flags: "
            f"{sorted(missing_evidence_flags)}"
        )

    evidence = {
        "read": bool(evidence["read"]),
        "storage": bool(evidence["storage"]),
        "write": bool(evidence["write"]),
        "linked": bool(evidence["linked"]),
    }

    evidence["complete"] = all(evidence.values())

    if read.get("available"):
        improvement = read.get("average_improvement_percentage")
        if improvement is None:
            raise ValueError(
                "Read evidence requires average_improvement_percentage."
            )

        read_classification = classify_read_benefit(improvement)
    else:
        read_classification = None

    if cost.get("storage_available"):
        storage_ratio = cost.get("index_table_ratio_percentage")
        if storage_ratio is None:
            raise ValueError(
                "Storage evidence requires "
                "index_table_ratio_percentage."
            )

        storage_classification = classify_storage_cost(storage_ratio)
    else:
        storage_classification = None

    if cost.get("write_available"):
        write_overhead = cost.get("average_overhead_percentage")
        if write_overhead is None:
            raise ValueError(
                "Write evidence requires average_overhead_percentage."
            )

        write_classification = classify_write_cost(write_overhead)
    else:
        write_classification = None

    rows_preserved = read.get("rows_preserved")
    index_used = read.get("index_used")

    decision = determine_production_decision(
        read_classification=read_classification,
        storage_classification=storage_classification,
        write_classification=write_classification,
        evidence_complete=evidence["complete"],
        rows_preserved=rows_preserved,
        index_used=index_used,
    )

    explanation = build_decision_explanation(
        decision=decision,
        read_classification=read_classification,
        storage_classification=storage_classification,
        write_classification=write_classification,
        evidence_complete=evidence["complete"],
        rows_preserved=rows_preserved,
        index_used=index_used,
    )

    return {
        "decision_policy_version": POLICY_VERSION,

        "recommendation": {
            "recommendation_id": recommendation.get(
                "recommendation_id"
            ),
            "score": recommendation.get("score"),
            "priority": recommendation.get("priority"),
        },

        "workload": {
            "priority": workload.get("priority"),
            "execution_time_share": workload.get(
                "execution_time_share"
            ),
            "frequency_share": workload.get("frequency_share"),
        },

        "read_evidence": {
            "available": read.get("available", False),
            "average_improvement_percentage": read.get(
                "average_improvement_percentage"
            ),
            "median_improvement_percentage": read.get(
                "median_improvement_percentage"
            ),
            "absolute_savings_ms": read.get(
                "absolute_savings_ms"
            ),
            "index_used": index_used,
            "plan_changed": read.get("plan_changed"),
            "rows_preserved": rows_preserved,
            "classification": read_classification,
        },

        "cost_evidence": {
            "storage_available": cost.get(
                "storage_available",
                False
            ),
            "index_table_ratio_percentage": cost.get(
                "index_table_ratio_percentage"
            ),
            "storage_classification": storage_classification,
            "write_available": cost.get(
                "write_available",
                False
            ),
            "average_overhead_percentage": cost.get(
                "average_overhead_percentage"
            ),
            "median_overhead_percentage": cost.get(
                "median_overhead_percentage"
            ),
            "write_classification": write_classification,
        },

        "evidence": evidence,

        "decision": decision,

        "explanation": explanation,
    }
