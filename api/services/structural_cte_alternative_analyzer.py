from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    StructuralCTEAlternativeCandidate,
    StructuralCTEAlternativeResult,
)
from api.services.structural_cte_alternative_rules import (
    StructuralCTEAlternativeRule,
    StructuralCTEAlternativeRuleEngine,
)
from api.services.structural_cte_semantic_preconditions import (
    CTESemanticPreconditionResult,
    StructuralCTESemanticPreconditionAnalyzer,
)


@dataclass(frozen=True)
class StructuralCTEAlternativeAnalysis:
    """Combines a CTE alternative candidate with its deterministic rule."""

    candidate: StructuralCTEAlternativeCandidate
    rule: StructuralCTEAlternativeRule


class StructuralCTEAlternativeAnalyzer:
    """Integrate generated CTE candidates with alternative rules.

    Semantic-precondition analysis is exposed separately so the established
    M21.10.6 rule-resolution behavior remains unchanged.
    """

    def __init__(
        self,
        rule_engine: StructuralCTEAlternativeRuleEngine | None = None,
        semantic_precondition_analyzer: (
            StructuralCTESemanticPreconditionAnalyzer | None
        ) = None,
    ) -> None:
        self._rule_engine = (
            rule_engine
            if rule_engine is not None
            else StructuralCTEAlternativeRuleEngine()
        )

        self._semantic_precondition_analyzer = (
            semantic_precondition_analyzer
            if semantic_precondition_analyzer is not None
            else StructuralCTESemanticPreconditionAnalyzer()
        )

    def analyze(
        self,
        candidate: StructuralCTEAlternativeCandidate,
    ) -> StructuralCTEAlternativeAnalysis:
        """Resolve the deterministic rule for one CTE candidate.

        This preserves the established M21.10.6 behavior. It does not
        perform semantic-precondition analysis or modify the candidate.
        """

        rule = self._rule_engine.get_rule(
            candidate.alternative_type
        )

        return StructuralCTEAlternativeAnalysis(
            candidate=candidate,
            rule=rule,
        )

    def analyze_result(
        self,
        result: StructuralCTEAlternativeResult,
    ) -> list[StructuralCTEAlternativeAnalysis]:
        """Resolve rules for all generated CTE candidates in order."""

        return [
            self.analyze(candidate)
            for candidate in result.candidates
        ]

    def analyze_semantic_preconditions(
        self,
        candidate: StructuralCTEAlternativeCandidate,
    ) -> CTESemanticPreconditionResult:
        """Analyze semantic preconditions for one CTE candidate.

        This is a separate M21.10.7 pathway. It does not modify the
        candidate and does not establish semantic equivalence or safety.
        """

        return self._semantic_precondition_analyzer.analyze(
            candidate.original_sql,
            candidate.alternative_type,
        )

    @staticmethod
    def preserve_candidate(
        candidate: StructuralCTEAlternativeCandidate,
    ) -> StructuralCTEAlternativeCandidate:
        """Return an unchanged candidate for downstream reporting."""

        return StructuralCTEAlternativeCandidate(
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

    def preserve_result(
        self,
        result: StructuralCTEAlternativeResult,
    ) -> StructuralCTEAlternativeResult:
        """Preserve the public candidate result without changing its schema."""

        return StructuralCTEAlternativeResult(
            candidates=[
                self.preserve_candidate(candidate)
                for candidate in result.candidates
            ]
        )
