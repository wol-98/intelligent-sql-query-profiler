"""M19.3 safety and production guardrails.

Analytical only.

This module evaluates whether recommendation evidence satisfies the
M19.3 safety policy before a production-oriented decision is considered.

It does not:
- access the database,
- create/drop indexes,
- execute benchmarks,
- modify recommendation scores,
- generate candidates,
- modify benchmark_results,
- change the M19.1 decision policy.
"""

from typing import Any, Dict


POLICY_VERSION = "M19.3-v1"

PASS = "PASS"
BLOCK = "BLOCK"
INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

VALID_STATUSES = {
    PASS,
    BLOCK,
    INSUFFICIENT_EVIDENCE,
}

VALID_EXPERIMENTAL_SCOPES = {
    "PROJECT_VALIDATED",
}


def validate_guardrail_input(
    evidence: Dict[str, Any],
) -> None:
    """Validate the minimum M19.3 input structure."""
    if not isinstance(evidence, dict):
        raise ValueError(
            "Guardrail evidence must be a dictionary."
        )

    required = {
        "evidence_completeness",
        "evidence_linkage",
        "read_evidence",
        "cost_evidence",
        "experimental_scope",
    }

    missing = required - set(evidence)

    if missing:
        raise ValueError(
            "Missing guardrail fields: "
            f"{sorted(missing)}"
        )


def check_evidence_completeness(
    evidence: Dict[str, Any],
) -> str:
    """Check whether read, storage, and write evidence are available."""
    required = {
        "read": bool(evidence.get("read", False)),
        "storage": bool(evidence.get("storage", False)),
        "write": bool(evidence.get("write", False)),
    }

    if all(required.values()):
        return PASS

    return INSUFFICIENT_EVIDENCE


def check_evidence_linkage(
    evidence: Dict[str, Any],
) -> str:
    """Check whether evidence is explicitly linked."""
    if bool(evidence.get("linked", False)):
        return PASS

    return INSUFFICIENT_EVIDENCE


def check_rows_preserved(
    read_evidence: Dict[str, Any],
) -> str:
    """Check query-result correctness preservation."""
    if "rows_preserved" not in read_evidence:
        return INSUFFICIENT_EVIDENCE

    if read_evidence["rows_preserved"] is False:
        return BLOCK

    if read_evidence["rows_preserved"] is True:
        return PASS

    return INSUFFICIENT_EVIDENCE


def check_index_usage(
    read_evidence: Dict[str, Any],
) -> str:
    """Check whether the experimental index was actually used."""
    if "index_used" not in read_evidence:
        return INSUFFICIENT_EVIDENCE

    if read_evidence["index_used"] is True:
        return PASS

    return INSUFFICIENT_EVIDENCE


def check_execution_evidence(
    read_evidence: Dict[str, Any],
    cost_evidence: Dict[str, Any],
) -> str:
    """Check whether required execution measurements are available."""
    required_read = {
        "average_improvement_percentage",
        "median_improvement_percentage",
        "absolute_savings_ms",
        "index_used",
        "plan_changed",
        "rows_preserved",
    }

    required_cost = {
        "storage_available",
        "index_table_ratio_percentage",
        "write_available",
        "average_overhead_percentage",
        "median_overhead_percentage",
    }

    if not required_read.issubset(read_evidence):
        return INSUFFICIENT_EVIDENCE

    if not required_cost.issubset(cost_evidence):
        return INSUFFICIENT_EVIDENCE

    if not all(
        read_evidence[field] is not None
        for field in required_read
    ):
        return INSUFFICIENT_EVIDENCE

    if not all(
        cost_evidence[field] is not None
        for field in required_cost
    ):
        return INSUFFICIENT_EVIDENCE

    return PASS


def check_experimental_scope(
    experimental_scope: Any,
) -> str:
    """Check whether the evidence belongs to a validated project scope."""
    if experimental_scope in VALID_EXPERIMENTAL_SCOPES:
        return PASS

    return INSUFFICIENT_EVIDENCE


def _combine_statuses(
    checks: Dict[str, str],
) -> str:
    """Apply M19.3 guardrail precedence."""
    if any(status == BLOCK for status in checks.values()):
        return BLOCK

    if any(
        status == INSUFFICIENT_EVIDENCE
        for status in checks.values()
    ):
        return INSUFFICIENT_EVIDENCE

    return PASS


def evaluate_production_guardrails(
    evidence: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate all M19.3 production safety guardrails."""
    validate_guardrail_input(evidence)

    read_evidence = evidence["read_evidence"]
    cost_evidence = evidence["cost_evidence"]

    if not isinstance(read_evidence, dict):
        raise ValueError(
            "read_evidence must be a dictionary."
        )

    if not isinstance(cost_evidence, dict):
        raise ValueError(
            "cost_evidence must be a dictionary."
        )

    checks = {
        "evidence_completeness": check_evidence_completeness(
            evidence["evidence_completeness"]
        ),
        "evidence_linkage": check_evidence_linkage(
            evidence["evidence_linkage"]
        ),
        "rows_preserved": check_rows_preserved(
            read_evidence
        ),
        "index_usage": check_index_usage(
            read_evidence
        ),
        "execution_evidence": check_execution_evidence(
            read_evidence,
            cost_evidence,
        ),
        "experimental_scope": check_experimental_scope(
            evidence["experimental_scope"]
        ),
    }

    status = _combine_statuses(checks)

    blocking_reasons = []
    insufficient_evidence_reasons = []

    if checks["rows_preserved"] == BLOCK:
        blocking_reasons.append(
            "Query result rows were not preserved."
        )

    reason_map = {
        "evidence_completeness":
            "Required read, storage, or write evidence is unavailable.",
        "evidence_linkage":
            "Evidence is not explicitly linked to the recommendation and experimental index.",
        "index_usage":
            "The experimental index was not confirmed as used.",
        "execution_evidence":
            "Required execution measurements are incomplete.",
        "experimental_scope":
            "The evidence is outside the project's validated experimental scope.",
    }

    for name, reason in reason_map.items():
        if checks[name] == INSUFFICIENT_EVIDENCE:
            insufficient_evidence_reasons.append(reason)

    return {
        "policy_version": POLICY_VERSION,
        "status": status,
        "checks": checks,
        "blocking_reasons": blocking_reasons,
        "insufficient_evidence_reasons":
            insufficient_evidence_reasons,
        "warnings": [],
    }
