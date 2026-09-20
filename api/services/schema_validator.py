"""
M21 Schema Validation
---------------------

Validates database objects referenced by supported SQL.

This module operates on SQLGlot ASTs and uses the read-only
SchemaIntrospector for database metadata.

It does not execute user SQL.
"""

from dataclasses import dataclass, field

from sqlglot import exp

from api.services.schema_introspector import (
    SchemaIntrospector,
)


@dataclass(frozen=True)
class TableReference:
    """A physical database table referenced by a query."""

    schema: str
    table: str
    alias: str | None = None


@dataclass(frozen=True)
class TableValidationResult:
    """Validation result for one table reference."""

    reference: TableReference
    exists: bool


@dataclass(frozen=True)
class ColumnReference:
    """A column referenced by a query."""

    name: str
    table: str | None = None
    schema: str | None = None


@dataclass(frozen=True)
class ColumnValidationResult:
    """Validation result for one column reference."""

    reference: ColumnReference
    resolved_table: str | None = None
    exists: bool = False
    ambiguous: bool = False


@dataclass(frozen=True)
class SchemaValidationResult:
    """Aggregated schema validation result."""

    valid: bool
    tables: tuple[TableValidationResult, ...] = field(
        default_factory=tuple
    )
    columns: tuple[ColumnValidationResult, ...] = field(
        default_factory=tuple
    )
    missing_tables: tuple[str, ...] = field(
        default_factory=tuple
    )
    missing_columns: tuple[str, ...] = field(
        default_factory=tuple
    )
    ambiguous_columns: tuple[str, ...] = field(
        default_factory=tuple
    )


def _explicit_table_alias(
    table: exp.Table,
) -> str | None:
    """Return the explicitly supplied table alias."""

    alias_expression = table.args.get("alias")

    if alias_expression is None:
        return None

    alias_name = alias_expression.name

    if not alias_name:
        return None

    return alias_name


def _cte_names(
    expression: exp.Expression,
) -> set[str]:
    """Return CTE names defined by the query."""

    return {
        cte.alias_or_name.lower()
        for cte in expression.find_all(exp.CTE)
        if cte.alias_or_name
    }


def extract_table_references(
    expression: exp.Expression,
    default_schema: str = "public",
) -> tuple[TableReference, ...]:
    """
    Extract physical table references from a SQLGlot AST.

    CTE definitions and references are excluded from physical
    database table validation.
    """

    cte_names = _cte_names(expression)

    references: list[TableReference] = []
    seen: set[tuple[str, str, str | None]] = set()

    for table in expression.find_all(exp.Table):
        table_name = table.name

        if not table_name:
            continue

        if table_name.lower() in cte_names:
            continue

        schema_name = table.db or default_schema
        alias = _explicit_table_alias(table)

        key = (
            schema_name.lower(),
            table_name.lower(),
            alias.lower() if alias else None,
        )

        if key in seen:
            continue

        seen.add(key)

        references.append(
            TableReference(
                schema=schema_name,
                table=table_name,
                alias=alias,
            )
        )

    return tuple(references)


def extract_column_references(
    expression: exp.Expression,
) -> tuple[ColumnReference, ...]:
    """
    Extract meaningful column references from a SQLGlot AST.

    Wildcards such as SELECT * and COUNT(*) are excluded because
    they do not identify a specific column that can be validated
    individually.
    """

    references: list[ColumnReference] = []

    for column in expression.find_all(exp.Column):
        references.append(
            ColumnReference(
                name=column.name,
                table=column.table or None,
                schema=column.db or None,
            )
        )

    return tuple(references)


def _cte_output_columns(
    expression: exp.Expression,
) -> dict[str, set[str]]:
    """
    Determine explicitly projected column names for CTEs.

    This supports simple CTE column resolution without treating
    the CTE as a physical database table.
    """

    outputs: dict[str, set[str]] = {}

    for cte in expression.find_all(exp.CTE):
        name = cte.alias_or_name

        if not name:
            continue

        columns: set[str] = set()

        for projection in cte.this.find_all(exp.Column):
            if projection.table:
                continue

            columns.add(projection.name.lower())

        outputs[name.lower()] = columns

    return outputs


