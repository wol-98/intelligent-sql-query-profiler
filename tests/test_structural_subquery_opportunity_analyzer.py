from api.schemas.structural_optimization import (
    EvidenceQuality,
    EvidenceStatus,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    SubqueryAlternativeCharacteristic,
    SubqueryAlternativeCharacteristicResult,
    SubqueryAlternativeCharacteristicType,
)
from api.services.structural_subquery_opportunity_analyzer import (
    StructuralSubqueryOpportunityAnalyzer,
)


def _characteristic(
    finding_index,
    characteristic_type,
    evidence_status=EvidenceStatus.COMPLETE,
):
    return SubqueryAlternativeCharacteristic(
        finding_index=finding_index,
        characteristic_type=characteristic_type,
        evidence_status=evidence_status,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="Structural subquery evidence.",
    )


def test_exists_creates_exists_opportunity():
    result = StructuralSubqueryOpportunityAnalyzer().analyze(
        SubqueryAlternativeCharacteristicResult(
            characteristics=[
                _characteristic(
                    2,
                    SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE,
                )
            ]
        )
    )

    assert len(result.opportunities) == 1

    opportunity = result.opportunities[0]

    assert (
        opportunity.opportunity_type
        == OptimizationOpportunityType.SUBQUERY_EXISTS_ANALYSIS
    )
    assert opportunity.status == OptimizationOpportunityStatus.IDENTIFIED
    assert opportunity.finding_index == 2


def test_in_creates_in_opportunity():
    result = StructuralSubqueryOpportunityAnalyzer().analyze(
        SubqueryAlternativeCharacteristicResult(
            characteristics=[
                _characteristic(
                    3,
                    SubqueryAlternativeCharacteristicType.IN_PREDICATE,
                )
            ]
        )
    )

    assert (
        result.opportunities[0].opportunity_type
        == OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS
    )


def test_any_creates_any_opportunity():
    result = StructuralSubqueryOpportunityAnalyzer().analyze(
        SubqueryAlternativeCharacteristicResult(
            characteristics=[
                _characteristic(
                    4,
                    SubqueryAlternativeCharacteristicType.ANY_PREDICATE,
                )
            ]
        )
    )

    assert (
        result.opportunities[0].opportunity_type
        == OptimizationOpportunityType.SUBQUERY_ANY_ANALYSIS
    )


def test_derived_table_creates_derived_table_opportunity():
    result = StructuralSubqueryOpportunityAnalyzer().analyze(
        SubqueryAlternativeCharacteristicResult(
            characteristics=[
                _characteristic(
                    5,
                    SubqueryAlternativeCharacteristicType.DERIVED_TABLE,
                )
            ]
        )
    )

    assert (
        result.opportunities[0].opportunity_type
        == OptimizationOpportunityType.DERIVED_TABLE_ANALYSIS
    )


def test_correlated_subquery_alone_does_not_create_opportunity():
    result = StructuralSubqueryOpportunityAnalyzer().analyze(
        SubqueryAlternativeCharacteristicResult(
            characteristics=[
                _characteristic(
                    6,
                    SubqueryAlternativeCharacteristicType.CORRELATED_SUBQUERY,
                )
            ]
        )
    )

    assert result.opportunities == []


def test_insufficient_evidence_is_not_assessed():
    result = StructuralSubqueryOpportunityAnalyzer().analyze(
        SubqueryAlternativeCharacteristicResult(
            characteristics=[
                _characteristic(
                    7,
                    SubqueryAlternativeCharacteristicType.IN_PREDICATE,
                    EvidenceStatus.INSUFFICIENT,
                )
            ]
        )
    )

    opportunity = result.opportunities[0]

    assert opportunity.status == OptimizationOpportunityStatus.NOT_ASSESSED
    assert opportunity.evidence_status == EvidenceStatus.INSUFFICIENT


def test_multiple_characteristics_preserve_order():
    result = StructuralSubqueryOpportunityAnalyzer().analyze(
        SubqueryAlternativeCharacteristicResult(
            characteristics=[
                _characteristic(
                    1,
                    SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE,
                ),
                _characteristic(
                    2,
                    SubqueryAlternativeCharacteristicType.IN_PREDICATE,
                ),
                _characteristic(
                    3,
                    SubqueryAlternativeCharacteristicType.ANY_PREDICATE,
                ),
                _characteristic(
                    4,
                    SubqueryAlternativeCharacteristicType.DERIVED_TABLE,
                ),
            ]
        )
    )

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        OptimizationOpportunityType.SUBQUERY_EXISTS_ANALYSIS,
        OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS,
        OptimizationOpportunityType.SUBQUERY_ANY_ANALYSIS,
        OptimizationOpportunityType.DERIVED_TABLE_ANALYSIS,
    ]


def test_opportunity_uses_finding_evidence_scope():
    result = StructuralSubqueryOpportunityAnalyzer().analyze(
        SubqueryAlternativeCharacteristicResult(
            characteristics=[
                _characteristic(
                    1,
                    SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE,
                )
            ]
        )
    )

    assert (
        result.opportunities[0].evidence_scope.value
        == "FINDING"
    )
