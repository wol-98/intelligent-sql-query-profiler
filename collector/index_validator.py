"""
Index Validation Runner v2
--------------------------
Performs a controlled BEFORE/AFTER experiment
for a single candidate index.

The validator:
1. Benchmarks the query before the index
2. Creates the test index
3. Runs ANALYZE
4. Benchmarks the query after the index
5. Detects whether the index was used
6. Compares performance
7. Checks that result rows are preserved
8. Always removes the experimental index
"""

import json

from config.database import get_connection
from collector.benchmark_runner import benchmark_query


# =========================================================
# INDEX NAME
# =========================================================

def generate_index_name(table_name, column_name):
    """
    Generate a deterministic test index name.
    """

    return f"idx_{table_name}_{column_name}"


# =========================================================
# IDENTIFIER VALIDATION
# =========================================================

def validate_identifier(identifier):
    """
    Validate a PostgreSQL identifier used by this module.
    """

    return (
        identifier
        and identifier.replace("_", "").isalnum()
    )


# =========================================================
# CREATE TEST INDEX
# =========================================================

def create_test_index(
    table_name,
    column_name,
    index_name=None
):
    """
    Create a temporary B-tree index.
    """

    if index_name is None:
        index_name = generate_index_name(
            table_name,
            column_name
        )

    if not validate_identifier(table_name):
        raise ValueError(
            f"Invalid table name: {table_name}"
        )

    if not validate_identifier(column_name):
        raise ValueError(
            f"Invalid column name: {column_name}"
        )

    if not validate_identifier(index_name):
        raise ValueError(
            f"Invalid index name: {index_name}"
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        sql = (
            f"CREATE INDEX {index_name} "
            f"ON {table_name} "
            f"USING BTREE ({column_name});"
        )

        cursor.execute(sql)

        connection.commit()

        return index_name

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# CREATE COMPOSITE TEST INDEX
# =========================================================

def create_composite_test_index(
    table_name,
    columns,
    index_name=None
):
    """
    Create a temporary B-tree index for multiple columns.

    This helper is used by controlled composite-index
    experiments such as M16.2.

    Each column is validated individually before the
    composite SQL expression is constructed.
    """

    if not isinstance(columns, (list, tuple)):
        raise ValueError(
            "columns must be a list or tuple."
        )

    normalized_columns = [
        str(column).strip()
        for column in columns
        if str(column).strip()
    ]

    if len(normalized_columns) < 2:
        raise ValueError(
            "A composite index requires at least 2 columns."
        )

    if not validate_identifier(table_name):
        raise ValueError(
            f"Invalid table name: {table_name}"
        )

    for column in normalized_columns:
        if not validate_identifier(column):
            raise ValueError(
                f"Invalid column name: {column}"
            )

    if index_name is None:
        index_name = generate_index_name(
            table_name,
            "_".join(normalized_columns)
        )

    if not validate_identifier(index_name):
        raise ValueError(
            f"Invalid index name: {index_name}"
        )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        column_expression = ", ".join(
            normalized_columns
        )

        sql = (
            f"CREATE INDEX {index_name} "
            f"ON {table_name} "
            f"USING BTREE ({column_expression});"
        )

        cursor.execute(sql)

        connection.commit()

        return index_name

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ANALYZE TABLE
# =========================================================

def analyze_table(table_name):
    """
    Update PostgreSQL statistics for a table.
    """

    if not validate_identifier(table_name):
        raise ValueError(
            f"Invalid table name: {table_name}"
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            f"ANALYZE {table_name};"
        )

        connection.commit()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# DROP TEST INDEX
# =========================================================

def drop_test_index(index_name):
    """
    Remove the experimental index.
    """

    if not validate_identifier(index_name):
        raise ValueError(
            f"Invalid index name: {index_name}"
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            f"DROP INDEX IF EXISTS {index_name};"
        )

        connection.commit()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# FIND INDEX USAGE
# =========================================================

def find_index_usage(
    plan,
    index_name
):
    """
    Recursively inspect a PostgreSQL execution plan
    and determine whether the specified index was used.

    Returns
    -------
    dict
        Usage information.
    """

    if not isinstance(plan, dict):
        return {
            "used": False,
            "node_type": None,
        }

    current_index = plan.get(
        "Index Name"
    )

    node_type = plan.get(
        "Node Type"
    )

    if current_index == index_name:

        return {
            "used": True,
            "node_type": node_type,
        }

    for child in plan.get(
        "Plans",
        []
    ):

        result = find_index_usage(
            child,
            index_name
        )

        if result["used"]:
            return result

    return {
        "used": False,
        "node_type": None,
    }


# =========================================================
# CALCULATE IMPROVEMENT
# =========================================================

def calculate_improvement(
    before_ms,
    after_ms
):
    """
    Calculate percentage performance improvement.

    Positive = faster
    Negative = slower
    """

    if before_ms <= 0:
        return 0.0

    return (
        (before_ms - after_ms)
        / before_ms
    ) * 100


# =========================================================
# VALIDATE INDEX
# =========================================================

def validate_index(
    query,
    table_name,
    column_name,
    index_name=None,
    iterations=10,
    warmup_runs=2
):
    """
    Perform a controlled BEFORE/AFTER experiment.

    The experimental index is always removed.

    Returns
    -------
    dict
    """

    # -----------------------------------------------------
    # BEFORE
    # -----------------------------------------------------

    print(
        "\nRunning BEFORE benchmark..."
    )

    before = benchmark_query(
        query,
        iterations=iterations,
        warmup_runs=warmup_runs
    )

    before_average = (
        before[
            "average_execution_time_ms"
        ]
    )

    before_median = (
        before[
            "median_execution_time_ms"
        ]
    )

    before_rows = int(
        round(
            before[
                "average_rows"
            ]
        )
    )

    before_plan = (
        before[
            "representative_plan"
        ]
    )

    # -----------------------------------------------------
    # CREATE INDEX
    # -----------------------------------------------------

    created_index = None

    try:

        print(
            "\nCreating experimental index..."
        )

        created_index = create_test_index(
            table_name,
            column_name,
            index_name
        )

        print(
            f"  Created: {created_index}"
        )

        # -------------------------------------------------
        # UPDATE STATISTICS
        # -------------------------------------------------

        print(
            "\nUpdating table statistics..."
        )

        analyze_table(
            table_name
        )

        # -------------------------------------------------
        # AFTER
        # -------------------------------------------------

        print(
            "\nRunning AFTER benchmark..."
        )

        after = benchmark_query(
            query,
            iterations=iterations,
            warmup_runs=warmup_runs
        )

        after_average = (
            after[
                "average_execution_time_ms"
            ]
        )

        after_median = (
            after[
                "median_execution_time_ms"
            ]
        )

        after_rows = int(
            round(
                after[
                    "average_rows"
                ]
            )
        )

        after_plan = (
            after[
                "representative_plan"
            ]
        )

        # -------------------------------------------------
        # INDEX USAGE
        # -------------------------------------------------

        index_usage = find_index_usage(
            after_plan,
            created_index
        )

        # -------------------------------------------------
        # PERFORMANCE
        # -------------------------------------------------

        average_improvement = (
            calculate_improvement(
                before_average,
                after_average
            )
        )

        median_improvement = (
            calculate_improvement(
                before_median,
                after_median
            )
        )

        # -------------------------------------------------
        # RESULT VALIDATION
        # -------------------------------------------------

        rows_preserved = (
            before_rows
            == after_rows
        )

        plan_changed = (
            json.dumps(
                before_plan,
                sort_keys=True
            )
            !=
            json.dumps(
                after_plan,
                sort_keys=True
            )
        )

        return {

            "table_name":
                table_name,

            "column_name":
                column_name,

            "index_name":
                created_index,

            "before":
                before,

            "after":
                after,

            "execution_time_before_ms":
                before_average,

            "execution_time_after_ms":
                after_average,

            "median_before_ms":
                before_median,

            "median_after_ms":
                after_median,

            "improvement_percentage":
                average_improvement,

            "median_improvement_percentage":
                median_improvement,

            "rows_before":
                before_rows,

            "rows_after":
                after_rows,

            "rows_preserved":
                rows_preserved,

            "index_used":
                index_usage["used"],

            "index_node_type":
                index_usage["node_type"],

            "plan_changed":
                plan_changed,

            "before_plan":
                before_plan,

            "after_plan":
                after_plan,
        }

    finally:

        # -------------------------------------------------
        # ALWAYS REMOVE EXPERIMENTAL INDEX
        # -------------------------------------------------

        if created_index:

            print(
                "\nRemoving experimental index..."
            )

            drop_test_index(
                created_index
            )

            print(
                f"  Dropped: {created_index}"
            )


# =========================================================
# PRINT RESULT
# =========================================================

def print_validation_result(
    result
):
    """
    Print a concise validation summary.
    """

    print("\n" + "=" * 70)
    print("INDEX VALIDATION RESULT")
    print("=" * 70)

    print(
        f"Table                 : "
        f"{result['table_name']}"
    )

    print(
        f"Column                : "
        f"{result['column_name']}"
    )

    print(
        f"Test index            : "
        f"{result['index_name']}"
    )

    print("\nPerformance:")

    print(
        f"  Average before      : "
        f"{result['execution_time_before_ms']:.3f} ms"
    )

    print(
        f"  Average after       : "
        f"{result['execution_time_after_ms']:.3f} ms"
    )

    print(
        f"  Average improvement : "
        f"{result['improvement_percentage']:.2f}%"
    )

    print(
        f"  Median before       : "
        f"{result['median_before_ms']:.3f} ms"
    )

    print(
        f"  Median after        : "
        f"{result['median_after_ms']:.3f} ms"
    )

    print(
        f"  Median improvement  : "
        f"{result['median_improvement_percentage']:.2f}%"
    )

    print("\nValidation:")

    print(
        f"  Index used          : "
        f"{result['index_used']}"
    )

    print(
        f"  Index node          : "
        f"{result['index_node_type']}"
    )

    print(
        f"  Plan changed        : "
        f"{result['plan_changed']}"
    )

    print(
        f"  Rows before         : "
        f"{result['rows_before']}"
    )

    print(
        f"  Rows after          : "
        f"{result['rows_after']}"
    )

    print(
        f"  Rows preserved      : "
        f"{result['rows_preserved']}"
    )

    print("=" * 70)
