from __future__ import annotations

from api.schemas.decision import (
    GuardrailCheck,
    ProductionDecisionResponse,
)
from collector.m19_4_real_analysis import (
    build_real_integrated_report,
)


def _build_decision_response(
    item: dict,
) -> ProductionDecisionResponse:
    record = item["record"]

    recommendation = record["recommendation"]
    decision = record["decision"]
    guardrails = record["guardrails"]
    linkage = record["linkage"]

    guardrail_checks = [
        GuardrailCheck(
            name=name,
            status=status,
        )
        for name, status in guardrails["checks"].items()
    ]

    return ProductionDecisionResponse(
        recommendation_id=recommendation[
            "recommendation_id"
        ],
        state=decision["decision"],
        reason=decision.get("explanation"),
        guardrail_status=guardrails["status"],
        guardrail_checks=guardrail_checks,
        evidence_status=linkage["evidence_status"],
    )


def get_production_decisions() -> list[
    ProductionDecisionResponse
]:
    """
    Return M19.4 production decisions through the
    read-only M20 reporting API.

    M19.4 remains authoritative for:
    - production decision
    - decision explanation
    - guardrail status
    - guardrail checks
    - evidence status

    No decision or guardrail logic is recalculated here.
    """
    report = build_real_integrated_report()

    return [
        _build_decision_response(item)
        for item in report["recommendations"]
    ]


def get_production_decision(
    recommendation_id: int,
) -> ProductionDecisionResponse:
    """
    Return one M19.4 production decision.

    Raises ValueError when the recommendation does not exist.
    """
    report = build_real_integrated_report()

    for item in report["recommendations"]:
        record = item["record"]

        if (
            record["recommendation"]["recommendation_id"]
            == recommendation_id
        ):
            return _build_decision_response(item)

    raise ValueError(
        f"Production decision for recommendation "
        f"{recommendation_id} not found."
    )
