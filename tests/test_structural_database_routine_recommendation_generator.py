from sqlglot import parse_one

from api.schemas.structural_optimization import (
    CandidateStatus,
    DatabaseRoutineRecommendationType,
    EvidenceStatus,
    OpportunityEvidenceScope,
    ProceduralWorkloadOpportunityStatus,
    ProceduralWorkloadOpportunityType,
    SemanticSafetyStatus,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralDatabaseRoutineRecommendationResult,
    StructuralFinding,
    StructuralLayer,
    StructuralProceduralWorkloadOpportunity,
    StructuralProceduralWorkloadOpportunityResult,
)
from api.services.structural_database_routine_recommendation_generator import (
    StructuralDatabaseRoutineRecommendationGenerator,
)
from api.services.structural_sql_analyzer import StructuralSQLAnalyzer


SQL = """
SELECT *
FROM orders
WHERE customer_id = $1
"""


def make_opportunity(
    opportunity_type: ProceduralWorkloadOpportunityType,
    *,
    finding_index: int = 0,
    status: ProceduralWorkloadOpportunityStatus = (
        ProceduralWorkloadOpportunityStatus.IDENTIFIED
    ),
    evidence_status: EvidenceStatus = EvidenceStatus.COMPLETE,
) -> StructuralProceduralWorkloadOpportunity:
    return StructuralProceduralWorkloadOpportunity(
        finding_index=finding_index,
        opportunity_type=opportunity_type,
        status=status,
        evidence_status=evidence_status,
        evidence_scope=OpportunityEvidenceScope.FINDING,
        rationale="Procedural workload opportunity identified.",
    )


def make_result(
    *opportunities: StructuralProceduralWorkloadOpportunity,
) -> StructuralProceduralWorkloadOpportunityResult:
    return StructuralProceduralWorkloadOpportunityResult(
        opportunities=list(opportunities)
    )


def make_analysis() -> StructuralAnalysis:
    expression = parse_one(
        SQL,
        dialect="postgres",
    )

    return StructuralSQLAnalyzer().analyze(
        expression
    )


def test_parameterized_operation_generates_function_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
                )
            ),
            SQL,
        )
    )

    assert isinstance(
        result,
        StructuralDatabaseRoutineRecommendationResult,
    )

    assert len(result.recommendations) == 1

    recommendation = result.recommendations[0]

    assert recommendation.recommendation_id == "ROUTINE-REC-0001"

    assert (
        recommendation.recommendation_type
        == DatabaseRoutineRecommendationType.FUNCTION
    )

    assert recommendation.status == CandidateStatus.CANDIDATE

    assert (
        recommendation.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )

    assert recommendation.evidence_status == EvidenceStatus.COMPLETE

    assert recommendation.original_sql == SQL


def test_multi_step_operation_generates_procedure_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
                )
            ),
            SQL,
        )
    )

    recommendation = result.recommendations[0]

    assert (
        recommendation.recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )

    assert recommendation.status == CandidateStatus.CANDIDATE

    assert (
        recommendation.semantic_safety
        == SemanticSafetyStatus.NOT_ASSESSED
    )


def test_reusable_computation_generates_function_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
                )
            ),
            SQL,
        )
    )

    recommendation = result.recommendations[0]

    assert (
        recommendation.recommendation_type
        == DatabaseRoutineRecommendationType.FUNCTION
    )


def test_data_mutation_workflow_generates_procedure_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.DATA_MUTATION_WORKFLOW
                )
            ),
            SQL,
        )
    )

    assert (
        result.recommendations[0].recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_complex_procedural_logic_generates_procedure_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.COMPLEX_PROCEDURAL_LOGIC
                )
            ),
            SQL,
        )
    )

    assert (
        result.recommendations[0].recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_side_effecting_workflow_generates_procedure_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW
                )
            ),
            SQL,
        )
    )

    assert (
        result.recommendations[0].recommendation_type
        == DatabaseRoutineRecommendationType.PROCEDURE
    )


def test_partial_evidence_does_not_generate_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
                    evidence_status=EvidenceStatus.PARTIAL,
                )
            ),
            SQL,
        )
    )

    assert result.recommendations == []


def test_insufficient_evidence_does_not_generate_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION,
                    evidence_status=EvidenceStatus.INSUFFICIENT,
                )
            ),
            SQL,
        )
    )

    assert result.recommendations == []


def test_not_assessed_opportunity_does_not_generate_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
                    status=(
                        ProceduralWorkloadOpportunityStatus.NOT_ASSESSED
                    ),
                )
            ),
            SQL,
        )
    )

    assert result.recommendations == []


def test_structurally_neutral_opportunity_does_not_generate_candidate():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
                    status=(
                        ProceduralWorkloadOpportunityStatus.STRUCTURALLY_NEUTRAL
                    ),
                )
            ),
            SQL,
        )
    )

    assert result.recommendations == []


def test_candidate_source_layer_is_preserved():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
                    finding_index=2,
                )
            ),
            SQL,
        )
    )

    recommendation = result.recommendations[0]

    assert (
        recommendation.source_layer
        == analysis.findings[2].layer
    )


def test_candidate_order_is_deterministic():
    analysis = make_analysis()

    opportunities = make_result(
        make_opportunity(
            ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
        ),
        make_opportunity(
            ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION
        ),
        make_opportunity(
            ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
        ),
    )

    generator = StructuralDatabaseRoutineRecommendationGenerator()

    first = generator.generate(
        analysis,
        opportunities,
        SQL,
    )

    second = generator.generate(
        analysis,
        opportunities,
        SQL,
    )

    assert first == second

    assert [
        recommendation.recommendation_id
        for recommendation in first.recommendations
    ] == [
        "ROUTINE-REC-0001",
        "ROUTINE-REC-0002",
        "ROUTINE-REC-0003",
    ]


def test_ineligible_opportunity_does_not_consume_candidate_id():
    analysis = make_analysis()

    opportunities = make_result(
        make_opportunity(
            ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
            evidence_status=EvidenceStatus.PARTIAL,
        ),
        make_opportunity(
            ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION,
        ),
    )

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            opportunities,
            SQL,
        )
    )

    assert len(result.recommendations) == 1

    assert (
        result.recommendations[0].recommendation_id
        == "ROUTINE-REC-0001"
    )


def test_invalid_finding_index_raises_error():
    analysis = make_analysis()

    opportunities = make_result(
        make_opportunity(
            ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
            finding_index=999,
        )
    )

    try:
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            opportunities,
            SQL,
        )
    except ValueError as exc:
        assert "finding index" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for invalid finding index"
        )


def test_original_sql_is_preserved_exactly():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
                )
            ),
            SQL,
        )
    )

    assert result.recommendations[0].original_sql == SQL


def test_generator_does_not_modify_analysis():
    analysis = make_analysis()

    before = analysis.model_dump()

    StructuralDatabaseRoutineRecommendationGenerator().generate(
        analysis,
        make_result(
            make_opportunity(
                ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
            )
        ),
        SQL,
    )

    assert analysis.model_dump() == before


def test_function_title_is_deterministic():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION
                )
            ),
            SQL,
        )
    )

    assert (
        result.recommendations[0].title
        == "Database function architectural candidate"
    )


def test_procedure_title_is_deterministic():
    analysis = make_analysis()

    result = (
        StructuralDatabaseRoutineRecommendationGenerator().generate(
            analysis,
            make_result(
                make_opportunity(
                    ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION
                )
            ),
            SQL,
        )
    )

    assert (
        result.recommendations[0].title
        == "Stored procedure architectural candidate"
    )
