"""
M18.2 - Linked Read/Write Benchmark

Performs a controlled read/write experiment in which:

1. A controlled experiment table is created from a source table.
2. Baseline read performance is measured.
3. The same experimental index defined by M18.1 is created.
4. PostgreSQL statistics are refreshed.
5. Indexed read performance is measured.
6. Index and table storage are measured.
7. Baseline write-maintenance cost is measured.
8. Indexed write-maintenance cost is measured.
9. Read and write effects are linked to the SAME experimental index.
10. All experimental database objects are removed.

This module is experimental only.

It does NOT:

- modify recommendation scores;
- generate candidates;
- modify recommendation priorities;
- write benchmark_results;
- modify production indexes.

The experiment uses a persistent controlled table rather than a
PostgreSQL TEMP table because the existing benchmark and metadata
helpers open independent database connections.

Write measurements use an explicit batch marker rather than CTID
so inserted rows can be removed deterministically.
"""

import statistics
import time
import uuid

from config.database import get_connection

from collector.benchmark_runner import benchmark_query
from collector.index_validator import (
    validate_identifier,
    create_test_index,
    create_composite_test_index,
    analyze_table,
    drop_test_index,
    find_index_usage,
    calculate_improvement,
)
from collector.index_cost_analyzer import (
    get_table_size,
    get_index_size,
    get_index_metadata,
)
from collector.linked_cost_benefit_experiment import (
    validate_experiment_definition,
    render_read_query,
    build_linked_result,
)


# =========================================================
# CONFIGURATION
# =========================================================

DEFAULT_WRITE_BATCH_SIZE = 1000


# =========================================================
# IDENTIFIERS
# =========================================================

def validate_experiment_table_name(table_name):
    """
    Validate a controlled experiment table name.
    """

    if not validate_identifier(table_name):
        raise ValueError(
            f"Invalid experiment table name: {table_name}"
        )

    return True


def build_experiment_table_name(
    experiment_id,
    source_table,
):
    """
    Build a deterministic controlled experiment table name.

    The generated name is based on the experiment identifier
    and source table.

    PostgreSQL identifiers are limited to 63 characters, so
    the result is truncated safely.
    """

    if not isinstance(experiment_id, str):
        raise ValueError(
            "experiment_id must be a string."
        )

    if not isinstance(source_table, str):
        raise ValueError(
            "source_table must be a string."
        )

    if not validate_identifier(source_table):
        raise ValueError(
            f"Invalid source table: {source_table}"
        )

    normalized_id = (
        experiment_id
        .strip()
        .lower()
        .replace("-", "_")
    )

    if not normalized_id:
        raise ValueError(
            "experiment_id cannot be empty."
        )

    candidate = (
        f"m18_{normalized_id}_{source_table}_test"
    )

    # PostgreSQL identifier maximum length.
    candidate = candidate[:63]

    if not validate_identifier(candidate):
        raise ValueError(
            f"Invalid generated experiment table: {candidate}"
        )

    return candidate


# =========================================================
# CONTROLLED TABLE CREATION
# =========================================================

def drop_experiment_table(
    table_name,
):
    """
    Remove a controlled experiment table if it exists.
    """

    validate_experiment_table_name(
        table_name
    )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            f"DROP TABLE IF EXISTS {table_name};"
        )

        connection.commit()

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def create_experiment_table(
    source_table,
    experiment_table,
):
    """
    Create a controlled experiment table containing a copy
    of the source table's data.

    The table deliberately does not copy source indexes or
    constraints through the CREATE TABLE AS operation.

    A private M18 batch-marker column is added for deterministic
    write cleanup.
    """

    if not validate_identifier(source_table):
        raise ValueError(
            f"Invalid source table: {source_table}"
        )

    validate_experiment_table_name(
        experiment_table
    )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Ensure stale experimental objects do not interfere.
        cursor.execute(
            f"DROP TABLE IF EXISTS {experiment_table};"
        )

        cursor.execute(
            f"""
            CREATE TABLE {experiment_table}
            AS TABLE {source_table};
            """
        )

        cursor.execute(
            f"""
            ALTER TABLE {experiment_table}
            ADD COLUMN m18_batch_id TEXT;
            """
        )

        connection.commit()

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# WRITE COLUMN DISCOVERY
# =========================================================

