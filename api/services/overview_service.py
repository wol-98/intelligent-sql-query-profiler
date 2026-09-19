from api.schemas.overview import (
    OverviewCounts,
    OverviewEvidence,
    OverviewPerformance,
    OverviewResponse,
)
from api.services.reporting_repository import fetch_overview_records
from collector.m19_4_real_analysis import (
    build_real_integrated_report,
)


def build_overview() -> OverviewResponse:
    """
    Build the M20 dashboard overview from established
    M19.4 integrated reporting data and read-only database
    reporting data.

    This service does not modify database state and does not
    reproduce M13-M19 recommendation or production-decision logic.
    """

    records = fetch_overview_records()
    integrated_report = build_real_integrated_report()

    recommendation_ids = {
        record["recommendation_id"]
        for record in records
        if record["recommendation_id"] is not None
    }

    evaluated_records = [
        record
        for record in records
        if record["benchmark_id"] is not None
    ]

    successful = sum(
        1
        for record in evaluated_records
        if record["validation_status"] == "SUCCESSFUL"
    )

    neutral = sum(
        1
        for record in evaluated_records
        if record["validation_status"] == "NEUTRAL"
    )

    unsuccessful = sum(
        1
        for record in evaluated_records
        if record["validation_status"] == "UNSUCCESSFUL"
    )

    average_improvements = [
        record["improvement_percentage"]
        for record in evaluated_records
        if record["improvement_percentage"] is not None
    ]

    # The database does not provide a complete stored median
    # for all benchmark observations. Do not calculate a median
    # by averaging median values.
    median_improvements = [
        record["median_improvement_percentage"]
        for record in evaluated_records
        if record["median_improvement_percentage"] is not None
    ]

    index_usage_values = [
        record["index_used"]
        for record in evaluated_records
        if record["index_used"] is not None
    ]

    rows_preserved_values = [
        record["rows_preserved"]
        for record in evaluated_records
        if record["rows_preserved"] is not None
    ]

    average_improvement = (
        sum(average_improvements) / len(average_improvements)
        if average_improvements
        else None
    )

    # Do not fabricate a workload-wide median by averaging
    # per-benchmark median values.
    median_improvement = None

    index_usage_percent = (
        sum(
            1
            for value in index_usage_values
            if value
        )
        / len(index_usage_values)
        * 100
        if index_usage_values
        else None
    )

    rows_preserved_percent = (
        sum(
            1
            for value in rows_preserved_values
            if value
        )
        / len(rows_preserved_values)
        * 100
        if rows_preserved_values
        else None
    )

    # ---------------------------------------------------------
    # M19.4 evidence status
    #
    # Use the established integrated report rather than
    # recreating evidence/linkage logic in the M20 API.
    #
    # Only recommendation records are counted here.
    # Unlinked experimental evidence is deliberately excluded
    # from recommendation evidence counts.
    # ---------------------------------------------------------

    evidence_counts = {
        "COMPLETE": 0,
        "PARTIAL": 0,
        "INSUFFICIENT": 0,
    }

    for item in integrated_report["recommendations"]:
        evidence_status = item[
            "record"
        ][
            "linkage"
        ][
            "evidence_status"
        ]

        if evidence_status in evidence_counts:
            evidence_counts[
                evidence_status
            ] += 1

    return OverviewResponse(
        counts=OverviewCounts(
            recommendations=len(
                recommendation_ids
            ),
            evaluated_recommendations=len({
                record["recommendation_id"]
                for record in evaluated_records
                if record["recommendation_id"]
                is not None
            }),
            benchmark_evaluations=len(
                evaluated_records
            ),
            successful_recommendations=successful,
            neutral_recommendations=neutral,
            unsuccessful_recommendations=unsuccessful,
        ),

        performance=OverviewPerformance(
            average_improvement_percent=(
                average_improvement
            ),
            median_improvement_percent=(
                median_improvement
            ),
            index_usage_percent=(
                index_usage_percent
            ),
            rows_preserved_percent=(
                rows_preserved_percent
            ),
        ),

        evidence=OverviewEvidence(
            complete=evidence_counts[
                "COMPLETE"
            ],
            partial=evidence_counts[
                "PARTIAL"
            ],
            insufficient=evidence_counts[
                "INSUFFICIENT"
            ],
        ),
    )
