from collections import defaultdict

from api.schemas.workload import WorkloadResponse
from api.services.workload_repository import fetch_workload_records
from collector.query_parser import parse_query


def _classify_priority(time_share, frequency_share):
    if time_share is None:
        return "Unknown"

    if time_share >= 50:
        return "Critical"

    if time_share >= 10:
        return "High"

    if time_share >= 5 or frequency_share >= 10:
        return "Moderate"

    return "Low"


def _group_profiles(profile_rows):
    groups = {}

    for row in profile_rows:
        (
            query_profile_id,
            query_hash,
            query_text,
            query_type,
            execution_count,
            total_execution_time_ms,
            average_execution_time_ms,
        ) = row

        metadata = parse_query(query_text)

        fingerprint = metadata["fingerprint"]
        normalized_template = metadata["normalized_template"]

        if fingerprint not in groups:
            groups[fingerprint] = {
                "fingerprint": fingerprint,
                "template": normalized_template,
                "query_text": query_text,
                "query_type": query_type,
                "execution_count": 0,
                "total_execution_time_ms": 0.0,
                "profile_ids": [],
            }

        group = groups[fingerprint]

        group["execution_count"] += execution_count or 0
        group["total_execution_time_ms"] += (
            total_execution_time_ms or 0.0
        )
        group["profile_ids"].append(query_profile_id)

    return groups

def build_workloads():
    profile_rows, recommendation_rows = fetch_workload_records()

    groups = _group_profiles(profile_rows)

    total_execution_time = sum(
        group["total_execution_time_ms"]
        for group in groups.values()
    )

    total_execution_count = sum(
        group["execution_count"]
        for group in groups.values()
    )

    recommendation_map = defaultdict(list)

    for recommendation_id, query_profile_id in recommendation_rows:
        recommendation_map[query_profile_id].append(recommendation_id)

    workloads = []

    for group in groups.values():
        execution_count = group["execution_count"]
        total_time = group["total_execution_time_ms"]

        average_time = (
            total_time / execution_count
            if execution_count
            else None
        )

        time_share = (
            (total_time / total_execution_time) * 100
            if total_execution_time
            else None
        )

        frequency_share = (
            (execution_count / total_execution_count) * 100
            if total_execution_count
            else None
        )

        recommendation_ids = sorted(
            {
                recommendation_id
                for profile_id in group["profile_ids"]
                for recommendation_id in recommendation_map[profile_id]
            }
        )

        workloads.append(
            WorkloadResponse(
                fingerprint=group["fingerprint"],
                template=group["template"],
                execution_count=execution_count,
                total_execution_time_ms=total_time,
                average_execution_time_ms=average_time,
                time_share=time_share,
                frequency_share=frequency_share,
                priority=_classify_priority(
                    time_share,
                    frequency_share,
                ),
                recommendation_ids=recommendation_ids,
            )
        )

    workloads.sort(
        key=lambda workload: (
            -(workload.total_execution_time_ms or 0),
            workload.fingerprint,
        )
    )

    return workloads


def get_workloads():
    return build_workloads()
