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
    """

    recommendation_type: ViewRecommendationType
    required_conditions: tuple[str, ...]
    rationale: str


VIEW_REQUIRED_CONDITIONS: tuple[str, ...] = (
    "PROJECTED_COLUMNS",
    "PROJECTED_ALIASES",
    "QUERY_SCOPE",
    "SOURCE_DEPENDENCIES",
    "FILTER_PREDICATES",
    "JOIN_SEMANTICS",
    "GROUPING_AGGREGATION",
    "HAVING_FILTER",
    "WINDOW_EXPRESSIONS",
    "DISTINCT_SEMANTICS",
    "SET_OPERATION_SEMANTICS",
    "NESTED_QUERY_SEMANTICS",
    "ORDERING_BEHAVIOR",
    "ROW_LIMITING",
)


MATERIALIZED_VIEW_REQUIRED_CONDITIONS: tuple[str, ...] = (
    "PROJECTED_COLUMNS",
    "PROJECTED_ALIASES",
    "QUERY_SCOPE",
    "SOURCE_DEPENDENCIES",
    "FILTER_PREDICATES",
    "JOIN_SEMANTICS",
    "GROUPING_AGGREGATION",
    "HAVING_FILTER",
    "WINDOW_EXPRESSIONS",
    "DISTINCT_SEMANTICS",
    "SET_OPERATION_SEMANTICS",
    "NESTED_QUERY_SEMANTICS",
    "ORDERING_BEHAVIOR",
    "ROW_LIMITING",
    "MATERIALIZATION_BEHAVIOR",
    "REFRESH_BEHAVIOR",
    "DATA_FRESHNESS_REQUIREMENTS",
)


DEFAULT_VIEW_SEMANTIC_PRECONDITION_RULES: tuple[
    ViewSemanticPreconditionRule, ...
] = (
    ViewSemanticPreconditionRule(
        recommendation_type=ViewRecommendationType.VIEW,
        required_conditions=VIEW_REQUIRED_CONDITIONS,
        rationale=(
            "VIEW candidates require validation that the exposed query "
            "semantics, dependencies, projected structure, relational "
            "operations, and row-shaping behavior are preserved."
        ),
    ),
    ViewSemanticPreconditionRule(
        recommendation_type=ViewRecommendationType.MATERIALIZED_VIEW,
        required_conditions=MATERIALIZED_VIEW_REQUIRED_CONDITIONS,
        rationale=(
            "MATERIALIZED VIEW candidates require validation of the same "
            "query semantics as a VIEW, together with materialization, "
            "refresh, and data-freshness behavior."
        ),
    ),
)


class StructuralViewSemanticPreconditionRuleEngine:
    """
    Resolve semantic-precondition rules for VIEW and MATERIALIZED VIEW
    recommendation types.

    The engine is intentionally contract-oriented at this milestone.
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

    @classmethod
    def with_default_rules(
        cls,
    ) -> "StructuralViewSemanticPreconditionRuleEngine":
        """
        Construct an engine using the deterministic project rules.

        These rules identify conditions that require later semantic
        validation. They do not establish semantic equivalence,
        safety, or performance.
        """

        return cls(
            rules=DEFAULT_VIEW_SEMANTIC_PRECONDITION_RULES
        )

    def get_rule(
        self,
        recommendation_type: ViewRecommendationType,
    ) -> ViewSemanticPreconditionRule | None:
        """
        Return the registered semantic-precondition rule for the
        recommendation type, or None when no rule is registered.
        """

        return self._rules.get(recommendation_type)
