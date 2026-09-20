from __future__ import annotations

from api.schemas.query import QueryPlan, QueryResponse
from api.services.query_repository import fetch_query_records
from collector.feature_extractor import extract_plan_features
from collector.plan_analyzer import analyze_plan
from collector.query_parser import QueryFingerprinter


def _get_root_plan(execution_plan):
    """
    Return the root PostgreSQL plan object from a stored EXPLAIN JSON
    structure.

    PostgreSQL EXPLAIN (FORMAT JSON) normally stores the plan as:

        [
            {
                "Plan": {...}
            }
        ]

    This helper also tolerates the already-unwrapped representation.
    """

    if execution_plan is None:
        return None

    if isinstance(execution_plan, list):
        if not execution_plan:
            return None

        execution_plan = execution_plan[0]

    if not isinstance(execution_plan, dict):
        return None

    if "Plan" in execution_plan:
        return execution_plan["Plan"]

    return execution_plan


def _build_plan(execution_plan) -> QueryPlan | None:
    """
    Build the dashboard query-plan summary from the stored execution plan.

    No SQL is executed here. The existing M20 reporting layer only
    analyzes plan data already stored in query_profiles.
    """

    root_plan = _get_root_plan(execution_plan)

    if root_plan is None:
        return None

    try:
        plan_nodes = analyze_plan(root_plan)
        features = extract_plan_features(plan_nodes)
    except (TypeError, KeyError, ValueError):
        return None

    return QueryPlan(
        node_types=features.get("node_types", []),
        sequential_scans=features.get("seq_scan_count"),
        index_scans=features.get("index_scan_count"),
        bitmap_scans=features.get("bitmap_scan_count"),
        joins=features.get("join_count"),
        has_filter=features.get("has_filter"),
        has_index_condition=features.get(
            "has_index_condition"
        ),
    )


def _build_query_response(record: dict) -> QueryResponse:
    """
    Convert a database query-profile record into the M20 API schema.
    """

    query_text = record.get("query_text") or ""

    fingerprint = record.get("query_hash")

    template = None

    if query_text:
        try:
            generated_fingerprint, normalized_template = (
                QueryFingerprinter.generate_fingerprint(
                    query_text
                )
            )

            template = normalized_template

            # The persisted query_hash is the database-side identifier.
            # Use it as the API fingerprint when available.
            if not fingerprint:
                fingerprint = generated_fingerprint

        except (TypeError, ValueError):
            template = query_text

    recommendation_ids = (
        record.get("recommendation_ids") or []
    )

    recommendation_ids = sorted(
        {
            int(recommendation_id)
            for recommendation_id in recommendation_ids
            if recommendation_id is not None
        }
    )

    return QueryResponse(
        query_profile_id=record["query_profile_id"],
        fingerprint=fingerprint or "",
        template=template,
        query_type=record.get("query_type") or "UNKNOWN",
        query_text=query_text,
        execution_count=record.get("execution_count"),
        total_execution_time_ms=record.get(
            "total_execution_time_ms"
        ),
        average_execution_time_ms=record.get(
            "average_execution_time_ms"
        ),
        rows_processed=record.get("rows_processed"),
        table_name=record.get("table_name"),
        captured_at=(
            record["captured_at"].isoformat()
            if record.get("captured_at") is not None
            else None
        ),
        plan=_build_plan(
            record.get("execution_plan")
        ),
        recommendation_ids=recommendation_ids,
    )


def get_queries() -> list[QueryResponse]:
    """
    Return all profiled queries available to the M20 dashboard.
    """

    records = fetch_query_records()

    return [
        _build_query_response(record)
        for record in records
    ]


def get_query(
    fingerprint: str,
) -> QueryResponse:
    """
    Return one query profile identified by its fingerprint.
    """

    records = fetch_query_records(
        fingerprint=fingerprint
    )

    if not records:
        raise ValueError(
            f"Query with fingerprint {fingerprint} not found."
        )

    return _build_query_response(records[0])
