"""
M19.4 - Integrated Optimization Report

Integrates existing workload, recommendation, performance, cost,
linkage, production-decision, and safety evidence.

This module is analytical/reporting-only.

It does NOT:
- generate recommendations
- modify recommendation scores or priorities
- execute database queries
- create or drop indexes
- run benchmarks
- modify benchmark_results
- recalculate M19.1 decisions
- recalculate M19.3 guardrails
- infer missing evidence or linkage

Authority:
- M19.1 owns production decisions.
- M19.2 owns evidence linkage.
- M19.3 owns production safety guardrails.
- M19.4 owns integration and reporting.
"""

from copy import deepcopy


REPORT_VERSION = "M19.4-v1"
DECISION_POLICY_VERSION = "M19.1-v1"
GUARDRAIL_POLICY_VERSION = "M19.3-v1"

VALID_DECISIONS = {
    "RECOMMEND",
    "REVIEW",
    "REJECT",
    "INSUFFICIENT_EVIDENCE",
}

VALID_GUARDRAIL_STATUSES = {
    "PASS",
    "BLOCK",
    "INSUFFICIENT_EVIDENCE",
}

VALID_EVIDENCE_STATUSES = {
    "COMPLETE",
    "PARTIAL",
    "INSUFFICIENT",
}


def _require_mapping(value, name):
    """Validate that a value is a dictionary-like mapping."""
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a dictionary.")


def _require_key(mapping, key, name):
    """Validate that a required key exists."""
    if key not in mapping:
        raise ValueError(f"{name} is missing required field: {key}.")


def _validate_recommendation(recommendation):
    """Validate recommendation information without changing it."""
    _require_mapping(recommendation, "recommendation")

    required = {
        "recommendation_id",
        "score",
        "priority",
        "candidate_type",
        "columns",
    }

    for key in required:
        _require_key(recommendation, key, "recommendation")

    if not isinstance(recommendation["columns"], (list, tuple)):
        raise ValueError("recommendation.columns must be a list or tuple.")


def _validate_query(query):
    """Validate query metadata."""
    _require_mapping(query, "query")

    required = {
        "fingerprint",
        "template",
        "query_type",
        "tables",
    }

    for key in required:
        _require_key(query, key, "query")

    if not isinstance(query["tables"], (list, tuple)):
        raise ValueError("query.tables must be a list or tuple.")


def _validate_workload(workload):
    """Validate workload metadata."""
    _require_mapping(workload, "workload")

    required = {
        "priority",
        "execution_time_share",
        "frequency_share",
    }

    for key in required:
        _require_key(workload, key, "workload")


def _validate_read_evidence(read_evidence):
    """Validate the canonical read-evidence structure."""
    _require_mapping(read_evidence, "read_evidence")

    required = {
        "available",
        "average_improvement_percentage",
        "median_improvement_percentage",
        "absolute_savings_ms",
        "index_used",
        "plan_changed",
        "rows_preserved",
    }

    for key in required:
        _require_key(read_evidence, key, "read_evidence")


def _validate_cost_evidence(cost_evidence):
    """Validate the canonical cost-evidence structure."""
    _require_mapping(cost_evidence, "cost_evidence")

    required = {
        "storage_available",
        "index_table_ratio_percentage",
        "write_available",
        "average_overhead_percentage",
        "median_overhead_percentage",
    }

    for key in required:
        _require_key(cost_evidence, key, "cost_evidence")


def _validate_linkage(linkage):
    """Validate evidence linkage metadata."""
    _require_mapping(linkage, "linkage")

    required = {
        "same_index",
        "index_name",
        "linked_experiment_id",
        "evidence_status",
    }

    for key in required:
        _require_key(linkage, key, "linkage")

    if linkage["evidence_status"] not in VALID_EVIDENCE_STATUSES:
        raise ValueError(
            f"Invalid evidence_status: {linkage['evidence_status']}."
        )


def _validate_decision(decision):
    """Validate the existing M19.1 decision record."""
    _require_mapping(decision, "decision")

    required = {
        "decision",
        "policy_version",
        "explanation",
    }

    for key in required:
        _require_key(decision, key, "decision")

    if decision["decision"] not in VALID_DECISIONS:
        raise ValueError(
            f"Invalid decision: {decision['decision']}."
        )