def _source_columns(
    reference: TableReference,
    introspector: SchemaIntrospector,
) -> set[str]:
    """Return the columns belonging to a physical table."""

    table = introspector.get_table(reference.table)

    if table is None:
        return set()

    return {
        column.name.lower()
        for column in table.columns
    }


def _build_source_map(
    expression: exp.Expression,
    introspector: SchemaIntrospector,
    default_schema: str,
) -> dict[str, set[str]]:
    """
    Build a lookup from table name/alias to available columns.

    Physical tables use database metadata. CTEs use their
    projected columns.
    """

    sources: dict[str, set[str]] = {}

    for reference in extract_table_references(
        expression,
        default_schema=default_schema,
    ):
        columns = _source_columns(
            reference,
            introspector,
        )

        sources[reference.table.lower()] = columns

        if reference.alias:
            sources[reference.alias.lower()] = columns

    for cte_name, columns in _cte_output_columns(
        expression
    ).items():
        sources[cte_name] = columns

    return sources


def validate_columns(
    expression: exp.Expression,
    introspector: SchemaIntrospector,
    default_schema: str = "public",
) -> tuple[
    tuple[ColumnValidationResult, ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    """
    Validate column references against physical tables and CTE
    output columns.

    Column resolution is performed per SELECT query block so that
    columns inside a CTE are resolved against the CTE's own sources,
    while columns in the outer query are resolved against the CTE
    output relation.

    Returns:
        column_results,
        missing_columns,
        ambiguous_columns
    """

    column_results: list[ColumnValidationResult] = []
    missing_columns: list[str] = []
    ambiguous_columns: list[str] = []

    def resolve_query_block(
        query: exp.Expression,
        inherited_ctes: dict[str, set[str]],
    ) -> None:
        """
        Resolve columns belonging to one SELECT query block.

        Nested SELECT/CTE blocks are handled independently so that
        their column references do not contaminate the source scope
        of the surrounding query.
        """

        local_ctes = dict(inherited_ctes)

        # ---------------------------------------------------------
        # Register CTE outputs belonging to this query block.
        # ---------------------------------------------------------

        with_expression = query.args.get("with")

        if with_expression:
            for cte in with_expression.find_all(exp.CTE):
                alias = cte.alias_or_name.lower()

                cte_query = cte.this

                # Resolve the CTE body against inherited sources.
                resolve_query_block(
                    cte_query,
                    inherited_ctes,
                )

                output_columns = _cte_output_columns(cte)
                local_ctes.update(output_columns)

        # ---------------------------------------------------------
        # Build sources for this query block.
        # ---------------------------------------------------------

        source_map: dict[str, set[str]] = {}

        for table in query.find_all(exp.Table):
            # Do not treat a table reference inside a nested SELECT
            # as belonging to this query block.
            parent_select = table.find_ancestor(exp.Select)

            current_select = (
                query
                if isinstance(query, exp.Select)
                else query.find(exp.Select)
            )

            if (
                parent_select is not None
                and current_select is not None
                and parent_select is not current_select
            ):
                continue

            table_name = table.name.lower()

            if table_name in local_ctes:
                columns = local_ctes[table_name]
            else:
                reference = TableReference(
                    schema=table.db or default_schema,
                    table=table_name,
                    alias=_explicit_table_alias(table),
                )
                columns = _source_columns(
                    reference,
                    introspector,
                )

            source_map[table_name] = columns

            alias = _explicit_table_alias(table)
            if alias:
                source_map[alias.lower()] = columns

        # ---------------------------------------------------------
        # Resolve columns belonging to this query block.
        # ---------------------------------------------------------

        for reference in query.find_all(exp.Column):
            # Ignore columns belonging to nested SELECT blocks.
            parent_select = reference.find_ancestor(exp.Select)

            current_select = (
                query
                if isinstance(query, exp.Select)
                else query.find(exp.Select)
            )

            if (
                parent_select is not None
                and current_select is not None
                and parent_select is not current_select
            ):
                continue

            column_name = reference.name.lower()

            # -----------------------------------------------------
            # Qualified column
            # -----------------------------------------------------

            if reference.table:
                source_name = reference.table.lower()
                available_columns = source_map.get(source_name)

                if available_columns is None:
                    result = ColumnValidationResult(
                        reference=ColumnReference(
                            name=reference.name,
                            table=reference.table,
                            schema=reference.db,
                        ),
                        exists=False,
                    )

                    column_results.append(result)

                    missing_columns.append(
                        f"{reference.table}.{reference.name}"
                    )
                    continue

                exists = column_name in available_columns

                result = ColumnValidationResult(
                    reference=ColumnReference(
                        name=reference.name,
                        table=reference.table,
                        schema=reference.db,
                    ),
                    resolved_table=source_name,
                    exists=exists,
                )

                column_results.append(result)

                if not exists:
                    missing_columns.append(
                        f"{reference.table}.{reference.name}"
                    )

                continue

            # -----------------------------------------------------
            # Unqualified column
            # -----------------------------------------------------

            matching_sources = []

            for source_name, columns in source_map.items():
                if column_name in columns:
                    matching_sources.append(source_name)

            # Aliases and physical table names can refer to the
            # same underlying source. Deduplicate by column set.
            unique_source_columns = []
            unique_source_names = []

            for source_name in matching_sources:
                columns = source_map[source_name]

                if any(columns is existing for existing in unique_source_columns):
                    continue

                unique_source_columns.append(columns)
                unique_source_names.append(source_name)

            if len(unique_source_names) == 1:
                resolved_source = unique_source_names[0]

                column_results.append(
                    ColumnValidationResult(
                        reference=ColumnReference(
                            name=reference.name,
                            table=None,
                            schema=reference.db,
                        ),
                        resolved_table=resolved_source,
                        exists=True,
                    )
                )

            elif len(unique_source_names) > 1:
                column_results.append(
                    ColumnValidationResult(
                        reference=ColumnReference(
                            name=reference.name,
                            table=None,
                            schema=reference.db,
                        ),
                        exists=False,
                        ambiguous=True,
                    )
                )

                ambiguous_columns.append(reference.name)

            else:
                column_results.append(
                    ColumnValidationResult(
                        reference=ColumnReference(
                            name=reference.name,
                            table=None,
                            schema=reference.db,
                        ),
                        exists=False,
                    )
                )

                missing_columns.append(reference.name)

        # ---------------------------------------------------------
        # Resolve nested SELECT blocks independently.
        # ---------------------------------------------------------

        for nested_select in query.find_all(exp.Select):
            if nested_select is query:
                continue

            # Skip SELECTs belonging to CTEs already resolved above.
            if with_expression:
                skip = False

                for cte in with_expression.find_all(exp.CTE):
                    if nested_select is cte.this:
                        skip = True
                        break

                if skip:
                    continue

            resolve_query_block(
                nested_select,
                local_ctes,
            )

    # -------------------------------------------------------------
    # Start with the root query.
    # -------------------------------------------------------------

    root_select = expression.find(exp.Select)

    if root_select is not None:
        resolve_query_block(
            root_select,
            {},
        )

    return (
        tuple(column_results),
        tuple(dict.fromkeys(missing_columns)),
        tuple(dict.fromkeys(ambiguous_columns)),
    )


def validate_tables(
    expression: exp.Expression,
    introspector: SchemaIntrospector | None = None,
    default_schema: str = "public",
) -> SchemaValidationResult:
    """
    Validate physical table references against the database
    schema and validate referenced columns.
    """

    introspector = introspector or SchemaIntrospector(
        schema=default_schema
    )

    references = extract_table_references(
        expression,
        default_schema=default_schema,
    )

    results: list[TableValidationResult] = []
    missing_tables: list[str] = []

    for reference in references:
        if reference.schema.lower() == default_schema.lower():
            exists = introspector.table_exists(
                reference.table
            )
        else:
            exists = False

        results.append(
            TableValidationResult(
                reference=reference,
                exists=exists,
            )
        )

        if not exists:
            missing_tables.append(
                f"{reference.schema}.{reference.table}"
            )

    (
        column_results,
        missing_columns,
        ambiguous_columns,
    ) = validate_columns(
        expression,
        introspector=introspector,
        default_schema=default_schema,
    )

    return SchemaValidationResult(
        valid=(
            not missing_tables
            and not missing_columns
            and not ambiguous_columns
        ),
        tables=tuple(results),
        columns=column_results,
        missing_tables=tuple(
            dict.fromkeys(missing_tables)
        ),
        missing_columns=missing_columns,
        ambiguous_columns=ambiguous_columns,
    )
