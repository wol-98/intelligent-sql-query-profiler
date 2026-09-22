import pytest
from pydantic import ValidationError

from api.schemas.structural_optimization import (
    CandidateStatus,
    DatabaseRoutineRecommendationType,
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralDatabaseRoutineRecommendation,
    StructuralDatabaseRoutineRecommendationResult,
    StructuralLayer,
)


ORIGINAL_SQL = """
SELECT
    customer_id,
    COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
"""


def test_function_recommendation_contract():
    recommendation = StructuralDatabaseRoutineRecommendation(
        recommendation_id="ROUTINE-REC-0001",
        recommendation_type=(
            DatabaseRoutineRecommendationType.FUNCTION
        ),
        evidence_status=EvidenceStatus.COMPLETE,
        title="FUNCTION architectural candidate",
        rationale=(
            "The query structure may be suitable for later "
            "function-oriented analysis."
        ),
        original_sql=ORIGINAL_SQL,
    )

    assert recommendation.recommendation_id == "ROUTINE-REC-0001"

    assert (
        recommendation.recommendation_type
        == DatabaseRoutineRecommendationType.FUNCTION
    )


def test_procedure_recommendation_contract():
    recommendation = StructuralDatabaseRoutineRecommendation(
        recommendation_id="ROUTINE-REC-0002",
        recommendation_type=(
            DatabaseRoutineRecommendationType.PROCEDURE
        ),
        evidence_status=EvidenceStatus.COMPLETE,
        title="PROCEDURE architectural candidate",
        rationale=(
            "The query structure may be suitable for later "
            "procedure-oriented analysis."
        ),
        original_sql=ORIGINAL_SQL,
    )

    assert recommendation.recommendation_id == "ROUTINE-REC-0002"

    assert (
        recommendation.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_recommendation_defaults_do_not_claim_validation():
    recommendation = StructuralDatabaseRoutineRecommendation(
        recommendation_id="ROUTINE-REC-0003",
        recommendation_type=(
            DatabaseRoutineRecommendationType.FUNCTION
        ),
        evidence_status=EvidenceStatus.COMPLETE,
        title="FUNCTION candidate",
        rationale="Candidate requires later validation.",
        original_sql=ORIGINAL_SQL,
    )

    assert recommendation.status == CandidateStatus.CANDIDATE

    assert (
        recommendation.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )


def test_source_layer_is_optional():
    recommendation = StructuralDatabaseRoutineRecommendation(
        recommendation_id="ROUTINE-REC-0004",
        recommendation_type=(
            DatabaseRoutineRecommendationType.FUNCTION
        ),
        evidence_status=EvidenceStatus.COMPLETE,
        title="FUNCTION candidate",
        rationale="Source layer is not required at this stage.",
        original_sql=ORIGINAL_SQL,
    )

    assert recommendation.source_layer is None


def test_source_layer_can_be_preserved():
    recommendation = StructuralDatabaseRoutineRecommendation(
        recommendation_id="ROUTINE-REC-0005",
        recommendation_type=(
            DatabaseRoutineRecommendationType.PROCEDURE
        ),
        evidence_status=EvidenceStatus.COMPLETE,
        title="PROCEDURE candidate",
        rationale="Candidate preserves structural provenance.",
        source_layer=StructuralLayer.GROUP_BY,
        original_sql=ORIGINAL_SQL,
    )

    assert recommendation.source_layer == StructuralLayer.GROUP_BY


def test_original_sql_is_required():
    with pytest.raises(ValidationError):
        StructuralDatabaseRoutineRecommendation(
            recommendation_id="ROUTINE-REC-0006",
            recommendation_type=(
                DatabaseRoutineRecommendationType.FUNCTION
            ),
            evidence_status=EvidenceStatus.COMPLETE,
            title="FUNCTION candidate",
            rationale="Original SQL is required for provenance.",
        )


def test_recommendation_id_is_required():
    with pytest.raises(ValidationError):
        StructuralDatabaseRoutineRecommendation(
            recommendation_type=(
                DatabaseRoutineRecommendationType.FUNCTION
            ),
            evidence_status=EvidenceStatus.COMPLETE,
            title="FUNCTION candidate",
            rationale="Recommendation ID is required.",
            original_sql=ORIGINAL_SQL,
        )


def test_result_defaults_to_empty_list():
    result = StructuralDatabaseRoutineRecommendationResult()

    assert result.recommendations == []


def test_result_preserves_recommendation_order():
    first = StructuralDatabaseRoutineRecommendation(
        recommendation_id="ROUTINE-REC-0007",
        recommendation_type=(
            DatabaseRoutineRecommendationType.FUNCTION
        ),
        evidence_status=EvidenceStatus.COMPLETE,
        title="FUNCTION candidate",
        rationale="First candidate.",
        original_sql=ORIGINAL_SQL,
    )

    second = StructuralDatabaseRoutineRecommendation(
        recommendation_id="ROUTINE-REC-0008",
        recommendation_type=(
            DatabaseRoutineRecommendationType.PROCEDURE
        ),
        evidence_status=EvidenceStatus.PARTIAL,
        title="PROCEDURE candidate",
        rationale="Second candidate.",
        original_sql=ORIGINAL_SQL,
    )

    result = StructuralDatabaseRoutineRecommendationResult(
        recommendations=[
            first,
            second,
        ]
    )

    assert [
        recommendation.recommendation_id
        for recommendation in result.recommendations
    ] == [
        "ROUTINE-REC-0007",
        "ROUTINE-REC-0008",
    ]


def test_evidence_status_is_preserved():
    recommendation = StructuralDatabaseRoutineRecommendation(
        recommendation_id="ROUTINE-REC-0009",
        recommendation_type=(
            DatabaseRoutineRecommendationType.PROCEDURE
        ),
        evidence_status=EvidenceStatus.PARTIAL,
        title="PROCEDURE candidate",
        rationale="Partial evidence remains explicitly represented.",
        original_sql=ORIGINAL_SQL,
    )

    assert recommendation.evidence_status == EvidenceStatus.PARTIAL
