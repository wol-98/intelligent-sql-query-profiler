from api.services.reporting_repository import (
    fetch_recommendation_records,
)

from api.schemas.recommendation import (
    RecommendationCost,
    RecommendationDecision,
    RecommendationProvenance,
    RecommendationQuery,
    RecommendationResponse,
    RecommendationValidation,
    RecommendationWorkload,
)

from collector.m19_4_real_analysis import (
    build_real_integrated_report,
)
def _normalize_validation_outcome(
    validation_status: str | None,
) -> str | None:
    """
    Normalize database benchmark validation status
    to the M20 API ValidationOutcome enum.
    """

    if validation_status is None:
        return None

    status_map = {
        "SUCCESSFUL": "SUCCESS",
        "SUCCESS": "SUCCESS",
        "NEUTRAL": "NEUTRAL",
        "UNSUCCESSFUL": "UNSUCCESSFUL",
        "UNSAFE": "UNSAFE",
    }

    return status_map.get(
        validation_status.upper()
    )

def _to_recommendation_response(
    item: dict,
    database_records: list[dict],
) -> RecommendationResponse:
    """
    Adapt one established M19.4 recommendation record
    to the M20 API response contract.

    M19.4 remains authoritative for:
    - production decision
    - guardrail status
    - evidence linkage
    - linked cost-benefit evidence

    The reporting repository supplies database-backed
    descriptive fields such as:
    - index/table metadata
    - recommendation reason
    - execution count
    - benchmark validation outcome

    No recommendation score, production decision,
    guardrail status, or evidence linkage is recalculated here.
    """

    record = item["record"]

    first_database_record = (
        database_records[0]
        if database_records
        else None
    )

    benchmark_records = [
        row
        for row in database_records
        if row["benchmark_id"] is not None
    ]

    latest_benchmark = (
        benchmark_records[-1]
        if benchmark_records
        else None
    )

    recommendation = record["recommendation"]
    query = record["query"]
    workload = record["workload"]
    read = record["read_evidence"]
    cost = record["cost_evidence"]
    linkage = record["linkage"]
    decision = record["decision"]
    guardrails = record["guardrails"]

    # ---------------------------------------------------------
    # Database-backed descriptive metadata
    # ---------------------------------------------------------

    database_table_name = (
        first_database_record["table_name"]
        if first_database_record
        else None
    )

    database_index_type = (
        first_database_record["index_type"]
        if first_database_record
        else None
    )

    database_reason = (
        first_database_record["reasoning"]
        if first_database_record
        else None
    )

    execution_count = (
        first_database_record["execution_count"]
        if first_database_record
        else None
    )

    # ---------------------------------------------------------
    # M14 benchmark validation evidence
    #
    # The validation outcome comes from benchmark_results.
    # The M19.4 linked read evidence remains separate.
    # ---------------------------------------------------------

    validation_outcome = _normalize_validation_outcome(
        latest_benchmark["validation_status"]
        if latest_benchmark
        else None
    )

    return RecommendationResponse(
        recommendation_id=recommendation[
            "recommendation_id"
        ],

        # M19.4 linkage is authoritative.
        # Unlinked recommendations legitimately have None.
        index_name=linkage.get(
            "index_name"
        ),

        table_name=(
            database_table_name
            if database_table_name is not None
            else (
                recommendation["columns"][0].split(
                    ".",
                    1,
                )[0]
                if recommendation["columns"]
                and "." in recommendation["columns"][0]
                else ""
            )
        ),

        columns=recommendation[
            "columns"
        ],

        index_type=(
            database_index_type
            if database_index_type is not None
            else recommendation.get(
                "candidate_type"
            )
        ),

        candidate_type=recommendation.get(
            "candidate_type"
        ),

        # M19.4 does not currently expose source_type.
        # Do not infer it.
        source_type=None,

        score=recommendation[
            "score"
        ],

        priority=recommendation[
            "priority"
        ],

        reason=database_reason,

        query=RecommendationQuery(
            fingerprint=query.get(
                "fingerprint"
            ),
            template=query.get(
                "template"
            ),
            query_type=query.get(
                "query_type"
            ),
        ),

        workload=RecommendationWorkload(
            priority=workload.get(
                "priority"
            ),
            execution_count=execution_count,
            time_share=workload.get(
                "execution_time_share"
            ),
            frequency_share=workload.get(
                "frequency_share"
            ),
        ),

        validation=RecommendationValidation(
            # Validation outcome comes from the stored
            # benchmark result, not from M19.4 decision evidence.
            outcome=validation_outcome,

            # These fields remain the M19.4 linked read
            # evidence when such evidence exists.
            improvement=read.get(
                "average_improvement_percentage"
            ),

            median_improvement=read.get(
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

        cost=RecommendationCost(
            storage_ratio_percent=cost.get(
                "index_table_ratio_percentage"
            ),

            write_overhead_percent=cost.get(
                "average_overhead_percentage"
            ),

            median_write_overhead_percent=cost.get(
                "median_overhead_percentage"
            ),

            evidence_status=linkage[
                "evidence_status"
            ],
        ),

        # M19.1 production decision remains authoritative.
        decision=RecommendationDecision(
            state=decision[
                "decision"
            ],

            guardrail=guardrails[
                "status"
            ],
        ),

        # M19.4 remains authoritative for provenance.
        provenance=RecommendationProvenance(
            linked_experiment_id=linkage.get(
                "linked_experiment_id"
            ),

            status=(
                "LINKED"
                if linkage.get(
                    "same_index"
                )
                else "NOT_ESTABLISHED"
            ),

            evidence_status=linkage[
                "evidence_status"
            ],
        ),
    )


def get_recommendations() -> list[
    RecommendationResponse
]:
    """
    Return all integrated M19.4 recommendations
    through the M20 read-only API.

    M19.4 provides the integrated intelligence.
    The reporting repository supplies database-backed
    descriptive and benchmark metadata.
    """

    report = build_real_integrated_report()

    database_records = fetch_recommendation_records()

    records_by_recommendation: dict[
        int,
        list[dict],
    ] = {}

    for row in database_records:
        recommendation_id = row[
            "recommendation_id"
        ]

        records_by_recommendation.setdefault(
            recommendation_id,
            [],
        ).append(row)

    responses = []

    for item in report[
        "recommendations"
    ]:
        recommendation_id = item[
            "record"
        ][
            "recommendation"
        ][
            "recommendation_id"
        ]

        responses.append(
            _to_recommendation_response(
                item,
                records_by_recommendation.get(
                    recommendation_id,
                    [],
                ),
            )
        )

    return responses


def get_recommendation(
    recommendation_id: int,
) -> RecommendationResponse:
    """
    Return one integrated recommendation.

    Raises ValueError when the recommendation
    does not exist.
    """

    report = build_real_integrated_report()

    database_records = fetch_recommendation_records(
        recommendation_id=recommendation_id,
    )

    for item in report[
        "recommendations"
    ]:
        record = item["record"]

        if (
            record["recommendation"][
                "recommendation_id"
            ]
            == recommendation_id
        ):
            return _to_recommendation_response(
                item,
                database_records,
            )

    raise ValueError(
        f"Recommendation {recommendation_id} not found."
    )