def _validate_guardrails(guardrails):
    """Validate the existing M19.3 guardrail record."""
    _require_mapping(guardrails, "guardrails")

    required = {
        "status",
        "policy_version",
        "checks",
        "blocking_reasons",
        "insufficient_evidence_reasons",
    }

    for key in required:
        _require_key(guardrails, key, "guardrails")

    if guardrails["status"] not in VALID_GUARDRAIL_STATUSES:
        raise ValueError(
            f"Invalid guardrail status: {guardrails['status']}."
        )


def validate_integrated_record(record):
    """
    Validate a complete M19.4 integrated optimization record.

    Validation is structural and does not reinterpret evidence.

    Returns:
        True when the record is valid.

    Raises:
        ValueError: when required information is missing or invalid.
    """
    _require_mapping(record, "record")

    required_sections = {
        "report",
        "recommendation",
        "query",
        "workload",
        "read_evidence",
        "cost_evidence",
        "linkage",
        "decision",
        "guardrails",
    }

    for section in required_sections:
        _require_key(record, section, "record")

    _require_mapping(record["report"], "report")

    report_required = {
        "report_version",
        "decision_policy_version",
        "guardrail_policy_version",
    }

    for key in report_required:
        _require_key(record["report"], key, "report")

    _validate_recommendation(record["recommendation"])
    _validate_query(record["query"])
    _validate_workload(record["workload"])
    _validate_read_evidence(record["read_evidence"])
    _validate_cost_evidence(record["cost_evidence"])
    _validate_linkage(record["linkage"])
    _validate_decision(record["decision"])
    _validate_guardrails(record["guardrails"])

    return True


def build_integrated_record(
    recommendation,
    query,
    workload,
    read_evidence,
    cost_evidence,
    linkage,
    decision,
    guardrails,
):
    """
    Build the canonical M19.4 integrated optimization record.

    All supplied evidence is preserved. No new score, decision,
    guardrail status, or evidence is calculated.
    """
    _validate_recommendation(recommendation)
    _validate_query(query)
    _validate_workload(workload)
    _validate_read_evidence(read_evidence)
    _validate_cost_evidence(cost_evidence)
    _validate_linkage(linkage)
    _validate_decision(decision)
    _validate_guardrails(guardrails)

    record = {
        "report": {
            "report_version": REPORT_VERSION,
            "decision_policy_version": DECISION_POLICY_VERSION,
            "guardrail_policy_version": GUARDRAIL_POLICY_VERSION,
        },
        "recommendation": deepcopy(recommendation),
        "query": deepcopy(query),
        "workload": deepcopy(workload),
        "read_evidence": deepcopy(read_evidence),
        "cost_evidence": deepcopy(cost_evidence),
        "linkage": deepcopy(linkage),
        "decision": deepcopy(decision),
        "guardrails": deepcopy(guardrails),
    }

    validate_integrated_record(record)

    return record


def build_recommendation_outcome(record):
    """
    Build a concise auditable outcome from an integrated M19.4 record.

    This function only extracts already-established evidence and decisions.
    It does not recalculate scores, decisions, guardrails, or evidence status.
    """
    validate_integrated_record(record)

    recommendation = record["recommendation"]
    query = record["query"]
    linkage = record["linkage"]
    read_evidence = record["read_evidence"]
    cost_evidence = record["cost_evidence"]
    decision = record["decision"]
    guardrails = record["guardrails"]

    return {
        "recommendation_id": recommendation["recommendation_id"],
        "index_name": linkage.get("index_name"),
        "query_fingerprint": query["fingerprint"],
        "experiment_id": linkage.get("linked_experiment_id"),
        "outcome": {
            "decision": decision["decision"],
            "guardrail_status": guardrails["status"],
            "evidence_status": linkage["evidence_status"],
        },
        "read": {
            "improvement": read_evidence[
                "average_improvement_percentage"
            ],
            "median_improvement": read_evidence[
                "median_improvement_percentage"
            ],
            "savings_ms": read_evidence["absolute_savings_ms"],
        },
        "cost": {
            "storage_ratio": cost_evidence[
                "index_table_ratio_percentage"
            ],
            "write_overhead": cost_evidence[
                "average_overhead_percentage"
            ],
            "median_write_overhead": cost_evidence[
                "median_overhead_percentage"
            ],
        },
    }


def _numeric_values(records, section, field):
    """
    Return available numeric values without treating missing data as zero.
    """
    values = []

    for record in records:
        value = record[section].get(field)

        if isinstance(value, bool):
            continue

        if isinstance(value, (int, float)):
            values.append(float(value))

    return values


