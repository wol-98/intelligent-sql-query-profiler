# Intelligent SQL Query Profiler & Index Optimization Engine

A research-oriented system for profiling SQL workloads, analyzing PostgreSQL execution plans, generating index recommendations, experimentally validating those recommendations, and evaluating their performance, workload, cost, decision, and provenance evidence.

**Project Type:** MSc End Semester Project
**Team:** Wol, Delvin, Leon, Samrin
**Database:** PostgreSQL / Supabase
**Backend:** Python + FastAPI
**Frontend:** React + Vite + Tailwind CSS

---

## 1. Project Overview

The **Intelligent SQL Query Profiler & Index Optimization Engine** is designed to investigate whether workload-aware analysis of SQL query patterns and database characteristics can be used to generate index recommendations that produce measurable changes in query performance.

The system observes SQL workloads, captures execution information, parses SQL structure, analyzes PostgreSQL execution plans, extracts features, generates candidate indexes, produces explainable recommendations, and validates selected recommendations through controlled experiments.

The project was subsequently extended with workload analysis, composite-index column-order experiments, index storage and maintenance analysis, cost-benefit experiments, production decision logic, and an evidence/provenance reporting dashboard.

The final system is a read-only reporting and analysis dashboard over the project's experimental evidence.

---

## 2. Problem Statement

Poorly optimized relational-database queries may scan large numbers of rows, perform costly joins, filter large tables, or otherwise consume database resources inefficiently.

Indexes can improve query performance, but secondary indexes also introduce storage and write-maintenance costs.

The project therefore focuses on:

- identifying potentially useful index candidates from observed workloads;
- analyzing query and execution-plan characteristics;
- generating explainable index recommendations;
- experimentally validating selected recommendations;
- measuring read-performance changes;
- measuring storage and write-side costs;
- evaluating workload-level importance;
- preserving explicit evidence linkage and provenance.

---

## 3. Research Question

> Can workload-aware analysis of SQL query patterns and database characteristics be used to generate effective index recommendations that produce measurable improvements in query performance?

The project treats this as an empirical question. Results are reported for the tested database, workload, PostgreSQL environment, data state, and experimental conditions rather than as universal performance claims.

---

## 4. Objectives

The project objectives are to:

1. Build a SQL workload observation and profiling pipeline.
2. Parse SQL queries and extract structural metadata.
3. Analyze PostgreSQL execution plans.
4. Extract features useful for index recommendation.
5. Generate candidate B-tree indexes.
6. Produce explainable recommendation scores and priorities.
7. Validate recommendations through controlled benchmarking.
8. Analyze workload frequency and execution-time concentration.
9. Evaluate composite-index column ordering experimentally.
10. Measure index storage and write-maintenance effects.
11. Link read-benefit and cost evidence when the same experimental index is used.
12. Establish production-oriented decision and guardrail states.
13. Preserve evidence provenance.
14. Present the resulting evidence through a read-only dashboard.

---

## 5. System Architecture

The final analytical workflow is:

```text
OBSERVE
   |
   v
PROFILE
   |
   v
PARSE
   |
   v
ANALYZE
   |
   v
RECOMMEND
   |
   v
VALIDATE
   |
   v
BENCHMARK
   |
   v
WORKLOAD ANALYSIS
   |
   v
COST / BENEFIT
   |
   v
PRODUCTION DECISION
   |
   v
EVIDENCE / PROVENANCE
   |
   v
REPORT / DASHBOARD
````

### Major layers

```text
PostgreSQL / Supabase
        |
        v
collector/
        |
        +-- Query collection
        +-- SQL parsing
        +-- Plan analysis
        +-- Feature extraction
        +-- Candidate generation
        +-- Recommendation engine
        +-- Benchmarking
        +-- Workload analysis
        +-- Experimental analysis
        |
        v
api/
        |
        +-- Read-only reporting API
        |
        v
