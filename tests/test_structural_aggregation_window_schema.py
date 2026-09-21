import pytest
from pydantic import ValidationError

from api.schemas.structural_optimization import (
    AggregationWindowCharacteristic,
    AggregationWindowCharacteristicResult,
    AggregationWindowCharacteristicType,
    EvidenceQuality,
    EvidenceStatus,
)


def test_characteristic_type_enum_contains_expected_values():
    assert AggregationWindowCharacteristicType.GROUPING.value == "GROUPING"
    assert (
        AggregationWindowCharacteristicType.AGGREGATE_FUNCTION.value
        == "AGGREGATE_FUNCTION"
    )
    assert (
        AggregationWindowCharacteristicType.HAVING_FILTER.value
        == "HAVING_FILTER"
    )
    assert (
        AggregationWindowCharacteristicType.WINDOW_FUNCTION.value
        == "WINDOW_FUNCTION"
    )
    assert (
        AggregationWindowCharacteristicType.WINDOW_PARTITION.value
        == "WINDOW_PARTITION"
    )
    assert (
        AggregationWindowCharacteristicType.WINDOW_ORDERING.value
        == "WINDOW_ORDERING"
    )


def test_grouping_characteristic_can_be_created():
    characteristic = AggregationWindowCharacteristic(
        finding_index=0,
        characteristic_type=AggregationWindowCharacteristicType.GROUPING,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="GROUP BY structure was identified from the structural finding.",
    )

    assert characteristic.finding_index == 0
    assert (
        characteristic.characteristic_type
        == AggregationWindowCharacteristicType.GROUPING
    )
    assert characteristic.evidence_status == EvidenceStatus.COMPLETE
    assert characteristic.evidence_quality == EvidenceQuality.EXACT


def test_aggregate_function_characteristic_can_be_created():
    characteristic = AggregationWindowCharacteristic(
        finding_index=1,
        characteristic_type=AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="Aggregate function structure was identified from the query.",
    )

    assert (
        characteristic.characteristic_type
        == AggregationWindowCharacteristicType.AGGREGATE_FUNCTION
    )


def test_having_characteristic_can_be_created():
    characteristic = AggregationWindowCharacteristic(
        finding_index=2,
        characteristic_type=AggregationWindowCharacteristicType.HAVING_FILTER,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="HAVING structure was identified from the structural finding.",
    )

    assert (
        characteristic.characteristic_type
        == AggregationWindowCharacteristicType.HAVING_FILTER
    )


def test_window_function_characteristic_can_be_created():
    characteristic = AggregationWindowCharacteristic(
        finding_index=3,
        characteristic_type=AggregationWindowCharacteristicType.WINDOW_FUNCTION,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="Window function structure was identified from the query.",
    )

    assert (
        characteristic.characteristic_type
        == AggregationWindowCharacteristicType.WINDOW_FUNCTION
    )


def test_window_partition_characteristic_can_be_created():
    characteristic = AggregationWindowCharacteristic(
        finding_index=4,
        characteristic_type=AggregationWindowCharacteristicType.WINDOW_PARTITION,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="Window PARTITION BY structure was identified.",
    )

    assert (
        characteristic.characteristic_type
        == AggregationWindowCharacteristicType.WINDOW_PARTITION
    )


def test_window_ordering_characteristic_can_be_created():
    characteristic = AggregationWindowCharacteristic(
        finding_index=5,
        characteristic_type=AggregationWindowCharacteristicType.WINDOW_ORDERING,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="Window ORDER BY structure was identified.",
    )

    assert (
        characteristic.characteristic_type
        == AggregationWindowCharacteristicType.WINDOW_ORDERING
    )


def test_characteristic_result_defaults_to_empty_list():
    result = AggregationWindowCharacteristicResult()

    assert result.characteristics == []


def test_characteristic_result_accepts_multiple_characteristics():
    characteristics = [
        AggregationWindowCharacteristic(
            finding_index=0,
            characteristic_type=AggregationWindowCharacteristicType.GROUPING,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_quality=EvidenceQuality.EXACT,
            rationale="GROUP BY structure was identified.",
        ),
        AggregationWindowCharacteristic(
            finding_index=1,
            characteristic_type=AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_quality=EvidenceQuality.EXACT,
            rationale="Aggregate function structure was identified.",
        ),
        AggregationWindowCharacteristic(
            finding_index=2,
            characteristic_type=AggregationWindowCharacteristicType.WINDOW_FUNCTION,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_quality=EvidenceQuality.EXACT,
            rationale="Window function structure was identified.",
        ),
    ]

    result = AggregationWindowCharacteristicResult(
        characteristics=characteristics
    )

    assert len(result.characteristics) == 3
    assert result.characteristics[0].finding_index == 0
    assert result.characteristics[1].finding_index == 1
    assert result.characteristics[2].finding_index == 2


@pytest.mark.parametrize("invalid_index", [-1, -10])
def test_negative_finding_index_is_rejected(invalid_index):
    with pytest.raises(ValidationError):
        AggregationWindowCharacteristic(
            finding_index=invalid_index,
            characteristic_type=AggregationWindowCharacteristicType.GROUPING,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_quality=EvidenceQuality.EXACT,
            rationale="Invalid finding index.",
        )


def test_characteristic_requires_rationale():
    with pytest.raises(ValidationError):
        AggregationWindowCharacteristic(
            finding_index=0,
            characteristic_type=AggregationWindowCharacteristicType.GROUPING,
            evidence_status=EvidenceStatus.COMPLETE,
            evidence_quality=EvidenceQuality.EXACT,
        )


def test_partial_structured_evidence_is_supported():
    characteristic = AggregationWindowCharacteristic(
        finding_index=7,
        characteristic_type=AggregationWindowCharacteristicType.WINDOW_FUNCTION,
        evidence_status=EvidenceStatus.PARTIAL,
        evidence_quality=EvidenceQuality.STRUCTURED,
        rationale="Window structure is available as structured evidence.",
    )

    assert characteristic.evidence_status == EvidenceStatus.PARTIAL
    assert characteristic.evidence_quality == EvidenceQuality.STRUCTURED


def test_insufficient_evidence_is_supported():
    characteristic = AggregationWindowCharacteristic(
        finding_index=8,
        characteristic_type=AggregationWindowCharacteristicType.AGGREGATE_FUNCTION,
        evidence_status=EvidenceStatus.INSUFFICIENT,
        evidence_quality=EvidenceQuality.MISSING,
        rationale="The available structural evidence is insufficient.",
    )

    assert characteristic.evidence_status == EvidenceStatus.INSUFFICIENT
    assert characteristic.evidence_quality == EvidenceQuality.MISSING
