import pytest

from api.schemas.structural_optimization import (
    EvidenceStatus,
    OpportunityEvidenceScope,
    OptimizationOpportunityStatus,
    OptimizationOpportunityType,
    OptimizationRelevance,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralClassificationResult,
    StructuralFinding,
    StructuralFindingClassification,
    StructuralFindingClassificationType,
    StructuralLayer,
)
from api.services.structural_opportunity_analyzer import (
    StructuralOpportunityAnalyzer,
)


def _finding(
    layer: StructuralLayer,
    evidence: str | None = "where=customer_id = 10",
) -> StructuralFinding:
    return StructuralFinding(
        layer=layer,
        finding_type=layer.value,
        severity="INFO",
        description=f"Structural finding for {layer.value}.",
        evidence=evidence,
    )


def _analysis(
    findings: list[StructuralFinding],
) -> StructuralAnalysis:
    return StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        findings=findings,
    )


def _classification(
    *,
    finding_index: int,
    classification: StructuralFindingClassificationType,
    evidence_status: EvidenceStatus = EvidenceStatus.COMPLETE,
    relevance: OptimizationRelevance = (
        OptimizationRelevance.POTENTIALLY_RELEVANT
    ),
) -> StructuralFindingClassification:
    return StructuralFindingClassification(
        finding_index=finding_index,
        classification=classification,
        evidence_status=evidence_status,
        evidence_quality=(
            "EXACT"
            if evidence_status == EvidenceStatus.COMPLETE
            else "MISSING"
        ),
        optimization_relevance=relevance,
        rationale="Established structural classification.",
    )


def test_predicate_classification_creates_predicate_opportunity():
    analyzer = StructuralOpportunityAnalyzer()

    analysis = _analysis(
        [_finding(StructuralLayer.WHERE)]
    )

    classifications = StructuralClassificationResult(
        classifications=[
            _classification(
                finding_index=0,
                classification=StructuralFindingClassificationType.PREDICATE,
            )
        ]
    )

    result = analyzer.analyze(analysis, classifications)

    assert len(result.opportunities) == 1

    opportunity = result.opportunities[0]

    assert opportunity.finding_index == 0
    assert opportunity.opportunity_type == (
        OptimizationOpportunityType.PREDICATE_ANALYSIS
    )
    assert opportunity.status == OptimizationOpportunityStatus.IDENTIFIED
    assert opportunity.evidence_status == EvidenceStatus.COMPLETE
    assert opportunity.evidence_scope == OpportunityEvidenceScope.CLASSIFICATION


@pytest.mark.parametrize(
    ("classification", "expected_type"),
    [
        (
            StructuralFindingClassificationType.PREDICATE,
            OptimizationOpportunityType.PREDICATE_ANALYSIS,
        ),
        (
            StructuralFindingClassificationType.RELATIONSHIP,
            OptimizationOpportunityType.JOIN_ANALYSIS,
        ),
        (
            StructuralFindingClassificationType.AGGREGATION,
            OptimizationOpportunityType.AGGREGATION_ANALYSIS,
        ),
        (
            StructuralFindingClassificationType.WINDOW_OPERATION,
            OptimizationOpportunityType.WINDOW_ANALYSIS,
        ),
        (
            StructuralFindingClassificationType.ORDERING,
            OptimizationOpportunityType.ORDERING_ANALYSIS,
        ),
        (
            StructuralFindingClassificationType.ROW_LIMITING,
            OptimizationOpportunityType.ROW_LIMITING_ANALYSIS,
        ),
        (
            StructuralFindingClassificationType.NESTED_QUERY,
            OptimizationOpportunityType.NESTED_QUERY_ANALYSIS,
        ),
    ],
)
def test_relevant_classifications_map_to_opportunities(
    classification,
    expected_type,
):
    analyzer = StructuralOpportunityAnalyzer()

    analysis = _analysis(
        [_finding(StructuralLayer.WHERE)]
    )

    classifications = StructuralClassificationResult(
        classifications=[
            _classification(
                finding_index=0,
                classification=classification,
            )
        ]
    )

    result = analyzer.analyze(analysis, classifications)

    assert len(result.opportunities) == 1
    assert result.opportunities[0].opportunity_type == expected_type


@pytest.mark.parametrize(
    "classification",
    [
        StructuralFindingClassificationType.DIRECT_OPERATION,
        StructuralFindingClassificationType.SOURCE_DEFINITION,
        StructuralFindingClassificationType.SET_OPERATION,
    ],
)
def test_contextual_classifications_do_not_create_opportunities(
    classification,
):
    analyzer = StructuralOpportunityAnalyzer()

    analysis = _analysis(
        [_finding(StructuralLayer.SELECT)]
    )

    classifications = StructuralClassificationResult(
        classifications=[
            _classification(
                finding_index=0,
                classification=classification,
                relevance=OptimizationRelevance.CONTEXTUAL,
            )
        ]
    )

    result = analyzer.analyze(analysis, classifications)

    assert result.opportunities == []


