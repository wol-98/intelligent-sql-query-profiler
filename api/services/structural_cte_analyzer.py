from __future__ import annotations

from sqlglot import exp

from api.schemas.structural_optimization import (
    CTECharacteristic,
    CTECharacteristicResult,
    CTECharacteristicType,
    EvidenceQuality,
    EvidenceStatus,
    StructuralAnalysis,
    StructuralLayer,
)


class StructuralCTEAnalyzer:
    """
    Analyze CTE-related structural characteristics from a SQLGlot AST.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate indexes,
      - rewrite SQL,
      - benchmark alternatives, or
      - make optimization decisions.

    It identifies CTE definitions, CTE references, and recursive CTE
    structures and links them to the corresponding structural findings.
    """

    def analyze(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> CTECharacteristicResult:
        """Return CTE structural characteristics from the supplied AST."""

        characteristics: list[CTECharacteristic] = []

        with_expression = expression.args.get("with")

        if not isinstance(with_expression, exp.With):
            return CTECharacteristicResult(
                characteristics=characteristics
            )

        cte_expressions = with_expression.args.get("expressions") or []

        cte_names = {
            cte.alias_or_name
            for cte in cte_expressions
            if cte.alias_or_name
        }

        self._add_definition_characteristics(
            analysis,
            cte_expressions,
            characteristics,
        )

        self._add_reference_characteristics(
            expression,
            analysis,
            cte_names,
            characteristics,
        )

        self._add_recursive_characteristic(
            analysis,
            with_expression,
            characteristics,
        )

        return CTECharacteristicResult(
            characteristics=characteristics
        )

    @staticmethod
    def _cte_finding_indices(
        analysis: StructuralAnalysis,
        finding_type: str,
    ) -> list[int]:
        """Return indices of CTE findings of the requested type."""

        return [
            index
            for index, finding in enumerate(analysis.findings)
            if (
                finding.layer == StructuralLayer.CTE
                and finding.finding_type == finding_type
            )
        ]

    @classmethod
    def _add_definition_characteristics(
        cls,
        analysis: StructuralAnalysis,
        cte_expressions: list[exp.CTE],
        characteristics: list[CTECharacteristic],
    ) -> None:
        """Add one characteristic for each CTE definition."""

        finding_indices = cls._cte_finding_indices(
            analysis,
            "CTE_DEFINITION",
        )

        for finding_index, cte in zip(
            finding_indices,
            cte_expressions,
        ):
            cte_name = cte.alias_or_name

            if not cte_name:
                continue

            characteristics.append(
                CTECharacteristic(
                    finding_index=finding_index,
                    characteristic_type=CTECharacteristicType.CTE_DEFINITION,
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_quality=EvidenceQuality.EXACT,
                    rationale=(
                        f"CTE definition {cte_name!r} was identified "
                        "from the structural CTE finding."
                    ),
                )
            )

    @classmethod
    def _add_reference_characteristics(
        cls,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
        cte_names: set[str],
        characteristics: list[CTECharacteristic],
    ) -> None:
        """Add one characteristic for each CTE reference."""

        finding_indices = cls._cte_finding_indices(
            analysis,
            "CTE_REFERENCE",
        )

        finding_index_by_reference: dict[tuple[str, str], int] = {}

        for finding_index in finding_indices:
            finding = analysis.findings[finding_index]

            if not finding.evidence:
                continue

            marker = "cte_name="

            if marker not in finding.evidence:
                continue

            cte_name = (
                finding.evidence.split(marker, 1)[1]
                .split(";", 1)[0]
            )

            reference = finding.evidence.split(
                "reference=",
                1,
            )[-1]

            finding_index_by_reference[(cte_name, reference)] = finding_index

        for table in expression.find_all(exp.Table):
            if table.name not in cte_names:
                continue

            parent = table.parent

            if not isinstance(parent, (exp.From, exp.Join)):
                continue

            reference_sql = table.sql(dialect="postgres")
            key = (table.name, reference_sql)

            finding_index = finding_index_by_reference.get(key)

            if finding_index is None:
                continue

            characteristics.append(
                CTECharacteristic(
                    finding_index=finding_index,
                    characteristic_type=CTECharacteristicType.CTE_REFERENCE,
                    evidence_status=EvidenceStatus.COMPLETE,
                    evidence_quality=EvidenceQuality.EXACT,
                    rationale=(
                        f"Reference to CTE {table.name!r} was identified "
                        "from the structural CTE finding."
                    ),
                )
            )

    @classmethod
    def _add_recursive_characteristic(
        cls,
        analysis: StructuralAnalysis,
        with_expression: exp.With,
        characteristics: list[CTECharacteristic],
    ) -> None:
        """Add a characteristic when the WITH clause is recursive."""

        if with_expression.args.get("recursive") is not True:
            return

        finding_indices = cls._cte_finding_indices(
            analysis,
            "RECURSIVE_CTE",
        )

        if not finding_indices:
            return

        characteristics.append(
            CTECharacteristic(
                finding_index=finding_indices[0],
                characteristic_type=CTECharacteristicType.RECURSIVE_CTE,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale=(
                    "Recursive CTE structure was identified from "
                    "the structural CTE finding."
                ),
            )
        )
