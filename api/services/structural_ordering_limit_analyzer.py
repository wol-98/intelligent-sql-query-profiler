from __future__ import annotations

from sqlglot import exp

from api.schemas.structural_optimization import (
    EvidenceQuality,
    EvidenceStatus,
    OrderingLimitCharacteristic,
    OrderingLimitCharacteristicResult,
    OrderingLimitCharacteristicType,
    StructuralAnalysis,
    StructuralLayer,
)


class StructuralOrderingLimitAnalyzer:
    """
    Analyze ordering and row-limiting structural characteristics
    from a SQLGlot AST.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate indexes,
      - rewrite SQL,
      - benchmark alternatives, or
      - make optimization decisions.

    It identifies ORDER BY, LIMIT, OFFSET, and WHERE-plus-row-limiting
    characteristics and links them to the corresponding structural findings.
    """

    def analyze(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> OrderingLimitCharacteristicResult:
        """Return ordering and row-limiting characteristics from the AST."""

        characteristics: list[OrderingLimitCharacteristic] = []

        selects = list(expression.find_all(exp.Select))

        for block_number, select in enumerate(selects, start=1):
            self._add_ordering_characteristic(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_limit_characteristic(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_offset_characteristic(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_filter_with_row_limit_characteristic(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_filter_with_ordering_characteristic(
                select,
                analysis,
                block_number,
                characteristics,
            )

        return OrderingLimitCharacteristicResult(
            characteristics=characteristics
        )

    @staticmethod
    def _query_block_finding_indices(
        analysis: StructuralAnalysis,
        layer: StructuralLayer,
        query_block: int,
    ) -> list[int]:
        marker = f"query_block={query_block};"

        return [
            index
            for index, finding in enumerate(analysis.findings)
            if finding.layer == layer
            and finding.evidence is not None
            and marker in finding.evidence
        ]

    @staticmethod
    def _add_ordering_characteristic(
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[OrderingLimitCharacteristic],
    ) -> None:
        order = select.args.get("order")

        if order is None:
            return

        finding_indices = (
            StructuralOrderingLimitAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.ORDER_BY,
                query_block,
            )
        )

        if not finding_indices:
            return

        characteristics.append(
            OrderingLimitCharacteristic(
                finding_index=finding_indices[0],
                characteristic_type=(
                    OrderingLimitCharacteristicType.ORDERING
                ),
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale=(
                    "ORDER BY structure was identified "
                    "within the query block."
                ),
            )
        )

    @staticmethod
    def _add_limit_characteristic(
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[OrderingLimitCharacteristic],
    ) -> None:
        limit = select.args.get("limit")

        if limit is None:
            return

        finding_indices = (
            StructuralOrderingLimitAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.LIMIT_OFFSET,
                query_block,
            )
        )

        if not finding_indices:
            return

        characteristics.append(
            OrderingLimitCharacteristic(
                finding_index=finding_indices[0],
                characteristic_type=(
                    OrderingLimitCharacteristicType.LIMIT
                ),
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale=(
                    "LIMIT structure was identified "
                    "within the query block."
                ),
            )
        )

    @staticmethod
    def _add_offset_characteristic(
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[OrderingLimitCharacteristic],
    ) -> None:
        offset = select.args.get("offset")

        if offset is None:
            return

        finding_indices = (
            StructuralOrderingLimitAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.LIMIT_OFFSET,
                query_block,
            )
        )

        if not finding_indices:
            return

        characteristics.append(
            OrderingLimitCharacteristic(
                finding_index=finding_indices[0],
                characteristic_type=(
                    OrderingLimitCharacteristicType.OFFSET
                ),
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale=(
                    "OFFSET structure was identified "
                    "within the query block."
                ),
            )
        )

    @staticmethod
    def _add_filter_with_row_limit_characteristic(
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[OrderingLimitCharacteristic],
    ) -> None:
        where = select.args.get("where")
        limit = select.args.get("limit")
        offset = select.args.get("offset")

        if where is None or (limit is None and offset is None):
            return

        where_findings = (
            StructuralOrderingLimitAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.WHERE,
                query_block,
            )
        )

        row_limit_findings = (
            StructuralOrderingLimitAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.LIMIT_OFFSET,
                query_block,
            )
        )

        if not where_findings or not row_limit_findings:
            return

        characteristics.append(
            OrderingLimitCharacteristic(
                finding_index=row_limit_findings[0],
                characteristic_type=(
                    OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT
                ),
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.STRUCTURED,
                rationale=(
                    "A WHERE predicate and row-limiting operation "
                    "coexist within the query block."
                ),
            )
        )

    @staticmethod
    def _add_filter_with_ordering_characteristic(
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[OrderingLimitCharacteristic],
    ) -> None:
        where = select.args.get("where")
        order = select.args.get("order")

        if where is None or order is None:
            return

        where_findings = (
            StructuralOrderingLimitAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.WHERE,
                query_block,
            )
        )

        ordering_findings = (
            StructuralOrderingLimitAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.ORDER_BY,
                query_block,
            )
        )

        if not where_findings or not ordering_findings:
            return

        characteristics.append(
            OrderingLimitCharacteristic(
                finding_index=ordering_findings[0],
                characteristic_type=(
                    OrderingLimitCharacteristicType.FILTER_WITH_ORDERING
                ),
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.STRUCTURED,
                rationale=(
                    "A WHERE predicate and ORDER BY operation "
                    "coexist within the query block."
                ),
            )
        )
