"""
M19.4 Real Integrated Optimization Analysis
--------------------------------------------

Builds the real M19.4 integrated optimization report from
existing project evidence.

Evidence sources:
    M13 - workload cost analysis
    M14 - recommendation / validation analysis
    M18 - linked cost-benefit experiments
    M19.1 - production decision model
    M19.2 - evidence linkage
    M19.3 - production guardrails
    M19.4 - integrated reporting

This module is analytical/reporting-only.

It does NOT:
    - create or drop indexes
    - execute SQL benchmarks
    - modify recommendations
    - modify recommendation scores
    - modify benchmark_results
    - invent recommendation-to-experiment linkage

Important:
    M18 experiment evidence is linked to an M14 recommendation only
    when an explicit recommendation_id is established through the
    project provenance chain.

    Query/table/column similarity alone is NOT treated as sufficient
    provenance.

    M18 experiments that cannot be explicitly linked to an M14
    recommendation remain visible as unlinked experimental evidence.
"""


from collector.cost_aware_recommendation_decision import (
    link_recommendation_evidence,
    evaluate_recommendation,
)

from collector.integrated_optimization_report import (
    build_integrated_record,
    build_integrated_report,
)

from collector.production_guardrails import (
    evaluate_production_guardrails,
)

from collector.recommendation_quality_analyzer import (
    load_recommendation_evaluation_records,
    build_workload_lookup,
)

from collector.workload_cost_analyzer import (
    analyze_workload_costs,
)


# =========================================================
# REAL M18 EXPERIMENT EVIDENCE
# =========================================================
#
# Explicit provenance:
#
#   M18_004 -> Q001 -> Query Profile 2  -> Recommendation 16
#   M18_005 -> Q009 -> Query Profile 10 -> Recommendation 8
#
# M18_006 does NOT have an explicitly established M14
# recommendation linkage.
#
# M18_006 is a standalone customer grouping/ordering
# experiment and is therefore retained as unlinked
# experimental evidence.
# =========================================================

M18_EVIDENCE = {
    "M18_004": {
        "query_fingerprint": None,
        "experiment_id": "M18_004",
        "index_name": "m18_004_idx_orders_customer_id",
        "recommendation_id": 16,

        "read": {
            "available": True,
            "average_improvement_percentage":
                96.14965492190338,
            "median_improvement_percentage":
                96.28863470430761,
            "absolute_savings_ms": 3.9705,
            "index_used": True,
            "plan_changed": True,
            "rows_preserved": True,
        },

        "storage": {
            "storage_available": True,
            "index_table_ratio_percentage":
                18.781725888324875,
        },

        "write": {
            "write_available": True,
            "average_overhead_percentage":
                61.94609033092008,
            "median_overhead_percentage":
                -1.5179438338635933,
        },

        "same_index": True,
    },

    "M18_005": {
        "query_fingerprint": None,
        "experiment_id": "M18_005",
        "index_name": "m18_005_idx_products_category_id",
        "recommendation_id": 8,

        "read": {
            "available": True,
            "average_improvement_percentage":
                0.8305888427800476,
            "median_improvement_percentage":
                1.3956137852463653,
            "absolute_savings_ms": 0.2638,
            "index_used": True,
            "plan_changed": True,
            "rows_preserved": True,
        },

        "storage": {
            "storage_available": True,
            "index_table_ratio_percentage": 25.0,
        },

        "write": {
            "write_available": True,
            "average_overhead_percentage":
                17.485675058851722,
            "median_overhead_percentage":
                26.842269039456816,
        },

        "same_index": True,
    },

    "M18_006": {
        "query_fingerprint": None,
        "experiment_id": "M18_006",
        "index_name": "m18_006_idx_orders_customer_id",

        # No explicit M14 recommendation provenance.
        "recommendation_id": None,

        "read": {
            "available": True,
            "average_improvement_percentage":
                97.80445858105796,
            "median_improvement_percentage":
                97.79797601199401,
            "absolute_savings_ms": 21.1553,
            "index_used": True,
            "plan_changed": True,
            "rows_preserved": True,
        },

        "storage": {
            "storage_available": True,
            "index_table_ratio_percentage":
                16.517857142857142,
        },

        "write": {
            "write_available": True,
            "average_overhead_percentage":
                88.6651322823625,
            "median_overhead_percentage":
                123.83336447415256,
        },

        # Explicitly unlinked.
        "same_index": False,
    },
}


