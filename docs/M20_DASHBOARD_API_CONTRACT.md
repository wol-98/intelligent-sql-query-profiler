# M20 Optimization Intelligence Dashboard
## API Contract

### 1. Purpose

The M20 API provides a read-only interface between the existing M13-M19
optimization intelligence layer and the dashboard frontend.

The API exposes existing recommendations, query profiles, workload analysis,
benchmark evidence, cost-benefit evidence, composite-index analysis,
production decisions, guardrails, and provenance.

The API does not introduce new recommendation, scoring, benchmarking,
cost-benefit, or production-decision logic.

---

### 2. Base Path

All dashboard endpoints use:

    /api

---

### 3. Read-Only Contract

M20 API endpoints must not:

- create database indexes
- drop database indexes
- execute benchmark experiments
- modify benchmark results
- generate new recommendations
- calculate production decisions independently
- modify M13-M19 evidence
- convert missing evidence into zero
- infer experimental linkage that has not been established

---

### 4. Endpoint Contract

The following endpoints define the target M20 API surface.

The endpoints currently implemented and validated are:

- `GET /api/overview`
- `GET /api/recommendations`
- `GET /api/recommendations/{recommendation_id}`

The remaining endpoints are part of the planned M20 implementation and will be added incrementally.
| Method | Endpoint | Response |
|---|---|---|
| GET | `/api/overview` | `OverviewResponse` |
| GET | `/api/recommendations` | `list[RecommendationResponse]` |
| GET | `/api/recommendations/{recommendation_id}` | `RecommendationResponse` |
| GET | `/api/queries` | `list[QueryResponse]` |
| GET | `/api/queries/{fingerprint}` | `QueryResponse` |
| GET | `/api/workloads` | `list[WorkloadResponse]` |
| GET | `/api/workloads/{fingerprint}` | `WorkloadResponse` |
| GET | `/api/benchmarks` | `list[BenchmarkResponse]` |
| GET | `/api/benchmarks/{benchmark_id}` | `BenchmarkResponse` |
| GET | `/api/cost-benefit` | `list[CostBenefitResponse]` |
| GET | `/api/composite-indexes` | `list[CompositeIndexResponse]` |
| GET | `/api/decisions` | `list[ProductionDecisionResponse]` |
| GET | `/api/decisions/{recommendation_id}` | `ProductionDecisionResponse` |
| GET | `/api/provenance/{recommendation_id}` | `ProvenanceResponse` |

---

### 5. Filtering

Collection endpoints may support read-only filtering.

Examples:

- recommendation priority
- recommendation score range
- workload priority
- validation outcome
- evidence status
- decision state
- query fingerprint

Filtering must not change the underlying evidence or decision.

---
### 6. Pagination

Collection endpoints may support:

- `limit`
- `offset`

Pagination is a planned API capability. Defaults and maximum values
will be defined when pagination is introduced during route implementation.

Pagination is a presentation/API concern and must not alter M13-M19 calculations.

---

### 7. Evidence Semantics

Missing evidence must remain explicitly missing.

For example:

```json
{
  "median_improvement_percent": null
}
