from __future__ import annotations

from dataclasses import dataclass

from sqlglot import exp

from api.schemas.structural_optimization import (
    CTEAlternativeType,
    StructuralLayer,
)


@dataclass(frozen=True)
class StructuralCTEAlternativeRule:
    """Deterministic rule describing a possible CTE structural alternative.

    The rule does not establish semantic equivalence and does not generate
    executable SQL. It describes the alternative family and the validation
    requirements that a later stage must satisfy.
    """

    source_type: CTEAlternativeType
    alternative_family: str
    source_layer: StructuralLayer
    requires_semantic_validation: bool
    safety_constraints: tuple[str, ...]


class StructuralCTEAlternativeRuleEngine:
    """Return deterministic rules for detected CTE structures."""

    _RULES = {
        CTEAlternativeType.CTE: StructuralCTEAlternativeRule(
            source_type=CTEAlternativeType.CTE,
            alternative_family="CTE_TO_STRUCTURAL_ALTERNATIVE",
            source_layer=StructuralLayer.CTE,
            requires_semantic_validation=True,
            safety_constraints=(
                "Preserve CTE output columns and aliases.",
                "Preserve CTE name and reference semantics.",
                "Preserve query-scope semantics.",
                "Validate materialization-related behavior.",
            ),
        ),
        CTEAlternativeType.RECURSIVE_CTE: StructuralCTEAlternativeRule(
            source_type=CTEAlternativeType.RECURSIVE_CTE,
            alternative_family="RECURSIVE_CTE_TO_STRUCTURAL_ALTERNATIVE",
            source_layer=StructuralLayer.CTE,
            requires_semantic_validation=True,
            safety_constraints=(
                "Preserve the recursive anchor query.",
                "Preserve the recursive member query.",
                "Preserve UNION or UNION ALL semantics.",
                "Preserve recursive termination behavior.",
                "Require dedicated recursive semantic validation.",
            ),
        ),
    }

    def get_rule(
        self,
        alternative_type: CTEAlternativeType,
    ) -> StructuralCTEAlternativeRule:
        """Return the deterministic rule for a CTE alternative type."""

        try:
            return self._RULES[alternative_type]
        except KeyError as exc:
            raise ValueError(
                "Unsupported CTE structural alternative type: "
                f"{alternative_type}"
            ) from exc

    def get_rule_for_node(
        self,
        node: exp.Expression,
    ) -> StructuralCTEAlternativeRule | None:
        """Return the rule for a supported CTE SQLGlot AST node.

        This method performs structural recognition only. It does not
        determine whether any CTE transformation is semantically safe.
        """

        alternative_type = self._classify_node(node)

        if alternative_type is None:
            return None

        return self.get_rule(alternative_type)

    @staticmethod
    def _classify_node(
        node: exp.Expression,
    ) -> CTEAlternativeType | None:
        """Classify supported CTE AST structures."""

        if not isinstance(node, exp.CTE):
            return None

        with_expression = node.find_ancestor(exp.With)

        if with_expression is not None:
            if with_expression.args.get("recursive") is True:
                return CTEAlternativeType.RECURSIVE_CTE

        return CTEAlternativeType.CTE