# =========================================================
# M18 EXPERIMENT CONTEXT
# =========================================================
#
# This is descriptive provenance only.
#
# M18_006 is intentionally NOT labelled Q015 because the
# actual experiment SQL is a standalone grouping/order
# query rather than the official Q015 customer-segment JOIN.
# =========================================================

M18_CONTEXT = {
    "M18_004": {
        "query_id": "Q001",
        "query_profile_id": 2,
        "recommendation_id": 16,
        "table_name": "orders",
        "column_name": "customer_id",
        "description": (
            "Q001 - selective equality lookup"
        ),
    },

    "M18_005": {
        "query_id": "Q009",
        "query_profile_id": 10,
        "recommendation_id": 8,
        "table_name": "products",
        "column_name": "category_id",
        "description": (
            "Q009 - join plus category filter"
        ),
    },

    "M18_006": {
        "query_id": None,
        "query_profile_id": None,
        "recommendation_id": None,
        "table_name": "orders",
        "column_name": "customer_id",
        "description": (
            "Standalone customer grouping and ordering "
            "experiment; recommendation linkage not established"
        ),
    },
}


# =========================================================
# HELPERS
# =========================================================

def _normalise_recommendation(record):
    """
    Convert an M14 database record into the canonical
    M19 recommendation structure.
    """

    return {
        "recommendation_id": record["recommendation_id"],
        "score": record["recommendation_score"],
        "priority": record["priority"],
        "candidate_type": record["index_type"],
        "columns": [
            record["table_name"]
            + "."
            + record["column_name"]
        ],
    }


def _build_query_metadata(record):
    """
    Build canonical query metadata from an M14 record.
    """

    return {
        "fingerprint": record["query_hash"],
        "template": record["query_text"],
        "query_type": record["query_type"],
        "tables": [record["table_name"]],
    }


def _build_workload_metadata(
    record,
    workload_lookup,
):
    """
    Resolve workload information from the query fingerprint.

    Missing workload information remains missing.
    """

    fingerprint = record["query_hash"]

    workload = workload_lookup.get(
        fingerprint
    )

    if workload is None:
        return {
            "priority": None,
            "execution_time_share": None,
            "frequency_share": None,
        }

    return {
        "priority": workload.get(
            "workload_priority"
        ),
        "execution_time_share": workload.get(
            "execution_time_share"
        ),
        "frequency_share": workload.get(
            "execution_frequency_share"
        ),
    }


def _build_read_evidence(record):
    """
    Build canonical read evidence from the existing M14
    benchmark/validation record.

    M14 remains the authoritative source for recommendation
    validation evidence.
    """

    improvement = record.get(
        "median_improvement_percentage"
    )

    if improvement is None:
        improvement = record.get(
            "improvement_percentage"
        )

    before = record.get(
        "median_before_ms"
    )

    after = record.get(
        "median_after_ms"
    )

    if before is None:
        before = record.get(
            "execution_time_before_ms"
        )

    if after is None:
        after = record.get(
            "execution_time_after_ms"
        )

    savings = None

    if before is not None and after is not None:
        savings = (
            float(before)
            - float(after)
        )

    available = (
        improvement is not None
        and record.get(
            "rows_preserved"
        ) is not None
        and record.get(
            "index_used"
        ) is not None
    )

    return {
        "available": available,

        "average_improvement_percentage": (
            record.get(
                "improvement_percentage"
            )
        ),

        "median_improvement_percentage": (
            record.get(
                "median_improvement_percentage"
            )
        ),

        "absolute_savings_ms": savings,

        "index_used": record.get(
            "index_used"
        ),

        "plan_changed": record.get(
            "plan_changed"
        ),

        "rows_preserved": record.get(
            "rows_preserved"
        ),
    }


