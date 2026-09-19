"""
M17.3 - Read Benefit vs Cost Analysis

Analytical layer combining:

1. Index storage-cost evidence from M17.1
2. Index maintenance-cost evidence from M17.2
3. Historical read-performance evidence from validated
   recommendation benchmarks

This module is analytical only.

It does NOT:
- create indexes
- drop indexes
- execute queries
- modify recommendation scores
- generate candidates
- change recommendation priorities
- write benchmark_results

Important methodological rule:
M17.1/M17.2 cost measurements and historical benchmark
read-benefit measurements are kept as separate evidence
streams unless both measurements were collected for the
same experimental index.
"""


# =========================================================
# VALIDATION
# =========================================================

def validate_benefit_cost_record(record):
    """
    Validate a combined benefit/cost evidence record.

    This function is intentionally conservative. It validates
    only fields that are actually present and does not infer
    missing measurements.
    """

    if not isinstance(record, dict):
        return False

    if (
        record.get("read_improvement_percentage")
        is not None
    ):
        if not isinstance(
            record["read_improvement_percentage"],
            (int, float)
        ):
            return False

    if (
        record.get("index_size_bytes")
        is not None
    ):
        if record["index_size_bytes"] < 0:
            return False

    if (
        record.get("table_size_bytes")
        is not None
    ):
        if record["table_size_bytes"] < 0:
            return False

    if (
        record.get("maintenance_overhead_percentage")
        is not None
    ):
        if not isinstance(
            record["maintenance_overhead_percentage"],
            (int, float)
        ):
            return False

    return True


# =========================================================
# READ BENEFIT
# =========================================================

def calculate_read_benefit_per_storage(
    read_improvement_percentage,
    index_size_bytes
):
    """
    Calculate read improvement per MB of index storage.

    This metric is only valid when the read-benefit and
    storage measurements belong to the same experimental
    index.

    Returns None when the required evidence is missing.
    """

    if read_improvement_percentage is None:
        return None

    if index_size_bytes is None:
        return None

    if index_size_bytes <= 0:
        return None

    index_size_mb = (
        index_size_bytes / (1024 * 1024)
    )

    if index_size_mb <= 0:
        return None

    return (
        read_improvement_percentage
        / index_size_mb
    )


# =========================================================
# BENEFIT / COST DIFFERENCE
# =========================================================

def calculate_benefit_cost_difference(
    read_improvement_percentage,
    maintenance_overhead_percentage
):
    """
    Calculate the difference between read improvement and
    maintenance overhead.

    This is a descriptive difference, not a profitability
    or optimization score.

    Returns None when either measurement is unavailable.
    """

    if read_improvement_percentage is None:
        return None

    if maintenance_overhead_percentage is None:
        return None

    return (
        read_improvement_percentage
        - maintenance_overhead_percentage
    )


# =========================================================
# CLASSIFICATION
# =========================================================

def classify_read_benefit(
    improvement_percentage
):
    """
    Classify read-performance benefit.

    Thresholds are project-defined descriptive categories.
    They are not PostgreSQL standards.
    """

    if improvement_percentage is None:
        return "UNKNOWN"

    if improvement_percentage >= 50:
        return "HIGH_BENEFIT"

    if improvement_percentage >= 10:
        return "MODERATE_BENEFIT"

    if improvement_percentage > 0:
        return "LOW_BENEFIT"

    return "NEGATIVE_BENEFIT"


def classify_cost_impact(
    maintenance_overhead_percentage
):
    """
    Classify maintenance overhead.

    Thresholds are project-defined descriptive categories.
    They are not PostgreSQL standards.
    """

    if maintenance_overhead_percentage is None:
        return "UNKNOWN"

    if maintenance_overhead_percentage <= 0:
        return "NONE_OR_NEGATIVE"

    if maintenance_overhead_percentage < 10:
        return "LOW_COST"

    if maintenance_overhead_percentage < 50:
        return "MODERATE_COST"

    return "HIGH_COST"


# =========================================================
# RECORD CONSTRUCTION
# =========================================================