def get_table_columns(
    table_name,
):
    """
    Return ordinary source columns for a table.

    The M18 batch marker is excluded.
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
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = %s
              AND column_name <> 'm18_batch_id'
            ORDER BY ordinal_position
            """,
            (table_name,),
        )

        rows = cursor.fetchall()

        columns = [
            row[0]
            for row in rows
        ]

        if not columns:
            raise ValueError(
                f"No writable columns found for table: "
                f"{table_name}"
            )

        for column in columns:
            if not validate_identifier(column):
                raise ValueError(
                    f"Invalid column name: {column}"
                )

        return columns

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# WRITE BATCH
# =========================================================

def insert_write_batch(
    source_table,
    experiment_table,
    batch_id,
    batch_size,
):
    """
    Insert one controlled write batch into the experiment table.

    The source rows are copied from the original source table,
    ensuring that every measured write starts from the same
    source distribution.

    Returns the elapsed INSERT+COMMIT time in milliseconds.
    """

    if not validate_identifier(source_table):
        raise ValueError(
            f"Invalid source table: {source_table}"
        )

    validate_experiment_table_name(
        experiment_table
    )

    if not isinstance(batch_size, int):
        raise ValueError(
            "batch_size must be an integer."
        )

    if batch_size <= 0:
        raise ValueError(
            "batch_size must be greater than 0."
        )

    columns = get_table_columns(
        source_table
    )

    column_list = ", ".join(
        columns + ["m18_batch_id"]
    )

    source_column_list = ", ".join(
        columns
    )

    connection = None
    cursor = None

    start = time.perf_counter()

    try:
        connection = get_connection()
        cursor = connection.cursor()

        sql = f"""
            INSERT INTO {experiment_table}
            ({column_list})
            SELECT
                {source_column_list},
                %s
            FROM {source_table}
            LIMIT %s;
        """

        cursor.execute(
            sql,
            (
                batch_id,
                batch_size,
            ),
        )

        connection.commit()

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000.0

        return elapsed_ms

    except Exception:
        if connection:
            connection.rollback()

        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def cleanup_write_batch(
    experiment_table,
    batch_id,
):
    """
    Remove one previously inserted write batch.
    """

    validate_experiment_table_name(
        experiment_table
    )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            f"""
            DELETE FROM {experiment_table}
            WHERE m18_batch_id = %s;
            """,
            (batch_id,),
        )

        connection.commit()

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# WRITE BENCHMARK
# =========================================================

def benchmark_write_workload(
    source_table,
    experiment_table,
    iterations,
    warmup_runs,
    batch_size=DEFAULT_WRITE_BATCH_SIZE,
):
    """
    Benchmark controlled INSERT workloads.

    Every measured batch is removed before the next measurement,
    ensuring that baseline and indexed measurements operate from
    the same logical table state.

    Returns a dictionary compatible with M18 linked evidence.
    """

    if iterations <= 0:
        raise ValueError(
            "iterations must be greater than 0."
        )

    if warmup_runs < 0:
        raise ValueError(
            "warmup_runs cannot be negative."
        )

    if batch_size <= 0:
        raise ValueError(
            "batch_size must be greater than 0."
        )

    # -----------------------------------------------------
    # Warmups
    # -----------------------------------------------------

    for _ in range(warmup_runs):

        batch_id = uuid.uuid4().hex

        insert_write_batch(
            source_table,
            experiment_table,
            batch_id,
            batch_size,
        )

        cleanup_write_batch(
            experiment_table,
            batch_id,
        )

    # -----------------------------------------------------
    # Measured runs
    # -----------------------------------------------------

    timings = []

    for _ in range(iterations):

        batch_id = uuid.uuid4().hex

        try:
            elapsed_ms = insert_write_batch(
                source_table,
                experiment_table,
                batch_id,
                batch_size,
            )

            timings.append(
                elapsed_ms
            )

        finally:
            cleanup_write_batch(
                experiment_table,
                batch_id,
            )

    average_ms = statistics.mean(
        timings
    )

    median_ms = statistics.median(
        timings
    )

    minimum_ms = min(timings)
    maximum_ms = max(timings)

    standard_deviation_ms = (
        statistics.stdev(timings)
        if len(timings) > 1
        else 0.0
    )

    return {
        "iterations": iterations,
        "warmup_runs": warmup_runs,
        "batch_size": batch_size,
        "execution_times_ms": timings,
        "average_execution_time_ms":
            average_ms,
        "median_execution_time_ms":
            median_ms,
        "minimum_execution_time_ms":
            minimum_ms,
        "maximum_execution_time_ms":
            maximum_ms,
        "standard_deviation_ms":
            standard_deviation_ms,
    }


