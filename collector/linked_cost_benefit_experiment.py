"""
M18.1 - Linked Cost-Benefit Experiment Design

Defines the controlled experiment contract used by M18.2.

The same experimental index must be associated with:

- read-performance evidence;
- storage-cost evidence;
- write-maintenance evidence.

The experiment is performed against a controlled experiment table.
The read query therefore uses a {table} placeholder so that M18.2
can render the same logical query against that controlled table.

This module is design/validation only.

It does NOT:

- create tables;
- create indexes;
- drop indexes;
- execute queries;
- modify recommendation scores;
- generate candidates;
- modify recommendation priorities;
- write benchmark_results.
"""


from collector.index_validator import validate_identifier


# =========================================================
# EXPERIMENT CONFIGURATION
# =========================================================

MIN_ITERATIONS = 1

DEFAULT_READ_ITERATIONS = 10
DEFAULT_READ_WARMUP_RUNS = 2

DEFAULT_WRITE_ITERATIONS = 5
DEFAULT_WRITE_WARMUP_RUNS = 2


# =========================================================
# VALIDATION
# =========================================================

def validate_experiment_definition(experiment):
    """
    Validate the structure of a linked cost-benefit
    experiment definition.

    The function validates the experimental contract only.

    It does not:

    - check whether database objects exist;
    - execute SQL;
    - create or drop database objects;
    - validate query semantics against the database.
    """

    if not isinstance(experiment, dict):
        return False

    required_fields = [
        "experiment_id",
        "index_name",
        "table_name",
        "columns",
        "read_query",
    ]

    for field in required_fields:
        if not experiment.get(field):
            return False

    # -----------------------------------------------------
    # Identity fields
    # -----------------------------------------------------

    if not isinstance(experiment["experiment_id"], str):
        return False

    if not isinstance(experiment["index_name"], str):
        return False

    if not isinstance(experiment["table_name"], str):
        return False

    # -----------------------------------------------------
    # Index columns
    # -----------------------------------------------------

    if not isinstance(
        experiment["columns"],
        (list, tuple),
    ):
        return False

    if not experiment["columns"]:
        return False

    for column in experiment["columns"]:
        if not isinstance(column, str):
            return False

        if not column.strip():
            return False

    # -----------------------------------------------------
    # Read query
    # -----------------------------------------------------

    if not isinstance(
        experiment["read_query"],
        str,
    ):
        return False

    if not experiment["read_query"].strip():
        return False

    # The read query must be renderable against the
    # controlled experiment table.
    if "{table}" not in experiment["read_query"]:
        return False

    # -----------------------------------------------------
    # Optional write table
    # -----------------------------------------------------

    write_table = experiment.get(
        "write_table",
        experiment["table_name"],
    )

    if not isinstance(write_table, str):
        return False

    if not write_table.strip():
        return False

    # -----------------------------------------------------
    # Iteration configuration
    # -----------------------------------------------------

    read_iterations = experiment.get(
        "read_iterations",
        DEFAULT_READ_ITERATIONS,
    )

    read_warmups = experiment.get(
        "read_warmup_runs",
        DEFAULT_READ_WARMUP_RUNS,
    )

    write_iterations = experiment.get(
        "write_iterations",
        DEFAULT_WRITE_ITERATIONS,
    )

    write_warmups = experiment.get(
        "write_warmup_runs",
        DEFAULT_WRITE_WARMUP_RUNS,
    )

    for value in (
        read_iterations,
        read_warmups,
        write_iterations,
        write_warmups,
    ):
        if not isinstance(value, int):
            return False

        if value < 0:
            return False

    if read_iterations < MIN_ITERATIONS:
        return False

    if write_iterations < MIN_ITERATIONS:
        return False

    return True


# =========================================================
# EXPERIMENT DEFINITION
# =========================================================