def build_benefit_cost_record(
    read_improvement_percentage,
    index_size_bytes,
    table_size_bytes,
    maintenance_overhead_percentage,
    maintenance_median_overhead_percentage=None
):
    """
    Build a combined benefit/cost record.

    This should only be used when all measurements refer to
    the same experimental index.
    """

    record = {
        "read_improvement_percentage":
            read_improvement_percentage,

        "index_size_bytes":
            index_size_bytes,

        "table_size_bytes":
            table_size_bytes,

        "maintenance_overhead_percentage":
            maintenance_overhead_percentage,

        "maintenance_median_overhead_percentage":
            maintenance_median_overhead_percentage,

        "read_benefit_class":
            classify_read_benefit(
                read_improvement_percentage
            ),

        "maintenance_cost_class":
            classify_cost_impact(
                maintenance_overhead_percentage
            ),

        "read_benefit_per_storage_mb":
            calculate_read_benefit_per_storage(
                read_improvement_percentage,
                index_size_bytes
            ),

        "benefit_cost_difference":
            calculate_benefit_cost_difference(
                read_improvement_percentage,
                maintenance_overhead_percentage
            ),
    }

    return record


# =========================================================
# HISTORICAL READ-BENEFIT SUMMARY
# =========================================================

def build_read_benefit_summary(dataset):
    """
    Summarize read-performance evidence from the existing
    recommendation validation dataset.

    The dataset is expected to contain the documented
    M14 evaluation metric:

        evaluation_improvement_percentage

    No cost measurements are attached to these historical
    observations.
    """

    evaluated = [
        row
        for row in dataset
        if row.get(
            "evaluation_improvement_percentage"
        ) is not None
    ]

    improvements = [
        row["evaluation_improvement_percentage"]
        for row in evaluated
    ]

    successful = [
        row
        for row in evaluated
        if row.get("validation_status")
        == "SUCCESSFUL"
    ]

    neutral = [
        row
        for row in evaluated
        if row.get("validation_status")
        == "NEUTRAL"
    ]

    unsuccessful = [
        row
        for row in evaluated
        if row.get("validation_status")
        == "UNSUCCESSFUL"
    ]

    unsafe = [
        row
        for row in evaluated
        if row.get("validation_status")
        == "UNSAFE"
    ]

    index_used = [
        row
        for row in evaluated
        if row.get("index_used") is True
    ]

    rows_preserved = [
        row
        for row in evaluated
        if row.get("rows_preserved") is True
    ]

    positive = [
        value
        for value in improvements
        if value > 0
    ]

    negative = [
        value
        for value in improvements
        if value <= 0
    ]

    return {
        "evaluated_observations":
            len(evaluated),

        "successful":
            len(successful),

        "neutral":
            len(neutral),

        "unsuccessful":
            len(unsuccessful),

        "unsafe":
            len(unsafe),

        "success_rate":
            (
                len(successful)
                / len(evaluated)
                * 100
                if evaluated
                else None
            ),

        "average_improvement":
            (
                sum(improvements)
                / len(improvements)
                if improvements
                else None
            ),

        "positive_benefit_count":
            len(positive),

        "negative_benefit_count":
            len(negative),

        "positive_benefit_rate":
            (
                len(positive)
                / len(evaluated)
                * 100
                if evaluated
                else None
            ),

        "index_used_count":
            len(index_used),

        "index_used_rate":
            (
                len(index_used)
                / len(evaluated)
                * 100
                if evaluated
                else None
            ),

        "rows_preserved_count":
            len(rows_preserved),

        "rows_preserved_rate":
            (
                len(rows_preserved)
                / len(evaluated)
                * 100
                if evaluated
                else None
            ),
    }


# =========================================================
# COST EVIDENCE SUMMARY
# =========================================================