def test_insufficient_evidence_produces_not_assessed_opportunity():
    analyzer = StructuralOpportunityAnalyzer()

    analysis = _analysis(
        [_finding(StructuralLayer.WHERE, evidence=None)]
    )

    classifications = StructuralClassificationResult(
        classifications=[
            _classification(
                finding_index=0,
                classification=StructuralFindingClassificationType.PREDICATE,
                evidence_status=EvidenceStatus.INSUFFICIENT,
                relevance=OptimizationRelevance.NOT_ASSESSED,
            )
        ]
    )

    result = analyzer.analyze(analysis, classifications)

    assert len(result.opportunities) == 1

    opportunity = result.opportunities[0]

    assert opportunity.status == OptimizationOpportunityStatus.NOT_ASSESSED
    assert opportunity.evidence_status == EvidenceStatus.INSUFFICIENT


def test_partial_evidence_can_identify_opportunity():
    analyzer = StructuralOpportunityAnalyzer()

    analysis = _analysis(
        [_finding(StructuralLayer.SUBQUERY, evidence="subquery_count=1")]
    )

    classifications = StructuralClassificationResult(
        classifications=[
            _classification(
                finding_index=0,
                classification=StructuralFindingClassificationType.NESTED_QUERY,
                evidence_status=EvidenceStatus.PARTIAL,
                relevance=OptimizationRelevance.POTENTIALLY_RELEVANT,
            )
        ]
    )

    result = analyzer.analyze(analysis, classifications)

    assert len(result.opportunities) == 1

    opportunity = result.opportunities[0]

    assert opportunity.status == OptimizationOpportunityStatus.IDENTIFIED
    assert opportunity.evidence_status == EvidenceStatus.PARTIAL


def test_structurally_neutral_classification_creates_neutral_opportunity():
    analyzer = StructuralOpportunityAnalyzer()

    analysis = _analysis(
        [_finding(StructuralLayer.WHERE)]
    )

    classifications = StructuralClassificationResult(
        classifications=[
            _classification(
                finding_index=0,
                classification=StructuralFindingClassificationType.PREDICATE,
                relevance=OptimizationRelevance.STRUCTURALLY_NEUTRAL,
            )
        ]
    )

    result = analyzer.analyze(analysis, classifications)

    assert len(result.opportunities) == 1

    opportunity = result.opportunities[0]

    assert opportunity.status == (
        OptimizationOpportunityStatus.STRUCTURALLY_NEUTRAL
    )


def test_finding_index_is_preserved():
    analyzer = StructuralOpportunityAnalyzer()

    analysis = _analysis(
        [
            _finding(StructuralLayer.SELECT),
            _finding(StructuralLayer.WHERE),
            _finding(StructuralLayer.ORDER_BY),
        ]
    )

    classifications = StructuralClassificationResult(
        classifications=[
            _classification(
                finding_index=2,
                classification=StructuralFindingClassificationType.ORDERING,
            ),
            _classification(
                finding_index=1,
                classification=StructuralFindingClassificationType.PREDICATE,
            ),
        ]
    )

    result = analyzer.analyze(analysis, classifications)

    assert [item.finding_index for item in result.opportunities] == [2, 1]


def test_invalid_finding_index_raises_error():
    analyzer = StructuralOpportunityAnalyzer()

    analysis = _analysis(
        [_finding(StructuralLayer.WHERE)]
    )

    classifications = StructuralClassificationResult(
        classifications=[
            _classification(
                finding_index=5,
                classification=StructuralFindingClassificationType.PREDICATE,
            )
        ]
    )

    with pytest.raises(ValueError, match="finding index"):
        analyzer.analyze(analysis, classifications)


def test_empty_classifications_return_empty_result():
    analyzer = StructuralOpportunityAnalyzer()

    analysis = _analysis(
        [_finding(StructuralLayer.WHERE)]
    )

    classifications = StructuralClassificationResult()

    result = analyzer.analyze(analysis, classifications)

    assert result.opportunities == []


def test_original_analysis_is_not_modified():
    analyzer = StructuralOpportunityAnalyzer()

    findings = [
        _finding(StructuralLayer.WHERE),
        _finding(StructuralLayer.ORDER_BY),
    ]

    analysis = _analysis(findings)

    original_findings = list(analysis.findings)

    classifications = StructuralClassificationResult(
        classifications=[
            _classification(
                finding_index=0,
                classification=StructuralFindingClassificationType.PREDICATE,
            ),
            _classification(
                finding_index=1,
                classification=StructuralFindingClassificationType.ORDERING,
            ),
        ]
    )

    analyzer.analyze(analysis, classifications)

    assert analysis.findings == original_findings
