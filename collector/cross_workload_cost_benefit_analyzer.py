"""M18.4 cross-workload cost-benefit analysis.

Analytical only.

This module:
- does not access PostgreSQL
- does not create/drop indexes
- does not benchmark queries
- does not modify recommendation scores
- does not modify candidate generation
- does not modify benchmark_results
"""

from statistics import mean, median


def validate_cross_workload_results(results):
    """Validate a collection of linked M18 experiment results."""

    if not isinstance(results, list):
        return False

    if not results:
        return False

    required = {
        "experiment_id",
        "index_name",
        "read_analysis",
        "storage_analysis",
        "write_analysis",
    }

    for result in results:
        if not isinstance(result, dict):
            return False

        if not required.issubset(result):
            return False

    return True


def extract_read_improvements(results):
    """Extract available average read improvements."""

    values = []

    for result in results:
        value = result["read_analysis"].get(
            "average_improvement_percentage"
        )

        if value is not None:
            values.append(float(value))

    return values


def extract_read_savings(results):
    """Extract available average absolute read savings."""

    values = []

    for result in results:
        value = result["read_analysis"].get(
            "absolute_average_savings_ms"
        )

        if value is not None:
            values.append(float(value))

    return values


def extract_storage_ratios(results):
    """Extract index/table storage ratios."""

    values = []

    for result in results:
        value = result["storage_analysis"].get(
            "index_table_ratio_percentage"
        )

        if value is not None:
            values.append(float(value))

    return values


def extract_write_overheads(results):
    """Extract available average write overhead percentages."""

    values = []

    for result in results:
        value = result["write_analysis"].get(
            "average_overhead_percentage"
        )

        if value is not None:
            values.append(float(value))

    return values


def summarize_values(values):
    """Return basic descriptive statistics."""

    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
        }

    return {
        "count": len(values),
        "mean": mean(values),
        "median": median(values),
        "minimum": min(values),
        "maximum": max(values),
    }


def build_cross_workload_summary(results):
    """Build workload-level and overall descriptive analysis."""

    if not validate_cross_workload_results(results):
        raise ValueError("Invalid cross-workload results.")

    workload_rows = []

    for result in results:
        read = result["read_analysis"]
        storage = result["storage_analysis"]
        write = result["write_analysis"]

        workload_rows.append(
            {
                "experiment_id": result["experiment_id"],
                "index_name": result["index_name"],
                "read_improvement_percent": read.get(
                    "average_improvement_percentage"
                ),
                "read_median_improvement_percent": read.get(
                    "median_improvement_percentage"
                ),
                "read_savings_ms": read.get(
                    "absolute_average_savings_ms"
                ),
                "storage_ratio_percent": storage.get(
                    "index_table_ratio_percentage"
                ),
                "write_overhead_percent": write.get(
                    "average_overhead_percentage"
                ),
                "write_median_overhead_percent": write.get(
                    "median_overhead_percentage"
                ),
                "index_used": read.get("index_used"),
                "plan_changed": read.get("plan_changed"),
                "rows_preserved": read.get("rows_preserved"),
            }
        )

    read_improvements = extract_read_improvements(results)
    read_savings = extract_read_savings(results)
    storage_ratios = extract_storage_ratios(results)
    write_overheads = extract_write_overheads(results)

    return {
        "experiment_count": len(results),
        "workloads": workload_rows,
        "aggregate": {
            "read_improvement_percent": summarize_values(
                read_improvements
            ),
            "read_savings_ms": summarize_values(
                read_savings
            ),
            "storage_ratio_percent": summarize_values(
                storage_ratios
            ),
            "write_overhead_percent": summarize_values(
                write_overheads
            ),
        },
    }
