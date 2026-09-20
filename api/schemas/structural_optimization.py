from enum import Enum

from pydantic import BaseModel, Field


class QueryValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNSUPPORTED = "UNSUPPORTED"


class StructuralAnalysisStatus(str, Enum):
    ANALYZED = "ANALYZED"
    UNSUPPORTED = "UNSUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class CandidateStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"


class AlternativeType(str, Enum):
    INDEX = "INDEX"
    SQL_REWRITE = "SQL_REWRITE"
    ARCHITECTURAL = "ARCHITECTURAL"


class EvidenceStatus(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"


class StructuralLayer(str, Enum):
    SELECT = "SELECT"
    FROM = "FROM"
    JOIN = "JOIN"
    WHERE = "WHERE"
    HAVING = "HAVING"
    GROUP_BY = "GROUP_BY"
    WINDOW = "WINDOW"
    ORDER_BY = "ORDER_BY"
    LIMIT_OFFSET = "LIMIT_OFFSET"
    SUBQUERY = "SUBQUERY"
    SET_OPERATION = "SET_OPERATION"


class QueryValidationResult(BaseModel):
    status: QueryValidationStatus
    message: str | None = None
    query_type: str | None = None
    normalized_query: str | None = None
    tables: list[str] = Field(default_factory=list)


class StructuralFinding(BaseModel):
    layer: StructuralLayer
    finding_type: str
    severity: str
    description: str
    evidence: str | None = None


class StructuralAnalysis(BaseModel):
    status: StructuralAnalysisStatus
    query_type: str | None = None
    layers_detected: list[StructuralLayer] = Field(default_factory=list)
    findings: list[StructuralFinding] = Field(default_factory=list)
    tables: list[str] = Field(default_factory=list)
    joins_detected: int | None = None
    subqueries_detected: int | None = None
    aggregates_detected: int | None = None
    window_functions_detected: int | None = None
    has_order_by: bool | None = None
    has_limit: bool | None = None
    has_offset: bool | None = None


class OptimizationCandidate(BaseModel):
    candidate_id: str
    alternative_type: AlternativeType
    status: CandidateStatus = CandidateStatus.CANDIDATE
    title: str
    rationale: str
    source_layer: StructuralLayer | None = None
    original_sql: str
    optimized_sql: str | None = None
    index_ddl: str | None = None
    architectural_recommendation: str | None = None


class BenchmarkEvidence(BaseModel):
    benchmark_id: str | None = None
    candidate_id: str
    baseline_time_ms: float | None = None
    alternative_time_ms: float | None = None
    improvement_percent: float | None = None
    savings_ms: float | None = None
    median_improvement_percent: float | None = None
    rows_preserved: bool | None = None
    plan_changed: bool | None = None
    evidence_status: EvidenceStatus


class OptimizationReport(BaseModel):
    query_validation: QueryValidationResult
    structural_analysis: StructuralAnalysis
    candidates: list[OptimizationCandidate] = Field(default_factory=list)
    benchmark_evidence: list[BenchmarkEvidence] = Field(default_factory=list)
    overall_evidence_status: EvidenceStatus