def _build_empty_cost_evidence():
    """
    Build an explicitly unavailable cost-evidence structure.

    M17/M18 evidence must not be substituted with unrelated
    measurements.
    """

    return {
        "storage_available": False,
        "index_table_ratio_percentage": None,

        "write_available": False,
        "average_overhead_percentage": None,
        "median_overhead_percentage": None,
    }


def _build_linked_evidence(
    recommendation,
    m18_evidence,
):
    """
    Build M19.2 evidence input for an explicitly linked M18
    experiment.

    The recommendation ID and same-index status have already
    been established through the project provenance chain.
    """

    return {
        "recommendation_id": (
            recommendation[
                "recommendation_id"
            ]
        ),

        "same_index": bool(
            m18_evidence.get(
                "same_index",
                False,
            )
        ),

        "linked": bool(
            m18_evidence.get(
                "same_index",
                False,
            )
        ),

        "read": bool(
            m18_evidence.get(
                "read",
                {},
            ).get(
                "available",
                False,
            )
        ),

        "storage": bool(
            m18_evidence.get(
                "storage",
                {},
            ).get(
                "storage_available",
                False,
            )
        ),

        "write": bool(
            m18_evidence.get(
                "write",
                {},
            ).get(
                "write_available",
                False,
            )
        ),

        "query_fingerprint": (
            m18_evidence.get(
                "query_fingerprint"
            )
        ),

        "index_name": (
            m18_evidence.get(
                "index_name"
            )
        ),

        "experiment_id": (
            m18_evidence.get(
                "experiment_id"
            )
        ),
    }


def _build_unlinked_evidence(
    recommendation,
):
    """
    Build M19.2 evidence input when no explicit M18
    recommendation linkage exists.

    No unrelated M18 measurement is copied into the
    recommendation's cost evidence.
    """

    return {
        "recommendation_id": (
            recommendation[
                "recommendation_id"
            ]
        ),

        "same_index": False,
        "linked": False,

        "read": False,
        "storage": False,
        "write": False,

        "query_fingerprint": None,
        "index_name": None,
        "experiment_id": None,
    }


def _build_guardrail_input(
    linkage,
    read_evidence,
    cost_evidence,
):
    """
    Build the M19.3 guardrail input.

    Guardrails operate on evidence assembled for the
    recommendation, not on unrelated experiments.
    """

    return {
        "evidence_completeness": {
            "read": read_evidence[
                "available"
            ],

            "storage": cost_evidence[
                "storage_available"
            ],

            "write": cost_evidence[
                "write_available"
            ],
        },

        "evidence_linkage": {
            "linked": linkage[
                "linked"
            ],
        },

        "read_evidence": read_evidence,

        "cost_evidence": cost_evidence,

        "experimental_scope": (
            "PROJECT_VALIDATED"
            if linkage["linked"]
            else None
        ),
    }


def _find_m18_for_recommendation(
    record,
):
    """
    Find the M18 experiment explicitly linked to the
    recommendation.

    This function does NOT infer linkage from:

        - table name
        - column name
        - query similarity
        - index naming similarity

    It requires an explicit recommendation_id.
    """

    recommendation_id = record[
        "recommendation_id"
    ]

    for experiment in M18_EVIDENCE.values():

        if (
            experiment.get(
                "recommendation_id"
            )
            == recommendation_id
            and experiment.get(
                "same_index"
            ) is True
        ):
            return experiment

    return None


