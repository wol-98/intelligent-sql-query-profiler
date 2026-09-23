# M21 Structural SQL Optimization Architecture

## 1. Purpose

M21 expands the Intelligent SQL Query Profiler & Index Optimization Engine
from primarily index-oriented workload optimization into dynamic structural
SQL analysis.

The user will be able to submit a SQL query for validation, structural
analysis, optimization candidate generation and, where safe and appropriate,
experimental comparison.

M21 is an extension of the existing evidence-driven architecture. It does
not replace the existing M1-M20 pipeline.

---

## 2. Architectural Principle

The M21 pipeline is:

USER SQL
    |
    v
VALIDATE
    |
    v
SCHEMA CHECK
    |
    v
PARSE
    |
    v
STRUCTURAL ANALYSIS
    |
    v
CANDIDATE GENERATION
    |
    v
SAFE VALIDATION
    |
    v
BENCHMARK
    |
    v
COST / BENEFIT
    |
    v
REPORT

Each stage must preserve the evidence boundary between:

1. What was detected.
2. What was proposed.
3. What was experimentally validated.
4. What remains unsupported or insufficiently evidenced.

---

## 3. M21.1 Scope

M21.1 establishes the contracts required by later milestones.

M21.1 includes:

- Query validation contract.
- Structural analysis contract.
- Structural finding contract.
- Optimization candidate contract.
- Benchmark evidence contract.
- Integrated optimization report contract.
- SQL structural layer taxonomy.
- Evidence status taxonomy.
- Candidate and validation status taxonomy.

M21.1 does not implement:

- SQL rewriting.
- Automatic index creation.
- Dynamic query execution.
- CTE generation.
- JOIN rewriting.
- Window-function rewriting.
- View creation.
- Materialized-view creation.
- Stored procedure generation.
- Interactive SQL optimization UI.
- New benchmark execution.

Those belong to later M21 milestones.

---

## 4. Dynamic Query Principle

The intended interface accepts user-submitted SQL.

However, accepting arbitrary SQL text does not mean arbitrary SQL should be
executed.

The initial dynamic optimization architecture is read-oriented and evidence
driven.

Later validation stages must distinguish:

- syntactically valid queries;
- schema-valid queries;
- supported query types;
- unsupported statements;
- queries that are safe to analyze;
- queries that require additional isolation before execution.

Mutation statements must not be automatically executed merely because they
are syntactically valid.

---

## 5. Query Validation Contract

The validation result records:

- validation status;
- human-readable validation message;
- detected query type;
- normalized query;
- referenced tables.

Possible validation states:

### VALID

The query passes the applicable validation rules.

### INVALID

The query cannot be parsed or otherwise fails validation.

### UNSUPPORTED

The query may be syntactically valid but is outside the currently supported
optimization scope.

---

## 6. Structural Analysis Contract

Structural analysis describes the query without claiming that an optimization
has already been achieved.

The analysis can identify:

- SELECT structure;
- FROM structure;
- JOINs;
- WHERE predicates;
- HAVING predicates;
- GROUP BY;
- window functions;
- ORDER BY;
- LIMIT/OFFSET;
- subqueries;
- set operations.

The analysis may also report:

- number of joins;
- number of subqueries;
- number of aggregate operations;
- number of window functions;
- presence of ORDER BY;
- presence of LIMIT;
- presence of OFFSET.

---

## 7. Structural Finding Contract

A finding contains:

- SQL structural layer;
- finding type;
- severity;
- description;
- optional evidence.

A finding is an observation.

It is not automatically a recommendation.

For example:

"Sequential scan detected on a filtered table"

is a finding.

A later component may decide whether an index is an appropriate candidate.

---

## 8. Optimization Candidate Contract

An optimization candidate records a proposed alternative.

Candidate types are:

### INDEX

An index-oriented alternative.

### SQL_REWRITE

A structural SQL alternative such as:

- CTE;
- derived table;
- JOIN rewrite;
- EXISTS/IN transformation;
- aggregation rewrite;
- window-function transformation;
- ORDER BY/LIMIT restructuring.

### ARCHITECTURAL

An architectural alternative such as:

- database view;
- materialized view;
- database function;
- stored procedure.

A candidate is not considered validated merely because it was generated.

---

## 9. Candidate Lifecycle

Candidates follow:

CANDIDATE
    |
    +----> VALIDATED
    |
    +----> REJECTED

CANDIDATE means the system proposed the alternative.

VALIDATED means the alternative has passed the applicable validation and
experimental evidence requirements.

