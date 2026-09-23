from __future__ import annotations

from dataclasses import dataclass

from api.schemas.structural_optimization import (
    DatabaseRoutineRecommendationType,
)


@dataclass(frozen=True)
class DatabaseRoutineSemanticPreconditionFinding:
    """
    One structural condition relevant to later routine validation.
    """

    name: str
    detected: bool
    rationale: str


@dataclass(frozen=True)
class DatabaseRoutineSemanticPreconditionResult:
    """
    Deterministic structural precondition analysis.

    This result does not establish behavioral equivalence, correctness,
    safety, or production suitability.
    """

    recommendation_type: DatabaseRoutineRecommendationType
    semantic_safety: SemanticSafetyStatus
    findings: tuple[
        DatabaseRoutineSemanticPreconditionFinding,
        ...,
    ] = ()


@dataclass(frozen=True)
class DatabaseRoutineSemanticPreconditionRule:
    """
    Preconditions required for later semantic/behavioral validation.
    """

    recommendation_type: DatabaseRoutineRecommendationType
    required_conditions: tuple[str, ...]
    rationale: str


class DatabaseRoutineSemanticPreconditionRuleEngine:
    """
    Resolve deterministic semantic/behavioral precondition rules for
    database function and stored-procedure candidates.
    """

    FUNCTION_REQUIRED_CONDITIONS = (
        "PARAMETER_SIGNATURE",
        "RETURN_VALUE_SEMANTICS",
        "INPUT_DATA_DEPENDENCIES",
        "NULL_AND_TYPE_SEMANTICS",
        "DETERMINISM_VOLATILITY",
        "ERROR_BEHAVIOR",
        "SIDE_EFFECT_BEHAVIOR",
        "SECURITY_CONTEXT",
    )

    PROCEDURE_REQUIRED_CONDITIONS = (
        "PARAMETER_SIGNATURE",
        "OUTPUT_OR_RESULT_SEMANTICS",
        "MULTI_STEP_EXECUTION",
        "DATA_MUTATION_BEHAVIOR",
        "TRANSACTION_BEHAVIOR",
        "SIDE_EFFECT_BEHAVIOR",
        "ERROR_AND_ROLLBACK_BEHAVIOR",
        "SECURITY_CONTEXT",
    )

    @classmethod
    def with_default_rules(
        cls,
    ) -> "DatabaseRoutineSemanticPreconditionRuleEngine":
        return cls(
            rules=(
                DatabaseRoutineSemanticPreconditionRule(
                    recommendation_type=(
                        DatabaseRoutineRecommendationType.FUNCTION
                    ),
                    required_conditions=(
                        cls.FUNCTION_REQUIRED_CONDITIONS
                    ),
                    rationale=(
                        "Function candidates require validation of "
                        "parameter, return-value, dependency, type, "
                        "volatility, error, side-effect, and security "
                        "semantics before acceptance."
                    ),
                ),
                DatabaseRoutineSemanticPreconditionRule(
                    recommendation_type=(
                        DatabaseRoutineRecommendationType.PROCEDURE
                    ),
                    required_conditions=(
                        cls.PROCEDURE_REQUIRED_CONDITIONS
                    ),
                    rationale=(
                        "Procedure candidates require validation of "
                        "parameter, output, execution sequencing, "
                        "mutation, transaction, side-effect, error, "
                        "rollback, and security semantics before "
                        "acceptance."
                    ),
                ),
            )
        )

    def __init__(
        self,
        *,
        rules: tuple[
            DatabaseRoutineSemanticPreconditionRule,
            ...,
        ],
    ) -> None:
        self._rules = {
            rule.recommendation_type: rule
            for rule in rules
        }

        if len(self._rules) != len(rules):
            raise ValueError(
                "Duplicate database routine semantic precondition rule."
            )

    def get_rule(
        self,
        recommendation_type: DatabaseRoutineRecommendationType,
    ) -> DatabaseRoutineSemanticPreconditionRule:
        try:
            return self._rules[recommendation_type]
        except KeyError as exc:
            raise ValueError(
                "No database routine semantic precondition rule exists "
                f"for {recommendation_type}"
            ) from exc