def build_experiment_definition(
    experiment_id,
    index_name,
    table_name,
    columns,
    read_query,
    write_table=None,
    read_iterations=DEFAULT_READ_ITERATIONS,
    read_warmup_runs=DEFAULT_READ_WARMUP_RUNS,
    write_iterations=DEFAULT_WRITE_ITERATIONS,
    write_warmup_runs=DEFAULT_WRITE_WARMUP_RUNS,
    index_type="BTREE",
    notes=None,
):
    """
    Build a linked cost-benefit experiment definition.

    Parameters
    ----------
    experiment_id : str
        Unique identifier for the complete experiment.

    index_name : str
        Name of the experimental index.

    table_name : str
        Logical source/experiment table name associated with
        the experiment definition.

    columns : list[str] | tuple[str]
        Columns belonging to the experimental index.

    read_query : str
        Logical read query.

        IMPORTANT:
        The query must contain the literal {table} placeholder.

        Example:
            SELECT *
            FROM {table}
            WHERE customer_id = 845;

    write_table : str | None
        Table used for the write-maintenance measurement.
        Defaults to table_name.

    read_iterations : int
        Number of measured read iterations.

    read_warmup_runs : int
        Number of read warmup executions.

    write_iterations : int
        Number of measured write iterations.

    write_warmup_runs : int
        Number of write warmup executions.

    index_type : str
        Experimental index type. Defaults to BTREE.

    notes : str | None
        Optional experiment notes.

    Returns
    -------
    dict
        Validated experiment definition.

    Notes
    -----
    The definition does not create any database objects.

    M18.2 is responsible for rendering the query against the
    controlled experiment table and performing the actual
    measurements.
    """

    experiment = {
        "experiment_id": experiment_id,
        "index_name": index_name,
        "table_name": table_name,
        "columns": list(columns),
        "index_type": index_type,
        "read_query": read_query,
        "write_table": (
            write_table
            if write_table is not None
            else table_name
        ),
        "read_iterations": read_iterations,
        "read_warmup_runs": read_warmup_runs,
        "write_iterations": write_iterations,
        "write_warmup_runs": write_warmup_runs,
        "notes": notes,
    }

    if not validate_experiment_definition(
        experiment
    ):
        raise ValueError(
            "Invalid linked cost-benefit "
            "experiment definition."
        )

    return experiment


# =========================================================
# READ QUERY RENDERING
# =========================================================

def render_read_query(
    experiment,
    table_name,
):
    """
    Render the experiment read query against a controlled
    experiment table.

    The experiment definition must contain the {table}
    placeholder.

    Parameters
    ----------
    experiment : dict
        Valid M18.1 experiment definition.

    table_name : str
        Controlled experiment table against which the query
        should be executed.

    Returns
    -------
    str
        Rendered SQL query.

    Raises
    ------
    ValueError
        If the experiment definition is invalid, the table
        identifier is invalid, or the required placeholder
        is missing.

    Notes
    -----
    This function does not execute SQL.

    Identifier validation is performed before interpolation
    so that the table name cannot be inserted as an
    unrestricted SQL fragment.
    """

    if not validate_experiment_definition(
        experiment
    ):
        raise ValueError(
            "Invalid experiment definition."
        )

    if not isinstance(table_name, str):
        raise ValueError(
            "Invalid experiment table name."
        )

    if not validate_identifier(table_name):
        raise ValueError(
            f"Invalid table name: {table_name}"
        )

    query = experiment["read_query"]

    if "{table}" not in query:
        raise ValueError(
            "read_query must contain the "
            "'{table}' placeholder."
        )

    rendered_query = query.format(
        table=table_name
    )

    return rendered_query


# =========================================================
# MEASUREMENT CONTRACT
# =========================================================

