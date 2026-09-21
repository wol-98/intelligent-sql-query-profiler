from api.schemas.structural_optimization import (
    EvidenceQuality,
    EvidenceStatus,
    SubqueryAlternativeCharacteristic,
    SubqueryAlternativeCharacteristicResult,
    SubqueryAlternativeCharacteristicType,
)


def test_subquery_alternative_characteristic_types():
    assert SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE.value == (
        "EXISTS_PREDICATE"
    )
    assert SubqueryAlternativeCharacteristicType.IN_PREDICATE.value == (
        "IN_PREDICATE"
    )
    assert SubqueryAlternativeCharacteristicType.ANY_PREDICATE.value == (
        "ANY_PREDICATE"
    )
    assert SubqueryAlternativeCharacteristicType.CORRELATED_SUBQUERY.value == (
        "CORRELATED_SUBQUERY"
    )
    assert SubqueryAlternativeCharacteristicType.DERIVED_TABLE.value == (
        "DERIVED_TABLE"
    )


def test_subquery_alternative_characteristic_requires_finding_index():
    characteristic = SubqueryAlternativeCharacteristic(
        finding_index=2,
        characteristic_type=SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="An EXISTS predicate is structurally present.",
    )

    assert characteristic.finding_index == 2
    assert (
        characteristic.characteristic_type
        == SubqueryAlternativeCharacteristicType.EXISTS_PREDICATE
    )
    assert characteristic.evidence_status == EvidenceStatus.COMPLETE
    assert characteristic.evidence_quality == EvidenceQuality.EXACT


def test_subquery_alternative_characteristic_result_defaults_to_empty():
    result = SubqueryAlternativeCharacteristicResult()

    assert result.characteristics == []


def test_subquery_alternative_characteristic_result_accepts_characteristics():
    characteristic = SubqueryAlternativeCharacteristic(
        finding_index=1,
        characteristic_type=SubqueryAlternativeCharacteristicType.IN_PREDICATE,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="An IN predicate is structurally present.",
    )

    result = SubqueryAlternativeCharacteristicResult(
        characteristics=[characteristic]
    )

    assert len(result.characteristics) == 1
    assert result.characteristics[0] == characteristic


def test_all_subquery_characteristics_have_explicit_evidence():
    characteristic_types = list(SubqueryAlternativeCharacteristicType)

    assert len(characteristic_types) == 5

    for characteristic_type in characteristic_types:
        characteristic = SubqueryAlternativeCharacteristic(
            finding_index=0,
            characteristic_type=characteristic_type,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_quality=EvidenceQuality.EXACT,
            rationale=f"Structural characteristic: {characteristic_type.value}.",
        )

        assert characteristic.evidence_status == EvidenceStatus.COMPLETE
        assert characteristic.evidence_quality == EvidenceQuality.EXACT
