"""M19.2 cost-aware recommendation decision layer.

Analytical only.

This module assembles recommendation, workload, read-performance,
storage, write-cost, and linkage evidence and delegates the final
production-oriented decision to the M19.1 decision model.

It does not:
- access the database,
- create/drop indexes,
- execute benchmarks,
- modify recommendation scores,
- generate candidates,
- modify benchmark_results.
"""

from typing import Any, Dict, List

from collector.production_decision_model import (
    build_production_decision,
)


VALID_EVIDENCE_STATUS = {
    "COMPLETE",
    "PARTIAL",
    "INSUFFICIENT",
}


def validate_recommendation_record(
    recommendation: Dict[str, Any],
) -> None:
    """Validate the minimum recommendation structure."""
    if not isinstance(recommendation, dict):
        raise ValueError(
            "Recommendation must be a dictionary."
        )

    required = {
        "recommendation_id",
        "score",
        "priority",
    }

    missing = required - set(recommendation)

    if missing:
        raise ValueError(
            "Missing recommendation fields: "
            f"{sorted(missing)}"
        )


def validate_evidence_record(
    evidence: Dict[str, Any],
) -> None:
    """Validate a linked evidence record."""
    if not isinstance(evidence, dict):
        raise ValueError(
            "Evidence must be a dictionary."
        )

    required = {
        "read",
        "storage",
        "write",
        "linked",
    }

    missing = required - set(evidence)

    if missing:
        raise ValueError(
            "Missing evidence fields: "
            f"{sorted(missing)}"
        )


def determine_evidence_status(
    read_available: bool,
    storage_available: bool,
    write_available: bool,
    linked: bool,
) -> str:
    """Determine M19.2 evidence completeness status."""
    available = [
        bool(read_available),
        bool(storage_available),
        bool(write_available),
    ]

    if linked and all(available):
        return "COMPLETE"

    if linked and any(available):
        return "PARTIAL"

    if any(available):
        return "INSUFFICIENT"

    return "INSUFFICIENT"


def link_recommendation_evidence(
    recommendation: Dict[str, Any],
    evidence: Dict[str, Any],
) -> Dict[str, Any]:
    """Determine whether supplied evidence belongs to a recommendation.

    M19.2 requires explicit linkage. It does not infer same-index
    linkage merely from table or column names.
    """
    validate_recommendation_record(recommendation)
    validate_evidence_record(evidence)

    recommendation_id = recommendation["recommendation_id"]

    evidence_recommendation_id = evidence.get(
        "recommendation_id"
    )

    same_recommendation = (
        evidence_recommendation_id == recommendation_id
    )

    same_index = bool(evidence.get("same_index", False))

    linked = same_recommendation and same_index

    status = determine_evidence_status(
        read_available=evidence["read"],
        storage_available=evidence["storage"],
        write_available=evidence["write"],
        linked=linked,
    )

    return {
        "recommendation_id": recommendation_id,
        "evidence_recommendation_id": evidence_recommendation_id,
        "same_recommendation": same_recommendation,
        "same_index": same_index,
        "linked": linked,
        "evidence_status": status,
        "query_fingerprint": evidence.get(
            "query_fingerprint"
        ),
        "index_name": evidence.get("index_name"),
        "experiment_id": evidence.get("experiment_id"),
    }