# =========================================================
# WRITE OVERHEAD
# =========================================================

def calculate_write_overhead(
    baseline_ms,
    indexed_ms,
):
    """
    Calculate percentage write-maintenance overhead.

    Positive = indexed workload is slower.
    Negative = indexed workload is faster.
    """

    if baseline_ms <= 0:
        return 0.0

    return (
        (indexed_ms - baseline_ms)
        / baseline_ms
    ) * 100.0


# =========================================================
# READ EVIDENCE
# =========================================================

def build_read_evidence(
    experiment,
    baseline,
    indexed,
    index_name,
):
    """
    Build linked read-performance evidence.
    """

    baseline_average = (
        baseline[
            "average_execution_time_ms"
        ]
    )

    indexed_average = (
        indexed[
            "average_execution_time_ms"
        ]
    )

    baseline_median = (
        baseline[
            "median_execution_time_ms"
        ]
    )

    indexed_median = (
        indexed[
            "median_execution_time_ms"
        ]
    )

    baseline_rows = int(
        round(
            baseline["average_rows"]
        )
    )

    indexed_rows = int(
        round(
            indexed["average_rows"]
        )
    )

    indexed_plan = indexed[
        "representative_plan"
    ]

    usage = find_index_usage(
        indexed_plan,
        index_name,
    )

    plan_changed = (
        baseline["representative_plan"]
        != indexed["representative_plan"]
    )

    return {
        "experiment_id":
            experiment["experiment_id"],

        "index_name":
            index_name,

        "query":
            experiment["read_query"],

        "baseline":
            baseline,

        "indexed":
            indexed,

        "execution_time_before_ms":
            baseline_average,

        "execution_time_after_ms":
            indexed_average,

        "median_before_ms":
            baseline_median,

        "median_after_ms":
            indexed_median,

        "improvement_percentage":
            calculate_improvement(
                baseline_average,
                indexed_average,
            ),

        "median_improvement_percentage":
            calculate_improvement(
                baseline_median,
                indexed_median,
            ),

        "rows_before":
            baseline_rows,

        "rows_after":
            indexed_rows,

        "rows_preserved":
            baseline_rows == indexed_rows,

        "index_used":
            usage["used"],

        "index_node_type":
            usage["node_type"],

        "plan_changed":
            plan_changed,
    }


# =========================================================
# STORAGE EVIDENCE
# =========================================================

def build_storage_evidence(
    experiment,
    experiment_table,
    index_name,
):
    """
    Collect storage evidence for the same experimental index
    used by the read and write measurements.
    """

    index_metadata = get_index_metadata(
        index_name
    )

    if index_metadata is None:
        raise RuntimeError(
            f"Index metadata not found: {index_name}"
        )

    index_size = get_index_size(
        index_name
    )

    table_size = get_table_size(
        experiment_table
    )

    table_size_bytes = table_size[
        "size_bytes"
    ]

    index_size_bytes = index_size[
        "size_bytes"
    ]

    if table_size_bytes > 0:
        ratio = (
            index_size_bytes
            / table_size_bytes
        ) * 100.0
    else:
        ratio = 0.0

    return {
        "experiment_id":
            experiment["experiment_id"],

        "index_name":
            index_name,

        "table_name":
            experiment_table,

        "index_size_bytes":
            index_size_bytes,

        "index_size_pretty":
            index_size["size_pretty"],

        "table_size_bytes":
            table_size_bytes,

        "table_size_pretty":
            table_size["size_pretty"],

        "index_table_ratio_percent":
            ratio,

        "index_metadata":
            index_metadata,
    }


# =========================================================
# WRITE EVIDENCE
# =========================================================

def build_write_evidence(
    experiment,
    baseline,
    indexed,
    index_name,
):
    """
    Build linked write-maintenance evidence.
    """

    average_overhead = (
        calculate_write_overhead(
            baseline[
                "average_execution_time_ms"
            ],
            indexed[
                "average_execution_time_ms"
            ],
        )
    )

    median_overhead = (
        calculate_write_overhead(
            baseline[
                "median_execution_time_ms"
            ],
            indexed[
                "median_execution_time_ms"
            ],
        )
    )

    return {
        "experiment_id":
            experiment["experiment_id"],

        "index_name":
            index_name,

        "baseline":
            baseline,

        "indexed":
            indexed,

        "average_write_overhead_percentage":
            average_overhead,

        "median_write_overhead_percentage":
            median_overhead,

        "batch_size":
            baseline["batch_size"],
    }


