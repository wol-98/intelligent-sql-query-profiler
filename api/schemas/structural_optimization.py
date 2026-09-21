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
    CTE = "CTE"
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


class StructuralFindingClassificationType(str, Enum):
    DIRECT_OPERATION = "DIRECT_OPERATION"
    PREDICATE = "PREDICATE"
    RELATIONSHIP = "RELATIONSHIP"
    AGGREGATION = "AGGREGATION"
    WINDOW_OPERATION = "WINDOW_OPERATION"
    ORDERING = "ORDERING"
    ROW_LIMITING = "ROW_LIMITING"
    NESTED_QUERY = "NESTED_QUERY"
    SET_OPERATION = "SET_OPERATION"
    SOURCE_DEFINITION = "SOURCE_DEFINITION"


class EvidenceQuality(str, Enum):
    EXACT = "EXACT"
    STRUCTURED = "STRUCTURED"
    SUMMARY = "SUMMARY"
    MISSING = "MISSING"


class OptimizationRelevance(str, Enum):
    NOT_ASSESSED = "NOT_ASSESSED"
    POTENTIALLY_RELEVANT = "POTENTIALLY_RELEVANT"
    CONTEXTUAL = "CONTEXTUAL"
    STRUCTURALLY_NEUTRAL = "STRUCTURALLY_NEUTRAL"


class StructuralFindingClassification(BaseModel):
    finding_index: int = Field(ge=0)
    classification: StructuralFindingClassificationType
    evidence_status: EvidenceStatus
    evidence_quality: EvidenceQuality
    optimization_relevance: OptimizationRelevance
    rationale: str


class StructuralClassificationResult(BaseModel):
    classifications: list[StructuralFindingClassification] = Field(
        default_factory=list
    )


class OptimizationOpportunityType(str, Enum):
    PREDICATE_ANALYSIS = "PREDICATE_ANALYSIS"
    JOIN_ANALYSIS = "JOIN_ANALYSIS"
    AGGREGATION_ANALYSIS = "AGGREGATION_ANALYSIS"
    WINDOW_ANALYSIS = "WINDOW_ANALYSIS"
    ORDERING_ANALYSIS = "ORDERING_ANALYSIS"
    ROW_LIMITING_ANALYSIS = "ROW_LIMITING_ANALYSIS"
    NESTED_QUERY_ANALYSIS = "NESTED_QUERY_ANALYSIS"
    SUBQUERY_EXISTS_ANALYSIS = "SUBQUERY_EXISTS_ANALYSIS"
    SUBQUERY_IN_ANALYSIS = "SUBQUERY_IN_ANALYSIS"
    SUBQUERY_ANY_ANALYSIS = "SUBQUERY_ANY_ANALYSIS"
    DERIVED_TABLE_ANALYSIS = "DERIVED_TABLE_ANALYSIS"
    CTE_ANALYSIS = "CTE_ANALYSIS"
    RECURSIVE_CTE_ANALYSIS = "RECURSIVE_CTE_ANALYSIS"


