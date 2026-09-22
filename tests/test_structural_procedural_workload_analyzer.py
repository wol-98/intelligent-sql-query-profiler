from sqlglot import parse_one

from api.schemas.structural_optimization import (
    EvidenceStatus,
    OpportunityEvidenceScope,
    ProceduralWorkloadOpportunityStatus,
    ProceduralWorkloadOpportunityType,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralFinding,
)
from api.services.structural_procedural_workload_analyzer import (
    StructuralProceduralWorkloadAnalyzer,
)
from api.services.structural_sql_analyzer import StructuralSQLAnalyzer


def _analyze(sql: str):
    expression = parse_one(
        sql,
        dialect="postgres",
    )

    analysis = StructuralSQLAnalyzer().analyze(
        expression
    )

    result = StructuralProceduralWorkloadAnalyzer().analyze(
        expression,
        analysis,
    )

    return expression, analysis, result


def test_repeated_cte_reference_creates_reusable_computation():
    _, _, result = _analyze(
        """
        WITH customer_orders AS (
            SELECT customer_id, COUNT(*) AS order_count
            FROM orders
            GROUP BY customer_id
        )
        SELECT
            a.customer_id,
            a.order_count,
            b.order_count
        FROM customer_orders a
        JOIN customer_orders b
            ON a.customer_id = b.customer_id
        """
    )

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        ProceduralWorkloadOpportunityType.REUSABLE_COMPUTATION,
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION,
    ]

    assert all(
        opportunity.status
        == ProceduralWorkloadOpportunityStatus.IDENTIFIED
        for opportunity in result.opportunities
    )

    assert all(
        opportunity.evidence_status
        == EvidenceStatus.COMPLETE
        for opportunity in result.opportunities
    )

    assert all(
        opportunity.evidence_scope
        == OpportunityEvidenceScope.FINDING
        for opportunity in result.opportunities
    )


def test_single_cte_reference_does_not_create_reusable_computation():
    _, _, result = _analyze(
        """
        WITH customer_orders AS (
            SELECT customer_id, COUNT(*) AS order_count
            FROM orders
            GROUP BY customer_id
        )
        SELECT *
        FROM customer_orders
        """
    )

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION,
    ]


def test_parameter_marker_creates_parameterized_operation():
    _, _, result = _analyze(
        """
        SELECT *
        FROM orders
        WHERE customer_id = $1
        """
    )

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        ProceduralWorkloadOpportunityType.PARAMETERIZED_OPERATION,
    ]

    assert result.opportunities[0].status == (
        ProceduralWorkloadOpportunityStatus.IDENTIFIED
    )


def test_literal_filter_does_not_create_parameterized_operation():
    _, _, result = _analyze(
        """
        SELECT *
        FROM orders
        WHERE customer_id = 845
        """
    )

    assert result.opportunities == []


def test_nested_query_creates_multi_step_operation():
    _, _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        WHERE customer_id IN (
            SELECT customer_id
            FROM customers
            WHERE active = true
        )
        """
    )

    assert [
        opportunity.opportunity_type
        for opportunity in result.opportunities
    ] == [
        ProceduralWorkloadOpportunityType.MULTI_STEP_DATA_OPERATION,
    ]


def test_simple_query_has_no_procedural_opportunity():
    _, _, result = _analyze(
        """
        SELECT customer_id
        FROM orders
        """
    )

    assert result.opportunities == []


def test_detector_does_not_infer_side_effecting_workflow_from_select():
    _, _, result = _analyze(
        """
        SELECT customer_id, COUNT(*)
        FROM orders
        GROUP BY customer_id
        """
    )

    assert all(
        opportunity.opportunity_type
        != ProceduralWorkloadOpportunityType.SIDE_EFFECTING_WORKFLOW
        for opportunity in result.opportunities
    )

    assert all(
        opportunity.opportunity_type
        != ProceduralWorkloadOpportunityType.DATA_MUTATION_WORKFLOW
        for opportunity in result.opportunities
    )


def test_detector_does_not_infer_complex_procedural_logic():
    _, _, result = _analyze(
        """
        SELECT
            customer_id,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) AS row_number
        FROM orders
        """
    )

    assert all(
        opportunity.opportunity_type
        != ProceduralWorkloadOpportunityType.COMPLEX_PROCEDURAL_LOGIC
        for opportunity in result.opportunities
    )


def test_result_order_is_deterministic():
    _, _, first = _analyze(
        """
        WITH customer_orders AS (
            SELECT customer_id
            FROM orders
        )
        SELECT *
        FROM customer_orders
        WHERE customer_id = $1
        """
    )

    _, _, second = _analyze(
        """
        WITH customer_orders AS (
            SELECT customer_id
            FROM orders
        )
        SELECT *
        FROM customer_orders
        WHERE customer_id = $1
        """
    )

    assert [
        opportunity.opportunity_type
        for opportunity in first.opportunities
    ] == [
        opportunity.opportunity_type
        for opportunity in second.opportunities
    ]


def test_original_analysis_is_not_modified():
    expression, analysis, _ = _analyze(
        """
        WITH customer_orders AS (
            SELECT customer_id
            FROM orders
        )
        SELECT *
        FROM customer_orders
        WHERE customer_id = $1
        """
    )

    original = analysis.model_dump()

    StructuralProceduralWorkloadAnalyzer().analyze(
        expression,
        analysis,
    )

    assert analysis.model_dump() == original


def test_empty_analysis_returns_empty_result():
    analysis = StructuralAnalysis(
        query="SELECT 1",
        status=StructuralAnalysisStatus.ANALYZED,
        findings=[],
    )

    expression = parse_one(
        "SELECT 1",
        dialect="postgres",
    )

    result = StructuralProceduralWorkloadAnalyzer().analyze(
        expression,
        analysis,
    )

    assert result.opportunities == []


def test_parameterized_operation_links_to_structural_finding():
    _, analysis, result = _analyze(
        """
        SELECT *
        FROM orders
        WHERE customer_id = $1
        """
    )

    opportunity = result.opportunities[0]

    assert (
        opportunity.finding_index
        < len(analysis.findings)
    )

    finding = analysis.findings[
        opportunity.finding_index
    ]

    assert finding.layer.value == "WHERE"
