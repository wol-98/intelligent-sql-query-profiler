from api.schemas.structural_optimization import (
    AlternativeType,
    BenchmarkEvidence,
    CandidateStatus,
    EvidenceStatus,
    OptimizationCandidate,
    OptimizationReport,
    QueryValidationResult,
    QueryValidationStatus,
    StructuralAnalysis,
    StructuralAnalysisStatus,
    StructuralFinding,
    StructuralLayer,
)


def test_query_validation_contract():
    result = QueryValidationResult(
        status=QueryValidationStatus.VALID,
        message="Query is valid.",
        query_type="SELECT",
        normalized_query="SELECT * FROM orders;",
        tables=["orders"],
    )

    assert result.status == QueryValidationStatus.VALID
    assert result.query_type == "SELECT"
    assert result.tables == ["orders"]


def test_structural_finding_contract():
    finding = StructuralFinding(
        layer=StructuralLayer.WHERE,
        finding_type="FILTER",
        severity="MEDIUM",
        description="Filter condition detected.",
        evidence="customer_id = ?",
    )

    assert finding.layer == StructuralLayer.WHERE
    assert finding.finding_type == "FILTER"
    assert finding.severity == "MEDIUM"


def test_structural_analysis_contract():
    analysis = StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        query_type="SELECT",
        layers_detected=[
            StructuralLayer.SELECT,
            StructuralLayer.FROM,
            StructuralLayer.WHERE,
        ],
        findings=[],
        tables=["orders"],
        joins_detected=0,
        subqueries_detected=0,
        aggregates_detected=0,
        window_functions_detected=0,
        has_order_by=False,
        has_limit=False,
        has_offset=False,
    )

    assert analysis.status == StructuralAnalysisStatus.ANALYZED
    assert StructuralLayer.WHERE in analysis.layers_detected
    assert analysis.tables == ["orders"]


def test_index_candidate_contract():
    candidate = OptimizationCandidate(
        candidate_id="candidate_001",
        alternative_type=AlternativeType.INDEX,
        status=CandidateStatus.CANDIDATE,
        title="Index orders.customer_id",
        rationale="Column appears in a filtering predicate.",
        source_layer=StructuralLayer.WHERE,
        original_sql="SELECT * FROM orders WHERE customer_id = 10;",
        index_ddl=(
            "CREATE INDEX idx_orders_customer_id "
            "ON orders (customer_id);"
        ),
    )

    assert candidate.candidate_id == "candidate_001"
    assert candidate.alternative_type == AlternativeType.INDEX
    assert candidate.status == CandidateStatus.CANDIDATE
    assert candidate.index_ddl is not None


def test_sql_rewrite_candidate_contract():
    candidate = OptimizationCandidate(
        candidate_id="candidate_002",
        alternative_type=AlternativeType.SQL_REWRITE,
        status=CandidateStatus.CANDIDATE,
        title="Derived-table alternative",
        rationale="Separates an aggregation stage from the outer query.",
        source_layer=StructuralLayer.GROUP_BY,
        original_sql="SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;",
        optimized_sql=(
            "SELECT customer_id, order_count "
            "FROM ("
            "SELECT customer_id, COUNT(*) AS order_count "
            "FROM orders GROUP BY customer_id"
            ") AS grouped_orders;"
        ),
    )

    assert candidate.alternative_type == AlternativeType.SQL_REWRITE
    assert candidate.optimized_sql is not None
    assert candidate.index_ddl is None


def test_architectural_candidate_contract():
    candidate = OptimizationCandidate(
        candidate_id="candidate_003",
        alternative_type=AlternativeType.ARCHITECTURAL,
        status=CandidateStatus.CANDIDATE,
        title="Materialized view candidate",
        rationale="Repeated expensive aggregation may justify precomputation.",
        source_layer=StructuralLayer.GROUP_BY,
        original_sql="SELECT customer_id, SUM(total_amount) FROM orders GROUP BY customer_id;",
        architectural_recommendation=(
            "Evaluate a materialized view if the result is reused frequently "
            "and refresh cost is acceptable."
        ),
    )

    assert candidate.alternative_type == AlternativeType.ARCHITECTURAL
    assert candidate.architectural_recommendation is not None


def test_benchmark_evidence_contract():
    evidence = BenchmarkEvidence(
        benchmark_id="M21_TEST_001",
        candidate_id="candidate_001",
        baseline_time_ms=10.0,
        alternative_time_ms=4.0,
        improvement_percent=60.0,
        savings_ms=6.0,
        median_improvement_percent=58.0,
        rows_preserved=True,
        plan_changed=True,
        evidence_status=EvidenceStatus.COMPLETE,
    )

    assert evidence.candidate_id == "candidate_001"
    assert evidence.improvement_percent == 60.0
    assert evidence.rows_preserved is True
    assert evidence.evidence_status == EvidenceStatus.COMPLETE


def test_missing_benchmark_values_remain_none():
    evidence = BenchmarkEvidence(
        candidate_id="candidate_without_benchmark",
        evidence_status=EvidenceStatus.INSUFFICIENT,
    )

    assert evidence.baseline_time_ms is None
    assert evidence.alternative_time_ms is None
    assert evidence.improvement_percent is None
    assert evidence.savings_ms is None
    assert evidence.median_improvement_percent is None


def test_integrated_optimization_report_contract():
    validation = QueryValidationResult(
        status=QueryValidationStatus.VALID,
        query_type="SELECT",
        normalized_query="SELECT * FROM orders;",
        tables=["orders"],
    )

    analysis = StructuralAnalysis(
        status=StructuralAnalysisStatus.ANALYZED,
        query_type="SELECT",
        layers_detected=[
            StructuralLayer.SELECT,
            StructuralLayer.FROM,
        ],
        tables=["orders"],
    )

    report = OptimizationReport(
        query_validation=validation,
        structural_analysis=analysis,
        candidates=[],
        benchmark_evidence=[],
        overall_evidence_status=EvidenceStatus.INSUFFICIENT,
    )

    assert report.query_validation.status == QueryValidationStatus.VALID
    assert report.structural_analysis.status == StructuralAnalysisStatus.ANALYZED
    assert report.overall_evidence_status == EvidenceStatus.INSUFFICIENT
