import pytest
from pydantic import ValidationError

from api.schemas.structural_optimization import (
    EvidenceQuality,
    EvidenceStatus,
    OptimizationRelevance,
    StructuralClassificationResult,
    StructuralFindingClassification,
    StructuralFindingClassificationType,
)


def test_structural_finding_classification_accepts_valid_values():
    result = StructuralFindingClassification(
        finding_index=0,
        classification=StructuralFindingClassificationType.PREDICATE,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        optimization_relevance=OptimizationRelevance.POTENTIALLY_RELEVANT,
        rationale="The finding contains an explicit WHERE predicate.",
    )

    assert result.finding_index == 0
    assert result.classification == StructuralFindingClassificationType.PREDICATE
    assert result.evidence_status == EvidenceStatus.COMPLETE
    assert result.evidence_quality == EvidenceQuality.EXACT
    assert (
        result.optimization_relevance
        == OptimizationRelevance.POTENTIALLY_RELEVANT
    )


def test_structural_finding_classification_rejects_negative_index():
    with pytest.raises(ValidationError):
        StructuralFindingClassification(
            finding_index=-1,
            classification=StructuralFindingClassificationType.PREDICATE,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_quality=EvidenceQuality.EXACT,
            optimization_relevance=OptimizationRelevance.POTENTIALLY_RELEVANT,
            rationale="Invalid finding index.",
        )


def test_structural_finding_classification_requires_rationale():
    with pytest.raises(ValidationError):
        StructuralFindingClassification(
            finding_index=0,
            classification=StructuralFindingClassificationType.PREDICATE,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_quality=EvidenceQuality.EXACT,
            optimization_relevance=OptimizationRelevance.POTENTIALLY_RELEVANT,
        )


def test_structural_classification_result_defaults_to_empty():
    result = StructuralClassificationResult()

    assert result.classifications == []


def test_structural_classification_result_accepts_multiple_classifications():
    result = StructuralClassificationResult(
        classifications=[
            StructuralFindingClassification(
                finding_index=0,
                classification=StructuralFindingClassificationType.DIRECT_OPERATION,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                optimization_relevance=OptimizationRelevance.CONTEXTUAL,
                rationale="Select-list structure is explicitly available.",
            )
        ]
    )

    assert len(result.classifications) == 1


def test_existing_evidence_status_enum_is_reused():
    assert set(EvidenceStatus) == {
        EvidenceStatus.COMPLETE,
        EvidenceStatus.PARTIAL,
        EvidenceStatus.INSUFFICIENT,
    }


def test_classification_enum_values_are_stable():
    assert StructuralFindingClassificationType.PREDICATE.value == "PREDICATE"
    assert StructuralFindingClassificationType.AGGREGATION.value == "AGGREGATION"
    assert StructuralFindingClassificationType.NESTED_QUERY.value == "NESTED_QUERY"
    assert StructuralFindingClassificationType.SET_OPERATION.value == "SET_OPERATION"


def test_evidence_quality_enum_values_are_stable():
    assert EvidenceQuality.EXACT.value == "EXACT"
    assert EvidenceQuality.STRUCTURED.value == "STRUCTURED"
    assert EvidenceQuality.SUMMARY.value == "SUMMARY"
    assert EvidenceQuality.MISSING.value == "MISSING"


def test_optimization_relevance_enum_values_are_stable():
    assert OptimizationRelevance.NOT_ASSESSED.value == "NOT_ASSESSED"
    assert (
        OptimizationRelevance.POTENTIALLY_RELEVANT.value
        == "POTENTIALLY_RELEVANT"
    )
    assert OptimizationRelevance.CONTEXTUAL.value == "CONTEXTUAL"
    assert (
        OptimizationRelevance.STRUCTURALLY_NEUTRAL.value
        == "STRUCTURALLY_NEUTRAL"
    )
