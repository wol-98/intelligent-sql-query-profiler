from __future__ import annotations

import re

from sqlglot import exp

from api.schemas.structural_optimization import (
    EvidenceStatus,
    OpportunityEvidenceScope,
    ProceduralWorkloadOpportunityStatus,
    ProceduralWorkloadOpportunityType,
    StructuralAnalysis,
    StructuralLayer,
    StructuralProceduralWorkloadOpportunity,
    StructuralProceduralWorkloadOpportunityResult,
)


class StructuralProceduralWorkloadAnalyzer:
    """
    Identify deterministic structural patterns that may warrant later
    database function or stored-procedure analysis.

    This service is analytical only. It does not:
      - execute SQL,
      - modify the database,
      - generate CREATE FUNCTION statements,
      - generate CREATE PROCEDURE statements,
      - benchmark alternatives,
      - establish procedural suitability, or
      - make production decisions.

    Only workload patterns directly supported by the supplied SQL
    structure are identified.
    """

    _POSTGRES_PARAMETER_PATTERN = re.compile(r"\$\d+")

    def analyze(
        self,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
    ) -> StructuralProceduralWorkloadOpportunityResult:
        """
        Identify deterministic procedural workload opportunities.

        Candidate order is deterministic and follows:
          1. reusable computation
          2. parameterized operation
          3. multi-step data operation
        """

        if not analysis.findings:
            return StructuralProceduralWorkloadOpportunityResult()

        opportunities: list[
            StructuralProceduralWorkloadOpportunity
        ] = []

        self._add_reusable_computation_opportunity(
            expression,
            analysis,
            opportunities,
        )

        self._add_parameterized_operation_opportunity(
            analysis,
            opportunities,
        )

        self._add_multi_step_operation_opportunity(
            expression,
            analysis,
            opportunities,
        )

        return StructuralProceduralWorkloadOpportunityResult(
            opportunities=opportunities
        )

    @classmethod
    def _add_reusable_computation_opportunity(
        cls,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
        opportunities: list[
            StructuralProceduralWorkloadOpportunity
        ],
    ) -> None:
        """
        Identify a CTE computation referenced more than once.

        Repeated CTE usage is direct structural evidence that a named
        computation is reused within the submitted SQL statement.
        It does not establish reuse across separate workload executions.
        """

        cte_names = cls._cte_names(expression)

        if not cte_names:
            return

        reference_counts: dict[str, int] = {
            name: 0 for name in cte_names
        }

        for table in expression.find_all(exp.Table):
            if table.name not in cte_names:
                continue

            if isinstance(table.parent, (exp.From, exp.Join)):
                reference_counts[table.name] += 1

        reusable_ctes = sorted(
            name
            for name, count in reference_counts.items()
            if count >= 2
        )

        if not reusable_ctes:
            return

        cte_name = reusable_ctes[0]

        finding_index = cls._cte_reference_finding_index(
            analysis,
            cte_name,
        )

        if finding_index is None:
            return

        opportunities.append(
            StructuralProceduralWorkloadOpportunity(
                finding_index=finding_index,
                opportunity_type=(
                    ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
                ),
                status=ProceduralWorkloadOpportunityStatus.IDENTIFIED,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_scope=OpportunityEvidenceScope.FINDING,
                rationale=(
                    f"CTE {cte_name!r} is referenced multiple times "
                    "within the submitted SQL statement, providing "
                    "direct structural evidence of a reusable "
                    "computation. This does not establish reuse across "
                    "separate workload executions or justify a database "
                    "function automatically."
                ),
            )
       )

    @classmethod
    def _add_parameterized_operation_opportunity(
        cls,
        analysis: StructuralAnalysis,
        opportunities: list[
            StructuralProceduralWorkloadOpportunity
        ],
    ) -> None:
        """
        Identify explicit PostgreSQL parameter markers from the
        established structural finding evidence.
        """

        finding_index = cls._parameterized_finding_index(
            analysis
        )

        if finding_index is None:
            return

        opportunities.append(
            StructuralProceduralWorkloadOpportunity(
                finding_index=finding_index,
                opportunity_type=(
                    ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
                ),
                status=ProceduralWorkloadOpportunityStatus.IDENTIFIED,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_scope=OpportunityEvidenceScope.FINDING,
                rationale=(
                    "The submitted PostgreSQL SQL contains an explicit "
                    "parameter marker and may warrant later analysis "
                    "of a reusable parameterized database routine. "
                    "This does not establish that a function or "
                    "procedure is required."
                ),
            )
        )

    @classmethod
    def _add_multi_step_operation_opportunity(
        cls,
        expression: exp.Expression,
        analysis: StructuralAnalysis,
        opportunities: list[
            StructuralProceduralWorkloadOpportunity
        ],
    ) -> None:
        """
        Identify staged query computation represented by CTEs or
        nested query blocks.
        """

        select_count = len(
            list(expression.find_all(exp.Select))
        )

        has_cte = bool(
            list(expression.find_all(exp.CTE))
        )

        has_nested_query = analysis.subqueries_detected > 0

        if select_count < 2:
            return

        if not has_cte and not has_nested_query:
            return

        finding_index = cls._multi_step_finding_index(
            analysis
        )

        if finding_index is None:
            return

        opportunities.append(
            StructuralProceduralWorkloadOpportunity(
                finding_index=finding_index,
                opportunity_type=(
                    ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
                ),
                status=ProceduralWorkloadOpportunityStatus.IDENTIFIED,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_scope=OpportunityEvidenceScope.FINDING,
                rationale=(
                    "Multiple SQL query blocks were identified through "
                    "CTE or nested-query structure, providing direct "
                    "evidence of staged data computation. This does "
                    "not establish that a stored procedure is required."
                ),
            )
        )

    @staticmethod
    def _cte_names(
        expression: exp.Expression,
    ) -> set[str]:
        names: set[str] = set()

        for cte in expression.find_all(exp.CTE):
            name = cte.alias_or_name

            if name:
                names.add(name)

        return names

    @staticmethod
    def _cte_reference_finding_index(
        analysis: StructuralAnalysis,
        cte_name: str,
    ) -> int | None:
        marker = f"cte_name={cte_name};"

        for index, finding in enumerate(analysis.findings):
            if (
                finding.layer == StructuralLayer.CTE
                and finding.finding_type == "CTE_REFERENCE"
                and finding.evidence
                and marker in finding.evidence
            ):
                return index

        return None

    @classmethod
    def _parameterized_finding_index(
        cls,
        analysis: StructuralAnalysis,
    ) -> int | None:
        """
        Return the first structural finding whose evidence contains
        a PostgreSQL positional parameter marker such as $1 or $2.
        """

        for index, finding in enumerate(analysis.findings):
            if not finding.evidence:
                continue

            if cls._POSTGRES_PARAMETER_PATTERN.search(
                finding.evidence
            ):
                return index

        return None

    @staticmethod
    def _multi_step_finding_index(
        analysis: StructuralAnalysis,
    ) -> int | None:
        preferred_layers = (
            StructuralLayer.CTE,
            StructuralLayer.SUBQUERY,
        )

        for layer in preferred_layers:
            for index, finding in enumerate(analysis.findings):
                if finding.layer == layer:
                    return index

        return None
