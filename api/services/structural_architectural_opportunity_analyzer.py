from __future__ import annotations

from collections import defaultdict

from api.schemas.structural_optimization import (
    AggregationWindowCharacteristicResult,
    AggregationWindowCharacteristicType,
    ArchitecturalOpportunityStatus,
    ArchitecturalOpportunityType,
    CTECharacteristicResult,
    CTECharacteristicType,
    EvidenceStatus,
    OpportunityEvidenceScope,
    StructuralAnalysis,
    StructuralArchitecturalOpportunity,
    StructuralArchitecturalOpportunityResult,
    StructuralLayer,
)


class StructuralArchitecturalOpportunityAnalyzer:
    """
    Identify deterministic architectural structures that may warrant
    later view or materialized-view analysis.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate CREATE VIEW statements,
      - generate CREATE MATERIALIZED VIEW statements,
      - benchmark alternatives, or
      - make architectural decisions.
    """

    def analyze(
        self,
        analysis: StructuralAnalysis,
        *,
        cte_characteristics: CTECharacteristicResult | None = None,
        aggregation_window_characteristics: (
            AggregationWindowCharacteristicResult | None
        ) = None,
    ) -> StructuralArchitecturalOpportunityResult:
        opportunities: list[StructuralArchitecturalOpportunity] = []

        if cte_characteristics is not None:
            self._add_cte_opportunities(
                analysis,
                cte_characteristics,
                opportunities,
            )

        if aggregation_window_characteristics is not None:
            self._add_aggregation_opportunities(
                analysis,
                aggregation_window_characteristics,
                opportunities,
            )

        self._add_filtered_relational_opportunities(
            analysis,
            opportunities,
        )

        self._add_analytical_opportunities(
            analysis,
            aggregation_window_characteristics,
            opportunities,
        )

        return StructuralArchitecturalOpportunityResult(
            opportunities=opportunities
        )
    @staticmethod
    def _add_cte_opportunities(
        analysis: StructuralAnalysis,
        characteristics: CTECharacteristicResult,
        opportunities: list[StructuralArchitecturalOpportunity],
    ) -> None:
        definitions: list[int] = []
        references: list[int] = []
        recursive_indices: list[int] = []

        for characteristic in characteristics.characteristics:
            if characteristic.finding_index >= len(analysis.findings):
                raise ValueError(
                    "CTE characteristic references a finding index that "
                    f"does not exist: {characteristic.finding_index}"
                )

            if characteristic.evidence_status != EvidenceStatus.COMPLETE:
                continue

            if characteristic.characteristic_type == (
                CTECharacteristicType.CTE_DEFINITION
            ):
                definitions.append(characteristic.finding_index)

            elif characteristic.characteristic_type == (
                CTECharacteristicType.CTE_REFERENCE
            ):
                references.append(characteristic.finding_index)

            elif characteristic.characteristic_type == (
                CTECharacteristicType.RECURSIVE_CTE
            ):
                recursive_indices.append(characteristic.finding_index)

        for finding_index in sorted(set(recursive_indices)):
            opportunities.append(
                StructuralArchitecturalOpportunity(
                    finding_index=finding_index,
                    opportunity_type=ArchitecturalOpportunityType.RECURSIVE_CTE,
                    status=ArchitecturalOpportunityStatus.IDENTIFIED,
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_scope=OpportunityEvidenceScope.FINDING,
                    rationale=(
                        "Recursive CTE structure was identified and may "
                        "warrant dedicated architectural analysis. "
                        "This does not establish a view or materialized-view "
                        "recommendation."
                    ),
                )
            )

        # Recursive CTEs are handled by the dedicated recursive opportunity.
        if recursive_indices:
            return

        if not definitions or not references:
            return

        # A reusable CTE is represented once per CTE definition rather than
        # once per reference.
        finding_index = sorted(definitions)[0]

        opportunities.append(
            StructuralArchitecturalOpportunity(
                finding_index=finding_index,
                opportunity_type=ArchitecturalOpportunityType.REUSABLE_CTE,
                status=ArchitecturalOpportunityStatus.IDENTIFIED,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_scope=OpportunityEvidenceScope.FINDING,
                rationale=(
                    "A CTE definition and reference structure was "
                    "identified and may warrant architectural analysis "
                    "of reusable query structure. This does not "
                    "establish a view recommendation."
                ),
            )
        )


    @staticmethod
    def _add_aggregation_opportunities(
        analysis: StructuralAnalysis,
        characteristics: AggregationWindowCharacteristicResult,
        opportunities: list[StructuralArchitecturalOpportunity],
    ) -> None:
        grouping_blocks: set[int] = set()
        aggregate_blocks: set[int] = set()

        for characteristic in characteristics.characteristics:
            if characteristic.finding_index >= len(analysis.findings):
                raise ValueError(
                    "Aggregation characteristic references a finding index "
                    f"that does not exist: {characteristic.finding_index}"
                )

            if characteristic.evidence_status != EvidenceStatus.COMPLETE:
                continue

            finding = analysis.findings[characteristic.finding_index]
            query_block = StructuralArchitecturalOpportunityAnalyzer._query_block(
                finding.evidence
            )

            if query_block is None:
                continue

            if characteristic.characteristic_type == (
                AggregationWindowCharacteristicType.GROUPING
            ):
                grouping_blocks.add(query_block)

            elif characteristic.characteristic_type == (
                AggregationWindowCharacteristicType.AGGREGATE_FUNCTION
            ):
                aggregate_blocks.add(query_block)

        for query_block in sorted(grouping_blocks | aggregate_blocks):
            finding_index = (
                StructuralArchitecturalOpportunityAnalyzer._first_finding_for_block(
                    analysis,
                    query_block,
                    {
                        StructuralLayer.GROUP_BY,
                        StructuralLayer.SELECT,
                    },
                )
            )

            if finding_index is None:
                continue

            opportunities.append(
                StructuralArchitecturalOpportunity(
                    finding_index=finding_index,
                    opportunity_type=(
                        ArchitecturalOpportunityType.AGGREGATED_RESULT
                    ),
                    status=ArchitecturalOpportunityStatus.IDENTIFIED,
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_scope=OpportunityEvidenceScope.FINDING,
                    rationale=(
                        f"Aggregated result structure was identified in "
                        f"query block {query_block} and may warrant later "
                        "architectural analysis. This does not establish "
                        "a materialized-view recommendation."
                    ),
                )
            )

    @staticmethod
    def _add_filtered_relational_opportunities(
        analysis: StructuralAnalysis,
        opportunities: list[StructuralArchitecturalOpportunity],
    ) -> None:
        from_blocks: set[int] = set()
        join_blocks: set[int] = set()
        where_blocks: set[int] = set()

        for finding in analysis.findings:
            query_block = StructuralArchitecturalOpportunityAnalyzer._query_block(
                finding.evidence
            )

            if query_block is None:
                continue

            if finding.layer == StructuralLayer.FROM:
                from_blocks.add(query_block)

            elif finding.layer == StructuralLayer.JOIN:
                join_blocks.add(query_block)

            elif finding.layer == StructuralLayer.WHERE:
                where_blocks.add(query_block)

        candidate_blocks = (from_blocks | join_blocks) & where_blocks

        for query_block in sorted(candidate_blocks):
            finding_index = (
                StructuralArchitecturalOpportunityAnalyzer._first_finding_for_block(
                    analysis,
                    query_block,
                    {
                        StructuralLayer.WHERE,
                        StructuralLayer.FROM,
                        StructuralLayer.JOIN,
                    },
                )
            )

            if finding_index is None:
                continue

            opportunities.append(
                StructuralArchitecturalOpportunity(
                    finding_index=finding_index,
                    opportunity_type=(
                        ArchitecturalOpportunityType.FILTERED_RELATIONAL_RESULT
                    ),
                    status=ArchitecturalOpportunityStatus.IDENTIFIED,
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_scope=OpportunityEvidenceScope.FINDING,
                    rationale=(
                        f"Filtered relational structure was identified in "
                        f"query block {query_block} and may warrant later "
                        "architectural analysis. This does not establish "
                        "a view recommendation."
                    ),
                )
            )

    @staticmethod
    def _add_analytical_opportunities(
        analysis: StructuralAnalysis,
        characteristics: AggregationWindowCharacteristicResult | None,
        opportunities: list[StructuralArchitecturalOpportunity],
    ) -> None:
        if characteristics is None:
            return

        blocks: set[int] = set()

        for characteristic in characteristics.characteristics:
            if characteristic.finding_index >= len(analysis.findings):
                raise ValueError(
                    "Window characteristic references a finding index that "
                    f"does not exist: {characteristic.finding_index}"
                )

            if (
                characteristic.characteristic_type
                != AggregationWindowCharacteristicType.WINDOW_FUNCTION
            ):
                continue

            if characteristic.evidence_status != EvidenceStatus.COMPLETE:
                continue

            query_block = StructuralArchitecturalOpportunityAnalyzer._query_block(
                analysis.findings[characteristic.finding_index].evidence
            )

            if query_block is not None:
                blocks.add(query_block)

        for query_block in sorted(blocks):
            finding_index = (
                StructuralArchitecturalOpportunityAnalyzer._first_finding_for_block(
                    analysis,
                    query_block,
                    {StructuralLayer.WINDOW},
                )
            )

            if finding_index is None:
                continue

            opportunities.append(
                StructuralArchitecturalOpportunity(
                    finding_index=finding_index,
                    opportunity_type=(
                        ArchitecturalOpportunityType.ANALYTICAL_RESULT
                    ),
                    status=ArchitecturalOpportunityStatus.IDENTIFIED,
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_scope=OpportunityEvidenceScope.FINDING,
                    rationale=(
                        f"Window-function analytical structure was identified "
                        f"in query block {query_block} and may warrant later "
                        "architectural analysis. This does not establish "
                        "a view recommendation."
                    ),
                )
            )

    @staticmethod
    def _query_block(evidence: str | None) -> int | None:
        if not evidence or "query_block=" not in evidence:
            return None

        value = evidence.split("query_block=", 1)[1].split(";", 1)[0]

        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def _first_finding_for_block(
        analysis: StructuralAnalysis,
        query_block: int,
        layers: set[StructuralLayer],
    ) -> int | None:
        for index, finding in enumerate(analysis.findings):
            if finding.layer not in layers:
                continue

            if StructuralArchitecturalOpportunityAnalyzer._query_block(
                finding.evidence
            ) == query_block:
                return index

        return None