def build_decision_input(
    recommendation: Dict[str, Any],
    workload: Dict[str, Any],
    read_evidence: Dict[str, Any],
    cost_evidence: Dict[str, Any],
    linkage: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the M19.1 decision input from M19.2 evidence."""
    validate_recommendation_record(recommendation)

    if not isinstance(workload, dict):
        raise ValueError(
            "Workload must be a dictionary."
        )

    if not isinstance(read_evidence, dict):
        raise ValueError(
            "Read evidence must be a dictionary."
        )

    if not isinstance(cost_evidence, dict):
        raise ValueError(
            "Cost evidence must be a dictionary."
        )

    if not isinstance(linkage, dict):
        raise ValueError(
            "Linkage must be a dictionary."
        )

    evidence = {
        "read": bool(read_evidence.get("available", False)),
        "storage": bool(
            cost_evidence.get(
                "storage_available",
                False,
            )
        ),
        "write": bool(
            cost_evidence.get(
                "write_available",
                False,
            )
        ),
        "linked": bool(
            linkage.get("linked", False)
        ),
    }

    return {
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
            "frequency_share": workload.get(
                "frequency_share"
            ),
        },

        "read_evidence": {
            "available": evidence["read"],
            "average_improvement_percentage": (
                read_evidence.get(
                    "average_improvement_percentage"
                )
            ),
            "median_improvement_percentage": (
                read_evidence.get(
                    "median_improvement_percentage"
                )
            ),
            "absolute_savings_ms": (
                read_evidence.get(
                    "absolute_savings_ms"
                )
            ),
            "index_used": read_evidence.get(
                "index_used"
            ),
            "plan_changed": read_evidence.get(
                "plan_changed"
            ),
            "rows_preserved": read_evidence.get(
                "rows_preserved"
            ),
        },

        "cost_evidence": {
            "storage_available": evidence["storage"],
            "index_table_ratio_percentage": (
                cost_evidence.get(
                    "index_table_ratio_percentage"
                )
            ),
            "write_available": evidence["write"],
            "average_overhead_percentage": (
                cost_evidence.get(
                    "average_overhead_percentage"
                )
            ),
            "median_overhead_percentage": (
                cost_evidence.get(
                    "median_overhead_percentage"
                )
            ),
        },

        "evidence": evidence,
    }


def evaluate_recommendation(
    recommendation: Dict[str, Any],
    workload: Dict[str, Any],
    read_evidence: Dict[str, Any],
    cost_evidence: Dict[str, Any],
    linkage: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate one recommendation using the M19.1 decision model."""
    decision_input = build_decision_input(
        recommendation=recommendation,
        workload=workload,
        read_evidence=read_evidence,
        cost_evidence=cost_evidence,
        linkage=linkage,
    )

    decision = build_production_decision(
        decision_input
    )

    return {
        "recommendation_id": recommendation[
            "recommendation_id"
        ],

        "recommendation": decision[
            "recommendation"
        ],

        "workload": decision[
            "workload"
        ],

        "linkage": linkage,

        "read_evidence": decision[
            "read_evidence"
        ],

        "cost_evidence": decision[
            "cost_evidence"
        ],

        "evidence": decision[
            "evidence"
        ],

        "decision": {
            "decision": decision["decision"],
            "policy_version": decision[
                "decision_policy_version"
            ],
            "explanation": decision[
                "explanation"
            ],
        },
    }


def evaluate_recommendations(
    records: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Evaluate multiple recommendation/evidence records."""
    if not isinstance(records, list):
        raise ValueError(
            "records must be a list."
        )

    results = []

    for record in records:
        if not isinstance(record, dict):
            raise ValueError(
                "Each recommendation record must be a dictionary."
            )

        result = evaluate_recommendation(
            recommendation=record["recommendation"],
            workload=record["workload"],
            read_evidence=record["read_evidence"],
            cost_evidence=record["cost_evidence"],
            linkage=record["linkage"],
        )

        results.append(result)

    return results


def summarize_cost_aware_decisions(
    results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Summarize M19.2 decision outcomes."""
    if not isinstance(results, list):
        raise ValueError(
            "results must be a list."
        )

    counts = {
        "RECOMMEND": 0,
        "REVIEW": 0,
        "REJECT": 0,
        "INSUFFICIENT_EVIDENCE": 0,
    }

    evidence_counts = {
        "COMPLETE": 0,
        "PARTIAL": 0,
        "INSUFFICIENT": 0,
    }

    for result in results:
        decision = result["decision"]["decision"]
        evidence_status = result["linkage"][
            "evidence_status"
        ]

        if decision not in counts:
            raise ValueError(
                f"Unknown decision: {decision}"
            )

        if evidence_status not in evidence_counts:
            raise ValueError(
                f"Unknown evidence status: "
                f"{evidence_status}"
            )

        counts[decision] += 1
        evidence_counts[evidence_status] += 1

    return {
        "recommendation_count": len(results),
        "decision_counts": counts,
        "evidence_status_counts": evidence_counts,
    }
