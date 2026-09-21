from __future__ import annotations

from dataclasses import dataclass

from sqlglot import exp

from api.schemas.structural_optimization import (
    StructuralLayer,
    SubqueryAlternativeType,
)


@dataclass(frozen=True)
class StructuralAlternativeRule:
    """Deterministic rule describing a possible structural alternative.

    The rule does not establish semantic equivalence and does not generate
    executable SQL. It describes the alternative family and the validation
    requirements that a later stage must satisfy.
    """

    source_type: SubqueryAlternativeType
    alternative_family: str
    source_layer: StructuralLayer
    requires_semantic_validation: bool
    safety_constraints: tuple[str, ...]


class StructuralAlternativeRuleEngine:
    """Return deterministic rules for detected subquery structures."""

    _RULES = {
        SubqueryAlternativeType.EXISTS: StructuralAlternativeRule(
            source_type=SubqueryAlternativeType.EXISTS,
            alternative_family="EXISTS_TO_SUBQUERY_ALTERNATIVE",
            source_layer=StructuralLayer.SUBQUERY,
            requires_semantic_validation=True,
            safety_constraints=(
                "Preserve correlated-reference semantics.",
                "Preserve predicate semantics.",
                "Validate NULL-sensitive behavior.",
            ),
        ),
        SubqueryAlternativeType.IN: StructuralAlternativeRule(
            source_type=SubqueryAlternativeType.IN,
            alternative_family="IN_TO_EXISTS",
            source_layer=StructuralLayer.SUBQUERY,
            requires_semantic_validation=True,
            safety_constraints=(
                "Preserve correlation semantics.",
                "Validate NULL-sensitive membership behavior.",
                "Preserve duplicate-insensitive membership semantics.",
            ),
        ),
        SubqueryAlternativeType.ANY: StructuralAlternativeRule(
            source_type=SubqueryAlternativeType.ANY,
            alternative_family="ANY_TO_OPERATOR_SPECIFIC_ALTERNATIVE",
            source_layer=StructuralLayer.SUBQUERY,
            requires_semantic_validation=True,
            safety_constraints=(
                "Preserve the comparison operator.",
                "Preserve quantified-comparison semantics.",
                "Validate NULL-sensitive behavior.",
            ),
        ),
        SubqueryAlternativeType.DERIVED_TABLE: StructuralAlternativeRule(
            source_type=SubqueryAlternativeType.DERIVED_TABLE,
            alternative_family="DERIVED_TABLE_TO_STRUCTURAL_ALTERNATIVE",
            source_layer=StructuralLayer.FROM,
            requires_semantic_validation=True,
            safety_constraints=(
                "Preserve projected columns and aliases.",
                "Preserve query-scope semantics.",
                "Preserve cardinality and predicate semantics.",
            ),
        ),
    }

    def get_rule(
        self,
        alternative_type: SubqueryAlternativeType,
    ) -> StructuralAlternativeRule:
        """Return the deterministic rule for an alternative type."""

        try:
            return self._RULES[alternative_type]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported structural alternative type: "
                f"{alternative_type}"
            ) from exc

    def get_rule_for_node(
        self,
        node: exp.Expression,
    ) -> StructuralAlternativeRule | None:
        """Return the rule for a supported SQLGlot AST node.

        This method is deliberately limited to structural recognition. It
        does not determine whether a transformation is semantically safe.
        """

        alternative_type = self._classify_node(node)

        if alternative_type is None:
            return None

        return self.get_rule(alternative_type)

    @staticmethod
    def _classify_node(
        node: exp.Expression,
    ) -> SubqueryAlternativeType | None:
        """Classify only the AST structures supported by M21.7."""

        if isinstance(node, exp.Exists):
            return SubqueryAlternativeType.EXISTS

        if isinstance(node, exp.In):
            query = node.args.get("query")

            if isinstance(query, exp.Subquery):
                return SubqueryAlternativeType.IN

            return None

        if isinstance(node, exp.Any):
            subquery = node.args.get("this")

            if isinstance(subquery, exp.Subquery):
                return SubqueryAlternativeType.ANY

            return None

        if isinstance(node, exp.Subquery):
            if isinstance(node.parent, exp.From):
                return SubqueryAlternativeType.DERIVED_TABLE

        return None
