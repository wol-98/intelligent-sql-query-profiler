from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralAlternativeCandidate,
    StructuralAlternativeResult,
)
from api.services.structural_alternative_detector import (
    StructuralAlternativeDetector,
)
from api.services.structural_alternative_rules import (
    StructuralAlternativeRule,
    StructuralAlternativeRuleEngine,
)


@dataclass(frozen=True)
class StructuralAlternativeAnalysis:
    """Integrated structural-alternative analysis result.

    This object combines the detected candidate with the deterministic rule
    that applies to it. It does not establish semantic equivalence and does
    not generate executable alternative SQL.
    """

    candidate: StructuralAlternativeCandidate
    rule: StructuralAlternativeRule


class StructuralAlternativeAnalyzer:
    """Integrate structural alternative detection and rule analysis.

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
    ) -> None:
        self._detector = detector or StructuralAlternativeDetector()
        self._rule_engine = rule_engine or StructuralAlternativeRuleEngine()

    def analyze(
        self,
        original_sql: str,
    ) -> list[StructuralAlternativeAnalysis]:
        """Detect alternatives and resolve their deterministic rules."""

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
        """Return the integrated candidate result.

        The public schema remains StructuralAlternativeResult so downstream
        components can continue consuming the established M21.7.1 contract.
        """

        analyses = self.analyze(original_sql)

        candidates = [
            self._preserve_candidate(analysis.candidate)
            for analysis in analyses
        ]

        return StructuralAlternativeResult(candidates=candidates)

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
