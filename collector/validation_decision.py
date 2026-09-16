"""
Validation Decision Engine
--------------------------
Converts benchmark evidence into an explicit validation decision.

Decision rules
--------------
UNSAFE:
    Rows are not preserved.

UNSUCCESSFUL:
    Performance becomes slower.

SUCCESSFUL:
    Rows are preserved,
    index is used,
    and performance improves by at least 5%.

NEUTRAL:
    Rows are preserved but the recommendation does not
    satisfy the successful criterion.
"""


SUCCESS_THRESHOLD = 5.0


def choose_improvement(result):
    """
    Prefer median improvement when available.

    Existing benchmark records may not contain median
    improvement because the original schema did not store it.
    In that case, use average improvement.
    """

    median = result.get(
        "median_improvement_percentage"
    )

    if median is not None:
        return float(median)

    average = result.get(
        "improvement_percentage"
    )

    if average is not None:
        return float(average)

    return 0.0


def evaluate_validation(result):
    """
    Evaluate one benchmark result.

    Returns
    -------
    dict
        status, improvement_metric, and explanation.
    """

    rows_preserved = result.get(
        "rows_preserved"
    )

    index_used = result.get(
        "index_used"
    )

    improvement = choose_improvement(
        result
    )

    metric_name = (
        "median"
        if result.get(
            "median_improvement_percentage"
        ) is not None
        else "average"
    )

    # -----------------------------------------------------
    # 1. Correctness
    # -----------------------------------------------------

    if rows_preserved is False:

        return {
            "status": "UNSAFE",
            "improvement_metric": metric_name,
            "improvement_percentage": improvement,
            "reason": (
                "Result rows changed after applying the "
                "experimental index."
            ),
        }

    # -----------------------------------------------------
    # 2. Negative performance
    # -----------------------------------------------------

    if improvement < 0:

        return {
            "status": "UNSUCCESSFUL",
            "improvement_metric": metric_name,
            "improvement_percentage": improvement,
            "reason": (
                f"The {metric_name} execution time became "
                f"slower by {abs(improvement):.2f}%."
            ),
        }

    # -----------------------------------------------------
    # 3. Successful validation
    # -----------------------------------------------------

    if (
        rows_preserved is True
        and index_used is True
        and improvement >= SUCCESS_THRESHOLD
    ):

        return {
            "status": "SUCCESSFUL",
            "improvement_metric": metric_name,
            "improvement_percentage": improvement,
            "reason": (
                f"The index was used and the {metric_name} "
                f"execution time improved by "
                f"{improvement:.2f}%, meeting the "
                f"{SUCCESS_THRESHOLD:.0f}% threshold."
            ),
        }

    # -----------------------------------------------------
    # 4. Neutral
    # -----------------------------------------------------

    if index_used is not True:

        return {
            "status": "NEUTRAL",
            "improvement_metric": metric_name,
            "improvement_percentage": improvement,
            "reason": (
                f"The {metric_name} execution time changed by "
                f"{improvement:.2f}%, but the experimental "
                f"index was not used by the execution plan."
            ),
        }

    return {
        "status": "NEUTRAL",
        "improvement_metric": metric_name,
        "improvement_percentage": improvement,
        "reason": (
            f"The index was used and results were preserved, "
            f"but the {metric_name} improvement of "
            f"{improvement:.2f}% did not meet the "
            f"{SUCCESS_THRESHOLD:.0f}% success threshold."
        ),
    }


def print_decision(result):
    """
    Print one validation decision.
    """

    decision = evaluate_validation(
        result
    )

    print("\n" + "=" * 75)
    print("VALIDATION DECISION")
    print("=" * 75)

    print(
        f"Status              : "
        f"{decision['status']}"
    )

    print(
        f"Improvement metric  : "
        f"{decision['improvement_metric']}"
    )

    print(
        f"Improvement         : "
        f"{decision['improvement_percentage']:.2f}%"
    )

    print(
        f"Reason              : "
        f"{decision['reason']}"
    )

    print("=" * 75)

    return decision