# =========================================================
# FULL LINKED EXPERIMENT
# =========================================================

def run_linked_cost_benefit_experiment(
    experiment,
    source_table=None,
    experiment_table=None,
    write_batch_size=DEFAULT_WRITE_BATCH_SIZE,
):
    """
    Run a complete M18.2 linked cost-benefit experiment.

    The same experimental index is used for:

    - indexed read evidence;
    - storage evidence;
    - indexed write evidence.

    All experimental objects are removed in the final cleanup.

    Parameters
    ----------
    experiment : dict
        M18.1 experiment definition.

    source_table : str | None
        Source table used to create the controlled experiment table.
        Defaults to experiment["table_name"].

    experiment_table : str | None
        Controlled experiment table.
        If omitted, a deterministic M18 name is generated.

    write_batch_size : int
        Number of source rows inserted during each write measurement.

    Returns
    -------
    dict
        Fully linked M18 experiment result.
    """

    if not validate_experiment_definition(
        experiment
    ):
        raise ValueError(
            "Invalid experiment definition."
        )

    if source_table is None:
        source_table = experiment[
            "table_name"
        ]

    if not validate_identifier(
        source_table
    ):
        raise ValueError(
            f"Invalid source table: {source_table}"
        )

    if experiment_table is None:
        experiment_table = (
            build_experiment_table_name(
                experiment["experiment_id"],
                source_table,
            )
        )

    validate_experiment_table_name(
        experiment_table
    )

    if not isinstance(
        write_batch_size,
        int,
    ) or write_batch_size <= 0:
        raise ValueError(
            "write_batch_size must be "
            "a positive integer."
        )

    index_name = experiment[
        "index_name"
    ]

    created_index = False

    try:
        # -------------------------------------------------
        # CONTROLLED TABLE
        # -------------------------------------------------

        create_experiment_table(
            source_table,
            experiment_table,
        )

        analyze_table(
            experiment_table
        )

        # -------------------------------------------------
        # READ QUERY
        # -------------------------------------------------

        read_query = render_read_query(
            experiment,
            experiment_table,
        )

        # -------------------------------------------------
        # BASELINE READ
        # -------------------------------------------------

        print(
            "\n[M18.2] Running baseline READ..."
        )

        baseline_read = benchmark_query(
            read_query,
            iterations=experiment[
                "read_iterations"
            ],
            warmup_runs=experiment[
                "read_warmup_runs"
            ],
        )

        # -------------------------------------------------
        # CREATE EXPERIMENTAL INDEX
        # -------------------------------------------------

        print(
            "\n[M18.2] Creating experimental index..."
        )

        if len(experiment["columns"]) == 1:

            create_test_index(
                experiment_table,
                experiment["columns"][0],
                index_name,
            )

        else:

            create_composite_test_index(
                experiment_table,
                experiment["columns"],
                index_name,
            )

        created_index = True

        # -------------------------------------------------
        # UPDATE STATISTICS
        # -------------------------------------------------

        analyze_table(
            experiment_table
        )

        # -------------------------------------------------
        # INDEXED READ
        # -------------------------------------------------

        print(
            "\n[M18.2] Running indexed READ..."
        )

        indexed_read = benchmark_query(
            read_query,
            iterations=experiment[
                "read_iterations"
            ],
            warmup_runs=experiment[
                "read_warmup_runs"
            ],
        )

        # -------------------------------------------------
        # STORAGE
        # -------------------------------------------------

        print(
            "\n[M18.2] Measuring index storage..."
        )

        storage_evidence = (
            build_storage_evidence(
                experiment,
                experiment_table,
                index_name,
            )
        )

        # -------------------------------------------------
        # READ EVIDENCE
        # -------------------------------------------------

        read_evidence = build_read_evidence(
            experiment,
            baseline_read,
            indexed_read,
            index_name,
        )

        # -------------------------------------------------
        # BASELINE WRITE
        # -------------------------------------------------

        print(
            "\n[M18.2] Running baseline WRITE..."
        )

        # The experimental index currently exists, so it must
        # be removed temporarily for a true no-index baseline.
        drop_test_index(
            index_name
        )

        created_index = False

        analyze_table(
            experiment_table
        )

        baseline_write = benchmark_write_workload(
            source_table,
            experiment_table,
            iterations=experiment[
                "write_iterations"
            ],
            warmup_runs=experiment[
                "write_warmup_runs"
            ],
            batch_size=write_batch_size,
        )

        # -------------------------------------------------
        # RECREATE EXPERIMENTAL INDEX
        # -------------------------------------------------

        print(
            "\n[M18.2] Recreating experimental index "
            "for indexed WRITE..."
        )

        if len(experiment["columns"]) == 1:

            create_test_index(
                experiment_table,
                experiment["columns"][0],
                index_name,
            )

        else:

            create_composite_test_index(
                experiment_table,
                experiment["columns"],
                index_name,
            )

        created_index = True

        analyze_table(
            experiment_table
        )

        # -------------------------------------------------
        # INDEXED WRITE
        # -------------------------------------------------

        print(
            "\n[M18.2] Running indexed WRITE..."
        )

        indexed_write = benchmark_write_workload(
            source_table,
            experiment_table,
            iterations=experiment[
                "write_iterations"
            ],
            warmup_runs=experiment[
                "write_warmup_runs"
            ],
            batch_size=write_batch_size,
        )

        # -------------------------------------------------
        # WRITE EVIDENCE
        # -------------------------------------------------

        write_evidence = build_write_evidence(
            experiment,
            baseline_write,
            indexed_write,
            index_name,
        )

        # -------------------------------------------------
        # LINK EVERYTHING
        # -------------------------------------------------

        result = build_linked_result(
            experiment,
            read_evidence,
            storage_evidence,
            write_evidence,
        )

        result["source_table"] = source_table
        result["experiment_table"] = experiment_table
        result["write_batch_size"] = write_batch_size

        return result

    finally:

        # -------------------------------------------------
        # ALWAYS REMOVE EXPERIMENTAL INDEX
        # -------------------------------------------------

        try:
            drop_test_index(
                index_name
            )
        except Exception:
            pass

        # -------------------------------------------------
        # ALWAYS REMOVE EXPERIMENT TABLE
        # -------------------------------------------------

        try:
            drop_experiment_table(
                experiment_table
            )
        except Exception:
            pass


