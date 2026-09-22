from __future__ import annotations

from dataclasses import dataclass, field

from sqlglot import exp, parse_one

from api.schemas.structural_optimization import (
    CTEAlternativeType,
    SemanticSafetyStatus,
)


@dataclass(frozen=True)
class CTESemanticPreconditionFinding:
    """One structural condition relevant to later CTE semantic validation."""

    name: str
    detected: bool
    rationale: str


@dataclass(frozen=True)
class CTESemanticPreconditionResult:
    """Deterministic CTE semantic-safety precondition analysis.

    This result records structural facts only. It does not establish
    semantic equivalence or declare a CTE alternative safe.
    """

    alternative_type: CTEAlternativeType
    semantic_safety: SemanticSafetyStatus
    findings: tuple[CTESemanticPreconditionFinding, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class CTESemanticPreconditionRule:
    """Deterministic semantic-precondition rule for a CTE alternative."""

    alternative_type: CTEAlternativeType
    required_conditions: tuple[str, ...]
    rationale: str


class StructuralCTESemanticPreconditionRuleEngine:
    """Return deterministic semantic-precondition rules for CTE alternatives."""

    _RULES = {
        CTEAlternativeType.CTE: CTESemanticPreconditionRule(
            alternative_type=CTEAlternativeType.CTE,
            required_conditions=(
                "CTE_DEFINITION",
                "CTE_REFERENCES",
                "CTE_OUTPUT_COLUMNS",
                "CTE_ALIASES",
                "QUERY_SCOPE",
                "MATERIALIZATION_BEHAVIOR",
            ),
            rationale=(
                "An ordinary CTE alternative must preserve the CTE "
                "definition, references, output columns, aliases, query "
                "scope, and materialization-related behavior before semantic "
                "equivalence can be validated."
            ),
        ),
        CTEAlternativeType.RECURSIVE_CTE: CTESemanticPreconditionRule(
            alternative_type=CTEAlternativeType.RECURSIVE_CTE,
            required_conditions=(
                "CTE_DEFINITION",
                "RECURSIVE_CTE",
                "RECURSIVE_ANCHOR",
                "RECURSIVE_MEMBER",
                "RECURSIVE_SET_OPERATION",
                "RECURSIVE_REFERENCES",
                "RECURSIVE_TERMINATION",
                "CTE_OUTPUT_COLUMNS",
                "CTE_ALIASES",
                "QUERY_SCOPE",
                "MATERIALIZATION_BEHAVIOR",
            ),
            rationale=(
                "A recursive CTE alternative must preserve the recursive "
                "definition, anchor and recursive member queries, set "
                "operation, recursive references, termination behavior, "
                "output columns, aliases, query scope, and "
                "materialization-related behavior before semantic "
                "equivalence can be validated."
            ),
        ),
    }

    def get_rule(
        self,
        alternative_type: CTEAlternativeType,
    ) -> CTESemanticPreconditionRule:
        """Return the deterministic rule for a CTE alternative type."""

        try:
            return self._RULES[alternative_type]
        except KeyError as exc:
            raise ValueError(
                "Unsupported CTE semantic-precondition alternative type: "
                f"{alternative_type}"
            ) from exc


class StructuralCTESemanticPreconditionAnalyzer:
    """Analyze structural conditions relevant to CTE semantic validation."""

    def __init__(
        self,
        rule_engine: StructuralCTESemanticPreconditionRuleEngine | None = None,
    ) -> None:
        self._rule_engine = (
            rule_engine or StructuralCTESemanticPreconditionRuleEngine()
        )

    def analyze(
        self,
        original_sql: str,
        alternative_type: CTEAlternativeType,
    ) -> CTESemanticPreconditionResult:
        """Analyze structural preconditions for a CTE alternative."""

        expression = parse_one(
            original_sql,
            dialect="postgres",
        )

        target = self._find_target(
            expression,
            alternative_type,
        )

        if target is None:
            return CTESemanticPreconditionResult(
                alternative_type=alternative_type,
                semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
            )

        rule = self._rule_engine.get_rule(alternative_type)

        findings = self._build_findings(
            expression,
            target,
            rule,
        )

        return CTESemanticPreconditionResult(
            alternative_type=alternative_type,
            semantic_safety=SemanticSafetyStatus.REQUIRES_VALIDATION,
            findings=tuple(findings),
        )

    @staticmethod
    def _find_target(
        expression: exp.Expression,
        alternative_type: CTEAlternativeType,
    ) -> exp.CTE | None:
        with_expression = expression.args.get("with")

        if not isinstance(with_expression, exp.With):
            return None

        cte_expressions = with_expression.args.get("expressions") or []

        for cte in cte_expressions:
            if not isinstance(cte, exp.CTE):
                continue

            if alternative_type == CTEAlternativeType.RECURSIVE_CTE:
                if with_expression.args.get("recursive") is True:
                    return cte

            elif alternative_type == CTEAlternativeType.CTE:
                return cte

        return None

    @staticmethod
    def _build_findings(
        expression: exp.Expression,
        target: exp.CTE,
        rule: CTESemanticPreconditionRule,
    ) -> list[CTESemanticPreconditionFinding]:
        with_expression = target.find_ancestor(exp.With)

        if with_expression is None:
            return []

        cte_name = target.alias_or_name
        cte_body = target.this

        references = [
            table
            for table in expression.find_all(exp.Table)
            if table.name == cte_name
            and isinstance(table.parent, (exp.From, exp.Join))
        ]

        is_recursive = (
            with_expression.args.get("recursive") is True
        )

        output_columns = StructuralCTESemanticPreconditionAnalyzer._output_columns(
            cte_body
        )

        alias_columns = StructuralCTESemanticPreconditionAnalyzer._alias_columns(
            target
        )

        materialized = target.args.get("materialized")

        anchor, recursive_member, set_operation = (
            StructuralCTESemanticPreconditionAnalyzer._recursive_parts(
                cte_body
            )
        )

        findings: list[CTESemanticPreconditionFinding] = []

        for condition in rule.required_conditions:
            if condition == "CTE_DEFINITION":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=True,
                        rationale=(
                            f"CTE definition {cte_name!r} is present."
                        ),
                    )
                )

            elif condition == "CTE_REFERENCES":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=bool(references),
                        rationale=(
                            f"CTE {cte_name!r} has "
                            f"{len(references)} structural reference(s)."
                        ),
                    )
                )

            elif condition == "CTE_OUTPUT_COLUMNS":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=bool(output_columns),
                        rationale=(
                            "The CTE body exposes "
                            f"{len(output_columns)} output expression(s)."
                        ),
                    )
                )

            elif condition == "CTE_ALIASES":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=bool(alias_columns),
                        rationale=(
                            "The CTE has an explicit column alias list."
                            if alias_columns
                            else (
                                "The CTE has no explicit column alias list; "
                                "output-column semantics still require "
                                "validation."
                            )
                        ),
                    )
                )

            elif condition == "QUERY_SCOPE":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=bool(references),
                        rationale=(
                            "The CTE is referenced within the surrounding "
                            "query scope."
                            if references
                            else (
                                "No structural CTE reference was found, "
                                "so query-scope equivalence is not assessed."
                            )
                        ),
                    )
                )

            elif condition == "MATERIALIZATION_BEHAVIOR":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=materialized is not None,
                        rationale=(
                            "The CTE contains explicit materialization "
                            "metadata."
                            if materialized is not None
                            else (
                                "No explicit materialization directive was "
                                "detected; materialization behavior requires "
                                "later validation."
                            )
                        ),
                    )
                )

            elif condition == "RECURSIVE_CTE":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=is_recursive,
                        rationale=(
                            "The WITH clause is explicitly recursive."
                            if is_recursive
                            else "The WITH clause is not explicitly recursive."
                        ),
                    )
                )

            elif condition == "RECURSIVE_ANCHOR":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=anchor is not None,
                        rationale=(
                            "A recursive CTE anchor query was identified."
                            if anchor is not None
                            else (
                                "No recursive anchor query was identified."
                            )
                        ),
                    )
                )

            elif condition == "RECURSIVE_MEMBER":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=recursive_member is not None,
                        rationale=(
                            "A recursive CTE member query was identified."
                            if recursive_member is not None
                            else (
                                "No recursive member query was identified."
                            )
                        ),
                    )
                )

            elif condition == "RECURSIVE_SET_OPERATION":
                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=set_operation is not None,
                        rationale=(
                            "A recursive set operation was identified."
                            if set_operation is not None
                            else (
                                "No recursive set operation was identified."
                            )
                        ),
                    )
                )

            elif condition == "RECURSIVE_REFERENCES":
                recursive_reference = (
                    recursive_member is not None
                    and any(
                        table.name == cte_name
                        for table in recursive_member.find_all(exp.Table)
                    )
                )

                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=recursive_reference,
                        rationale=(
                            f"The recursive member references CTE "
                            f"{cte_name!r}."
                            if recursive_reference
                            else (
                                "No recursive self-reference was identified "
                                "in the recursive member."
                            )
                        ),
                    )
                )

            elif condition == "RECURSIVE_TERMINATION":
                termination = (
                    recursive_member is not None
                    and StructuralCTESemanticPreconditionAnalyzer
                    ._has_recursive_termination_condition(
                        recursive_member
                    )
                )

                findings.append(
                    CTESemanticPreconditionFinding(
                        name=condition,
                        detected=termination,
                        rationale=(
                            "A structural termination predicate was "
                            "identified in the recursive member."
                            if termination
                            else (
                                "No structural termination predicate was "
                                "identified; recursive termination requires "
                                "later semantic validation."
                            )
                        ),
                    )
                )

        return findings

    @staticmethod
    def _output_columns(
        cte_body: exp.Expression,
    ) -> tuple[str, ...]:
        select = next(
            cte_body.find_all(exp.Select),
            None,
        )

        if select is None:
            return ()

        columns: list[str] = []

        for expression in select.args.get("expressions") or []:
            if isinstance(expression, exp.Alias):
                columns.append(expression.alias)
            else:
                columns.append(expression.sql(dialect="postgres"))

        return tuple(columns)

    @staticmethod
    def _alias_columns(
        cte: exp.CTE,
    ) -> tuple[str, ...]:
        alias = cte.args.get("alias")

        if not isinstance(alias, exp.TableAlias):
            return ()

        columns = alias.args.get("columns") or []

        return tuple(
            column.name
            for column in columns
            if isinstance(column, exp.Identifier)
        )

    @staticmethod
    def _recursive_parts(
        cte_body: exp.Expression,
    ) -> tuple[
        exp.Expression | None,
        exp.Expression | None,
        exp.Expression | None,
    ]:
        if not isinstance(cte_body, exp.Union):
            return None, None, None

        return (
            cte_body.this,
            cte_body.expression,
            cte_body,
        )

    @staticmethod
    def _has_recursive_termination_condition(
        recursive_member: exp.Expression,
    ) -> bool:
        return any(
            isinstance(node, exp.Where)
            for node in recursive_member.walk()
        )