dashboard/
        |
        +-- React + Vite + Tailwind
        +-- Optimization Intelligence Dashboard
```

---

## 6. Technology Stack

### Backend and analysis

* Python 3.12.3
* PostgreSQL
* Supabase PostgreSQL
* psycopg2
* SQLAlchemy
* pandas
* NumPy
* Faker
* SQL parsing utilities
* FastAPI
* Pydantic
* Uvicorn

### Frontend

* React
* Vite
* Tailwind CSS
* ESLint

### Development and version control

* Linux
* Git
* GitHub
* Python virtual environment (`.venv`)

The complete Python dependency environment is maintained in `requirements.txt`.

---

## 7. Database and Workload

The project uses PostgreSQL hosted through Supabase.

The database contains a synthetic transactional workload with the following primary business tables:

* `customers`
* `products`
* `orders`
* `order_items`
* `payments`
* `shipments`

The profiler also maintains analytical tables including:

* `query_profiles`
* `index_recommendations`
* `benchmark_results`

The database schema is maintained in:

```text
database/schema.sql
```

The controlled workload is maintained in:

```text
database/workload.sql
```

The official workload contains 15 queries identified as Q001-Q015.

The workload covers patterns including:

* equality filters;
* range filters;
* multiple predicates;
* joins;
* `ORDER BY` / `LIMIT`;
* `GROUP BY`;
* aggregation;
* large-table queries;
* queries where indexing may provide limited benefit.

All 15 official workload queries were successfully executed through the workload runner.

---

## 8. Baseline Workload

The official baseline workload contains:

| Query | Main Pattern                                         |
| ----- | ---------------------------------------------------- |
| Q001  | Equality filter on `orders.customer_id`              |
| Q002  | Equality filter on order status                      |
| Q003  | Recent-date filter                                   |
| Q004  | Multiple predicates                                  |
| Q005  | Date + amount range                                  |
| Q006  | Customer/order JOIN                                  |
| Q007  | Product category filter                              |
| Q008  | Product price range                                  |
| Q009  | `order_items` / `products` JOIN with category filter |
| Q010  | `ORDER BY` + `LIMIT`                                 |
| Q011  | `GROUP BY` customer                                  |
| Q012  | Filter + aggregation + `GROUP BY`                    |
| Q013  | Payment-status filter                                |
| Q014  | Shipment delivery-status filter                      |
| Q015  | Customer segment + JOIN + grouping/order             |

Baseline benchmarking uses PostgreSQL execution-plan information obtained through:

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
```

---

## 9. Core Components

### 9.1 Query Collector

Implemented in:

```text
collector/query_collector.py
```

The collector captures structured execution information including:

* query hash;
* query text;
* query type;
* execution time;
* planning time;
* actual rows;
* rows removed by filter;
* shared buffer hits;
* shared buffer reads;
* root plan information;
* detailed plan nodes;
* extracted plan features;
* capture timestamp.

### 9.2 SQL Parser

Implemented in:

```text
collector/query_parser.py
```

The parser normalizes query text and extracts structural metadata including:

* query type;
* tables;
* aliases;
* `WHERE` columns;
* JOIN columns;
* `ORDER BY` columns;
* `GROUP BY` columns.

The parser does not execute SQL.

### 9.3 Execution Plan Analyzer

Implemented in:

```text
collector/plan_analyzer.py
```

The analyzer recursively processes PostgreSQL JSON execution plans.

Extracted plan information includes:

* node type;
* relation;
* alias;
* index name;
* join type;
* actual rows;
* loops;
* estimated costs;
* estimated rows;
* rows removed by filters;
* shared buffer hits;
* shared buffer reads;
* filter conditions;
* index conditions;
* join conditions;
* hash conditions.

### 9.4 Feature Extraction

Implemented in:

```text
collector/feature_extractor.py
```

The system derives features describing:

