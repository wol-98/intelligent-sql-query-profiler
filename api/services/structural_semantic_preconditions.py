from __future__ import annotations

from dataclasses import dataclass, field

from sqlglot import exp

from api.schemas.structural_optimization import (
    SemanticSafetyStatus,
    SubqueryAlternativeType,
)


@dataclass(frozen=True)
class SemanticPreconditionFinding:
    """One structural condition relevant to later semantic validation."""

    name: str
    detected: bool
    rationale: str


@dataclass(frozen=True)
class SemanticPreconditionResult:
    """Deterministic semantic-safety precondition analysis.

    This result records structural facts only. It does not establish semantic
    equivalence or declare an alternative safe.
    """

    alternative_type: SubqueryAlternativeType
    semantic_safety: SemanticSafetyStatus
    findings: tuple[SemanticPreconditionFinding, ...] = field(
        default_factory=tuple
    )


class StructuralSemanticPreconditionAnalyzer:
    """Analyze structural conditions relevant to semantic validation."""

    def analyze(
        self,
        original_sql: str,
        alternative_type: SubqueryAlternativeType,
    ) -> SemanticPreconditionResult:
        expression = __import__("sqlglot").parse_one(
            original_sql,
            dialect="postgres",
        )

        target = self._find_target(
            expression,
            alternative_type,
        )

        if target is None:
            return SemanticPreconditionResult(
                alternative_type=alternative_type,
                semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
            )

        if alternative_type == SubqueryAlternativeType.EXISTS:
            findings = self._analyze_exists(target)
        elif alternative_type == SubqueryAlternativeType.IN:
            findings = self._analyze_in(target)
        elif alternative_type == SubqueryAlternativeType.ANY:
            findings = self._analyze_any(target)
        elif alternative_type == SubqueryAlternativeType.DERIVED_TABLE:
            findings = self._analyze_derived_table(target)
        else:
            findings = ()

        return SemanticPreconditionResult(
            alternative_type=alternative_type,
            semantic_safety=SemanticSafetyStatus.REQUIRES_VALIDATION,
            findings=findings,
        )

    @staticmethod
    def _find_target(
        expression: exp.Expression,
        alternative_type: SubqueryAlternativeType,
    ) -> exp.Expression | None:
        for node in expression.walk():
            if alternative_type == SubqueryAlternativeType.EXISTS:
                if isinstance(node, exp.Exists):
                    return node

            elif alternative_type == SubqueryAlternativeType.IN:
                if isinstance(node, exp.In):
                    query = node.args.get("query")
                    if isinstance(query, exp.Subquery):
                        return node

            elif alternative_type == SubqueryAlternativeType.ANY:
                if isinstance(node, exp.Any):
                    query = node.args.get("this")
                    if isinstance(query, exp.Subquery):
                        return node

            elif alternative_type == SubqueryAlternativeType.DERIVED_TABLE:
                if isinstance(node, exp.Subquery):
                    if isinstance(node.parent, exp.From):
                        return node

        return None

    @staticmethod
    def _analyze_exists(
        node: exp.Exists,
    ) -> tuple[SemanticPreconditionFinding, ...]:
        subquery = node.this

        return StructuralSemanticPreconditionAnalyzer._subquery_findings(
            subquery,
            include_projection=False,
        )

    @staticmethod
    def _analyze_in(
        node: exp.In,
    ) -> tuple[SemanticPreconditionFinding, ...]:
        query = node.args.get("query")

        findings = list(
            StructuralSemanticPreconditionAnalyzer._subquery_findings(
                query,
                include_projection=True,
            )
        )

        left_expression = node.this

        findings.append(
            SemanticPreconditionFinding(
                name="membership_expression",
                detected=left_expression is not None,
                rationale=(
                    "The IN left-hand expression must be considered when "
                    "checking membership and NULL semantics."
                ),
            )
        )

        return tuple(findings)

    @staticmethod
    def _analyze_any(
        node: exp.Any,
    ) -> tuple[SemanticPreconditionFinding, ...]:
        query = node.args.get("this")

        findings = list(
            StructuralSemanticPreconditionAnalyzer._subquery_findings(
                query,
                include_projection=True,
            )
        )

        parent = node.parent

        operator = None

        if isinstance(parent, exp.EQ):
            operator = "="
        elif isinstance(parent, exp.NEQ):
            operator = "<>"
        elif isinstance(parent, exp.GT):
            operator = ">"
        elif isinstance(parent, exp.GTE):
            operator = ">="
        elif isinstance(parent, exp.LT):
            operator = "<"
        elif isinstance(parent, exp.LTE):
            operator = "<="

        findings.append(
            SemanticPreconditionFinding(
                name="comparison_operator",
                detected=operator is not None,
                rationale=(
                    f"ANY comparison operator is {operator!r}; the operator "
                    "must be preserved during semantic validation."
                ),
            )
        )

        return tuple(findings)

    @staticmethod
    def _analyze_derived_table(
        node: exp.Subquery,
    ) -> tuple[SemanticPreconditionFinding, ...]:
        select = node.this

        if not isinstance(select, exp.Select):
            return ()

        findings = [
            SemanticPreconditionFinding(
                name="projection",
                detected=bool(select.args.get("expressions")),
                rationale=(
                    "Derived-table projected columns must remain compatible "
                    "with the outer query."
                ),
            ),
            SemanticPreconditionFinding(
                name="alias",
                detected=bool(node.alias),
                rationale=(
                    "The derived-table alias participates in outer-query "
                    "scope and must be preserved."
                ),
            ),
        ]

        findings.extend(
            StructuralSemanticPreconditionAnalyzer._select_findings(
                select
            )
        )

        return tuple(findings)

    @staticmethod
    def _subquery_findings(
        node: exp.Expression | None,
        *,
        include_projection: bool,
    ) -> tuple[SemanticPreconditionFinding, ...]:
        if node is None:
            return ()

        select = node.this if isinstance(node, exp.Subquery) else node

        if not isinstance(select, exp.Select):
            return ()

        findings = list(
            StructuralSemanticPreconditionAnalyzer._select_findings(
                select
            )
        )

        if include_projection:
            findings.insert(
                0,
                SemanticPreconditionFinding(
                    name="projection",
                    detected=bool(select.args.get("expressions")),
                    rationale=(
                        "Subquery projection must be considered when "
                        "checking semantic equivalence."
                    ),
                ),
            )

        findings.append(
            SemanticPreconditionFinding(
                name="correlated_reference",
                detected=StructuralSemanticPreconditionAnalyzer._has_outer_reference(
                    select
                ),
                rationale=(
                    "Outer-scope references require explicit correlation "
                    "analysis before a transformation can be validated."
                ),
            )
        )

        findings.append(
            SemanticPreconditionFinding(
                name="null_sensitive_expression",
                detected=StructuralSemanticPreconditionAnalyzer._has_null_sensitive_expression(
                    select
                ),
                rationale=(
                    "NULL-sensitive expressions require explicit semantic "
                    "comparison."
                ),
            )
        )

        return tuple(findings)

    @staticmethod
    def _select_findings(
        select: exp.Select,
    ) -> tuple[SemanticPreconditionFinding, ...]:
        return (
            SemanticPreconditionFinding(
                name="distinct",
                detected=select.args.get("distinct") is not None,
                rationale=(
                    "DISTINCT can affect result semantics and must be "
                    "preserved or explicitly validated."
                ),
            ),
            SemanticPreconditionFinding(
                name="aggregation",
                detected=any(
                    isinstance(node, exp.AggFunc)
                    for node in select.find_all(exp.AggFunc)
                ),
                rationale=(
                    "Aggregation can affect cardinality and transformation "
                    "equivalence."
                ),
            ),
            SemanticPreconditionFinding(
                name="group_by",
                detected=select.args.get("group") is not None,
                rationale=(
                    "GROUP BY can affect result cardinality and semantics."
                ),
            ),
            SemanticPreconditionFinding(
                name="having",
                detected=select.args.get("having") is not None,
                rationale=(
                    "HAVING predicates must be preserved during semantic "
                    "validation."
                ),
            ),
            SemanticPreconditionFinding(
                name="limit",
                detected=select.args.get("limit") is not None,
                rationale=(
                    "LIMIT can affect result cardinality and therefore "
                    "requires explicit validation."
                ),
            ),
            SemanticPreconditionFinding(
                name="offset",
                detected=select.args.get("offset") is not None,
                rationale=(
                    "OFFSET can affect result cardinality and ordering "
                    "semantics."
                ),
            ),
            SemanticPreconditionFinding(
                name="window_function",
                detected=any(
                    isinstance(node, exp.Window)
                    for node in select.find_all(exp.Window)
                ),
                rationale=(
                    "Window functions can depend on query ordering and "
                    "partitioning semantics."
                ),
            ),
        )

    @staticmethod
    def _has_outer_reference(
        select: exp.Select,
    ) -> bool:
        """Detect qualified columns whose table is not locally sourced."""

        local_sources: set[str] = set()

        for table in select.find_all(exp.Table):
            if table.find_ancestor(exp.Select) is select:
                local_sources.add(table.alias_or_name)

        for column in select.find_all(exp.Column):
            if column.find_ancestor(exp.Select) is not select:
                continue

            if not column.table:
                continue

            if column.table not in local_sources:
                return True

        return False

    @staticmethod
    def _has_null_sensitive_expression(
        select: exp.Select,
    ) -> bool:
        for node in select.walk():
            if isinstance(node, exp.Null):
                return True

            if isinstance(node, exp.Is):
                return True

            if isinstance(node, exp.NullSafeEQ):
                return True

        return False