def _average(values):
    """Return the arithmetic mean or None when no values exist."""
    if not values:
        return None

    return sum(values) / len(values)


def _median(values):
    """Return the median or None when no values exist."""
    if not values:
        return None

    ordered = sorted(values)
    middle = len(ordered) // 2

    if len(ordered) % 2:
        return ordered[middle]

    return (ordered[middle - 1] + ordered[middle]) / 2


def summarize_integrated_decisions(records):
    """
    Build a descriptive portfolio summary from integrated M19.4 records.

    This function:
    - counts existing decisions, guardrails, and evidence states
    - summarizes available read evidence
    - summarizes available cost evidence
    - preserves missing evidence as missing

    It does NOT:
    - recalculate decisions
    - recalculate guardrails
    - recalculate recommendation scores
    - infer evidence linkage
    - treat missing evidence as zero
    - rank recommendations
    """
    if not isinstance(records, (list, tuple)):
        raise ValueError("records must be a list or tuple.")

    validated_records = []

    for record in records:
        validate_integrated_record(record)
        validated_records.append(record)

    decision_counts = {
        "RECOMMEND": 0,
        "REVIEW": 0,
        "REJECT": 0,
        "INSUFFICIENT_EVIDENCE": 0,
    }

    guardrail_counts = {
        "PASS": 0,
        "BLOCK": 0,
        "INSUFFICIENT_EVIDENCE": 0,
    }

    evidence_counts = {
        "COMPLETE": 0,
        "PARTIAL": 0,
        "INSUFFICIENT": 0,
    }

    for record in validated_records:
        decision = record["decision"]["decision"]
        guardrail_status = record["guardrails"]["status"]
        evidence_status = record["linkage"]["evidence_status"]

        decision_counts[decision] += 1
        guardrail_counts[guardrail_status] += 1
        evidence_counts[evidence_status] += 1

    read_improvements = _numeric_values(
        validated_records,
        "read_evidence",
        "average_improvement_percentage",
    )

    median_read_improvements = _numeric_values(
        validated_records,
        "read_evidence",
        "median_improvement_percentage",
    )

    read_savings = _numeric_values(
        validated_records,
        "read_evidence",
        "absolute_savings_ms",
    )

    storage_ratios = _numeric_values(
        validated_records,
        "cost_evidence",
        "index_table_ratio_percentage",
    )

    write_overheads = _numeric_values(
        validated_records,
        "cost_evidence",
        "average_overhead_percentage",
    )

    median_write_overheads = _numeric_values(
        validated_records,
        "cost_evidence",
        "median_overhead_percentage",
    )

    return {
        "total_recommendations": len(validated_records),

        "decision_counts": decision_counts,

        "guardrail_counts": guardrail_counts,

        "evidence_counts": evidence_counts,

        "read_summary": {
            "observations": len(read_improvements),
            "average_improvement_percentage": _average(
                read_improvements
            ),
            "median_improvement_percentage": _median(
                median_read_improvements
            ),
            "average_savings_ms": _average(read_savings),
        },

        "cost_summary": {
            "storage_observations": len(storage_ratios),
            "average_storage_ratio_percentage": _average(
                storage_ratios
            ),
            "write_observations": len(write_overheads),
            "average_write_overhead_percentage": _average(
                write_overheads
            ),
            "median_write_overhead_percentage": _median(
                median_write_overheads
            ),
        },
    }
def build_integrated_report(records):
    """
    Build the final M19.4 integrated optimization report.

    The report combines:
    - validated integrated evidence records
    - existing recommendation outcomes
    - descriptive portfolio summary

    It does not:
    - recalculate decisions
    - recalculate guardrails
    - change recommendation scores
    - generate recommendations
    - infer missing evidence
    - perform database operations
    """
    if not isinstance(records, (list, tuple)):
        raise ValueError("records must be a list or tuple.")

    for record in records:
        validate_integrated_record(record)

    integrated_records = deepcopy(list(records))

    outcomes = [
        build_recommendation_outcome(record)
        for record in integrated_records
    ]

    summary = summarize_integrated_decisions(
        integrated_records
    )

    return {
        "report": {
            "report_version": REPORT_VERSION,
            "decision_policy_version": DECISION_POLICY_VERSION,
            "guardrail_policy_version": GUARDRAIL_POLICY_VERSION,
        },
        "summary": summary,
        "recommendations": [
            {
                "record": record,
                "outcome": outcome,
            }
            for record, outcome in zip(
                integrated_records,
                outcomes,
            )
        ],
    }