def _build_integrated_record_for_m14(
    record,
    workload_lookup,
):
    """
    Build one M19.4 record from one M14 recommendation.

    If an explicitly linked M18 experiment exists, its
    complete read/storage/write evidence is incorporated.

    Otherwise, M19.4 preserves the M14 read evidence while
    leaving M18 cost evidence unavailable.
    """

    recommendation = _normalise_recommendation(
        record
    )

    query = _build_query_metadata(
        record
    )

    workload = _build_workload_metadata(
        record,
        workload_lookup,
    )

    # -----------------------------------------------------
    # Find explicitly linked M18 evidence
    # -----------------------------------------------------

    m18 = _find_m18_for_recommendation(
        record
    )

    # -----------------------------------------------------
    # Read evidence
    # -----------------------------------------------------
    #
    # If M18 is explicitly linked to this recommendation,
    # M18 supplies the complete controlled read evidence.
    #
    # Otherwise, retain the existing M14 read evidence.
    # -----------------------------------------------------

    if m18 is not None:

        read_evidence = {
            "available": (
                m18["read"]["available"]
            ),

            "average_improvement_percentage": (
                m18["read"][
                    "average_improvement_percentage"
                ]
            ),

            "median_improvement_percentage": (
                m18["read"][
                    "median_improvement_percentage"
                ]
            ),

            "absolute_savings_ms": (
                m18["read"][
                    "absolute_savings_ms"
                ]
            ),

            "index_used": (
                m18["read"]["index_used"]
            ),

            "plan_changed": (
                m18["read"]["plan_changed"]
            ),

            "rows_preserved": (
                m18["read"]["rows_preserved"]
            ),
        }

    else:

        read_evidence = _build_read_evidence(
            record
        )

    # -----------------------------------------------------
    # Cost evidence and M19.2 linkage
    # -----------------------------------------------------

    if m18 is None:

        cost_evidence = (
            _build_empty_cost_evidence()
        )

        evidence = (
            _build_unlinked_evidence(
                recommendation
            )
        )

    else:

        cost_evidence = {
            "storage_available": (
                m18["storage"][
                    "storage_available"
                ]
            ),

            "index_table_ratio_percentage": (
                m18["storage"][
                    "index_table_ratio_percentage"
                ]
            ),

            "write_available": (
                m18["write"][
                    "write_available"
                ]
            ),

            "average_overhead_percentage": (
                m18["write"][
                    "average_overhead_percentage"
                ]
            ),

            "median_overhead_percentage": (
                m18["write"][
                    "median_overhead_percentage"
                ]
            ),
        }

        evidence = _build_linked_evidence(
            recommendation,
            m18,
        )

    # -----------------------------------------------------
    # M19.2 evidence linkage
    # -----------------------------------------------------

    linkage = link_recommendation_evidence(
        recommendation,
        evidence,
    )

    # -----------------------------------------------------
    # M19.1 production decision
    # -----------------------------------------------------

    decision_result = evaluate_recommendation(
        recommendation,
        workload,
        read_evidence,
        cost_evidence,
        linkage,
    )

    decision = decision_result[
        "decision"
    ]

    # -----------------------------------------------------
    # M19.3 safety guardrails
    # -----------------------------------------------------

    guardrail_input = (
        _build_guardrail_input(
            linkage,
            read_evidence,
            cost_evidence,
        )
    )

    guardrails = (
        evaluate_production_guardrails(
            guardrail_input
        )
    )

    # -----------------------------------------------------
    # M19.4 integrated record
    # -----------------------------------------------------

    return build_integrated_record(
        recommendation=recommendation,
        query=query,
        workload=workload,
        read_evidence=read_evidence,
        cost_evidence=cost_evidence,

        linkage={
            "same_index": (
                linkage["same_index"]
            ),

            "index_name": (
                linkage["index_name"]
            ),

            "linked_experiment_id": (
                linkage["experiment_id"]
            ),

            "evidence_status": (
                linkage["evidence_status"]
            ),
        },

        decision=decision,

        guardrails=guardrails,
    )
# =========================================================
# UNLINKED M18 EXPERIMENT REPORTING
# =========================================================