def build_cost_evidence_summary(
    index_size_bytes,
    table_size_bytes,
    index_table_ratio_percentage,
    maintenance_mean_overhead_percentage,
    maintenance_median_overhead_percentage,
    maintenance_standard_deviation_percentage=None,
    maintenance_min_overhead_percentage=None,
    maintenance_max_overhead_percentage=None
):
    """
    Build a summary of M17.1/M17.2 cost evidence.

    These values must come from the controlled M17
    experiments.
    """

    return {
        "index_size_bytes":
            index_size_bytes,

        "table_size_bytes":
            table_size_bytes,

        "index_table_ratio_percentage":
            index_table_ratio_percentage,

        "maintenance_mean_overhead_percentage":
            maintenance_mean_overhead_percentage,

        "maintenance_median_overhead_percentage":
            maintenance_median_overhead_percentage,

        "maintenance_standard_deviation_percentage":
            maintenance_standard_deviation_percentage,

        "maintenance_min_overhead_percentage":
            maintenance_min_overhead_percentage,

        "maintenance_max_overhead_percentage":
            maintenance_max_overhead_percentage,

        "maintenance_mean_cost_class":
            classify_cost_impact(
                maintenance_mean_overhead_percentage
            ),

        "maintenance_median_cost_class":
            classify_cost_impact(
                maintenance_median_overhead_percentage
            ),
    }


# =========================================================
# INTEGRATED ANALYSIS
# =========================================================

def build_integrated_benefit_cost_analysis(
    dataset,
    cost_evidence
):
    """
    Combine historical read-benefit evidence with the
    separately measured M17 cost evidence.

    No artificial per-recommendation cost is assigned.
    """

    read_summary = (
        build_read_benefit_summary(dataset)
    )

    return {
        "read_benefit_evidence":
            read_summary,

        "cost_evidence":
            cost_evidence,

        "cost_benefit_linked":
            False,

        "methodological_note": (
            "Read-benefit observations come from "
            "historical recommendation benchmarks, "
            "while storage and maintenance measurements "
            "come from controlled M17 experiments. "
            "No per-index cost-benefit ratio is assigned "
            "unless both measurements refer to the same "
            "experimental index."
        ),
    }


# =========================================================
# DISPLAY
# =========================================================

def print_benefit_cost_analysis(
    analysis
):
    """
    Print the M17.3 integrated analytical summary.
    """

    read = analysis.get(
        "read_benefit_evidence",
        {}
    )

    cost = analysis.get(
        "cost_evidence",
        {}
    )

    print()
    print("=" * 60)
    print("M17.3 READ BENEFIT VS COST ANALYSIS")
    print("=" * 60)

    print()
    print("READ-BENEFIT EVIDENCE")
    print("-" * 60)

    print(
        "Evaluated observations:",
        read.get(
            "evaluated_observations"
        )
    )

    print(
        "Successful:",
        read.get("successful")
    )

    print(
        "Neutral:",
        read.get("neutral")
    )

    print(
        "Unsuccessful:",
        read.get("unsuccessful")
    )

    print(
        "Average improvement:",
        read.get(
            "average_improvement"
        )
    )

    print(
        "Positive-benefit observations:",
        read.get(
            "positive_benefit_count"
        )
    )

    print(
        "Index-used rate:",
        read.get(
            "index_used_rate"
        )
    )

    print()
    print("COST EVIDENCE")
    print("-" * 60)

    print(
        "Index size:",
        cost.get(
            "index_size_bytes"
        ),
        "bytes"
    )

    print(
        "Table size:",
        cost.get(
            "table_size_bytes"
        ),
        "bytes"
    )

    print(
        "Index/table ratio:",
        cost.get(
            "index_table_ratio_percentage"
        ),
        "%"
    )

    print(
        "Maintenance mean overhead:",
        cost.get(
            "maintenance_mean_overhead_percentage"
        ),
        "%"
    )

    print(
        "Maintenance median overhead:",
        cost.get(
            "maintenance_median_overhead_percentage"
        ),
        "%"
    )

    print()
    print("METHODOLOGICAL NOTE")
    print("-" * 60)

    print(
        analysis.get(
            "methodological_note"
        )
    )

    print("=" * 60)
