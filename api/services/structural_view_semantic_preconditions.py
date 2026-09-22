from __future__ import annotations

from dataclasses import dataclass, field

from api.schemas.structural_optimization import (
    SemanticSafetyStatus,
    ViewRecommendationType,
)


@dataclass(frozen=True)
class ViewSemanticPreconditionFinding:
    """
    One semantic precondition that must be considered before a
    VIEW or MATERIALIZED VIEW recommendation can be validated.

    This is a structural/analytical contract only. The finding does
    not establish semantic equivalence or safety.
    """

    name: str
    detected: bool
    rationale: str


@dataclass(frozen=True)
class ViewSemanticPreconditionResult:
    """
    Result container for semantic-precondition analysis of a
    VIEW or MATERIALIZED VIEW recommendation candidate.
    """

    recommendation_type: ViewRecommendationType
    semantic_safety: SemanticSafetyStatus
    findings: tuple[ViewSemanticPreconditionFinding, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class ViewSemanticPreconditionRule:
    """
    Contract describing the semantic conditions that must be considered
    for a particular VIEW or MATERIALIZED VIEW recommendation type.

    Concrete condition lists are defined in the subsequent rule-analysis
    milestone.
    """

    recommendation_type: ViewRecommendationType
    required_conditions: tuple[str, ...]
    rationale: str


class StructuralViewSemanticPreconditionRuleEngine:
    """
    Resolve semantic-precondition rules for VIEW and MATERIALIZED VIEW
    recommendation types.

    The engine is intentionally contract-oriented at this milestone.
    Concrete rules can be supplied explicitly and resolved deterministically.
    """

    def __init__(
        self,
        rules: tuple[ViewSemanticPreconditionRule, ...] | None = None,
    ) -> None:
        supplied_rules = rules or ()

        seen_types: set[ViewRecommendationType] = set()

        for rule in supplied_rules:
            if rule.recommendation_type in seen_types:
                raise ValueError(
                    "Duplicate semantic-precondition rule for "
                    f"{rule.recommendation_type.value}"
                )

            seen_types.add(rule.recommendation_type)

        self._rules = {
            rule.recommendation_type: rule
            for rule in supplied_rules
        }

    def get_rule(
        self,
        recommendation_type: ViewRecommendationType,
    ) -> ViewSemanticPreconditionRule | None:
        """
        Return the registered semantic-precondition rule for the
        recommendation type, or None when no rule is registered.
        """

        return self._rules.get(recommendation_type)
