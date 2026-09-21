"""Tests for the M21.9 ordering and row-limiting characteristic contract."""

import pytest
from pydantic import ValidationError

from api.schemas.structural_optimization import (
    EvidenceQuality,
    EvidenceStatus,
    OrderingLimitCharacteristic,
    OrderingLimitCharacteristicResult,
    OrderingLimitCharacteristicType,
)


def test_ordering_limit_characteristic_types_are_defined():
    assert OrderingLimitCharacteristicType.ORDERING.value == "ORDERING"
    assert OrderingLimitCharacteristicType.LIMIT.value == "LIMIT"
    assert OrderingLimitCharacteristicType.OFFSET.value == "OFFSET"
    assert (
        OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT.value
        == "FILTER_WITH_ROW_LIMIT"
    )


def test_ordering_limit_characteristic_accepts_valid_values():
    characteristic = OrderingLimitCharacteristic(
        finding_index=2,
        characteristic_type=OrderingLimitCharacteristicType.ORDERING,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="ORDER BY is present in the query block.",
    )

    assert characteristic.finding_index == 2
    assert (
        characteristic.characteristic_type
        == OrderingLimitCharacteristicType.ORDERING
    )
    assert characteristic.evidence_status == EvidenceStatus.COMPLETE
    assert characteristic.evidence_quality == EvidenceQuality.EXACT
    assert characteristic.rationale == "ORDER BY is present in the query block."


def test_ordering_limit_characteristic_rejects_negative_finding_index():
    with pytest.raises(ValidationError):
        OrderingLimitCharacteristic(
            finding_index=-1,
            characteristic_type=OrderingLimitCharacteristicType.LIMIT,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_quality=EvidenceQuality.EXACT,
            rationale="LIMIT is present in the query block.",
        )


def test_ordering_limit_characteristic_result_defaults_to_empty():
    result = OrderingLimitCharacteristicResult()

    assert result.characteristics == []


def test_ordering_limit_characteristic_result_accepts_multiple_characteristics():
    result = OrderingLimitCharacteristicResult(
        characteristics=[
            OrderingLimitCharacteristic(
                finding_index=1,
                characteristic_type=OrderingLimitCharacteristicType.ORDERING,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale="ORDER BY is present in the query block.",
            ),
            OrderingLimitCharacteristic(
                finding_index=2,
                characteristic_type=OrderingLimitCharacteristicType.LIMIT,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale="LIMIT is present in the query block.",
            ),
            OrderingLimitCharacteristic(
                finding_index=2,
                characteristic_type=OrderingLimitCharacteristicType.OFFSET,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale="OFFSET is present in the query block.",
            ),
            OrderingLimitCharacteristic(
                finding_index=3,
                characteristic_type=(
                    OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT
                ),
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.STRUCTURED,
                rationale=(
                    "A WHERE predicate and row-limiting operation "
                    "coexist in the query block."
                ),
            ),
        ]
    )

    assert len(result.characteristics) == 4
    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        OrderingLimitCharacteristicType.ORDERING,
        OrderingLimitCharacteristicType.LIMIT,
        OrderingLimitCharacteristicType.OFFSET,
        OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT,
    ]


def test_ordering_limit_characteristic_preserves_evidence_fields():
    characteristic = OrderingLimitCharacteristic(
        finding_index=4,
        characteristic_type=OrderingLimitCharacteristicType.OFFSET,
        evidence_status=EvidenceStatus.INSUFFICIENT,
        evidence_quality=EvidenceQuality.MISSING,
        rationale="The required structural evidence is unavailable.",
    )

    assert characteristic.evidence_status == EvidenceStatus.INSUFFICIENT
    assert characteristic.evidence_quality == EvidenceQuality.MISSING


def test_ordering_limit_characteristic_serializes_to_expected_values():
    characteristic = OrderingLimitCharacteristic(
        finding_index=5,
        characteristic_type=OrderingLimitCharacteristicType.LIMIT,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="LIMIT is present in the query block.",
    )

    data = characteristic.model_dump()

    assert data["finding_index"] == 5
    assert data["characteristic_type"] == "LIMIT"
    assert data["evidence_status"] == "COMPLETE"
    assert data["evidence_quality"] == "EXACT"
    assert data["rationale"] == "LIMIT is present in the query block."


def test_ordering_limit_characteristic_round_trips_through_model_dump():
    characteristic = OrderingLimitCharacteristic(
        finding_index=6,
        characteristic_type=OrderingLimitCharacteristicType.FILTER_WITH_ROW_LIMIT,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.STRUCTURED,
        rationale=(
            "A WHERE predicate and row-limiting operation "
            "coexist in the query block."
        ),
    )

    restored = OrderingLimitCharacteristic.model_validate(
        characteristic.model_dump()
    )

    assert restored == characteristic