* plan structure;
* scans;
* joins;
* aggregates;
* sorts;
* filters;
* index conditions;
* row statistics;
* buffer statistics;
* scan counts;
* join counts;
* Boolean plan indicators.

### 9.5 Index Candidate Generation

Implemented in:

```text
collector/index_candidate_generator.py
```

Candidate generation considers query and execution-plan information such as:

* `WHERE` columns;
* JOIN columns;
* `ORDER BY` columns;
* `GROUP BY` columns.

The system resolves qualified references and avoids generating candidates for already indexed columns where applicable.

### 9.6 Recommendation Engine

Implemented in:

```text
collector/recommendation_engine.py
```

The recommendation engine uses an explainable heuristic scoring model.

Signals include:

* filter usage;
* rows removed by filters;
* sequential scans;
* JOIN participation;
* `ORDER BY`;
* `GROUP BY`;
* existing index conditions.

Recommendations contain explanations describing the evidence contributing to the recommendation.

---

## 10. Validation and Benchmarking

Benchmarking is implemented in:

```text
collector/benchmark_runner.py
```

Repeated experiments can collect:

* execution time;
* planning time;
* actual rows;
* shared buffer hits;
* shared buffer reads;
* execution plans;
* average;
* median;
* minimum;
* maximum;
* standard deviation.

Candidate indexes are created temporarily during controlled experiments and removed afterward.

This preserves a controlled baseline and avoids treating experimental indexes as permanent production configuration.

---

## 11. Workload Analysis

The workload analysis layer groups observed queries using normalized query fingerprints.

The project records workload-level measures including:

* execution count;
* total execution time;
* average execution time;
* time share;
* frequency share;
* workload priority.

This allows recommendation analysis to consider not only an individual query but also its contribution to the observed workload.

---

## 12. Composite Index Analysis

The project includes query-pattern-aware composite-index generation and controlled column-order experiments.

M16.2 evaluates whether changing the ordering of columns within a composite B-tree index changes observed query performance.

Four controlled recommendations were evaluated:

| Recommendation | Original Order               | Alternative Order            |
| -------------- | ---------------------------- | ---------------------------- |
| Rec32          | `customer_id, status`        | `status, customer_id`        |
| Rec33          | `order_date, total_amount`   | `total_amount, order_date`   |
| Rec34          | `status, customer_id`        | `customer_id, status`        |
| Rec35          | `segment, customer_id, name` | `name, customer_id, segment` |

The project reports the measured effect of each ordering rather than assuming that one column ordering is universally optimal.

---

## 13. Index Cost Analysis

The project separately measures index cost.

### Storage

One controlled experiment measured:

| Metric            |          Result |
| ----------------- | --------------: |
| Index size        |   606,208 bytes |
| Table size        | 3,227,648 bytes |
| Index/table ratio |        18.7817% |

### Write maintenance

A controlled write experiment measured:

| Metric          |              Result |
| --------------- | ------------------: |
| Mean overhead   |            76.4914% |
| Median overhead | approximately 3.43% |

The observed write measurements showed substantial variability. The mean and median are therefore retained separately rather than treating the mean as a universal maintenance-cost estimate.

---

## 14. Cost-Benefit Experiments

M18 measures read benefit, storage cost, and write-side cost within controlled experiments.

| Experiment | Workload                       | Read Improvement | Storage Ratio | Mean Write Overhead |
| ---------- | ------------------------------ | ---------------: | ------------: | ------------------: |
| M18_004    | Q001 selective equality lookup |           96.15% |        18.78% |              61.95% |
| M18_005    | Q009 JOIN + category filter    |            0.83% |        25.00% |              17.49% |
| M18_006    | Q015 grouping + ordering       |           97.80% |        16.52% |              88.67% |

These values are descriptive of the tested experiments.

M18_004 and M18_005 have established same-index linkage to recommendation evidence in the integrated reporting dataset.

M18_006 is retained as a separate experimental cost-benefit result and is not treated as an established recommendation linkage.

