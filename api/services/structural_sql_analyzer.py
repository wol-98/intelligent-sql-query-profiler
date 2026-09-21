from __future__ import annotations

from sqlglot import exp

from api.schemas.structural_optimization import (
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralFinding,
    StructuralLayer,
)


class StructuralSQLAnalyzer:
    """
    Analyze the structural characteristics of a validated SQLGlot AST.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate optimization candidates,
      - benchmark alternatives, or
      - make optimization decisions.

    M21.4.2 adds query-block-aware structural evidence while
    preserving the existing StructuralAnalysis contract.
    """

    def analyze(
        self,
        expression: exp.Expression,
        *,
        query_type: str | None = None,
        tables: list[str] | None = None,
    ) -> StructuralAnalysis:
        """
        Return a structural description of the supplied SQL expression.

        Structural findings are generated independently for each SELECT
        query block so that nested queries and CTEs retain their own
        structural context.
        """

        layers: list[StructuralLayer] = []
        findings: list[StructuralFinding] = []

        def add_layer(layer: StructuralLayer) -> None:
            if layer not in layers:
                layers.append(layer)

        def sql_text(node: exp.Expression | None) -> str | None:
            if node is None:
                return None

            return node.sql(dialect="postgres")

        def add_finding(
            *,
            layer: StructuralLayer,
            finding_type: str,
            description: str,
            evidence: str | None,
        ) -> None:
            add_layer(layer)

            findings.append(
                StructuralFinding(
                    layer=layer,
                    finding_type=finding_type,
                    severity="INFO",
                    description=description,
                    evidence=evidence,
                )
            )

        # ---------------------------------------------------------
        # Query blocks
        # ---------------------------------------------------------

        # ---------------------------------------------------------
        # CTEs
        # ---------------------------------------------------------

        with_expression = expression.args.get("with")

        if with_expression is not None:
            cte_expressions = with_expression.args.get("expressions") or []

            cte_names = {
                cte.alias_or_name
                for cte in cte_expressions
                if cte.alias_or_name
            }

            for cte in cte_expressions:
                cte_name = cte.alias_or_name

                add_finding(
                    layer=StructuralLayer.CTE,
                    finding_type="CTE_DEFINITION",
                    description=(
                        f"Query contains CTE definition "
                        f"{cte_name!r}."
                    ),
                    evidence=(
                        f"cte_name={cte_name}; "
                        f"definition={sql_text(cte)}"
                    ),
                )

            if with_expression.args.get("recursive") is True:
                add_finding(
                    layer=StructuralLayer.CTE,
                    finding_type="RECURSIVE_CTE",
                    description="Query contains a recursive CTE.",
                    evidence=(
                        f"cte_names={', '.join(sorted(cte_names))}"
                    ),
                )

            for table in expression.find_all(exp.Table):
                if table.name in cte_names:
                    parent = table.parent

                    if isinstance(parent, exp.From) or isinstance(
                        parent, exp.Join
                    ):
                        add_finding(
                            layer=StructuralLayer.CTE,
                            finding_type="CTE_REFERENCE",
                            description=(
                                f"Query references CTE "
                                f"{table.name!r}."
                            ),
                            evidence=(
                                f"cte_name={table.name}; "
                                f"reference={sql_text(table)}"
                            ),
                        )
        selects = list(expression.find_all(exp.Select))

        # ---------------------------------------------------------
        # Process every SELECT query block independently.
        # ---------------------------------------------------------

        for block_number, select in enumerate(selects, start=1):
            block_prefix = f"query_block={block_number}; "

            # -----------------------------------------------------
            # SELECT
            # -----------------------------------------------------

            select_expressions = select.args.get("expressions") or []

            select_evidence = ", ".join(
                sql_text(item) or ""
                for item in select_expressions
            )

            add_finding(
                layer=StructuralLayer.SELECT,
                finding_type="SELECT_LIST",
                description=(
                    f"SELECT query block {block_number} contains "
                    f"{len(select_expressions)} select expression(s)."
                ),
                evidence=(
                    block_prefix
                    + f"expressions={select_evidence}"
                ),
            )

            # -----------------------------------------------------
            # FROM
            # -----------------------------------------------------

            from_clause = select.args.get("from")

            if from_clause is not None:
                add_finding(
                    layer=StructuralLayer.FROM,
                    finding_type="TABLE_SOURCE",
                    description=(
                        f"SELECT query block {block_number} "
                        "contains a FROM source."
                    ),
                    evidence=(
                        block_prefix
                        + f"from={sql_text(from_clause)}"
                    ),
                )

            # -----------------------------------------------------
            # JOIN
            # -----------------------------------------------------

            joins = select.args.get("joins") or []

            for join_number, join in enumerate(joins, start=1):
                add_finding(
                    layer=StructuralLayer.JOIN,
                    finding_type="JOIN",
                    description=(
                        f"SELECT query block {block_number} "
                        f"contains JOIN {join_number}."
                    ),
                    evidence=(
                        block_prefix
                        + f"join={sql_text(join)}"
                    ),
                )

            # -----------------------------------------------------
            # WHERE
            # -----------------------------------------------------

            where = select.args.get("where")

            if where is not None:
                add_finding(
                    layer=StructuralLayer.WHERE,
                    finding_type="FILTER",
                    description=(
                        f"SELECT query block {block_number} "
                        "contains a WHERE filter."
                    ),
                    evidence=(
                        block_prefix
                        + f"where={sql_text(where)}"
                    ),
                )

            # -----------------------------------------------------
            # GROUP BY
            # -----------------------------------------------------

            group = select.args.get("group")

            if group is not None:
                add_finding(
                    layer=StructuralLayer.GROUP_BY,
                    finding_type="GROUPING",
                    description=(
                        f"SELECT query block {block_number} "
                        "contains GROUP BY."
                    ),
                    evidence=(
                        block_prefix
                        + f"group_by={sql_text(group)}"
                    ),
                )

            # -----------------------------------------------------
            # HAVING
            # -----------------------------------------------------

            having = select.args.get("having")

            if having is not None:
                add_finding(
                    layer=StructuralLayer.HAVING,
                    finding_type="AGGREGATE_FILTER",
                    description=(
                        f"SELECT query block {block_number} "
                        "contains HAVING."
                    ),
                    evidence=(
                        block_prefix
                        + f"having={sql_text(having)}"
                    ),
                )

            # -----------------------------------------------------
            # WINDOW
            # -----------------------------------------------------

            windows = list(select.find_all(exp.Window))

            # Keep windows belonging to this SELECT block only.
            windows = [
                window
                for window in windows
                if window.find_ancestor(exp.Select) is select
            ]

            for window_number, window in enumerate(windows, start=1):
                add_finding(
                    layer=StructuralLayer.WINDOW,
                    finding_type="WINDOW_FUNCTION",
                    description=(
                        f"SELECT query block {block_number} "
                        f"contains window expression {window_number}."
                    ),
                    evidence=(
                        block_prefix
                        + f"window={sql_text(window)}"
                    ),
                )

            # -----------------------------------------------------
            # ORDER BY
            # -----------------------------------------------------

            order = select.args.get("order")

            if order is not None:
                add_finding(
                    layer=StructuralLayer.ORDER_BY,
                    finding_type="ORDERING",
                    description=(
                        f"SELECT query block {block_number} "
                        "contains ORDER BY."
                    ),
                    evidence=(
                        block_prefix
                        + f"order_by={sql_text(order)}"
                    ),
                )

            # -----------------------------------------------------
            # LIMIT
            # -----------------------------------------------------

            limit = select.args.get("limit")
            offset = select.args.get("offset")

            if limit is not None or offset is not None:
                evidence_parts: list[str] = []

                if limit is not None:
                    evidence_parts.append(
                        f"limit={sql_text(limit)}"
                    )

                if offset is not None:
                    evidence_parts.append(
                        f"offset={sql_text(offset)}"
                    )

                add_finding(
                    layer=StructuralLayer.LIMIT_OFFSET,
                    finding_type="ROW_LIMITING",
                    description=(
                        f"SELECT query block {block_number} "
                        "contains LIMIT and/or OFFSET."
                    ),
                    evidence=(
                        block_prefix
                        + "; ".join(evidence_parts)
                    ),
                )

        # ---------------------------------------------------------
        # Global structural counts
        #
        # These preserve the M21.4.1 StructuralAnalysis contract.
        # ---------------------------------------------------------

        joins = list(expression.find_all(exp.Join))
        subqueries = list(expression.find_all(exp.Subquery))
        aggregates = list(expression.find_all(exp.AggFunc))
        windows = list(expression.find_all(exp.Window))

        has_order_by = any(
            select.args.get("order") is not None
            for select in selects
        )

        has_limit = any(
            select.args.get("limit") is not None
            for select in selects
        )

        has_offset = any(
            select.args.get("offset") is not None
            for select in selects
        )

        # ---------------------------------------------------------
        # Set operations
        # ---------------------------------------------------------

        set_operations = list(
            expression.find_all(
                (
                    exp.Union,
                    exp.Intersect,
                    exp.Except,
                )
            )
        )

        if set_operations:
            operation_names = [
                type(operation).__name__.upper()
                for operation in set_operations
            ]

            add_finding(
                layer=StructuralLayer.SET_OPERATION,
                finding_type="SET_OPERATION",
                description=(
                    f"Query contains {len(set_operations)} "
                    "set operation(s)."
                ),
                evidence=", ".join(operation_names),
            )

        # ---------------------------------------------------------
        # Subqueries
        # ---------------------------------------------------------

        if subqueries:
            add_finding(
                layer=StructuralLayer.SUBQUERY,
                finding_type="SUBQUERY",
                description=(
                    f"Query contains {len(subqueries)} "
                    "subquery expression(s)."
                ),
                evidence=f"subquery_count={len(subqueries)}",
            )

        # ---------------------------------------------------------
        # Tables
        # ---------------------------------------------------------

        tables_detected = list(expression.find_all(exp.Table))

        detected_tables = [
            table.name
            for table in tables_detected
            if table.name
        ]

        resolved_tables = (
            tables
            if tables is not None
            else detected_tables
        )

        return StructuralAnalysis(
            status=StructuralAnalysisStatus.ANALYZED,
            query_type=query_type,
            layers_detected=layers,
            findings=findings,
            tables=list(dict.fromkeys(resolved_tables)),
            joins_detected=len(joins),
            subqueries_detected=len(subqueries),
            aggregates_detected=len(aggregates),
            window_functions_detected=len(windows),
            has_order_by=has_order_by,
            has_limit=has_limit,
            has_offset=has_offset,
        )
