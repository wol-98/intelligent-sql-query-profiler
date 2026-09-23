from api.schemas.structural_optimization import (
    CandidateStatus,
    DatabaseRoutineRecommendationType,
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralDatabaseRoutineRecommendation,
    StructuralDatabaseRoutineRecommendationResult,
)
from api.services.structural_database_routine_recommendation_integration import (
    StructuralDatabaseRoutineRecommendationIntegrator,
)


FUNCTION_SQL = """
SELECT total_amount
FROM orders
WHERE customer_id = $1;
"""

PROCEDURE_SQL = """
WITH recent_orders AS (
    SELECT order_id, customer_id
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT order_id, customer_id
FROM recent_orders;
"""


def make_recommendation(
    recommendation_id: str,
    recommendation_type: DatabaseRoutineRecommendationType,
    original_sql: str,
) -> StructuralDatabaseRoutineRecommendation:
    return StructuralDatabaseRoutineRecommendation(
        recommendation_id=recommendation_id,
        recommendation_type=recommendation_type,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.NOT_ASSESSED,
        evidence_status=EvidenceStatus.COMPLETE,
        title="Database routine architectural candidate",
        rationale="Structural procedural workload opportunity detected.",
        source_layer=None,
        original_sql=original_sql,
    )


def test_empty_result_produces_empty_analysis() -> None:
    result = StructuralDatabaseRoutineRecommendationResult()

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    assert integrated.analyses == ()


def test_function_candidate_receives_function_preconditions() -> None:
    recommendation = make_recommendation(
        "ROUTINE-REC-0001",
        DatabaseRoutineRecommendationType.FUNCTION,
        FUNCTION_SQL,
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[recommendation]
    )

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    assert len(integrated.analyses) == 1

    analysis = integrated.analyses[0]

    assert (
        analysis.recommendation.recommendation_id
        == "ROUTINE-REC-0001"
    )

    assert (
        analysis.semantic_preconditions.recommendation_type
        == DatabaseRoutineRecommendationType.FUNCTION
    )

    assert (
        analysis.semantic_preconditions.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )


def test_procedure_candidate_receives_procedure_preconditions() -> None:
    recommendation = make_recommendation(
        "ROUTINE-REC-0002",
        DatabaseRoutineRecommendationType.PROCEDURE,
        PROCEDURE_SQL,
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[recommendation]
    )

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    assert len(integrated.analyses) == 1

    analysis = integrated.analyses[0]

    assert (
        analysis.semantic_preconditions.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )

    assert (
        analysis.semantic_preconditions.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )


def test_candidate_is_preserved_unchanged() -> None:
    recommendation = make_recommendation(
        "ROUTINE-REC-0003",
        DatabaseRoutineRecommendationType.FUNCTION,
        FUNCTION_SQL,
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[recommendation]
    )

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    preserved = integrated.analyses[0].recommendation

    assert preserved == recommendation
    assert preserved.status == CandidateStatus.CANDIDATE
    assert (
        preserved.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )
    assert preserved.original_sql == FUNCTION_SQL


def test_candidate_identity_is_preserved() -> None:
    recommendation = make_recommendation(
        "ROUTINE-REC-0004",
        DatabaseRoutineRecommendationType.FUNCTION,
        FUNCTION_SQL,
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[recommendation]
    )

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    assert integrated.analyses[0].recommendation is recommendation


def test_original_candidate_order_is_preserved() -> None:
    first = make_recommendation(
        "ROUTINE-REC-0005",
        DatabaseRoutineRecommendationType.FUNCTION,
        FUNCTION_SQL,
    )

    second = make_recommendation(
        "ROUTINE-REC-0006",
        DatabaseRoutineRecommendationType.PROCEDURE,
        PROCEDURE_SQL,
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[first, second]
    )

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    assert [
        analysis.recommendation.recommendation_id
        for analysis in integrated.analyses
    ] == [
        "ROUTINE-REC-0005",
        "ROUTINE-REC-0006",
    ]

    assert [
        analysis.semantic_preconditions.recommendation_type
        for analysis in integrated.analyses
    ] == [
        DatabaseRoutineRecommendationType.FUNCTION,
        DatabaseRoutineRecommendationType.PROCEDURE,
    ]


def test_parse_failure_does_not_upgrade_candidate_safety() -> None:
    recommendation = make_recommendation(
        "ROUTINE-REC-0007",
        DatabaseRoutineRecommendationType.FUNCTION,
        "SELECT FROM",
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[recommendation]
    )

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    analysis = integrated.analyses[0]

    assert (
        analysis.semantic_preconditions.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )

    assert (
        analysis.recommendation.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )


def test_precondition_findings_are_attached() -> None:
    recommendation = make_recommendation(
        "ROUTINE-REC-0008",
        DatabaseRoutineRecommendationType.FUNCTION,
        FUNCTION_SQL,
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[recommendation]
    )

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    findings = (
        integrated
        .analyses[0]
        .semantic_preconditions
        .findings
    )

    assert findings

    names = {finding.name for finding in findings}

    assert "PARAMETER_SIGNATURE" in names
    assert "RETURN_VALUE_SEMANTICS" in names
    assert "INPUT_DATA_DEPENDENCIES" in names


def test_integration_does_not_generate_sql() -> None:
    recommendation = make_recommendation(
        "ROUTINE-REC-0009",
        DatabaseRoutineRecommendationType.FUNCTION,
        FUNCTION_SQL,
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[recommendation]
    )

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    analysis = integrated.analyses[0]

    assert not hasattr(
        analysis,
        "generated_sql",
    )

    assert not hasattr(
        analysis,
        "routine_ddl",
    )


def test_integration_does_not_execute_sql() -> None:
    recommendation = make_recommendation(
        "ROUTINE-REC-0010",
        DatabaseRoutineRecommendationType.FUNCTION,
        FUNCTION_SQL,
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[recommendation]
    )

    integrated = (
        StructuralDatabaseRoutineRecommendationIntegrator()
        .analyze(result)
    )

    assert len(integrated.analyses) == 1
