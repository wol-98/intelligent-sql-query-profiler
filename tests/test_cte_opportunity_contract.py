from api.schemas.structural_optimization import (
    OptimizationOpportunityType,
)


def test_cte_analysis_opportunity_type_exists():
    assert (
        OptimizationOpportunityType.CTE_ANALYSIS.value
        == "CTE_ANALYSIS"
    )


def test_recursive_cte_analysis_opportunity_type_exists():
    assert (
        OptimizationOpportunityType.RECURSIVE_CTE_ANALYSIS.value
        == "RECURSIVE_CTE_ANALYSIS"
    )
