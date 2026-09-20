"""Tests for the M21.7 structural alternative contract."""

import pytest
from pydantic import ValidationError

from api.schemas.structural_optimization import (
    CandidateStatus,
    EvidenceStatus,
    SemanticSafetyStatus,
    StructuralAlternativeCandidate,
    StructuralAlternativeResult,
    StructuralLayer,
    SubqueryAlternativeType,
)


ORIGINAL_SQL = (
    "SELECT customer_id "
    "FROM orders "
    "WHERE customer_id IN "
    "(SELECT customer_id FROM customers)"
)


@pytest.mark.parametrize(
    "alternative_type",
    [
        SubqueryAlternativeType.EXISTS,
        SubqueryAlternativeType.IN,
        SubqueryAlternativeType.ANY,
        SubqueryAlternativeType.DERIVED_TABLE,
    ],
)
def test_all_structural_alternative_types_are_supported(
    alternative_type,
):
    candidate = StructuralAlternativeCandidate(
        candidate_id="ALT-0001",
        alternative_type=alternative_type,
        evidence_status=EvidenceStatus.COMPLETE,
        title="Structural alternative candidate",
        rationale="Candidate identified for later semantic validation.",
        source_layer=StructuralLayer.SUBQUERY,
        original_sql=ORIGINAL_SQL,
    )

    assert candidate.alternative_type == alternative_type


def test_candidate_defaults_to_unvalidated_and_unassessed() -> None:
    candidate = StructuralAlternativeCandidate(
        candidate_id="ALT-0001",
        alternative_type=SubqueryAlternativeType.EXISTS,
        evidence_status=EvidenceStatus.COMPLETE,
        title="EXISTS alternative",
        rationale="Requires later validation.",
        original_sql=ORIGINAL_SQL,
    )

    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert candidate.alternative_sql is None


def test_candidate_can_explicitly_require_semantic_validation() -> None:
    candidate = StructuralAlternativeCandidate(
        candidate_id="ALT-0002",
        alternative_type=SubqueryAlternativeType.IN,
        status=CandidateStatus.CANDIDATE,
        semantic_safety=SemanticSafetyStatus.REQUIRES_VALIDATION,
        evidence_status=EvidenceStatus.PARTIAL,
        title="IN alternative",
        rationale="Semantic equivalence requires controlled validation.",
        source_layer=StructuralLayer.WHERE,
        original_sql=ORIGINAL_SQL,
        alternative_sql=(
            "SELECT customer_id "
            "FROM orders "
            "WHERE EXISTS "
            "(SELECT 1 FROM customers WHERE customers.customer_id = orders.customer_id)"
        ),
    )

    assert (
        candidate.semantic_safety
        == SemanticSafetyStatus.REQUIRES_VALIDATION
    )
    assert candidate.alternative_sql is not None


def test_candidate_can_represent_unsafe_alternative() -> None:
    candidate = StructuralAlternativeCandidate(
        candidate_id="ALT-0003",
        alternative_type=SubqueryAlternativeType.ANY,
        semantic_safety=SemanticSafetyStatus.UNSAFE,
        evidence_status=EvidenceStatus.COMPLETE,
        title="ANY alternative",
        rationale="The proposed transformation is not semantically safe.",
        original_sql=ORIGINAL_SQL,
    )

    assert candidate.semantic_safety == SemanticSafetyStatus.UNSAFE


def test_candidate_preserves_original_sql_exactly() -> None:
    original_sql = (
        "select  customer_id\n"
        "FROM orders\n"
        "where customer_id IN "
        "(SELECT customer_id FROM customers)"
    )

    candidate = StructuralAlternativeCandidate(
        candidate_id="ALT-0004",
        alternative_type=SubqueryAlternativeType.IN,
        evidence_status=EvidenceStatus.COMPLETE,
        title="IN alternative",
        rationale="Original SQL preserved for provenance.",
        original_sql=original_sql,
    )

    assert candidate.original_sql == original_sql


def test_source_layer_is_optional() -> None:
    candidate = StructuralAlternativeCandidate(
        candidate_id="ALT-0005",
        alternative_type=SubqueryAlternativeType.DERIVED_TABLE,
        evidence_status=EvidenceStatus.PARTIAL,
        title="Derived-table alternative",
        rationale="Structural alternative requiring later validation.",
        original_sql=ORIGINAL_SQL,
    )

    assert candidate.source_layer is None


def test_alternative_sql_is_optional() -> None:
    candidate = StructuralAlternativeCandidate(
        candidate_id="ALT-0006",
        alternative_type=SubqueryAlternativeType.EXISTS,
        evidence_status=EvidenceStatus.INSUFFICIENT,
        title="EXISTS alternative",
        rationale="Alternative SQL has not yet been generated.",
        original_sql=ORIGINAL_SQL,
    )

    assert candidate.alternative_sql is None


def test_result_defaults_to_empty_candidate_list() -> None:
    result = StructuralAlternativeResult()

    assert result.candidates == []


def test_result_preserves_candidate_order() -> None:
    candidates = [
        StructuralAlternativeCandidate(
            candidate_id="ALT-0001",
            alternative_type=SubqueryAlternativeType.EXISTS,
            evidence_status=EvidenceStatus.COMPLETE,
            title="EXISTS alternative",
            rationale="Candidate one.",
            original_sql=ORIGINAL_SQL,
        ),
        StructuralAlternativeCandidate(
            candidate_id="ALT-0002",
            alternative_type=SubqueryAlternativeType.DERIVED_TABLE,
            evidence_status=EvidenceStatus.PARTIAL,
            title="Derived-table alternative",
            rationale="Candidate two.",
            original_sql=ORIGINAL_SQL,
        ),
    ]

    result = StructuralAlternativeResult(candidates=candidates)

    assert [candidate.candidate_id for candidate in result.candidates] == [
        "ALT-0001",
        "ALT-0002",
    ]


def test_candidate_requires_evidence_status() -> None:
    with pytest.raises(ValidationError):
        StructuralAlternativeCandidate(
            candidate_id="ALT-0007",
            alternative_type=SubqueryAlternativeType.EXISTS,
            title="EXISTS alternative",
            rationale="Evidence status is intentionally missing.",
            original_sql=ORIGINAL_SQL,
        )


def test_candidate_requires_original_sql() -> None:
    with pytest.raises(ValidationError):
        StructuralAlternativeCandidate(
            candidate_id="ALT-0008",
            alternative_type=SubqueryAlternativeType.IN,
            evidence_status=EvidenceStatus.COMPLETE,
            title="IN alternative",
            rationale="Original SQL is required for provenance.",
        )


def test_candidate_defaults_do_not_claim_validation() -> None:
    candidate = StructuralAlternativeCandidate(
        candidate_id="ALT-0009",
        alternative_type=SubqueryAlternativeType.DERIVED_TABLE,
        evidence_status=EvidenceStatus.COMPLETE,
        title="Derived-table alternative",
        rationale="Candidate requires later validation.",
        original_sql=ORIGINAL_SQL,
    )

    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.semantic_safety == SemanticSafetyStatus.NOT_ASSESSED
    assert candidate.alternative_sql is None