def _build_unlinked_m18_experiments():
    """
    Return M18 experiments that have no explicit
    recommendation linkage.

    These experiments remain visible for auditability,
    but they are not incorporated into recommendation
    decisions.
    """

    unlinked = []

    for experiment in M18_EVIDENCE.values():

        if (
            experiment.get(
                "recommendation_id"
            )
            is not None
            and experiment.get(
                "same_index"
            ) is True
        ):
            continue

        experiment_id = experiment[
            "experiment_id"
        ]

        context = M18_CONTEXT.get(
            experiment_id,
            {},
        )

        unlinked.append(
            {
                "experiment_id": experiment_id,

                "index_name": experiment[
                    "index_name"
                ],

                "table_name": context.get(
                    "table_name"
                ),

                "column_name": context.get(
                    "column_name"
                ),

                "query_id": context.get(
                    "query_id"
                ),

                "query_profile_id": context.get(
                    "query_profile_id"
                ),

                "recommendation_id": None,

                "linkage_status": (
                    "NOT_ESTABLISHED"
                ),

                "description": context.get(
                    "description"
                ),

                "read_evidence": experiment[
                    "read"
                ],

                "storage_evidence": experiment[
                    "storage"
                ],

                "write_evidence": experiment[
                    "write"
                ],
            }
        )

    return unlinked


# =========================================================
# REAL M19.4 ANALYSIS
# =========================================================

def build_real_integrated_report():
    """
    Build the real M19.4 report from existing project evidence.

    Database access occurs only through the existing M14
    analytical loader and M13 workload analysis.

    No indexes are created or dropped and no benchmark
    measurements are executed.

    Unlinked M18 experiments are retained separately from
    recommendation-linked evidence.
    """

    workload_analysis = (
        analyze_workload_costs()
    )

    workload_lookup = (
        build_workload_lookup(
            workload_analysis
        )
    )

    recommendation_records = (
        load_recommendation_evaluation_records()
    )

    records = []

    seen_recommendations = set()

    for record in recommendation_records:

        recommendation_id = record[
            "recommendation_id"
        ]

        # M14 may contain multiple benchmark rows
        # for one recommendation.
        #
        # M19.4 reports one integrated record per
        # recommendation.
        if recommendation_id in (
            seen_recommendations
        ):
            continue

        seen_recommendations.add(
            recommendation_id
        )

        integrated_record = (
            _build_integrated_record_for_m14(
                record,
                workload_lookup,
            )
        )

        records.append(
            integrated_record
        )

    report = build_integrated_report(
        records
    )

    # Preserve M18 experiments that could not be
    # safely attributed to an M14 recommendation.
    report[
        "unlinked_experimental_evidence"
    ] = _build_unlinked_m18_experiments()

    return report


# =========================================================
# REPORTING
# =========================================================