REJECTED means the alternative was evaluated and failed the applicable
criteria.

---

## 10. Benchmark Evidence

Benchmark evidence records measurable comparison between an original query
and an alternative.

Possible evidence includes:

- baseline execution time;
- alternative execution time;
- improvement percentage;
- execution-time savings;
- median improvement;
- row preservation;
- plan change;
- benchmark identifier.

Missing values must remain unavailable.

Missing evidence must never be converted into zero.

---

## 11. Evidence States

### COMPLETE

Required evidence is available.

### PARTIAL

Some relevant evidence exists, but the complete evidence chain is not
available.

### INSUFFICIENT

The available evidence is insufficient to support the relevant conclusion.

These states preserve the evidence discipline established by M19.

---

## 12. Separation of Proposal and Decision

M21 must not confuse:

- structural detection;
- optimization proposal;
- experimental validation;
- production decision.

The pipeline is therefore:

Observation
    ->
Analysis
    ->
Candidate
    ->
Validation
    ->
Evidence
    ->
Decision

A structurally attractive rewrite is not automatically a successful
optimization.

---

## 13. Relationship to Existing M19/M20 Architecture

M21 builds on the existing system.

M19 remains the production decision and guardrail framework.

M20 remains the reporting API and dashboard foundation.

M21 introduces a new candidate-generation path for structural SQL
optimization.

The eventual integrated architecture is:

Existing workload/index pipeline
             |
             v
      Recommendation
             |
             +--------------------+
             |                    |
             v                    v
      Index Candidate      Structural Candidate
             |                    |
             +---------+----------+
                       |
                       v
                 Validation
                       |
                       v
                  Benchmark
                       |
                       v
                Cost / Benefit
                       |
                       v
                  M19 Decision
                       |
                       v
                   M20/M21
                   Reporting

---

## 14. Safety Boundaries

M21 must preserve the following principles:

1. Do not execute arbitrary mutation SQL automatically.
2. Do not claim semantic equivalence without validation.
3. Do not claim performance improvement without measurement.
4. Do not treat a generated SQL rewrite as universally optimal.
5. Do not treat missing evidence as zero.
6. Do not create production indexes automatically.
7. Do not allow dashboard visualization to replace experimental evidence.
8. Keep experimental execution isolated from production workloads.

---

## 15. M21 Milestone Sequence

### M21.1
Architecture and contracts.

### M21.2
Dynamic SQL syntax validation and safe failure handling.

### M21.3
Schema/table/column validation.

### M21.4
Expanded SQL structural parser and query-shape classification.

### M21.5
FROM/JOIN structural analysis.

### M21.6
WHERE/HAVING and correlated-subquery analysis.

### M21.7
EXISTS/IN/ANY and derived-table alternatives.

### M21.8
Aggregation and window-function analysis.

### M21.9
ORDER BY/LIMIT/OFFSET analysis.

### M21.10
CTE and structural SQL alternative generation.

### M21.11
View/materialized-view recommendations.

### M21.12
Database function/stored-procedure recommendations.

### M21.13
Integrated index plus structural optimization.

### M21.14
Alternative-query benchmarking.

Implemented with safety-aware benchmarkability checks and explicit separation
between measured and simulated evidence.

### M21.15
Dynamic optimization report.

Implemented using the five-section dynamic optimization blueprint:
Structural Performance Evaluation, Matrix Comparison, Optimized Structural SQL
Code, Indexing Blueprint, and Architectural Recommendations and Trade-offs.

### M21.16
Interactive SQL Optimization Studio.

Implemented as a React/Tailwind dashboard page connected to the dynamic
optimization blueprint endpoint.

### M21.17
Interactive analytics.

Implemented as a dedicated React/Tailwind analytics page with workload,
benchmark, cost-benefit, composite-index, query, decision and provenance
visualizations plus cross-filtering through recommendation relationships.

### M21.18
End-to-end validation and documentation.

Validated through full Python regression, dashboard lint/build, live API
smoke tests, dynamic SQL/schema safety tests, analytics data-path checks, and
documentation updates.

---

## 16. M21.1 Definition of Done

M21.1 is complete when:

- structural optimization schemas exist;
- Pydantic models validate correctly;
- status/enumeration values are explicit;
- structural SQL layers are explicitly represented;
- candidates are separated from validated alternatives;
- benchmark evidence is separated from recommendations;
- evidence completeness is explicitly represented;
- the M21 architecture document exists;
- the existing test suite remains green;
- M21 contract tests pass;
- no existing M19/M20 analytical logic is modified.
