from api.schemas.structural_optimization import (
    CTECharacteristic,
    CTECharacteristicResult,
    CTECharacteristicType,
    EvidenceQuality,
    EvidenceStatus,
    StructuralLayer,
)


def test_cte_layer_exists():
    assert StructuralLayer.CTE.value == "CTE"


def test_cte_characteristic_types_exist():
    assert CTECharacteristicType.CTE_DEFINITION.value == "CTE_DEFINITION"
    assert CTECharacteristicType.CTE_REFERENCE.value == "CTE_REFERENCE"
    assert CTECharacteristicType.RECURSIVE_CTE.value == "RECURSIVE_CTE"


def test_cte_characteristic_contract():
    characteristic = CTECharacteristic(
        finding_index=0,
        characteristic_type=CTECharacteristicType.CTE_DEFINITION,
        evidence_status=EvidenceStatus.COMPLETE,
        evidence_quality=EvidenceQuality.EXACT,
        rationale="A CTE definition was structurally identified.",
    )

    assert characteristic.finding_index == 0
    assert (
        characteristic.characteristic_type
        == CTECharacteristicType.CTE_DEFINITION
    )
    assert characteristic.evidence_status == EvidenceStatus.COMPLETE
    assert characteristic.evidence_quality == EvidenceQuality.EXACT


def test_cte_characteristic_result_defaults_to_empty():
    result = CTECharacteristicResult()

    assert result.characteristics == []


def test_cte_characteristic_result_preserves_order():
    result = CTECharacteristicResult(
        characteristics=[
            CTECharacteristic(
                finding_index=0,
                characteristic_type=CTECharacteristicType.CTE_DEFINITION,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale="CTE definition identified.",
            ),
            CTECharacteristic(
                finding_index=0,
                characteristic_type=CTECharacteristicType.CTE_REFERENCE,
                evidence_status=EvidenceStatus.COMPLETE,
                evidence_quality=EvidenceQuality.EXACT,
                rationale="CTE reference identified.",
            ),
        ]
    )

    assert [
        characteristic.characteristic_type
        for characteristic in result.characteristics
    ] == [
        CTECharacteristicType.CTE_DEFINITION,
        CTECharacteristicType.CTE_REFERENCE,
    ]
