"""
Composite Index Column-Order Experiment
---------------------------------------
Builds controlled alternative column-order variants for
M15 composite index candidates.

This module is experimental only.

It does not:
    - create database indexes;
    - execute queries;
    - use benchmark results;
    - use recommendation scores;
    - modify recommendation generation.
"""

from collector.index_candidate_generator import (
    normalize_candidate_columns,
)


# =========================================================
# EXPERIMENT CONSTANTS
# =========================================================

MIN_COMPOSITE_COLUMNS = 2
MAX_COMPOSITE_COLUMNS = 3


# =========================================================
# CHECK COMPOSITE ELIGIBILITY
# =========================================================

def is_eligible_composite_candidate(candidate):
    """
    Determine whether a candidate is eligible for the
    controlled column-order experiment.

    Eligibility requires:
        - candidate_type == "composite";
        - 2 to 3 normalized columns;
        - a valid table name;
        - consistent column_count metadata.
    """

    if not isinstance(candidate, dict):
        return False

    if candidate.get("candidate_type") != "composite":
        return False

    if not candidate.get("table_name"):
        return False

    columns = normalize_candidate_columns(
        candidate.get("column_name")
    )

    if not (
        MIN_COMPOSITE_COLUMNS
        <= len(columns)
        <= MAX_COMPOSITE_COLUMNS
    ):
        return False

    column_count = candidate.get("column_count")

    if column_count != len(columns):
        return False

    return True


# =========================================================
# BUILD ALTERNATIVE COLUMN ORDER
# =========================================================

def build_alternative_column_order(column_names):
    """
    Build one controlled alternative ordering.

    The alternative is the reverse of the original
    column ordering.

    No exhaustive permutations are generated.
    """

    columns = normalize_candidate_columns(
        column_names
    )

    if not (
        MIN_COMPOSITE_COLUMNS
        <= len(columns)
        <= MAX_COMPOSITE_COLUMNS
    ):
        return []

    alternative = list(reversed(columns))

    if alternative == columns:
        return []

    return alternative


# =========================================================
# BUILD EXPERIMENT RECORD
# =========================================================

def build_order_experiment(candidate):
    """
    Build an experimental record for an eligible composite
    candidate.

    Returns
    -------
    dict or None
        Experimental record containing the original and
        alternative column ordering.
    """

    if not is_eligible_composite_candidate(candidate):
        return None

    original_columns = normalize_candidate_columns(
        candidate.get("column_name")
    )

    alternative_columns = build_alternative_column_order(
        original_columns
    )

    if not alternative_columns:
        return None

    return {
        "recommendation_id": candidate.get(
            "recommendation_id"
        ),
        "query_id": candidate.get(
            "query_id"
        ),
        "fingerprint": candidate.get(
            "fingerprint"
        ),
        "table_name": candidate.get(
            "table_name"
        ),
        "candidate_type": candidate.get(
            "candidate_type"
        ),
        "source_type": candidate.get(
            "source_type"
        ),
        "column_count": len(original_columns),
        "original_columns": original_columns,
        "alternative_columns": alternative_columns,
        "experiment_type": "column_order",
    }


# =========================================================
# BUILD EXPERIMENT RECORDS
# =========================================================

def build_order_experiments(candidates):
    """
    Build controlled column-order experiments for all
    eligible composite candidates.

    Ineligible candidates are excluded.

    The input candidate list is not modified.
    """

    experiments = []

    for candidate in candidates or []:

        experiment = build_order_experiment(
            candidate
        )

        if experiment is not None:
            experiments.append(
                experiment
            )

    return experiments
