from __future__ import annotations

from sqlglot import exp

from api.schemas.structural_optimization import (
    AggregationWindowCharacteristic,
    AggregationWindowCharacteristicResult,
    AggregationWindowCharacteristicType,
    EvidenceQuality,
    EvidenceStatus,
    StructuralAnalysis,
    StructuralLayer,
)


class StructuralAggregationAnalyzer:
    """
    Analyze aggregation-related structural characteristics from a SQLGlot AST.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate indexes,
      - rewrite SQL,
      - benchmark alternatives, or
      - make optimization decisions.

    It identifies GROUP BY, aggregate-function, and HAVING characteristics
    and links them to the corresponding structural findings.
    """

    def analyze(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> AggregationWindowCharacteristicResult:
        """Return aggregation characteristics from the supplied SQL AST."""

        characteristics: list[AggregationWindowCharacteristic] = []

        selects = list(expression.find_all(exp.Select))

        for block_number, select in enumerate(selects, start=1):
            self._add_grouping_characteristic(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_aggregate_characteristics(
                select,
                analysis,
                block_number,
                characteristics,
            )

            self._add_having_characteristic(
                select,
                analysis,
                block_number,
                characteristics,
            )

        return AggregationWindowCharacteristicResult(
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
    def _add_grouping_characteristic(
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[AggregationWindowCharacteristic],
    ) -> None:
        group = select.args.get("group")

        if group is None:
            return

        finding_indices = (
            StructuralAggregationAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.GROUP_BY,
                query_block,
            )
        )

        if not finding_indices:
            return

        characteristics.append(
            AggregationWindowCharacteristic(
                finding_index=finding_indices[0],
                characteristic_type=(
                    AggregationWindowCharacteristicType.GROUPING
                ),
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale=(
                    "GROUP BY structure was identified from the "
                    "query-block structural finding."
                ),
            )
        )

    @staticmethod
    def _add_aggregate_characteristics(
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[AggregationWindowCharacteristic],
    ) -> None:
        finding_indices = (
            StructuralAggregationAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.SELECT,
                query_block,
            )
        )

        if not finding_indices:
            return

        finding_index = finding_indices[0]

        aggregates = [
            node
            for node in select.walk()
            if isinstance(node, exp.AggFunc)
            and node.find_ancestor(exp.Select) is select
        ]

        for _aggregate in aggregates:
            characteristics.append(
                AggregationWindowCharacteristic(
                    finding_index=finding_index,
                    characteristic_type=(
                        AggregationWindowCharacteristicType.AGGREGATE_FUNCTION
                    ),
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_quality=EvidenceQuality.EXACT,
                    rationale=(
                        "Aggregate-function structure was identified "
                        "within the query block."
                    ),
                )
            )

    @staticmethod
    def _add_having_characteristic(
        select: exp.Select,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[AggregationWindowCharacteristic],
    ) -> None:
        having = select.args.get("having")

        if having is None:
            return

        finding_indices = (
            StructuralAggregationAnalyzer._query_block_finding_indices(
                analysis,
                StructuralLayer.HAVING,
                query_block,
            )
        )

        if not finding_indices:
            return

        characteristics.append(
            AggregationWindowCharacteristic(
                finding_index=finding_indices[0],
                characteristic_type=(
                    AggregationWindowCharacteristicType.HAVING_FILTER
                ),
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale=(
                    "HAVING structure was identified from the "
                    "query-block structural finding."
                ),
            )
        )