In particular, M18_005 demonstrates that an experimental index can be used by the query plan while producing only a small measured read improvement. Therefore, index usage by itself is not treated as sufficient evidence of meaningful benefit.

---

## 15. Recommendation Evaluation

The project contains a recommendation-evaluation dataset with:

* 28 recommendation records;
* 22 evaluated recommendations;
* 23 stored benchmark records;
* 13 successful outcomes;
* 6 neutral outcomes;
* 4 unsuccessful outcomes;
* 0 unsafe outcomes.

The project retains measured evidence rather than converting these results into a universal claim about index effectiveness.

---

## 16. Production Decision Framework

The production decision layer combines:

* read-performance evidence;
* storage evidence;
* write-maintenance evidence;
* workload context;
* explicit evidence linkage;
* validation evidence;
* safety/guardrail checks.

Decision states include:

```text
RECOMMEND
REVIEW
REJECT
INSUFFICIENT_EVIDENCE
```

Guardrail states include:

```text
PASS
BLOCK
INSUFFICIENT_EVIDENCE
```

The decision layer does not treat missing evidence as zero cost or zero benefit.

Recommendations without sufficient linked evidence remain explicitly represented as insufficient evidence.

---

## 17. Evidence and Provenance

The final system maintains explicit provenance between recommendations and controlled experiments.

The provenance model distinguishes:

```text
LINKED
NOT_ESTABLISHED
```

from evidence completeness:

```text
COMPLETE
PARTIAL
INSUFFICIENT
```

A table/column similarity or matching query fingerprint is not by itself treated as proof that an experiment belongs to a recommendation.

For example, the final evidence dataset contains:

* 28 provenance records;
* 2 explicitly linked records;
* 26 records where provenance is not established;
* 2 complete evidence records;
* 26 insufficient evidence records.

This distinction is surfaced directly in the dashboard.

---

## 18. Optimization Intelligence Dashboard

The final dashboard is implemented with:

* React;
* Vite;
* Tailwind CSS.

It provides read-only reporting views for:

* Overview;
* Recommendations;
* Queries;
* Workloads;
* Benchmarks;
* Cost & Benefit;
* Composite Indexes;
* Production Decisions;
* Evidence & Provenance.

The dashboard does not create indexes, rerun experiments, or modify recommendation evidence.

The FastAPI reporting API exposes read-only endpoints for these analytical domains.

---

## 19. Project Structure

```text
intelligent-sql-query-profiler/
│
├── api/
│   ├── routes/
│   ├── schemas/
│   └── services/
│
├── collector/
│   ├── query_collector.py
│   ├── query_parser.py
│   ├── plan_analyzer.py
│   ├── feature_extractor.py
│   ├── index_candidate_generator.py
│   ├── recommendation_engine.py
│   ├── benchmark_runner.py
│   └── experimental analysis modules
│
├── config/
│   └── database.py
│
├── database/
│   ├── schema.sql
│   └── workload.sql
│
├── dashboard/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   ├── experiments.md
│   ├── PROJECT_IMPLEMENTATION_LOG.md
│   └── M20 dashboard documentation
│
├── tests/
│   └── project test suite
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 20. Installation

### Clone the repository

```bash
git clone https://github.com/wol-98/intelligent-sql-query-profiler.git
cd intelligent-sql-query-profiler
```

### Create the Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Configure the database

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` and provide the PostgreSQL/Supabase connection string:

```env
DATABASE_URL=postgresql://username:password@host:5432/database
```

Do not commit `.env`.

---

## 21. Database Setup

The schema is maintained in:

```text
database/schema.sql
```

The official workload is maintained in:

```text
database/workload.sql
```

The project uses PostgreSQL/Supabase as its database environment.

The database connection is centralized in:

```text
config/database.py
```

---

## 22. Running the Reporting API

From the project root:

```bash
source .venv/bin/activate
uvicorn api.main:app --reload
```

