from __future__ import annotations

from api.schemas.composite import CompositeIndexResponse
from collector.m16_2_reporting import (
    get_m16_2_result,
    get_m16_2_results,
)


def _build_response(result: dict) -> CompositeIndexResponse:
    original_order = result["original_columns"]
    alternative_order = result["alternative_columns"]

    return CompositeIndexResponse(
        recommendation_id=result["recommendation_id"],
        original_order=original_order,
        alternative_order=alternative_order,
        column_count=len(original_order),
        original_improvement_percent=result[
            "original_improvement_percentage"
        ],
        alternative_improvement_percent=result[
            "alternative_improvement_percentage"
        ],
        order_effect_percentage_points=result[
            "improvement_difference_percentage_points"
        ],
        original_index_used=result["original_index_used"],
        alternative_index_used=result["alternative_index_used"],
        original_rows_preserved=result["original_rows_preserved"],
        alternative_rows_preserved=result["alternative_rows_preserved"],
    )


def get_composite_indexes() -> list[CompositeIndexResponse]:
    return [
        _build_response(result)
        for result in get_m16_2_results()
    ]


def get_composite_index(
    recommendation_id: int,
) -> CompositeIndexResponse:
    try:
        result = get_m16_2_result(recommendation_id)
    except ValueError:
        raise

    return _build_response(result)
