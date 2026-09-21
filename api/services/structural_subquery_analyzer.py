from __future__ import annotations

from sqlglot import exp

from api.schemas.structural_optimization import (
    EvidenceQuality,
    EvidenceStatus,
    StructuralAnalysis,
    StructuralLayer,
    SubqueryAlternativeCharacteristic,
    SubqueryAlternativeCharacteristicResult,
    SubqueryAlternativeCharacteristicType,
)


class StructuralSubqueryAnalyzer:
    """
    Analyze subquery-related structural characteristics from a SQLGlot AST.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate indexes,
      - rewrite SQL,
      - benchmark alternatives, or
      - make optimization decisions.

    It identifies EXISTS, IN, ANY, correlated-subquery, and derived-table
    structures and links them to the corresponding structural findings.
    """

    def analyze(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> SubqueryAlternativeCharacteristicResult:
        """Return subquery-related characteristics from the SQL AST."""

        characteristics: list[SubqueryAlternativeCharacteristic] = []

        selects = list(expression.find_all(exp.Select))

        for block_number, select in enumerate(selects, start=1):
            self._add_exists_characteristics(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_in_characteristics(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_any_characteristics(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_derived_table_characteristics(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_correlated_subquery_characteristics(
                select,
                analysis,
                block_number,
                characteristics,
            )

        return SubqueryAlternativeCharacteristicResult(
            characteristics=characteristics
        )

    @staticmethod
    def _query_block_finding_indices(
        analysis: StructuralAnalysis,
        layer: StructuralLayer,
        query_block: int,
    ) -> list[int]:
        """Return finding indices belonging to the specified query block."""

        marker = f"query_block={query_block};"

        return [
            index
            for index, finding in enumerate(analysis.findings)
            if finding.layer == layer
            and finding.evidence is not None
            and marker in finding.evidence
        ]

    @classmethod
    def _add_exists_characteristics(
        cls,
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[SubqueryAlternativeCharacteristic],
    ) -> None:
        """Identify EXISTS predicates belonging to the query block."""

        finding_indices = cls._query_block_finding_indices(
            analysis,
            StructuralLayer.WHERE,
            query_block,
        )

        if not finding_indices:
            return

        finding_index = finding_indices[0]

        for exists in select.find_all(exp.Exists):
            characteristics.append(
                SubqueryAlternativeCharacteristic(
                    finding_index=finding_index,
                    characteristic_type=(
                        SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE
                    ),
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_quality=EvidenceQuality.EXACT,
                    rationale=(
                        "An EXISTS predicate is structurally present "
                        "within the query block."
                    ),
                )
            )

    @classmethod
    def _add_in_characteristics(
        cls,
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[SubqueryAlternativeCharacteristic],
    ) -> None:
        """Identify IN predicates containing subqueries."""

        finding_indices = cls._query_block_finding_indices(
            analysis,
            StructuralLayer.WHERE,
            query_block,
        )

        if not finding_indices:
            return

        finding_index = finding_indices[0]

        for in_expression in select.find_all(exp.In):
            query = in_expression.args.get("query")

            if not isinstance(query, exp.Subquery):
                continue

            characteristics.append(
                SubqueryAlternativeCharacteristic(
                    finding_index=finding_index,
                    characteristic_type=(
                        SubqueryAlternativeCharacteristicType.IN_PREDICATE
                    ),
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_quality=EvidenceQuality.EXACT,
                    rationale=(
                        "An IN predicate containing a subquery is "
                        "structurally present within the query block."
                    ),
                )
            )

    @classmethod
    def _add_any_characteristics(
        cls,
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[SubqueryAlternativeCharacteristic],
    ) -> None:
        """Identify ANY predicates containing subqueries."""

        finding_indices = cls._query_block_finding_indices(
            analysis,
            StructuralLayer.WHERE,
            query_block,
        )

        if not finding_indices:
            return

        finding_index = finding_indices[0]

        for any_expression in select.find_all(exp.Any):
            query = any_expression.args.get("this")

            if not isinstance(query, exp.Subquery):
                continue

            characteristics.append(
                SubqueryAlternativeCharacteristic(
                    finding_index=finding_index,
                    characteristic_type=(
                        SubqueryAlternativeCharacteristicType.ANY_PREDICATE
                    ),
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_quality=EvidenceQuality.EXACT,
                    rationale=(
                        "An ANY predicate containing a subquery is "
                        "structurally present within the query block."
                    ),
                )
            )

    @classmethod
    def _add_derived_table_characteristics(
        cls,
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[SubqueryAlternativeCharacteristic],
    ) -> None:
        """Identify subqueries used as derived tables in FROM."""

        finding_indices = cls._query_block_finding_indices(
            analysis,
            StructuralLayer.FROM,
            query_block,
        )

        if not finding_indices:
            return

        finding_index = finding_indices[0]

        from_expression = select.args.get("from")

        if not isinstance(from_expression, exp.From):
            return

        sources = [from_expression.this]
        sources.extend(from_expression.expressions)

        for source in sources:
            if isinstance(source, exp.Subquery):
                characteristics.append(
                    SubqueryAlternativeCharacteristic(
                        finding_index=finding_index,
                        characteristic_type=(
                            SubqueryAlternativeCharacteristicType.DERIVED_TABLE
                        ),
                        evidence_status=EvidenceStatus.COMPLETE,
                        evidence_quality=EvidenceQuality.EXACT,
                        rationale=(
                            "A subquery is structurally present as a "
                            "derived table in the FROM clause."
                        ),
                    )
                )

    @classmethod
    def _add_correlated_subquery_characteristics(
        cls,
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[SubqueryAlternativeCharacteristic],
    ) -> None:
        """Identify nested queries that reference outer query sources."""

        finding_indices = cls._query_block_finding_indices(
            analysis,
            StructuralLayer.WHERE,
            query_block,
        )

        if not finding_indices:
            return

        finding_index = finding_indices[0]

        outer_sources = cls._source_names(select)

        if not outer_sources:
            return

        nested_selects: list[exp.Select] = []

        # EXISTS stores its nested SELECT directly in the `this`
        # argument of exp.Exists.
        for exists in select.find_all(exp.Exists):
            inner_select = exists.args.get("this")

            if isinstance(inner_select, exp.Select):
                nested_selects.append(inner_select)

        # IN and ANY subqueries, and derived tables, are represented
        # through exp.Subquery.
        for subquery in select.find_all(exp.Subquery):
            inner_select = subquery.this

            if isinstance(inner_select, exp.Select):
                nested_selects.append(inner_select)

        for inner_select in nested_selects:
            if not cls._references_outer_source(
                inner_select,
                outer_sources,
            ):
                continue

            characteristics.append(
                SubqueryAlternativeCharacteristic(
                    finding_index=finding_index,
                    characteristic_type=(
                        SubqueryAlternativeCharacteristicType.CORRELATED_SUBQUERY
                    ),
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_quality=EvidenceQuality.EXACT,
                    rationale=(
                        "The nested query contains a column reference "
                        "to a source belonging to its outer query block."
                    ),
                )
            )
    @staticmethod
    def _source_names(select: exp.Select) -> set[str]:
        """Return aliases/names of sources belonging to this query block."""

        names: set[str] = set()

        from_expression = select.args.get("from")

        if isinstance(from_expression, exp.From):
            sources = [from_expression.this]
            sources.extend(from_expression.expressions)

            for source in sources:
                if isinstance(source, exp.Table):
                    names.add(source.alias_or_name)

        for join in select.args.get("joins") or []:
            if not isinstance(join, exp.Join):
                continue

            source = join.this

            if isinstance(source, exp.Table):
                names.add(source.alias_or_name)

        return names

    @staticmethod
    def _references_outer_source(
        inner_select: exp.Select,
        outer_sources: set[str],
    ) -> bool:
        """Return True when an inner query references an outer source."""

        for column in inner_select.find_all(exp.Column):
            table = column.table

            if table and table in outer_sources:
                return True

        return False
