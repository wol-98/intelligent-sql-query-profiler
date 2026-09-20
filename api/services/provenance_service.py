from __future__ import annotations

from api.schemas.provenance import ProvenanceResponse
from collector.m19_4_real_analysis import build_real_integrated_report


def _build_provenance_response(item: dict) -> ProvenanceResponse:
    record = item["record"]

    recommendation = record["recommendation"]
    query = record["query"]
    linkage = record["linkage"]

    linked_experiment_id = linkage.get("linked_experiment_id")
    same_index = bool(linkage.get("same_index", False))

    if linked_experiment_id is not None and same_index:
        status = "LINKED"
    else:
        status = "NOT_ESTABLISHED"

    return ProvenanceResponse(
        recommendation_id=recommendation["recommendation_id"],
        query_fingerprint=query.get("fingerprint"),
        index_name=linkage.get("index_name"),
        linked_experiment_id=linked_experiment_id,
        status=status,
        evidence_status=linkage["evidence_status"],
    )


def get_provenance_records() -> list[ProvenanceResponse]:
    report = build_real_integrated_report()

    return [
        _build_provenance_response(item)
        for item in report["recommendations"]
    ]


def get_provenance_record(
    recommendation_id: int,
) -> ProvenanceResponse:
    report = build_real_integrated_report()

    for item in report["recommendations"]:
        record = item["record"]

        if (
            record["recommendation"]["recommendation_id"]
            == recommendation_id
        ):
            return _build_provenance_response(item)

    raise ValueError(
        f"Provenance for recommendation "
        f"{recommendation_id} not found."
    )
