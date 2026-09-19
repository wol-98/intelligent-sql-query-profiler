from __future__ import annotations

from typing import Any

from api.schemas.cost_benefit import (
    CostBenefitResponse,
    ReadBenefit,
    StorageImpact,
    WriteImpact,
)
from collector.m19_4_real_analysis import (
    build_real_integrated_report,
)


def _get_records() -> list[dict[str, Any]]:
    """
    Return recommendation records from the authoritative
    M19.4 integrated report.

    This service only adapts existing M19.4 evidence to the
    M20 reporting API schema. It does not recalculate evidence.
    """

    report = build_real_integrated_report()

    if not isinstance(report, dict):
        raise ValueError(
            "M19.4 integrated report must be a dictionary."
        )

    records = report.get("recommendations", [])

    if not isinstance(records, list):
        raise ValueError(
            "M19.4 recommendations must be a list."
        )

    return records


def _build_response(
    wrapper: dict[str, Any],
) -> CostBenefitResponse:
    """
    Convert one M19.4 recommendation wrapper into the M20
    cost-benefit API response.
    """

    record = wrapper.get("record")

    if not isinstance(record, dict):
        raise ValueError(
            "M19.4 recommendation wrapper is missing record."
        )

    cost = record.get("cost_evidence")
    read = record.get("read_evidence")
    linkage = record.get("linkage")

    if not isinstance(cost, dict):
        raise ValueError(
            "Recommendation record is missing cost evidence."
        )

    if not isinstance(read, dict):
        raise ValueError(
            "Recommendation record is missing read evidence."
        )

    if not isinstance(linkage, dict):
        raise ValueError(
            "Recommendation record is missing evidence linkage."
        )

    experiment_id = linkage.get(
        "linked_experiment_id"
    )

    if experiment_id is None:
        raise ValueError(
            "Recommendation has no linked experiment."
        )

    recommendation = record.get(
        "recommendation",
        {},
    )

    if not isinstance(recommendation, dict):
        recommendation = {}

    return CostBenefitResponse(
        experiment_id=str(experiment_id),

        recommendation_id=recommendation.get(
            "recommendation_id"
        ),

        read=ReadBenefit(
            average_improvement_percent=read.get(
                "average_improvement_percentage"
            ),
            median_improvement_percent=read.get(
                "median_improvement_percentage"
            ),
            savings_ms=read.get(
                "absolute_savings_ms"
            ),
            index_used=read.get(
                "index_used"
            ),
            plan_changed=read.get(
                "plan_changed"
            ),
            rows_preserved=read.get(
                "rows_preserved"
            ),
        ),

        storage=StorageImpact(
            index_size_bytes=cost.get(
                "index_size_bytes"
            ),
            table_size_bytes=cost.get(
                "table_size_bytes"
            ),
            ratio_percent=cost.get(
                "index_table_ratio_percentage"
            ),
        ),

        write=WriteImpact(
            average_overhead_percent=cost.get(
                "average_overhead_percentage"
            ),
            median_overhead_percent=cost.get(
                "median_overhead_percentage"
            ),
            absolute_overhead_ms=cost.get(
                "absolute_overhead_ms"
            ),
        ),

        evidence_status=linkage.get(
            "evidence_status",
            "INSUFFICIENT",
        ),
    )


def get_cost_benefits() -> list[CostBenefitResponse]:
    """
    Return cost-benefit evidence for recommendations that
    have an explicitly linked M18 experiment.
    """

    records = _get_records()

    responses: list[CostBenefitResponse] = []

    for wrapper in records:
        try:
            responses.append(
                _build_response(wrapper)
            )
        except ValueError:
            continue

    return responses


def get_cost_benefit(
    experiment_id: str,
) -> CostBenefitResponse:
    """
    Return cost-benefit evidence for one linked experiment.
    """

    records = _get_records()

    for wrapper in records:
        record = wrapper.get("record")

        if not isinstance(record, dict):
            continue

        linkage = record.get("linkage")

        if not isinstance(linkage, dict):
            continue

        linked_experiment_id = linkage.get(
            "linked_experiment_id"
        )

        if str(linked_experiment_id) == experiment_id:
            return _build_response(wrapper)

    raise ValueError(
        f"Cost-benefit experiment "
        f"'{experiment_id}' was not found."
    )
