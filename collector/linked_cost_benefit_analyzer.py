"""
M18.3 - Linked Cost-Benefit Analysis

Analytical layer for M18 linked read/storage/write evidence.

This module:
- does not access the database
- does not create or drop indexes
- does not modify recommendation scores
- does not modify benchmark_results
- does not generate candidates
- does not assign recommendation priorities

It analyzes evidence already produced by M18.2.
"""


def validate_linked_evidence(result):
    """Validate the minimum structure required for M18.3 analysis."""
    if not isinstance(result, dict):
        return False

    required = [
        "experiment_id",
        "index_name",
        "read_evidence",
        "storage_evidence",
        "write_evidence",
    ]

    if not all(key in result for key in required):
        return False

    if not isinstance(result["read_evidence"], dict):
        return False

    if not isinstance(result["storage_evidence"], dict):
        return False

    if not isinstance(result["write_evidence"], dict):
        return False

    return True


def calculate_absolute_read_savings(
    before_ms,
    after_ms,
):
    """Calculate absolute read execution-time savings."""
    if before_ms <= 0:
        raise ValueError("Baseline execution time must be greater than zero.")

    return before_ms - after_ms


def calculate_read_improvement(
    before_ms,
    after_ms,
):
    """Calculate read execution-time improvement percentage."""
    if before_ms <= 0:
        raise ValueError("Baseline execution time must be greater than zero.")

    return ((before_ms - after_ms) / before_ms) * 100


def calculate_storage_ratio(
    index_size_bytes,
    table_size_bytes,
):
    """Calculate index size as a percentage of table size."""
    if table_size_bytes <= 0:
        raise ValueError("Table size must be greater than zero.")

    return (index_size_bytes / table_size_bytes) * 100


def calculate_write_overhead(
    baseline_ms,
    indexed_ms,
):
    """Calculate write execution-time overhead percentage."""
    if baseline_ms <= 0:
        raise ValueError("Baseline write time must be greater than zero.")

    return ((indexed_ms - baseline_ms) / baseline_ms) * 100


def classify_effect(value):
    """
    Describe the direction of an observed effect.

    Positive:
        value > 0

    Neutral:
        value == 0

    Negative:
        value < 0

    This is descriptive, not a recommendation judgment.
    """
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def build_read_analysis(read_evidence):
    """Build analytical metrics for read performance."""
    baseline = read_evidence["baseline"]
    indexed = read_evidence["indexed"]

    baseline_avg = baseline["average_execution_time_ms"]
    indexed_avg = indexed["average_execution_time_ms"]

    baseline_median = baseline["median_execution_time_ms"]
    indexed_median = indexed["median_execution_time_ms"]

    return {
        "baseline_average_ms": baseline_avg,
        "indexed_average_ms": indexed_avg,
        "absolute_average_savings_ms": calculate_absolute_read_savings(
            baseline_avg,
            indexed_avg,
        ),
        "average_improvement_percentage": calculate_read_improvement(
            baseline_avg,
            indexed_avg,
        ),
        "baseline_median_ms": baseline_median,
        "indexed_median_ms": indexed_median,
        "absolute_median_savings_ms": calculate_absolute_read_savings(
            baseline_median,
            indexed_median,
        ),
        "median_improvement_percentage": calculate_read_improvement(
            baseline_median,
            indexed_median,
        ),
        "rows_preserved": read_evidence["rows_preserved"],
        "index_used": read_evidence["index_used"],
        "plan_changed": read_evidence["plan_changed"],
        "baseline_plan_node": baseline["representative_plan"]["Node Type"],
        "indexed_plan_node": indexed["representative_plan"]["Node Type"],
    }


def build_storage_analysis(storage_evidence):
    """Build analytical metrics for index storage cost."""
    index_size = storage_evidence["index_size_bytes"]
    table_size = storage_evidence["table_size_bytes"]

    return {
        "index_size_bytes": index_size,
        "index_size_pretty": storage_evidence["index_size_pretty"],
        "table_size_bytes": table_size,
        "table_size_pretty": storage_evidence["table_size_pretty"],
        "index_table_ratio_percentage": calculate_storage_ratio(
            index_size,
            table_size,
        ),
        "index_type": storage_evidence["index_metadata"]["index_type"],
        "column_count": storage_evidence["index_metadata"]["column_count"],
        "columns": storage_evidence["index_metadata"]["columns"],
        "is_valid": storage_evidence["index_metadata"]["is_valid"],
    }


def build_write_analysis(write_evidence):
    """Build analytical metrics for write-maintenance cost."""
    baseline = write_evidence["baseline"]
    indexed = write_evidence["indexed"]

    baseline_avg = baseline["average_execution_time_ms"]
    indexed_avg = indexed["average_execution_time_ms"]

    baseline_median = baseline["median_execution_time_ms"]
    indexed_median = indexed["median_execution_time_ms"]

    return {
        "baseline_average_ms": baseline_avg,
        "indexed_average_ms": indexed_avg,
        "average_absolute_overhead_ms": indexed_avg - baseline_avg,
        "average_overhead_percentage": calculate_write_overhead(
            baseline_avg,
            indexed_avg,
        ),
        "baseline_median_ms": baseline_median,
        "indexed_median_ms": indexed_median,
        "median_absolute_overhead_ms": indexed_median - baseline_median,
        "median_overhead_percentage": calculate_write_overhead(
            baseline_median,
            indexed_median,
        ),
        "baseline_standard_deviation_ms": baseline["standard_deviation_ms"],
        "indexed_standard_deviation_ms": indexed["standard_deviation_ms"],
        "batch_size": write_evidence["batch_size"],
    }


def build_linked_cost_benefit_analysis(result):
    """
    Build the complete M18.3 analytical result.

    All measurements remain explicitly linked to the same
    experiment and index.
    """
    if not validate_linked_evidence(result):
        raise ValueError("Invalid linked M18 evidence.")

    read = build_read_analysis(result["read_evidence"])
    storage = build_storage_analysis(result["storage_evidence"])
    write = build_write_analysis(result["write_evidence"])

    return {
        "experiment_id": result["experiment_id"],
        "index_name": result["index_name"],
        "table_name": result["table_name"],
        "columns": result["columns"],
        "index_type": result["index_type"],
        "evidence_linked": result.get("evidence_linked", False),
        "read_analysis": read,
        "storage_analysis": storage,
        "write_analysis": write,
    }
