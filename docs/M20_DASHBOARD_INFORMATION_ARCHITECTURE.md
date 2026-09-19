# M20 Optimization Intelligence Dashboard
## Frontend Information Architecture

### 1. Purpose

The dashboard provides a read-only visual interface for exploring the
optimization intelligence and experimental evidence produced by M13-M19.

The frontend visualizes existing intelligence. It does not independently
calculate recommendations, validation outcomes, cost-benefit decisions,
production decisions, or safety guardrails.

### 2. Primary Navigation

- Overview
- Recommendations
- Queries
- Workloads
- Benchmarks
- Cost & Benefit
- Composite Indexes
- Production Decisions
- Evidence & Provenance

### 3. Overview

Purpose:

Provide a high-level summary of the optimization project.

Displays:

- recommendation counts
- validation outcomes
- average and median improvement when available
- index usage
- rows preserved
- evidence completeness

The Overview page must not recalculate M13-M19 metrics.

### 4. Recommendations

Purpose:

Allow users to browse and filter generated index recommendations.

Displays:

- recommendation ID
- index name
- table
- columns
- score
- priority
- candidate type
- source type
- reason
- workload information
- validation information
- cost information
- production decision
- evidence status

### 5. Recommendation Evidence Detail

Purpose:

Provide a complete evidence trail for an individual recommendation.

Navigation flow:

Recommendation
→ Query
→ Workload
→ Validation
→ Cost & Benefit
→ Production Decision
→ Provenance

### 6. Queries

Purpose:

Explore profiled SQL queries and their execution characteristics.

Displays:

- query fingerprint
- template
- query type
- execution count
- execution time
- rows processed
- execution-plan characteristics
- associated recommendations

### 7. Workloads

Purpose:

Explore fingerprint-level workload importance.

Displays:

- fingerprint
- template
- execution count
- total execution time
- time share
- frequency share
- workload priority
- associated recommendations

### 8. Benchmarks

Purpose:

Explore experimental validation results.

Displays:

- recommendation
- experiment
- baseline execution time
- indexed execution time
- improvement
- median improvement when available
- savings
- index usage
- plan change
- row preservation
- validation outcome
- experimental scope

### 9. Cost & Benefit

Purpose:

Explore linked read-performance, storage, and write-impact evidence.

Displays:

- read improvement
- read savings
- storage size
- storage ratio
- write overhead
- median write overhead when available
- evidence completeness

### 10. Composite Indexes

Purpose:

Explore M15 composite candidate generation and M16 column-order experiments.

Displays:

- index
- table
- columns
- source pattern
- candidate type
- original column order
- alternative order
- original improvement
- alternative improvement
- order effect
- index usage

The page must preserve the distinction between original and alternative
experiments.

### 11. Production Decisions

Purpose:

Expose M19 production optimization decisions.

Displays:

- recommendation
- decision state
- decision reason
- evidence status
- guardrail status
- guardrail checks
- linked experiment

The frontend must not independently derive the decision.

### 12. Evidence & Provenance

Purpose:

Make evidence lineage explicit.

Displays:

- recommendation
- query fingerprint
- index name
- linked experiment
- linkage status
- evidence status

The interface must clearly distinguish:

- LINKED
- NOT_ESTABLISHED

The frontend must never imply an experimental relationship that the backend
has not established.

### 13. Cross-Page Navigation

The dashboard should allow navigation between related entities.

Examples:

Recommendation → Query

Recommendation → Workload

Recommendation → Benchmark

Recommendation → Cost & Benefit

Recommendation → Production Decision

Recommendation → Provenance

Query → Recommendations

Workload → Recommendations

Benchmark → Recommendation

Production Decision → Evidence

### 14. Empty States

Pages must distinguish between:

- no records exist
- records exist but evidence is unavailable
- evidence is partial
- linkage has not been established

Missing evidence must not be presented as zero.

### 15. Read-Only Scope

The dashboard is initially read-only.

No UI action should:

- create an index
- drop an index
- run a benchmark
- modify experimental data
- modify recommendations
- modify production decisions

### 16. Design Principle

The dashboard is an exploration and evidence interface.

M13-M19 remain the source of optimization intelligence.

M20 visualizes and exposes that intelligence without creating a second
decision engine.
