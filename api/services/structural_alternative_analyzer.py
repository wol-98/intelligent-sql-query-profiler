from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    StructuralAlternativeCandidate,
    StructuralAlternativeResult,
    StructuralCTEAlternativeResult,
)
from api.services.structural_alternative_detector import (
    StructuralAlternativeDetector,
)
from api.services.structural_alternative_rules import (
    StructuralAlternativeRule,
    StructuralAlternativeRuleEngine,
)
from api.services.structural_cte_alternative_analyzer import (
    StructuralCTEAlternativeAnalysis,
    StructuralCTEAlternativeAnalyzer,
)


@dataclass(frozen=True)
class StructuralAlternativeAnalysis:
    """Integrated subquery structural-alternative analysis result.

    This object combines the detected subquery candidate with the
    deterministic rule that applies to it.

    It does not establish semantic equivalence and does not generate
    executable alternative SQL.
    """

    candidate: StructuralAlternativeCandidate
    rule: StructuralAlternativeRule


@dataclass(frozen=True)
class StructuralAlternativeFrameworkAnalysis:
    """Unified structural-alternative framework result.

    Subquery and CTE alternatives remain separate typed families.
    This object provides a common integration boundary without changing
    either family's established public schema.
    """

    subquery_analyses: tuple[StructuralAlternativeAnalysis, ...]
    cte_analyses: tuple[StructuralCTEAlternativeAnalysis, ...]


class StructuralAlternativeAnalyzer:
    """Integrate structural alternatives across supported families.

    The existing M21.7 subquery framework remains unchanged in behavior.
    M21.10 CTE alternatives are exposed through a separate typed family
    within the unified framework result.

    This service is analytical only. It does not:

    - rewrite SQL,
    - execute SQL,
    - validate semantic equivalence,
    - benchmark alternatives,
    - modify database objects, or
    - make production decisions.
    """

    def __init__(
        self,
        detector: StructuralAlternativeDetector | None = None,
        rule_engine: StructuralAlternativeRuleEngine | None = None,
        cte_analyzer: StructuralCTEAlternativeAnalyzer | None = None,
    ) -> None:
        self._detector = detector or StructuralAlternativeDetector()
        self._rule_engine = rule_engine or StructuralAlternativeRuleEngine()
        self._cte_analyzer = (
            cte_analyzer or StructuralCTEAlternativeAnalyzer()
        )

    def analyze(
        self,
        original_sql: str,
    ) -> list[StructuralAlternativeAnalysis]:
        """Detect subquery alternatives and resolve their rules."""

        detected = self._detector.detect(original_sql)

        analyses: list[StructuralAlternativeAnalysis] = []

        for candidate in detected.candidates:
            rule = self._rule_engine.get_rule(candidate.alternative_type)

            analyses.append(
                StructuralAlternativeAnalysis(
                    candidate=candidate,
                    rule=rule,
                )
            )

        return analyses

    def analyze_result(
        self,
        original_sql: str,
    ) -> StructuralAlternativeResult:
        """Return the established M21.7 subquery candidate result."""

        analyses = self.analyze(original_sql)

        candidates = [
            self._preserve_candidate(analysis.candidate)
            for analysis in analyses
        ]

        return StructuralAlternativeResult(candidates=candidates)

    def analyze_cte_result(
        self,
        result: StructuralCTEAlternativeResult,
    ) -> list[StructuralCTEAlternativeAnalysis]:
        """Resolve CTE alternatives through the unified framework boundary."""

        return self._cte_analyzer.analyze_result(result)

    def analyze_framework(
        self,
        original_sql: str,
        cte_result: StructuralCTEAlternativeResult | None = None,
    ) -> StructuralAlternativeFrameworkAnalysis:
        """Return subquery and CTE alternative analyses together.

        The two alternative families remain separately typed. If no CTE
        result is supplied, the CTE analysis collection is empty.
        """

        subquery_analyses = tuple(
            self.analyze(original_sql)
        )

        cte_analyses: tuple[
            StructuralCTEAlternativeAnalysis, ...
        ]

        if cte_result is None:
            cte_analyses = ()
        else:
            cte_analyses = tuple(
                self.analyze_cte_result(cte_result)
            )

        return StructuralAlternativeFrameworkAnalysis(
            subquery_analyses=subquery_analyses,
            cte_analyses=cte_analyses,
        )

    @staticmethod
    def _preserve_candidate(
        candidate: StructuralAlternativeCandidate,
    ) -> StructuralAlternativeCandidate:
        """Return a contract-safe copy without introducing validation claims."""

        return StructuralAlternativeCandidate(
            candidate_id=candidate.candidate_id,
            alternative_type=candidate.alternative_type,
            status=candidate.status,
            semantic_safety=candidate.semantic_safety,
            evidence_status=candidate.evidence_status,
            title=candidate.title,
            rationale=candidate.rationale,
            source_layer=candidate.source_layer,
            original_sql=candidate.original_sql,
            alternative_sql=candidate.alternative_sql,
        )
