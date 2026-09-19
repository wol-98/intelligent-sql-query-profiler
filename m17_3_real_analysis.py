from __future__ import annotations

from collector.index_benefit_cost_analyzer import (
    build_cost_evidence_summary,
    build_integrated_benefit_cost_analysis,
    print_benefit_cost_analysis,
)

from collector.recommendation_quality_analyzer import (
    build_recommendation_evaluation_dataset,
)

from collector.recommendation_quality_analysis import (
    analyze_recommendation_quality,
)

from collector.workload_analyzer import (
    analyze_profiled_workload,
)


# ------------------------------------------------------------------
# M17.1 — Real storage measurement
# ------------------------------------------------------------------

M17_1_INDEX_NAME = "m17_1_idx_orders_customer_id"
M17_1_TABLE_NAME = "orders"
M17_1_COLUMNS = ["customer_id"]

M17_1_INDEX_SIZE_BYTES = 606208
M17_1_TABLE_SIZE_BYTES = 3227648
M17_1_INDEX_TABLE_RATIO_PERCENT = 18.7817


# ------------------------------------------------------------------
# M17.2 — Real maintenance measurement
# ------------------------------------------------------------------

M17_2_MEAN_OVERHEAD_PERCENT = 76.4914
M17_2_MEDIAN_OVERHEAD_PERCENT = 3.43


# ------------------------------------------------------------------
# M17.1 + M17.2 cost evidence
# ------------------------------------------------------------------

def build_m17_3_cost_evidence():
    """
    Build the directly observed M17.1/M17.2 cost evidence.

    These measurements refer to the controlled M17 experiment
    involving orders(customer_id).

    They are not assigned to historical recommendations.
    """

    return build_cost_evidence_summary(
        index_size_bytes=M17_1_INDEX_SIZE_BYTES,
        table_size_bytes=M17_1_TABLE_SIZE_BYTES,
        index_table_ratio_percentage=(
            M17_1_INDEX_TABLE_RATIO_PERCENT
        ),
        maintenance_mean_overhead_percentage=(
            M17_2_MEAN_OVERHEAD_PERCENT
        ),
        maintenance_median_overhead_percentage=(
            M17_2_MEDIAN_OVERHEAD_PERCENT
        ),
    )


# ------------------------------------------------------------------
# Existing recommendation-quality pipeline
# ------------------------------------------------------------------

def load_real_read_benefit_dataset():
    """
    Build the existing M14 recommendation-quality dataset.

    This reuses the established workload and benchmark analysis
    rather than duplicating database queries.
    """

    workload_analysis = analyze_profiled_workload()

    dataset = build_recommendation_evaluation_dataset(
        workload_analysis
    )

    return dataset


# ------------------------------------------------------------------
# M17.3 integrated analysis
# ------------------------------------------------------------------

def build_real_m17_3_analysis():
    """
    Build the complete M17.3 analytical result.

    Cost evidence:
        M17.1 + M17.2 controlled experiments

    Read-benefit evidence:
        Existing validated recommendation benchmarks

    The two evidence streams remain explicitly separate.
    """

    dataset = load_real_read_benefit_dataset()

    cost_evidence = (
        build_m17_3_cost_evidence()
    )

    analysis = (
        build_integrated_benefit_cost_analysis(
            dataset,
            cost_evidence,
        )
    )

    # Keep the existing M14 quality analysis available in the
    # report so that the read-benefit evidence remains traceable
    # to the established analytical pipeline.
    analysis[
        "recommendation_quality_analysis"
    ] = analyze_recommendation_quality(
        dataset
    )

    analysis[
        "m17_1_index_name"
    ] = M17_1_INDEX_NAME

    analysis[
        "m17_1_table_name"
    ] = M17_1_TABLE_NAME

    analysis[
        "m17_1_columns"
    ] = M17_1_COLUMNS

    return analysis


# ------------------------------------------------------------------
# Display
# ------------------------------------------------------------------

def print_m17_3_report(analysis):
    """
    Print the complete M17.3 report.
    """

    print()
    print("=" * 70)
    print("M17.3 — READ BENEFIT VS COST ANALYSIS")
    print("=" * 70)

    print()
    print("EXPERIMENT")
    print("-" * 70)

    print(
        f"Index                  : "
        f"{analysis['m17_1_index_name']}"
    )

    print(
        f"Table                  : "
        f"{analysis['m17_1_table_name']}"
    )

    print(
        "Columns                : "
        f"{', '.join(analysis['m17_1_columns'])}"
    )

    print_benefit_cost_analysis(
        analysis
    )

    quality = analysis[
        "recommendation_quality_analysis"
    ]

    print()
    print("=" * 70)
    print("EXISTING M14 READ-EVIDENCE ANALYSIS")
    print("=" * 70)

    metrics = quality["metrics"]

    print(
        f"Evaluated observations : "
        f"{metrics['evaluated_rows']}"
    )

    print(
        f"Successful             : "
        f"{metrics['successful']}"
    )

    print(
        f"Neutral                : "
        f"{metrics['neutral']}"
    )

    print(
        f"Unsuccessful           : "
        f"{metrics['unsuccessful']}"
    )

    print(
        f"Average improvement    : "
        f"{metrics['average_improvement']:.2f}%"
    )

    print(
        f"Median improvement     : "
        f"{metrics['median_improvement']:.2f}%"
    )

    print(
        f"Index-used rate        : "
        f"{metrics['index_used_rate']:.2f}%"
    )

    print()
    print("=" * 70)
    print("M17.3 INTERPRETATION")
    print("=" * 70)

    print(
        "1. M17.1 provides direct storage-cost evidence for "
        "the tested orders(customer_id) index."
    )

    print(
        "2. M17.2 provides direct write-maintenance evidence "
        "for the controlled indexed-write experiment."
    )

    print(
        "3. Existing benchmark_results provide historical "
        "read-performance evidence for validated recommendations."
    )

    print(
        "4. The historical read-benefit observations are not "
        "assigned the M17.1/M17.2 cost measurements."
    )

    print(
        "5. No per-index cost-benefit ratio is calculated because "
        "read benefit and cost were not measured together for "
        "the same experimental index."
    )

    print(
        "6. M17.3 therefore provides evidence for later "
        "cost-aware recommendation analysis without changing "
        "the current recommendation score."
    )

    print("=" * 70)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    analysis = build_real_m17_3_analysis()

    print_m17_3_report(
        analysis
    )


if __name__ == "__main__":
    main()