# =========================================================
# RESULT SUMMARY
# =========================================================

def print_linked_result(
    result,
):
    """
    Print a concise M18.2 experiment summary.
    """

    read = result[
        "read_evidence"
    ]

    storage = result[
        "storage_evidence"
    ]

    write = result[
        "write_evidence"
    ]

    print("\n" + "=" * 72)
    print("M18.2 LINKED COST-BENEFIT EXPERIMENT")
    print("=" * 72)

    print(
        f"Experiment ID       : "
        f"{result['experiment_id']}"
    )

    print(
        f"Index               : "
        f"{result['index_name']}"
    )

    print(
        f"Source table        : "
        f"{result['source_table']}"
    )

    print(
        f"Experiment table    : "
        f"{result['experiment_table']}"
    )

    print("\nREAD PERFORMANCE")

    print(
        f"  Baseline average  : "
        f"{read['execution_time_before_ms']:.3f} ms"
    )

    print(
        f"  Indexed average   : "
        f"{read['execution_time_after_ms']:.3f} ms"
    )

    print(
        f"  Improvement       : "
        f"{read['improvement_percentage']:.2f}%"
    )

    print(
        f"  Median improvement: "
        f"{read['median_improvement_percentage']:.2f}%"
    )

    print(
        f"  Index used        : "
        f"{read['index_used']}"
    )

    print(
        f"  Plan changed      : "
        f"{read['plan_changed']}"
    )

    print(
        f"  Rows preserved    : "
        f"{read['rows_preserved']}"
    )

    print("\nSTORAGE COST")

    print(
        f"  Index size        : "
        f"{storage['index_size_pretty']}"
    )

    print(
        f"  Table size        : "
        f"{storage['table_size_pretty']}"
    )

    print(
        f"  Index/table ratio : "
        f"{storage['index_table_ratio_percent']:.2f}%"
    )

    print("\nWRITE MAINTENANCE")

    print(
        f"  Baseline average  : "
        f"{write['baseline']['average_execution_time_ms']:.3f} ms"
    )

    print(
        f"  Indexed average   : "
        f"{write['indexed']['average_execution_time_ms']:.3f} ms"
    )

    print(
        f"  Mean overhead     : "
        f"{write['average_write_overhead_percentage']:.2f}%"
    )

    print(
        f"  Median overhead   : "
        f"{write['median_write_overhead_percentage']:.2f}%"
    )

    print(
        f"  Batch size        : "
        f"{write['batch_size']}"
    )

    print("\nLINKAGE")

    print(
        f"  Evidence linked   : "
        f"{result['evidence_linked']}"
    )

    print("=" * 72)