def print_real_integrated_report(
    report,
):
    """
    Print a concise audit-oriented M19.4 report.
    """

    print(
        "\n"
        + "=" * 90
    )

    print(
        "M19.4 — INTEGRATED OPTIMIZATION REPORT"
    )

    print(
        "=" * 90
    )

    print(
        f"\nReport version              : "
        f"{report['report']['report_version']}"
    )

    print(
        f"Decision policy             : "
        f"{report['report']['decision_policy_version']}"
    )

    print(
        f"Guardrail policy            : "
        f"{report['report']['guardrail_policy_version']}"
    )

    summary = report[
        "summary"
    ]

    print(
        "\n"
        + "-" * 90
    )

    print(
        "PORTFOLIO SUMMARY"
    )

    print(
        "-" * 90
    )

    print(
        f"Total recommendations       : "
        f"{summary['total_recommendations']}"
    )

    print(
        f"Decision counts             : "
        f"{summary['decision_counts']}"
    )

    print(
        f"Guardrail counts            : "
        f"{summary['guardrail_counts']}"
    )

    print(
        f"Evidence counts             : "
        f"{summary['evidence_counts']}"
    )

    print(
        "\n"
        + "-" * 90
    )

    print(
        "RECOMMENDATION OUTCOMES"
    )

    print(
        "-" * 90
    )

    print(
        f"{'ID':>4} | "
        f"{'Candidate':<40} | "
        f"{'Evidence':<14} | "
        f"{'Decision':<22} | "
        f"{'Guardrail':<20}"
    )

    print(
        "-" * 110
    )

    for item in report[
        "recommendations"
    ]:

        record = item[
            "record"
        ]

        outcome = item[
            "outcome"
        ]

        recommendation = record[
            "recommendation"
        ]

        candidate = (
            recommendation[
                "columns"
            ][0]
            if recommendation[
                "columns"
            ]
            else "N/A"
        )

        print(
            f"{recommendation['recommendation_id']:>4} | "
            f"{candidate:<40} | "
            f"{outcome['outcome']['evidence_status']:<14} | "
            f"{outcome['outcome']['decision']:<22} | "
            f"{outcome['outcome']['guardrail_status']:<20}"
        )

    print(
        "\n"
        + "-" * 90
    )

    print(
        "READ / COST EVIDENCE"
    )

    print(
        "-" * 90
    )

    for item in report[
        "recommendations"
    ]:

        outcome = item[
            "outcome"
        ]

        print(
            f"\nRecommendation "
            f"{outcome['recommendation_id']}"
        )

        print(
            f"  Index                     : "
            f"{outcome['index_name']}"
        )

        print(
            f"  Experiment                : "
            f"{outcome['experiment_id']}"
        )

        print(
            f"  Evidence status           : "
            f"{outcome['outcome']['evidence_status']}"
        )

        print(
            f"  Decision                  : "
            f"{outcome['outcome']['decision']}"
        )

        print(
            f"  Guardrail status          : "
            f"{outcome['outcome']['guardrail_status']}"
        )

        print(
            f"  Read improvement          : "
            f"{outcome['read']['improvement']}"
        )

        print(
            f"  Read median improvement   : "
            f"{outcome['read']['median_improvement']}"
        )

        print(
            f"  Read savings (ms)         : "
            f"{outcome['read']['savings_ms']}"
        )

        print(
            f"  Storage ratio             : "
            f"{outcome['cost']['storage_ratio']}"
        )

        print(
            f"  Write overhead            : "
            f"{outcome['cost']['write_overhead']}"
        )

        print(
            f"  Median write overhead     : "
            f"{outcome['cost']['median_write_overhead']}"
        )

    # -----------------------------------------------------
    # Unlinked experimental evidence
    # -----------------------------------------------------

    print(
        "\n"
        + "-" * 90
    )

    print(
        "UNLINKED EXPERIMENTAL EVIDENCE"
    )

    print(
        "-" * 90
    )

    unlinked = report.get(
        "unlinked_experimental_evidence",
        [],
    )

    if not unlinked:

        print(
            "No unlinked M18 experiments."
        )

    else:

        for experiment in unlinked:

            print(
                f"\nExperiment                : "
                f"{experiment['experiment_id']}"
            )

            print(
                f"  Index                   : "
                f"{experiment['index_name']}"
            )

            print(
                f"  Candidate               : "
                f"{experiment['table_name']}."
                f"{experiment['column_name']}"
            )

            print(
                f"  Query ID                : "
                f"{experiment['query_id']}"
            )

            print(
                f"  Query Profile ID       : "
                f"{experiment['query_profile_id']}"
            )

            print(
                f"  Recommendation ID      : "
                f"{experiment['recommendation_id']}"
            )

            print(
                f"  Linkage status          : "
                f"{experiment['linkage_status']}"
            )

            print(
                f"  Description             : "
                f"{experiment['description']}"
            )

            print(
                "  Production decision     : "
                "NOT EVALUATED"
            )


# =========================================================
# MAIN
# =========================================================

def main():
    """
    Execute the real M19.4 analysis.
    """

    report = (
        build_real_integrated_report()
    )

    print_real_integrated_report(
        report
    )


if __name__ == "__main__":
    main()