class OptimizationOpportunityStatus(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    NOT_ASSESSED = "NOT_ASSESSED"
    STRUCTURALLY_NEUTRAL = "STRUCTURALLY_NEUTRAL"


class OpportunityEvidenceScope(str, Enum):
    FINDING = "FINDING"
    CLASSIFICATION = "CLASSIFICATION"


class StructuralOptimizationOpportunity(BaseModel):
    finding_index: int = Field(ge=0)
    opportunity_type: OptimizationOpportunityType
    status: OptimizationOpportunityStatus
    evidence_status: EvidenceStatus
    evidence_scope: OpportunityEvidenceScope
    rationale: str


class StructuralOpportunityResult(BaseModel):
    opportunities: list[StructuralOptimizationOpportunity] = Field(
        default_factory=list
    )


class AggregationWindowCharacteristicType(str, Enum):
    GROUPING = "GROUPING"
    AGGREGATE_FUNCTION = "AGGREGATE_FUNCTION"
    HAVING_FILTER = "HAVING_FILTER"
    WINDOW_FUNCTION = "WINDOW_FUNCTION"
    WINDOW_PARTITION = "WINDOW_PARTITION"
    WINDOW_ORDERING = "WINDOW_ORDERING"


class AggregationWindowCharacteristic(BaseModel):
    finding_index: int = Field(ge=0)
    characteristic_type: AggregationWindowCharacteristicType
    evidence_status: EvidenceStatus
    evidence_quality: EvidenceQuality
    rationale: str


class OrderingLimitCharacteristicType(str, Enum):
    ORDERING = "ORDERING"
    LIMIT = "LIMIT"
    OFFSET = "OFFSET"
    FILTER_WITH_ROW_LIMIT = "FILTER_WITH_ROW_LIMIT"
    FILTER_WITH_ORDERING = "FILTER_WITH_ORDERING"


class OrderingLimitCharacteristic(BaseModel):
    finding_index: int = Field(ge=0)
    characteristic_type: OrderingLimitCharacteristicType
    evidence_status: EvidenceStatus
    evidence_quality: EvidenceQuality
    rationale: str


class OrderingLimitCharacteristicResult(BaseModel):
    characteristics: list[OrderingLimitCharacteristic] = Field(
        default_factory=list
    )


class AggregationWindowCharacteristicResult(BaseModel):
    characteristics: list[AggregationWindowCharacteristic] = Field(
        default_factory=list
    )


class SubqueryAlternativeType(str, Enum):
    EXISTS = "EXISTS"
    IN = "IN"
    ANY = "ANY"
    DERIVED_TABLE = "DERIVED_TABLE"


class SemanticSafetyStatus(str, Enum):
    NOT_ASSESSED = "NOT_ASSESSED"
    REQUIRES_VALIDATION = "REQUIRES_VALIDATION"
    UNSAFE = "UNSAFE"


class StructuralAlternativeCandidate(BaseModel):
    candidate_id: str
    alternative_type: SubqueryAlternativeType
    status: CandidateStatus = CandidateStatus.CANDIDATE
    semantic_safety: SemanticSafetyStatus = SemanticSafetyStatus.NOT_ASSESSED
    evidence_status: EvidenceStatus
    title: str
    rationale: str
    source_layer: StructuralLayer | None = None
    original_sql: str
    alternative_sql: str | None = None


class StructuralAlternativeResult(BaseModel):
    candidates: list[StructuralAlternativeCandidate] = Field(
        default_factory=list
    )


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


class SubqueryAlternativeCharacteristicType(str, Enum):
    EXISTS_PREDICATE = "EXISTS_PREDICATE"
    IN_PREDICATE = "IN_PREDICATE"
    ANY_PREDICATE = "ANY_PREDICATE"
    CORRELATED_SUBQUERY = "CORRELATED_SUBQUERY"
    DERIVED_TABLE = "DERIVED_TABLE"


class SubqueryAlternativeCharacteristic(BaseModel):
    finding_index: int = Field(ge=0)
    characteristic_type: SubqueryAlternativeCharacteristicType
    evidence_status: EvidenceStatus
    evidence_quality: EvidenceQuality
    rationale: str


class SubqueryAlternativeCharacteristicResult(BaseModel):
    characteristics: list[SubqueryAlternativeCharacteristic] = Field(
        default_factory=list
    )

class CTECharacteristicType(str, Enum):
    CTE_DEFINITION = "CTE_DEFINITION"
    CTE_REFERENCE = "CTE_REFERENCE"
    RECURSIVE_CTE = "RECURSIVE_CTE"


class CTECharacteristic(BaseModel):
    finding_index: int = Field(ge=0)
    characteristic_type: CTECharacteristicType
    evidence_status: EvidenceStatus
    evidence_quality: EvidenceQuality
    rationale: str


class CTECharacteristicResult(BaseModel):
    characteristics: list[CTECharacteristic] = Field(
        default_factory=list
    )