def build_measurement_contract(
    experiment,
):
    """
    Build the measurement contract for an experiment.

    This defines which evidence must eventually be collected
    by M18.2.

    The contract requires read, storage, and write evidence
    to be linked to the same experiment and experimental index.
    """

    if not validate_experiment_definition(
        experiment
    ):
        raise ValueError(
            "Invalid experiment definition."
        )

    return {
        "experiment_id":
            experiment["experiment_id"],

        "index_name":
            experiment["index_name"],

        "table_name":
            experiment["table_name"],

        "write_table":
            experiment["write_table"],

        "read_query_template":
            experiment["read_query"],

        "read": {
            "required": True,
            "baseline_required": True,
            "indexed_required": True,
            "iterations":
                experiment["read_iterations"],
            "warmup_runs":
                experiment["read_warmup_runs"],
        },

        "storage": {
            "required": True,
            "index_size_required": True,
            "table_size_required": True,
            "index_table_ratio_required": True,
        },

        "write": {
            "required": True,
            "baseline_required": True,
            "indexed_required": True,
            "iterations":
                experiment["write_iterations"],
            "warmup_runs":
                experiment["write_warmup_runs"],
        },

        "linkage": {
            "same_experiment_required": True,
            "same_index_required": True,
        },
    }


# =========================================================
# RESULT VALIDATION
# =========================================================

def validate_linked_result(
    result,
):
    """
    Validate that a completed result contains the identity
    and evidence-linkage fields required for M18 analysis.

    This function validates structural completeness only.

    It does not validate:

    - numerical performance values;
    - benchmark correctness;
    - index effectiveness;
    - cost-benefit conclusions.
    """

    if not isinstance(result, dict):
        return False

    required_fields = [
        "experiment_id",
        "index_name",
        "read_evidence",
        "storage_evidence",
        "write_evidence",
    ]

    for field in required_fields:
        if field not in result:
            return False

    if not isinstance(
        result["experiment_id"],
        str,
    ):
        return False

    if not isinstance(
        result["index_name"],
        str,
    ):
        return False

    if not isinstance(
        result["read_evidence"],
        dict,
    ):
        return False

    if not isinstance(
        result["storage_evidence"],
        dict,
    ):
        return False

    if not isinstance(
        result["write_evidence"],
        dict,
    ):
        return False

    return True


# =========================================================
# LINKAGE CHECK
# =========================================================

def verify_measurement_linkage(
    experiment_id,
    index_name,
    measurement_records,
):
    """
    Verify that all supplied measurement records belong
    to the same experiment and index.

    Returns True only when every record has matching
    experiment_id and index_name.
    """

    if not measurement_records:
        return False

    for record in measurement_records:
        if not isinstance(record, dict):
            return False

        if (
            record.get("experiment_id")
            != experiment_id
        ):
            return False

        if (
            record.get("index_name")
            != index_name
        ):
            return False

    return True


# =========================================================
# RESULT CONSTRUCTION
# =========================================================

def build_linked_result(
    experiment,
    read_evidence,
    storage_evidence,
    write_evidence,
):
    """
    Construct a linked result from measurements belonging
    to the same experimental index.

    The three evidence records must share:

    - experiment_id;
    - index_name.

    No database operations are performed.
    """

    if not validate_experiment_definition(
        experiment
    ):
        raise ValueError(
            "Invalid experiment definition."
        )

    measurement_records = [
        read_evidence,
        storage_evidence,
        write_evidence,
    ]

    if not verify_measurement_linkage(
        experiment["experiment_id"],
        experiment["index_name"],
        measurement_records,
    ):
        raise ValueError(
            "Measurement evidence does not belong "
            "to the same experiment and index."
        )

    result = {
        "experiment_id":
            experiment["experiment_id"],

        "index_name":
            experiment["index_name"],

        "table_name":
            experiment["table_name"],

        "columns":
            experiment["columns"],

        "index_type":
            experiment["index_type"],

        "read_evidence":
            read_evidence,

        "storage_evidence":
            storage_evidence,

        "write_evidence":
            write_evidence,

        "evidence_linked":
            True,
    }

    if not validate_linked_result(
        result
    ):
        raise ValueError(
            "Invalid linked experiment result."
        )

    return result
