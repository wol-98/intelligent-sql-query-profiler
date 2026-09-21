from api.schemas.structural_optimization import (
    OptimizationOpportunityType,
)


def test_subquery_opportunity_types_exist():
    assert (
        OptimizationOpportunityType.SUBQUERY_EXISTS_ANALYSIS.value
        == "SUBQUERY_EXISTS_ANALYSIS"
    )
    assert (
        OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS.value
        == "SUBQUERY_IN_ANALYSIS"
    )
    assert (
        OptimizationOpportunityType.SUBQUERY_ANY_ANALYSIS.value
        == "SUBQUERY_ANY_ANALYSIS"
    )
    assert (
        OptimizationOpportunityType.DERIVED_TABLE_ANALYSIS.value
        == "DERIVED_TABLE_ANALYSIS"
    )


def test_subquery_opportunity_types_are_distinct():
    values = {
        OptimizationOpportunityType.SUBQUERY_EXISTS_ANALYSIS.value,
        OptimizationOpportunityType.SUBQUERY_IN_ANALYSIS.value,
        OptimizationOpportunityType.SUBQUERY_ANY_ANALYSIS.value,
        OptimizationOpportunityType.DERIVED_TABLE_ANALYSIS.value,
    }

    assert len(values) == 4
