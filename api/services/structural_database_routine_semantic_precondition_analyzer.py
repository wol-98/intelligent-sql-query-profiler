from __future__ import annotations

import re

from sqlglot import exp, parse_one
from sqlglot.errors import ParseError

from api.schemas.structural_optimization import (
    DatabaseRoutineRecommendationType,
    SemanticSafetyStatus,
)
from api.services.database_routine_semantic_preconditions import (
    DatabaseRoutineSemanticPreconditionFinding,
    DatabaseRoutineSemanticPreconditionResult,
    DatabaseRoutineSemanticPreconditionRuleEngine,
)


class StructuralDatabaseRoutineSemanticPreconditionAnalyzer:
    """
    Analyze structural semantic/behavioral preconditions for database
    function and stored-procedure recommendation candidates.

    This service does not:
      - generate function/procedure SQL,
      - create routines,
      - execute SQL,
      - execute routines,
      - establish behavioral equivalence,
      - establish semantic safety,
      - benchmark performance, or
      - make production decisions.
    """

    _PARAMETER_PATTERN = re.compile(r"\$\d+")

    def __init__(
        self,
        rule_engine: (
            DatabaseRoutineSemanticPreconditionRuleEngine | None
        ) = None,
    ) -> None:
        self._rule_engine = (
            rule_engine
            or DatabaseRoutineSemanticPreconditionRuleEngine
            .with_default_rules()
        )

    def analyze(
        self,
        original_sql: str,
        recommendation_type: DatabaseRoutineRecommendationType,
    ) -> DatabaseRoutineSemanticPreconditionResult:
        """
        Analyze deterministic structural preconditions for a routine
        recommendation type.

        A recognized and parseable SQL statement receives
        REQUIRES_VALIDATION. This does not establish safety.
        """

        rule = self._rule_engine.get_rule(
            recommendation_type
        )

        try:
            expression = parse_one(
                original_sql,
                dialect="postgres",
            )
        except ParseError:
            return DatabaseRoutineSemanticPreconditionResult(
                recommendation_type=recommendation_type,
                semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
            )

        findings = tuple(
            self._analyze_condition(
                original_sql,
                expression,
                condition,
            )
            for condition in rule.required_conditions
        )

        return DatabaseRoutineSemanticPreconditionResult(
            recommendation_type=recommendation_type,
            semantic_safety=(
                SemanticSafetyStatus.REQUIRES_VALIDATION
            ),
            findings=findings,
        )

    def _analyze_condition(
        self,
        original_sql: str,
        expression: exp.Expression,
        condition: str,
    ) -> DatabaseRoutineSemanticPreconditionFinding:
        detector = self._detectors().get(condition)

        if detector is None:
            return DatabaseRoutineSemanticPreconditionFinding(
                name=condition,
                detected=False,
                rationale=(
                    "No deterministic structural detector is defined "
                    "for this precondition."
                ),
            )

        detected = detector(
            original_sql,
            expression,
        )

        if detected:
            rationale = (
                f"Structural evidence relevant to {condition} was "
                "identified. Behavioral and semantic validation "
                "remains required before the routine candidate can "
                "be accepted."
            )
        else:
            rationale = (
                f"{condition} was not established from the submitted "
                "SQL structure. Absence of structural evidence does "
                "not establish semantic equivalence or safety."
            )

        return DatabaseRoutineSemanticPreconditionFinding(
            name=condition,
            detected=detected,
            rationale=rationale,
        )

    @staticmethod
    def _detectors():
        return {
            "PARAMETER_SIGNATURE": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_parameter_signature
            ),
            "RETURN_VALUE_SEMANTICS": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_result_producing_query
            ),
            "INPUT_DATA_DEPENDENCIES": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_table_dependencies
            ),
            "NULL_AND_TYPE_SEMANTICS": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_null_or_type_constructs
            ),
            "DETERMINISM_VOLATILITY": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_known_volatility_construct
            ),
            "ERROR_BEHAVIOR": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_error_construct
            ),
            "SIDE_EFFECT_BEHAVIOR": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_mutation
            ),
            "SECURITY_CONTEXT": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_security_construct
            ),
            "OUTPUT_OR_RESULT_SEMANTICS": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_result_producing_query
            ),
            "MULTI_STEP_EXECUTION": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_multiple_execution_stages
            ),
            "DATA_MUTATION_BEHAVIOR": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_mutation
            ),
            "TRANSACTION_BEHAVIOR": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_transaction_construct
            ),
            "ERROR_AND_ROLLBACK_BEHAVIOR": (
                StructuralDatabaseRoutineSemanticPreconditionAnalyzer
                ._has_transaction_construct
            ),
        }

    @classmethod
    def _has_parameter_signature(
        cls,
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        return bool(
            cls._PARAMETER_PATTERN.search(original_sql)
        )

    @staticmethod
    def _has_result_producing_query(
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        return any(
            isinstance(node, exp.Select)
            for node in expression.walk()
        )

    @staticmethod
    def _has_table_dependencies(
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        return any(
            isinstance(node, exp.Table)
            for node in expression.walk()
        )

    @staticmethod
    def _has_null_or_type_constructs(
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        if any(
            isinstance(node, exp.Cast)
            for node in expression.walk()
        ):
            return True

        normalized = original_sql.upper()

        return (
            " IS NULL" in normalized
            or " IS NOT NULL" in normalized
            or "::" in original_sql
        )

    @staticmethod
    def _has_known_volatility_construct(
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        normalized = original_sql.lower()

        known_constructs = (
            "random(",
            "clock_timestamp(",
            "timeofday(",
        )

        return any(
            construct in normalized
            for construct in known_constructs
        )

    @staticmethod
    def _has_error_construct(
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        normalized = original_sql.upper()

        return (
            "RAISE " in normalized
            or "EXCEPTION" in normalized
            or "ASSERT " in normalized
        )

    @staticmethod
    def _has_mutation(
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        mutation_types = (
            exp.Insert,
            exp.Update,
            exp.Delete,
        )

        return any(
            isinstance(node, mutation_types)
            for node in expression.walk()
        )

    @staticmethod
    def _has_security_construct(
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        normalized = original_sql.upper()

        security_constructs = (
            "CURRENT_USER",
            "SESSION_USER",
            "CURRENT_ROLE",
        )

        return any(
            construct in normalized
            for construct in security_constructs
        )

    @staticmethod
    def _has_multiple_execution_stages(
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        select_count = sum(
            1
            for node in expression.walk()
            if isinstance(node, exp.Select)
        )

        has_cte = any(
            isinstance(node, exp.CTE)
            for node in expression.walk()
        )

        return select_count >= 2 or has_cte

    @staticmethod
    def _has_transaction_construct(
        original_sql: str,
        expression: exp.Expression,
    ) -> bool:
        normalized = original_sql.upper()

        transaction_constructs = (
            "BEGIN",
            "COMMIT",
            "ROLLBACK",
            "SAVEPOINT",
        )

        return any(
            re.search(
                rf"\b{construct}\b",
                normalized,
            )
            for construct in transaction_constructs
        )
