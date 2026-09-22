from __future__ import annotations

from sqlglot import exp, parse_one
from sqlglot.errors import ParseError

from api.schemas.structural_optimization import (
    SemanticSafetyStatus,
    ViewRecommendationType,
)
from api.services.structural_view_semantic_preconditions import (
    StructuralViewSemanticPreconditionRuleEngine,
    ViewSemanticPreconditionFinding,
    ViewSemanticPreconditionResult,
)


class StructuralViewSemanticPreconditionAnalyzer:
    """
    Analyze structural semantic preconditions for VIEW and
    MATERIALIZED VIEW recommendation candidates.

    This service:
      - parses the supplied SQL,
      - inspects structural characteristics,
      - reports deterministic semantic-precondition findings.

    This service does not:
      - rewrite SQL,
      - create VIEW or MATERIALIZED VIEW DDL,
      - execute SQL,
      - establish semantic equivalence,
      - establish safety,
      - benchmark performance, or
      - make production decisions.
    """

    def __init__(
        self,
        rule_engine: StructuralViewSemanticPreconditionRuleEngine | None = None,
    ) -> None:
        self._rule_engine = (
            rule_engine
            or StructuralViewSemanticPreconditionRuleEngine.with_default_rules()
        )

    def analyze(
        self,
        original_sql: str,
        recommendation_type: ViewRecommendationType,
    ) -> ViewSemanticPreconditionResult:
        """
        Analyze semantic preconditions for the supplied recommendation type.

        A recognized and structurally parsed candidate receives
        REQUIRES_VALIDATION. This status does not establish semantic
        equivalence or safety.
        """

        rule = self._rule_engine.get_rule(recommendation_type)

        if rule is None:
            return ViewSemanticPreconditionResult(
                recommendation_type=recommendation_type,
                semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
            )

        try:
            expression = parse_one(
                original_sql,
                dialect="postgres",
            )
        except ParseError:
            return ViewSemanticPreconditionResult(
                recommendation_type=recommendation_type,
                semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
            )

        findings = tuple(
            self._analyze_condition(
                expression,
                condition,
            )
            for condition in rule.required_conditions
        )

        return ViewSemanticPreconditionResult(
            recommendation_type=recommendation_type,
            semantic_safety=SemanticSafetyStatus.REQUIRES_VALIDATION,
            findings=findings,
        )

    def _analyze_condition(
        self,
        expression: exp.Expression,
        condition: str,
    ) -> ViewSemanticPreconditionFinding:
        detector = self._detectors().get(condition)

        if detector is None:
            return ViewSemanticPreconditionFinding(
                name=condition,
                detected=False,
                rationale=(
                    "No deterministic structural detector is defined "
                    "for this precondition."
                ),
            )

        detected = detector(expression)

        if detected:
            rationale = (
                f"The SQL contains structural evidence relevant to "
                f"{condition}. This condition requires semantic "
                "validation before the architectural candidate can "
                "be accepted."
            )
        else:
            rationale = (
                f"No structural evidence for {condition} was detected "
                "in the submitted SQL. Absence of the structure does "
                "not establish semantic equivalence or safety."
            )

        return ViewSemanticPreconditionFinding(
            name=condition,
            detected=detected,
            rationale=rationale,
        )

    @staticmethod
    def _detectors():
        return {
            "PROJECTED_COLUMNS": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_projected_columns
            ),
            "PROJECTED_ALIASES": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_projected_aliases
            ),
            "QUERY_SCOPE": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_query_scope
            ),
            "SOURCE_DEPENDENCIES": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_source_dependencies
            ),
            "FILTER_PREDICATES": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_filter_predicates
            ),
            "JOIN_SEMANTICS": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_joins
            ),
            "GROUPING_AGGREGATION": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_grouping_or_aggregation
            ),
            "HAVING_FILTER": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_having
            ),
            "WINDOW_EXPRESSIONS": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_windows
            ),
            "DISTINCT_SEMANTICS": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_distinct
            ),
            "SET_OPERATION_SEMANTICS": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_set_operations
            ),
            "NESTED_QUERY_SEMANTICS": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_nested_queries
            ),
            "ORDERING_BEHAVIOR": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_ordering
            ),
            "ROW_LIMITING": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_row_limiting
            ),
            "MATERIALIZATION_BEHAVIOR": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_no_sql_level_materialization_evidence
            ),
            "REFRESH_BEHAVIOR": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_no_sql_level_refresh_evidence
            ),
            "DATA_FRESHNESS_REQUIREMENTS": (
                StructuralViewSemanticPreconditionAnalyzer
                ._has_no_sql_level_freshness_evidence
            ),
        }

    @staticmethod
    def _selects(expression: exp.Expression) -> list[exp.Select]:
        return list(expression.find_all(exp.Select))

    @staticmethod
    def _has_projected_columns(
        expression: exp.Expression,
    ) -> bool:
        return any(
            bool(select.args.get("expressions"))
            for select in StructuralViewSemanticPreconditionAnalyzer
            ._selects(expression)
        )

    @staticmethod
    def _has_projected_aliases(
        expression: exp.Expression,
    ) -> bool:
        for select in StructuralViewSemanticPreconditionAnalyzer._selects(
            expression
        ):
            if any(
                isinstance(item, exp.Alias)
                for item in select.args.get("expressions", [])
            ):
                return True

        return False

    @staticmethod
    def _has_query_scope(
        expression: exp.Expression,
    ) -> bool:
        return bool(
            StructuralViewSemanticPreconditionAnalyzer._selects(expression)
        )

    @staticmethod
    def _has_source_dependencies(
        expression: exp.Expression,
    ) -> bool:
        return expression.find(exp.Table) is not None

    @staticmethod
    def _has_filter_predicates(
        expression: exp.Expression,
    ) -> bool:
        return any(
            select.args.get("where") is not None
            for select in StructuralViewSemanticPreconditionAnalyzer
            ._selects(expression)
        )

    @staticmethod
    def _has_joins(
        expression: exp.Expression,
    ) -> bool:
        return any(
            bool(select.args.get("joins"))
            for select in StructuralViewSemanticPreconditionAnalyzer
            ._selects(expression)
        )

    @staticmethod
    def _has_grouping_or_aggregation(
        expression: exp.Expression,
    ) -> bool:
        if any(
            select.args.get("group") is not None
            for select in StructuralViewSemanticPreconditionAnalyzer
            ._selects(expression)
        ):
            return True

        return expression.find(exp.AggFunc) is not None

    @staticmethod
    def _has_having(
        expression: exp.Expression,
    ) -> bool:
        return any(
            select.args.get("having") is not None
            for select in StructuralViewSemanticPreconditionAnalyzer
            ._selects(expression)
        )

    @staticmethod
    def _has_windows(
        expression: exp.Expression,
    ) -> bool:
        return expression.find(exp.Window) is not None

    @staticmethod
    def _has_distinct(
        expression: exp.Expression,
    ) -> bool:
        return any(
            select.args.get("distinct") is not None
            for select in StructuralViewSemanticPreconditionAnalyzer
            ._selects(expression)
        )

    @staticmethod
    def _has_set_operations(
        expression: exp.Expression,
    ) -> bool:
        return any(
            isinstance(
                node,
                (
                    exp.Union,
                    exp.Intersect,
                    exp.Except,
                ),
            )
            for node in expression.walk()
        )

    @staticmethod
    def _has_nested_queries(
        expression: exp.Expression,
    ) -> bool:
        return any(
            isinstance(
                node,
                (
                    exp.Subquery,
                    exp.Exists,
                    exp.CTE,
                ),
            )
            for node in expression.walk()
        )

    @staticmethod
    def _has_ordering(
        expression: exp.Expression,
    ) -> bool:
        return any(
            select.args.get("order") is not None
            for select in StructuralViewSemanticPreconditionAnalyzer
            ._selects(expression)
        )

    @staticmethod
    def _has_row_limiting(
        expression: exp.Expression,
    ) -> bool:
        return any(
            select.args.get("limit") is not None
            or select.args.get("offset") is not None
            for select in StructuralViewSemanticPreconditionAnalyzer
            ._selects(expression)
        )

    @staticmethod
    def _has_no_sql_level_materialization_evidence(
        expression: exp.Expression,
    ) -> bool:
        """
        SQL text does not establish PostgreSQL materialized-view
        materialization behavior for this recommendation candidate.
        """

        return False

    @staticmethod
    def _has_no_sql_level_refresh_evidence(
        expression: exp.Expression,
    ) -> bool:
        """
        Refresh behavior is an operational concern and is not established
        by structural SQL analysis.
        """

        return False

    @staticmethod
    def _has_no_sql_level_freshness_evidence(
        expression: exp.Expression,
    ) -> bool:
        """
        Data-freshness requirements are not established by the submitted
        SQL text and require later validation.
        """

        return False
