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
        """

        layers: list[StructuralLayer] = []
        findings: list[StructuralFinding] = []

        def add_layer(layer: StructuralLayer) -> None:
            if layer not in layers:
                layers.append(layer)

        # ---------------------------------------------------------
        # SELECT
        # ---------------------------------------------------------

        selects = list(expression.find_all(exp.Select))

        if selects:
            add_layer(StructuralLayer.SELECT)

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.SELECT,
                    finding_type="SELECT_LIST",
                    severity="INFO",
                    description=(
                        f"Query contains {len(selects)} SELECT "
                        f"query block(s)."
                    ),
                    evidence=(
                        f"select_blocks={len(selects)}"
                    ),
                )
            )

        # ---------------------------------------------------------
        # FROM
        # ---------------------------------------------------------

        tables_detected = list(expression.find_all(exp.Table))

        if tables_detected:
            add_layer(StructuralLayer.FROM)

            table_names = [
                table.sql(dialect="postgres")
                for table in tables_detected
            ]

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.FROM,
                    finding_type="TABLE_SOURCE",
                    severity="INFO",
                    description=(
                        f"Query references {len(tables_detected)} "
                        f"table source(s)."
                    ),
                    evidence=", ".join(table_names),
                )
            )

        # ---------------------------------------------------------
        # JOIN
        # ---------------------------------------------------------

        joins = list(expression.find_all(exp.Join))

        if joins:
            add_layer(StructuralLayer.JOIN)

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.JOIN,
                    finding_type="JOIN",
                    severity="INFO",
                    description=(
                        f"Query contains {len(joins)} JOIN operation(s)."
                    ),
                    evidence=f"join_count={len(joins)}",
                )
            )

        # ---------------------------------------------------------
        # WHERE
        # ---------------------------------------------------------

        wheres = list(expression.find_all(exp.Where))

        if wheres:
            add_layer(StructuralLayer.WHERE)

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.WHERE,
                    finding_type="FILTER",
                    severity="INFO",
                    description=(
                        f"Query contains {len(wheres)} WHERE "
                        f"filter clause(s)."
                    ),
                    evidence=f"where_count={len(wheres)}",
                )
            )

        # ---------------------------------------------------------
        # HAVING
        # ---------------------------------------------------------

        havings = list(expression.find_all(exp.Having))

        if havings:
            add_layer(StructuralLayer.HAVING)

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.HAVING,
                    finding_type="AGGREGATE_FILTER",
                    severity="INFO",
                    description=(
                        f"Query contains {len(havings)} HAVING "
                        f"clause(s)."
                    ),
                    evidence=f"having_count={len(havings)}",
                )
            )

        # ---------------------------------------------------------
        # GROUP BY
        # ---------------------------------------------------------

        groups = list(expression.find_all(exp.Group))

        if groups:
            add_layer(StructuralLayer.GROUP_BY)

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.GROUP_BY,
                    finding_type="GROUPING",
                    severity="INFO",
                    description=(
                        f"Query contains {len(groups)} GROUP BY "
                        f"clause(s)."
                    ),
                    evidence=f"group_by_count={len(groups)}",
                )
            )

        # ---------------------------------------------------------
        # WINDOW
        # ---------------------------------------------------------

        windows = list(expression.find_all(exp.Window))

        if windows:
            add_layer(StructuralLayer.WINDOW)

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.WINDOW,
                    finding_type="WINDOW_FUNCTION",
                    severity="INFO",
                    description=(
                        f"Query contains {len(windows)} "
                        f"window function expression(s)."
                    ),
                    evidence=f"window_count={len(windows)}",
                )
            )

        # ---------------------------------------------------------
        # ORDER BY
        # ---------------------------------------------------------

        orders = list(expression.find_all(exp.Order))

        has_order_by = bool(orders)

        if has_order_by:
            add_layer(StructuralLayer.ORDER_BY)

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.ORDER_BY,
                    finding_type="ORDERING",
                    severity="INFO",
                    description=(
                        f"Query contains {len(orders)} ORDER BY "
                        f"clause(s)."
                    ),
                    evidence=f"order_by_count={len(orders)}",
                )
            )

        # ---------------------------------------------------------
        # LIMIT / OFFSET
        # ---------------------------------------------------------

        limits = list(expression.find_all(exp.Limit))
        offsets = list(expression.find_all(exp.Offset))

        has_limit = bool(limits)
        has_offset = bool(offsets)

        if has_limit or has_offset:
            add_layer(StructuralLayer.LIMIT_OFFSET)

            evidence_parts = []

            if has_limit:
                evidence_parts.append(
                    f"limit_count={len(limits)}"
                )

            if has_offset:
                evidence_parts.append(
                    f"offset_count={len(offsets)}"
                )

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.LIMIT_OFFSET,
                    finding_type="ROW_LIMITING",
                    severity="INFO",
                    description=(
                        "Query contains LIMIT and/or OFFSET."
                    ),
                    evidence=", ".join(evidence_parts),
                )
            )

        # ---------------------------------------------------------
        # SUBQUERY
        # ---------------------------------------------------------

        subqueries = list(expression.find_all(exp.Subquery))

        if subqueries:
            add_layer(StructuralLayer.SUBQUERY)

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.SUBQUERY,
                    finding_type="SUBQUERY",
                    severity="INFO",
                    description=(
                        f"Query contains {len(subqueries)} "
                        f"subquery expression(s)."
                    ),
                    evidence=f"subquery_count={len(subqueries)}",
                )
            )

        # ---------------------------------------------------------
        # SET OPERATION
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
            add_layer(StructuralLayer.SET_OPERATION)

            operation_names = [
                type(operation).__name__.upper()
                for operation in set_operations
            ]

            findings.append(
                StructuralFinding(
                    layer=StructuralLayer.SET_OPERATION,
                    finding_type="SET_OPERATION",
                    severity="INFO",
                    description=(
                        f"Query contains {len(set_operations)} "
                        f"set operation(s)."
                    ),
                    evidence=", ".join(operation_names),
                )
            )

        # ---------------------------------------------------------
        # Aggregates
        # ---------------------------------------------------------

        aggregates = list(expression.find_all(exp.AggFunc))

        # ---------------------------------------------------------
        # Tables
        # ---------------------------------------------------------

        detected_tables = [
            table.name
            for table in tables_detected
            if table.name
        ]

        resolved_tables = tables if tables is not None else detected_tables

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