The API includes a health endpoint:

```text
GET /api/health
```

The service is designed as a read-only reporting API.

---

## 23. Running the Dashboard

In a second terminal:

```bash
cd dashboard
npm install
npm run dev
```

The development dashboard is served by Vite.

The frontend communicates with the local FastAPI reporting API.

---

## 24. Testing

### Python test suite

From the project root:

```bash
pytest -q
```

The final development checkpoint passed:

```text
430 passed
```

### Dashboard linting

```bash
npm --prefix dashboard run lint
```

### Dashboard production build

```bash
npm --prefix dashboard run build
```

### Git whitespace validation

```bash
git diff --check
```

---

## 25. Reproducibility and Evidence

The project separates:

* baseline workload evidence;
* recommendation evidence;
* validation evidence;
* benchmark evidence;
* workload evidence;
* composite-index evidence;
* storage evidence;
* write-maintenance evidence;
* linked cost-benefit evidence;
* production decision evidence;
* provenance evidence.

Experimental indexes are temporary and are removed after controlled experiments.

The project avoids assigning cost evidence to historical recommendations unless explicit same-index experimental linkage has been established.

---

## 26. Limitations

The results should be interpreted within the experimental scope.

Important limitations include:

* the workload uses synthetic data;
* experiments are conducted on a specific PostgreSQL/Supabase environment;
* execution time can vary because of caching, planner behavior, system load, and other environmental conditions;
* some experiments contain a limited number of measured iterations;
* mean and median measurements can differ substantially;
* workload behavior is specific to the tested queries and data distribution;
* not every recommendation has complete experimental cost-benefit evidence;
* the recommendation engine uses an explainable heuristic rather than a learned optimizer model;
* experimental measurements are not universal estimates of index performance.

The project therefore reports evidence and uncertainty explicitly rather than treating experimental observations as universal guarantees.

---

## 27. Future Scope

Possible future extensions include:

* larger and more diverse workloads;
* additional database engines;
* learned recommendation models;
* broader composite-index search;
* more extensive index-cost experiments;
* longer-running maintenance experiments;
* automated workload replay;
* additional query-plan features;
* production telemetry integration;
* expanded dashboard analytics.

These are future directions and are not represented as completed functionality.

---

## 28. Documentation

Detailed project documentation is maintained in:

```text
docs/
```

Important documents include:

```text
docs/PROJECT_IMPLEMENTATION_LOG.md
docs/experiments.md
docs/M20_DASHBOARD_ARCHITECTURE.md
docs/M20_DASHBOARD_API_CONTRACT.md
docs/M20_DASHBOARD_EVIDENCE_CONTRACT.md
docs/M20_DASHBOARD_ERROR_CONTRACT.md
docs/M20_DASHBOARD_INFORMATION_ARCHITECTURE.md
```

The implementation log is a chronological development record. It should be read together with the current README and dashboard documentation.

---

## 29. Team

| Member | Primary Area                              |
| ------ | ----------------------------------------- |
| Wol    | Database & Workload Engineering           |
| Delvin | Python Query Analysis                     |
| Leon   | Optimization & Recommendation Engineering |
| Samrin | Benchmarking & Visualization              |

The project is developed as an integrated system, with individual implementation responsibilities across the major components.

---

## 30. Project Status

The implementation roadmap has reached its final dashboard and evidence/provenance stage.

The current repository includes:

* SQL workload profiling;
* SQL parsing;
* execution-plan analysis;
* feature extraction;
* index candidate generation;
* recommendation scoring;
* benchmark validation;
* workload analysis;
* composite-index analysis;
* index cost analysis;
* cost-benefit experiments;
* production decision and guardrail logic;
* evidence and provenance reporting;
* read-only optimization intelligence dashboard.

The repository is maintained under Git version control and the final implementation is available on the `main` branch.

---

## License

This project was developed as an MSc academic project.
