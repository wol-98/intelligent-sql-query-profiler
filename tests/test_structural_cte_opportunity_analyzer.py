from api.schemas.structural_optimization import (
    CTECharacteristic,
    CTECharacteristicResult,
    CTECharacteristicType,
    EvidenceQuality,
    EvidenceStatus,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
)
from api.services.structural_cte_opportunity_analyzer import (
    StructuralCTEOpportunityAnalyzer,
)


def characteristic(
    finding_index,
    characteristic_type,
    evidence_status=EvidenceStatus.COMPLETE,
):
    return CTECharacteristic(
        finding_index=finding_index,
        characteristic_type=characteristic_type,
        evidence_status=evidence_status,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="Test CTE structural evidence.",
    )


def test_cte_definition_generates_cte_analysis_opportunity():
    result = StructuralCTEOpportunityAnalyzer().analyze(
        CTECharacteristicResult(
            characteristics=[
                characteristic(
                    0,
                    CTECharacteristicType.CTE_DEFINITION,
                )
            ]
        )
    )

    assert len(result.opportunities) == 1

    opportunity = result.opportunities[0]

    assert (
        opportunity.opportunity_type
        == OptimizationOpportunityType.CTE_ANALYSIS
    )
    assert opportunity.status == OptimizationOpportunityStatus.IDENTIFIED
    assert opportunity.finding_index == 0


def test_cte_reference_generates_cte_analysis_opportunity():
    result = StructuralCTEOpportunityAnalyzer().analyze(
        CTECharacteristicResult(
            characteristics=[
                characteristic(
                    2,
                    CTECharacteristicType.CTE_REFERENCE,
                )
            ]
        )
    )

    opportunity = result.opportunities[0]

    assert (
        opportunity.opportunity_type
        == OptimizationOpportunityType.CTE_ANALYSIS
    )
    assert opportunity.status == OptimizationOpportunityStatus.IDENTIFIED


def test_recursive_cte_generates_recursive_opportunity():
    result = StructuralCTEOpportunityAnalyzer().analyze(
        CTECharacteristicResult(
            characteristics=[
                characteristic(
                    4,
                    CTECharacteristicType.RECURSIVE_CTE,
                )
            ]
        )
    )

    opportunity = result.opportunities[0]

    assert (
        opportunity.opportunity_type
        == OptimizationOpportunityType.RECURSIVE_CTE_ANALYSIS
    )
    assert opportunity.status == OptimizationOpportunityStatus.IDENTIFIED


def test_insufficient_evidence_is_not_assessed():
    result = StructuralCTEOpportunityAnalyzer().analyze(
        CTECharacteristicResult(
            characteristics=[
                characteristic(
                    1,
                    CTECharacteristicType.CTE_DEFINITION,
                    EvidenceStatus.INSUFFICIENT,
                )
            ]
        )
    )

    opportunity = result.opportunities[0]

    assert opportunity.status == OptimizationOpportunityStatus.NOT_ASSESSED
    assert (
        opportunity.evidence_status
        == EvidenceStatus.INSUFFICIENT
    )


def test_multiple_cte_characteristics_preserve_order():
    result = StructuralCTEOpportunityAnalyzer().analyze(
        CTECharacteristicResult(
            characteristics=[
                characteristic(
                    0,
                    CTECharacteristicType.CTE_DEFINITION,
                ),
                characteristic(
                    1,
                    CTECharacteristicType.CTE_REFERENCE,
                ),
                characteristic(
                    2,
                    CTECharacteristicType.RECURSIVE_CTE,
                ),
            ]
        )
    )

    assert [
        opportunity.finding_index
        for opportunity in result.opportunities
    ] == [0, 1, 2]

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        OptimizationOpportunityType.CTE_ANALYSIS,
        OptimizationOpportunityType.CTE_ANALYSIS,
        OptimizationOpportunityType.RECURSIVE_CTE_ANALYSIS,
    ]
