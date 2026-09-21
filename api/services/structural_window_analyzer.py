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


class StructuralWindowAnalyzer:
    """
    Analyze window-related structural characteristics from a SQLGlot AST.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate indexes,
      - rewrite SQL,
      - benchmark alternatives, or
      - make optimization decisions.

    It identifies window-function, PARTITION BY, and window ORDER BY
    characteristics and links them to the corresponding structural findings.
    """

    def analyze(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> AggregationWindowCharacteristicResult:
        """Return window characteristics from the supplied SQL AST."""

        characteristics: list[AggregationWindowCharacteristic] = []

        selects = list(expression.find_all(exp.Select))

        for block_number, select in enumerate(selects, start=1):
            windows = [
                window
                for window in select.find_all(exp.Window)
                if window.find_ancestor(exp.Select) is select
            ]

            for window in windows:
                self._add_window_characteristics(
                    window,
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
        query_block: int,
    ) -> list[int]:
        marker = f"query_block={query_block};"

        return [
            index
            for index, finding in enumerate(analysis.findings)
            if finding.layer == StructuralLayer.WINDOW
            and finding.evidence is not None
            and marker in finding.evidence
        ]

    @staticmethod
    def _add_window_characteristics(
        window: exp.Window,
        analysis: StructuralAnalysis,
        query_block: int,
        characteristics: list[AggregationWindowCharacteristic],
    ) -> None:
        finding_indices = (
            StructuralWindowAnalyzer._query_block_finding_indices(
                analysis,
                query_block,
            )
        )

        if not finding_indices:
            return

        finding_index = finding_indices[0]

        characteristics.append(
            AggregationWindowCharacteristic(
                finding_index=finding_index,
                characteristic_type=(
                    AggregationWindowCharacteristicType.WINDOW_FUNCTION
                ),
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale=(
                    "Window-function structure was identified "
                    "within the query block."
                ),
            )
        )

        partition_by = window.args.get("partition_by")

        if partition_by:
            characteristics.append(
                AggregationWindowCharacteristic(
                    finding_index=finding_index,
                    characteristic_type=(
                        AggregationWindowCharacteristicType.WINDOW_PARTITION
                    ),
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_quality=EvidenceQuality.EXACT,
                    rationale=(
                        "PARTITION BY structure was identified "
                        "within the window expression."
                    ),
                )
            )

        order = window.args.get("order")

        if order is not None:
            characteristics.append(
                AggregationWindowCharacteristic(
                    finding_index=finding_index,
                    characteristic_type=(
                        AggregationWindowCharacteristicType.WINDOW_ORDERING
                    ),
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_quality=EvidenceQuality.EXACT,
                    rationale=(
                        "Window ORDER BY structure was identified "
                        "within the window expression."
                    ),
                )
            )
