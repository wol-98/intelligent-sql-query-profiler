**Intelligent SQL Query Profiler & Index Optimization Engine**  
**Project Implementation Log**  
**Project Type:** MSc End Semester Project  
   
 **Project Scope:** 100-mark research-oriented prototype  
   
 **Team:** Wol, Delvin, Leon, Samrin  
   
 **Current implementation checkpoint:** M15 — Query-Pattern-Aware Composite Index Generation
   
 **Repository:** intelligent-sql-query-profiler  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCkJfE1pYGfHAiAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrse4dwF6o2O55YAAAAASUVORK5CYII=)  
**1. Purpose of This Document**  
This document records the actual development and implementation progress of the **Intelligent SQL Query Profiler & Index Optimization Engine**.  
It is intended to:  
- maintain a chronological technical record of the project;  
- distinguish the originally planned scope from functionality actually implemented;  
- document the implementation approach, modules, experiments, findings, and limitations;  
- provide a basis for the final project report, presentation, and viva;  
- establish a clear baseline before the project is extended with advanced features.  
This is an **implementation log**, not the final project report. Future enhancements are explicitly separated from completed work.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsaeILbwZ9Fewo0Gs4E2ELcGWmTmqKwAA/uLeqr06v54AAPDa+gAthwNEfGhnhAAAAABJRU5ErkJggg==)  
**2. Original Project Definition**  
**2.1 Project Aim**  
The project aims to design and develop an intelligent SQL query profiling and index optimization system that analyzes database workloads, recommends appropriate indexes, and measures their actual impact on query performance.  
The original project plan defines the system as one that observes SQL workloads, profiles query performance, analyzes SQL structure and database characteristics, recommends candidate indexes, and experimentally validates whether recommendations improve query performance.  
**2.2 Problem Statement**  
Poorly optimized relational-database queries may scan large numbers of rows, perform costly joins, filter large tables, or otherwise consume database resources inefficiently.  
Indexes can improve query performance, but unnecessary indexes introduce storage and write-maintenance costs.  
The project therefore focuses on identifying useful index candidates from observed workloads and validating recommendations through measured experiments.  
**2.3 Research Question**  
*Can workload-aware analysis of SQL query patterns and database characteristics be used to generate effective index recommendations that produce measurable improvements in query performance?*  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSfYxKK/kYXEkyk8WcGbCFuCLTOzVXsAAPzFuVZ3dXw9AQDgtesB/v8F8JQadPwAAAAASUVORK5CYII=)  
**3. Original Planned Architecture**  
The original project plan defined the following high-level workflow:  
OBSERVE  
    ↓  
 PROFILE  
    ↓  
 PARSE  
    ↓  
 ANALYZE  
    ↓  
 RECOMMEND  
    ↓  
 IMPLEMENT  
    ↓  
 BENCHMARK  
    ↓  
 REPORT  
   
The planned system components were:  
1. PostgreSQL database  
2. Workload generator  
3. Query collector  
4. SQL parser  
5. Statistics analyzer  
6. Candidate generator  
7. Recommendation engine  
8. Benchmark engine  
9. Dashboard  
The project plan also identified the major development phases as requirements and architecture, database/workload development, query collection and parsing, candidate generation and scoring, benchmarking, integration, dashboard integration, experiments/refinement, and final report/viva preparation.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OUQmAABBAsSeYxZyXSzCJASxgACv4J8KWYMvMbNURAAB/ca7VXe1fTwAAeO16AKe+BdmJqrPdAAAAAElFTkSuQmCC)  
**4. Team Responsibilities**  
| | | |  
|-|-|-|  
| **Member** | **Role** | **Main Responsibility** |   
| Wol | Database & Workload Engineer | PostgreSQL, schema, synthetic data, workload, database environment |   
| Delvin | Python Query Analysis Engineer | Query collection, SQL parsing, classification and feature extraction |   
| Leon | Optimization & Recommendation Engineer | Candidate generation, scoring, ranking and explanations |   
| Samrin | Benchmarking & Visualization Engineer | Controlled experiments, metrics, validation and dashboard |   
   
The project is being developed as one integrated system. Individual ownership is used for implementation, but the complete architecture is intended to be understood by all members.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OMQ0AIAwAwZIgBKm1gjSMNCwYYCIkd9OP3zJzRMQMAAB+sfqJeroBAMCN2pTWBSSZVtjzAAAAAElFTkSuQmCC)  
**5. Development Milestone Overview**  
| | | |  
|-|-|-|  
| **Milestone** | **Area** | **Status** |   
| M0 | Environment and dependencies | Completed |   
| M1 | Database foundation | Completed |   
| M2 | Workload and baseline benchmarking | Completed |   
| M3 | Query collector | Completed |   
| M4 | SQL parser | Completed |   
| M5 | Execution-plan analysis and feature extraction | Completed |   
| M6 | Index candidate generation | Completed |   
| M7 | Recommendation engine | Completed |   
| M8 | Benchmarking engine | Completed |   
| M9 | Dashboard | Planned / not yet completed |   
| M10 | Validation decision layer | Completed |   
| M11 | Validation analysis and evaluation metrics | Completed |   
| Git checkpoint | Version-controlled baseline | Completed |   
| Advanced phase | Extended optimization intelligence | Next phase |   
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd49m4tA8nPaQJjWMGbCFuCLTOzV2cAAPzFvVZbdXw9AQDgtesBorcEPwOKyvQAAAAASUVORK5CYII=)  
   
**6. M0 — Environment and Project Setup**  
**6.1 Development Environment**  
The project is being developed in a Linux environment using Linux Mint.  
The Python environment uses:  
Python 3.12.3  
   
A project-specific virtual environment is maintained as:  
.venv/  
   
The virtual environment is excluded from Git.  
**6.2 Main Technologies**  
The current implementation uses:  
- Python  
- PostgreSQL  
- Supabase PostgreSQL  
- psycopg2  
- pandas  
- NumPy  
- SQL parsing utilities  
- SQLAlchemy  
- Faker  
- Streamlit  
- Plotly  
- Git/GitHub  
The project dependency list is maintained in:  
requirements.txt  
   
**6.3 Database Connection**  
Database access is centralized in:  
config/database.py  
   
The connection wrapper loads configuration from environment variables and connects to PostgreSQL using SSL.  
The .env file is deliberately excluded from Git because it contains database credentials.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsSfYxZo/kSGMYQLPJrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA4qrBdGuSdJuAAAAAElFTkSuQmCC)  
**7. M1 — Database Foundation**  
**7.1 Database Platform**  
The project uses **Supabase PostgreSQL** rather than a locally hosted PostgreSQL instance.  
The confirmed database environment is:  
PostgreSQL 17.6  
 Architecture: aarch64  
 Database: postgres  
 User: postgres  
   
The connection was independently tested successfully.  
**7.2 Relational Schema**  
The project uses a transactional business-style relational schema containing:  
customers  
 products  
 orders  
 order_items  
 payments  
 shipments  
   
The schema is maintained in:  
database/schema.sql  
   
**Customers**  
customer_id  
 name  
 city  
 segment  
 registration_date  
   
**Products**  
product_id  
 category_id  
 price  
 stock  
 product_name  
   
**Orders**  
order_id  
 customer_id  
 order_date  
 status  
 total_amount  
   
**Order Items**  
order_item_id  
 order_id  
 product_id  
 quantity  
 unit_price  
   
**Payments**  
payment_id  
 order_id  
 payment_date  
 method  
 amount  
 status  
   
**Shipments**  
shipment_id  
 order_id  
 shipment_date  
 carrier  
 delivery_status  
   
   
**7.3 Current Data Volume**  
The current database contains approximately:  
| | |  
|-|-|  
| **Table** | **Rows** |   
| customers | 10,000 |   
| products | 1,000 |   
| orders | 50,000 |   
| order_items | 150,000 |   
| payments | 50,000 |   
| shipments | 25,100 |   
   
The dataset is synthetic and is intended to provide repeatable workloads containing filtering, joining, sorting and aggregation patterns.  
**7.4 Secondary Index Strategy**  
No permanent secondary indexes are maintained for the baseline workload.  
Primary-key indexes remain part of the database schema.  
Candidate indexes are created temporarily during controlled validation experiments and removed after the experiment.  
This allows BEFORE/AFTER measurements without permanently changing the baseline database state.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3KsQ0AIRAEsUW6Qij1KvnevhMSYmKQ7GiCGd09k3wBAOAVf+2o4wYAwE1qAdYuAy151mgcAAAAAElFTkSuQmCC)  
**8. M2 — Workload Design and Baseline**  
The controlled workload is maintained in:  
database/workload.sql  
   
It currently contains 15 SQL queries identified as Q001–Q015.  
The workload was designed to cover the query patterns identified in the original project plan:  
- equality filters;  
- range filters;  
- multiple predicates;  
- JOIN-heavy queries;  
- ORDER BY/LIMIT;  
- GROUP BY and aggregation;  
- large-table queries;  
- queries where indexing may provide little benefit.  
**8.1 Query Workload**  
| | |  
|-|-|  
| **Query** | **Main Pattern** |   
| Q001 | Equality filter on orders.customer_id |   
| Q002 | Equality filter on orders.status |   
| Q003 | Recent-date filter |   
| Q004 | Multiple predicates |   
| Q005 | Date + amount range conditions |   
| Q006 | JOIN with customer-city filter |   
| Q007 | Product category filter |   
| Q008 | Product price range |   
| Q009 | JOIN between order_items and products with category filter |   
| Q010 | ORDER BY/LIMIT |   
| Q011 | GROUP BY customer |   
| Q012 | Filter + aggregation + GROUP BY |   
| Q013 | Payment-status filter |   
| Q014 | Shipment delivery-status filter |   
| Q015 | Customer segment + JOIN + GROUP BY/ORDER BY |   
   
All 15 workload queries were successfully executed through the workload runner.  
Result:  
15 successful  
 0 failures  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsad4EEtY9QcxnUms4E2ELcGWmTmrKwAA/uLeqrU6vp4AAPDa/gDzXgM37EF77AAAAABJRU5ErkJggg==)  
**9. M2 — Baseline Benchmarking**  
The complete baseline workload was benchmarked using PostgreSQL:  
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)  
   
The benchmark runner records execution and planning information from the returned JSON plan.  
Representative baseline execution times included:  
| | |  
|-|-|  
| **Query** | **Average Execution Time** |   
| Q001 | 3.644 ms |   
| Q002 | 6.770 ms |   
| Q003 | 13.373 ms |   
| Q004 | 4.238 ms |   
| Q005 | 14.218 ms |   
| Q006 | 14.525 ms |   
| Q007 | 0.184 ms |   
| Q008 | 0.232 ms |   
| Q009 | 32.374 ms |   
| Q010 | 9.178 ms |   
| Q011 | 20.768 ms |   
| Q012 | 17.768 ms |   
| Q013 | 7.474 ms |   
| Q014 | 3.630 ms |   
| Q015 | 26.720 ms |   
   
Q009 was one of the most expensive controlled workload queries and consequently became an important validation case.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSPBCj7fFRYQwYwEZiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AMTJBeJDClAyAAAAAElFTkSuQmCC)  
**10. M3 — Query Collector**  
The query collection functionality is implemented in:  
collector/query_collector.py  
   
The collector executes workload queries using PostgreSQL EXPLAIN ANALYZE information and stores structured profiling information.  
The captured profile includes:  
- query hash;  
- query text;  
- query type;  
- execution time;  
- planning time;  
- actual rows;  
- rows removed by filter;  
- shared buffer hits;  
- shared buffer reads;  
- root plan information;  
- detailed plan nodes;  
- extracted plan features;  
- capture timestamp.  
The collector therefore forms the bridge between raw SQL execution and structured analysis.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NIGRTPXNaQBrWMGbCFuCLTOzV2cAAPzFvVZbdXw9AQDgtesBhZQEOYZGgUEAAAAASUVORK5CYII=)  
**11. M4 — SQL Parser**  
The SQL parser is implemented in:  
collector/query_parser.py  
   
The parser does not execute SQL.  
It normalizes query text and extracts structural metadata including:  
query  
 query_type  
 tables  
 aliases  
 where_columns  
 join_columns  
 order_by_columns  
 group_by_columns  
   
The parser was tested against the controlled workload.  
A later diagnostic identified and corrected GROUP BY parsing so that examples such as:  
Q011 → customer_id  
 Q012 → customer_id  
 Q015 → c.customer_id, c.name  
   
are correctly represented.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsad4EEtY9QcxnUms4E2ELcGWmTmrKwAA/uLeqrU6vp4AAPDa/gDzXgM37EF77AAAAABJRU5ErkJggg==)  
**12. M5 — Execution Plan Analysis**  
Execution-plan analysis is implemented in:  
collector/plan_analyzer.py  
   
The analyzer recursively walks PostgreSQL's JSON execution plan.  
For every plan node, the system extracts information such as:  
depth  
 node_type  
 relation_name  
 alias  
 index_name  
 join_type  
 actual_rows  
 actual_loops  
 startup_cost  
 total_cost  
 plan_rows  
 plan_width  
 rows_removed_by_filter  
 shared_hit_blocks  
 shared_read_blocks  
 filter  
 index_condition  
 join_filter  
 hash_condition  
   
The recursive analyzer was tested on a Hash Join example containing:  
Hash Join  
 ├── Seq Scan  
 └── Hash  
     └── Seq Scan  
   
and correctly identified four plan nodes.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsSdYxKY/jMFMIZ7ECt5E2BJsmZmt2gMA4C+Otbqr8+sJAACvXQ85QgYXd/O+eQAAAABJRU5ErkJggg==)  
**13. M5 — Feature Extraction**  
Feature extraction is implemented in:  
collector/feature_extractor.py  
   
The system derives structured features from the analyzed execution plan.  
Current feature groups include:  
**Plan structure**  
node_count  
 node_types  
 tables  
   
**Operations**  
scan_nodes  
 join_nodes  
 aggregate_nodes  
 sort_nodes  
   
**Conditions**  
filters  
 index_conditions  
 join_conditions  
 index_names  
   
**Row and buffer statistics**  
total_actual_rows  
 total_plan_rows  
 total_rows_removed_by_filter  
 total_shared_hit_blocks  
 total_shared_read_blocks  
   
**Scan and join counts**  
seq_scan_count  
 index_scan_count  
 bitmap_scan_count  
 hash_join_count  
 nested_loop_count  
 merge_join_count  
   
**Boolean indicators**  
has_filter  
 has_index_condition  
 has_join  
 has_sequential_scan  
 has_index_scan  
   
An important implementation detail is that actual_rows at the root of a plan represents the query's returned rows, while total_actual_rows sums rows across plan nodes. These are intentionally different measurements.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NIGhrOTvaQBrWMGbCFuCLTOzV2cAAPzFvVZbdXw9AQDgtesBhYQEO+64Y8AAAAAASUVORK5CYII=)  
**14. M6 — Index Candidate Generation**  
Candidate generation is implemented in:  
collector/index_candidate_generator.py  
   
The generator identifies possible B-tree indexes from query metadata and execution-plan information.  
Candidate sources currently include:  
- WHERE columns;  
- JOIN columns;  
- ORDER BY columns;  
- GROUP BY columns.  
The generator resolves qualified references through table aliases and avoids generating candidates for existing indexed columns.  
Examples generated from the controlled workload include:  
orders.customer_id  
 orders.status  
 orders.order_date  
 orders.total_amount  
 customers.city  
 customers.segment  
 customers.name  
 products.category_id  
 products.price  
 order_items.product_id  
 payments.status  
 shipments.delivery_status  
   
Candidate diagnostics were run successfully across the workload.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OUQmAABBAsSeILQSjXgcrmkOs4J8IW4ItM7NXZwAA/MW1Vlt1fBwBAOC9+wEukwQ+V/SggAAAAABJRU5ErkJggg==)  
**15. M7 — Recommendation Engine**  
The recommendation engine is implemented in:  
collector/recommendation_engine.py  
   
The current system uses an explainable heuristic score.  
Signals include:  
- filter usage;  
- rows removed by filters;  
- sequential scans;  
- JOIN participation;  
- ORDER BY usage;  
- GROUP BY usage;  
- presence of an existing index condition.  
The current scoring model uses weighted evidence.  
Examples of score contributions include:  
Filter condition                  +30  
 Very high rows removed            +25  
 High rows removed                 +15  
 Significant rows removed          +10  
 Rows removed                      +5  
 Sequential scan                   +20  
 Join condition                    +15  
 ORDER BY                          +10  
 GROUP BY                          +10  
 Existing index condition          -20  
   
The final score is bounded between 0 and 100.  
Each recommendation contains an explanation describing the evidence that contributed to the score.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAALUlEQVR4nO3OQQ0AIAwEsAMlSJ0UrOFkGngRklZBR1WtJDsAAPzizNcDAADuNcKwAyU+nb+5AAAAAElFTkSuQmCC)  
**16. M7 — Recommendation Results**  
The recommendation pipeline generated 24 stored recommendation records.  
The official workload profiles correspond to profiles 2–16.  
There is one duplicate Q009 profile/recommendation occurrence in the current development history, so benchmark records and recommendation records are not interpreted as a strict one-to-one mapping.  
Current recommendation priorities include:  
High  
 Medium  
 Low  
   
The recommendation engine successfully produces candidate indexes and persists them in:  
index_recommendations  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNBACPykMH4NpGACyywEZJWQZeZ2aszAAD+4l6rrTo+jgAA8N71AL/CBEiG5xPoAAAAAElFTkSuQmCC)  
**17. M8 — Benchmark Engine**  
Benchmark functionality is implemented in:  
collector/benchmark_runner.py  
   
The benchmark runner executes:  
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)  
   
and extracts:  
- execution time;  
- planning time;  
- root actual rows;  
- root shared buffer hits;  
- root shared buffer reads;  
- execution plan.  
For repeated benchmarking it calculates:  
average  
 median  
 minimum  
 maximum  
 standard deviation  
 average planning time  
 average rows  
 average shared buffer hits  
 average shared buffer reads  
   
A representative plan is also retained.  
The benchmark runner supports warm-up executions before measured runs.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhwgJOUPcjIpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaJEEL8XMiYMAAAAASUVORK5CYII=)  
**18. M8 — Controlled Index Validation**  
Index validation is implemented in:  
collector/index_validator.py  
   
The validation protocol is:  
1. Benchmark BEFORE  
 2. Create temporary index  
 3. ANALYZE affected table  
 4. Benchmark AFTER  
 5. Detect whether the experimental index was used  
 6. Compare plans  
 7. Compare returned rows  
 8. Calculate improvement  
 9. Drop temporary index  
   
The validator always attempts to remove the temporary index after the experiment.  
The index name is generated deterministically:  
idx_<table>_<column>  
   
The validator checks the returned execution plan recursively for use of the experimental index.  
It records:  
execution_time_before_ms  
 execution_time_after_ms  
 median_before_ms  
 median_after_ms  
 improvement_percentage  
 median_improvement_percentage  
 rows_before  
 rows_after  
 rows_preserved  
 index_used  
 index_node_type  
 plan_changed  
 before_plan  
 after_plan  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhYMMAKlD4OzrxgQU2QtIq6DIzR3UFAMBf3Gu1VefXEwAAXtsfSqADWz4G/HUAAAAASUVORK5CYII=)  
**19. Q009 Validation Experiment**  
Q009 became an important test case because it performs a join involving:  
order_items  
 products  
   
with a category filter.  
The baseline plan included:  
Hash Join  
 ├── Seq Scan → order_items  
 └── Hash  
     └── Seq Scan → products  
   
The baseline Q009 benchmark was approximately:  
Average execution time: 32.623 ms  
 Median execution time: 32.499 ms  
   
A controlled experiment using:  
products(category_id)  
   
demonstrated that the experimental index could be used through a:  
Bitmap Index Scan  
   
while the measured performance benefit varied across repeated experiments.  
One experiment produced approximately:  
Average improvement: 1.55%  
 Median improvement: 2.53%  
   
Another later controlled experiment produced a negative average improvement while still showing index usage.  
This variation became an important observation for evaluating the recommendation scoring model.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNhYMEBIpD4ArCJDyywEZJWQZeZOaorAAD+4l6rrTq/ngAA8Nr+AEqmA1hl45m5AAAAAElFTkSuQmCC)  
**20. Benchmark Result Persistence**  
Benchmark results are stored in:  
benchmark_results  
   
The original table stored:  
benchmark_id  
 recommendation_id  
 query_text  
 execution_time_before_ms  
 execution_time_after_ms  
 improvement_percentage  
 rows_before  
 rows_after  
 before_plan  
 after_plan  
 benchmarked_at  
   
The schema was subsequently extended to preserve validation evidence:  
median_before_ms  
 median_after_ms  
 median_improvement_percentage  
 rows_preserved  
 index_used  
 index_node_type  
 plan_changed  
 validation_status  
 validation_reason  
   
This change allowed the project to retain not only performance numbers but also evidence about correctness and execution-plan behavior.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsad4FCtY9ecwnkms4E2ELcGWmTmrKwAA/uLeqrU6vp4AAPDa/gDzUgM9+S8z3AAAAABJRU5ErkJggg==)  
**21. M10 — Validation Evidence Backfill**  
A backfill procedure was created in:  
tests/backfill_validation_evidence.py  
   
The purpose was to reconstruct validation evidence for previously stored benchmark results.  
The procedure:  
1. reads stored BEFORE/AFTER plans;  
2. retrieves the corresponding recommendation;  
3. reconstructs the expected temporary index name;  
4. searches the AFTER plan recursively for index usage;  
5. compares BEFORE and AFTER plans;  
6. verifies row preservation;  
7. updates validation evidence fields.  
All 23 existing benchmark records were successfully updated.  
Observed evidence:  
Rows preserved: 100% of records  
 Plan changed: 100% of records  
   
Index usage varied between recommendations.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSPBCj5fFyM6mJHAjAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrsexOEF35f1aEgAAAAASUVORK5CYII=)  
**22. M10 — Validation Decision Layer**  
The decision layer is implemented in:  
collector/validation_decision.py  
   
The current decision rules are:  
If rows are not preserved:  
     UNSAFE  
   
 Else if improvement < 0%:  
     UNSUCCESSFUL  
   
 Else if rows are preserved,  
      index is used,  
      and improvement >= 5%:  
     SUCCESSFUL  
   
 Else:  
     NEUTRAL  
   
Where median improvement is available, it is used preferentially; otherwise average improvement is used.  
The threshold currently used for a successful recommendation is:  
5%  
   
The decision layer does not rerun benchmark experiments. It evaluates already stored validation evidence.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhZscYahheJwqQgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseoqcEQXyAWBgAAAAASUVORK5CYII=)  
   
**23. M10 — Validation Results**  
The current validation dataset contains:  
23 benchmark experiments  
 22 distinct validated recommendations  
   
Current decision summary:  
| | |  
|-|-|  
| **Status** | **Count** |   
| SUCCESSFUL | 13 |   
| NEUTRAL | 6 |   
| UNSUCCESSFUL | 4 |   
| UNSAFE | 0 |   
   
This corresponds to:  
Success rate: 56.52%  
   
The results demonstrate that the recommendation engine does not automatically treat every candidate as beneficial.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OMQ0AIAwAwZIgBKnVgjN8dGDBABMhuZt+/JaZIyJmAADwi9VP1NMNAABu1AaU3AUhiyfJeAAAAABJRU5ErkJggg==)  
   
**24. M11 — Validation Analysis**  
Validation analysis is implemented in:  
collector/validation_analysis.py  
   
The module is read-only with respect to the validation results. It does not:  
- execute benchmark queries;  
- create indexes;  
- modify database indexes.  
It reads completed benchmark and recommendation records and calculates project-level evaluation metrics.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd49m4tA8nPaQJjWMGbCFuCLTOzV2cAAPzFvVZbdXw9AQDgtesBorcEPwOKyvQAAAAASUVORK5CYII=)  
   
**25. M11 — Overall Validation Metrics**  
Current results:  
Total experiments       : 23  
 Successful              : 13  
 Neutral                 : 6  
 Unsuccessful            : 4  
 Unsafe                  : 0  
   
Performance metrics:  
Success rate            : 56.52%  
 Index usage rate        : 78.26%  
 Rows preserved rate     : 100.00%  
 Plan change rate        : 100.00%  
 Average improvement     : 33.19%  
   
These metrics describe the current validation dataset and should not be interpreted as universal performance guarantees.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OMQ0AIAwAwZIgBKn1gjJsdGLBABMhuZt+/JaZIyJmAADwi9VP1NMNAABu1AaU4gUeBSGW2wAAAABJRU5ErkJggg==)  
**26. M11 — Performance by Validation Status**  
Current results:  
| | | | | |  
|-|-|-|-|-|  
| **Status** | **Count** | **Average Improvement** | **Maximum** | **Minimum** |   
| SUCCESSFUL | 13 | 58.16% | 97.79% | 11.92% |   
| NEUTRAL | 6 | 2.64% | 4.16% | 0.79% |   
| UNSUCCESSFUL | 4 | -2.12% | -1.33% | -2.68% |   
| UNSAFE | 0 | 0.00% | 0.00% | 0.00% |   
   
The results provide evidence that the validation layer can distinguish useful, low-benefit and negatively performing recommendations.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhwgJGkPcrHpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaJkELjbMzy0AAAAASUVORK5CYII=)  
**27. M11 — Recommendation Quality**  
Current recommendation-score analysis:  
Average recommendation score       : 61.09  
 Successful average score            : 66.92  
 Neutral average score               : 58.33  
 Unsuccessful average score          : 46.25  
   
Priority analysis:  
High-priority recommendations       : 10  
 High-priority successful             : 9  
 High-priority success rate           : 90.00%  
   
The high-priority success rate is an observation from the current experimental dataset. It is not sufficient by itself to establish general predictive accuracy.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSPBCj5fFyM6mJHAjAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrsexOEF35f1aEgAAAAASUVORK5CYII=)  
**28. M11 — Detailed Recommendation Evaluation**  
The analysis now produces a row-level evaluation containing:  
Benchmark  
 Query profile  
 Table  
 Column  
 Recommendation score  
 Priority  
 Measured improvement  
 Index usage  
 Plan change  
 Validation status  
   
The detailed evaluation exposed several useful cases.  
One important example is Q009:  
products.category_id  
 Score: 60  
 Measured result: low/negative improvement in recorded experiments  
   
 order_items.product_id  
 Score: 35  
 Measured result: approximately 76% improvement in one validated experiment  
   
This demonstrates an important limitation of the current heuristic:  
*Recommendation score is a prioritization heuristic and is not a guarantee of measured performance improvement.*  
This finding provides a direct motivation for future improvements to the recommendation model.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNBACP6MMH6NpGACyywEZJWQZeZ2aszAAD+4l6rrTq+ngAA8Nr1AL+6BElk4wV6AAAAAElFTkSuQmCC)  
**29. M11 — Query-Level Validation Analysis**  
Validation results are grouped by query profile.  
The current analysis calculates:  
number of recommendations  
 successful recommendations  
 neutral recommendations  
 unsuccessful recommendations  
 unsafe recommendations  
 average improvement  
 best improvement  
   
Examples from the current results:  
| | | | | | |  
|-|-|-|-|-|-|  
| **Profile** | **Recommendations** | **Successful** | **Neutral** | **Unsuccessful** | **Avg Improvement** |   
| 2 | 1 | 1 | 0 | 0 | 96.11% |   
| 3 | 1 | 1 | 0 | 0 | 39.30% |   
| 4 | 1 | 1 | 0 | 0 | 89.04% |   
| 5 | 2 | 2 | 0 | 0 | 59.90% |   
| 6 | 2 | 1 | 1 | 0 | 38.29% |   
| 7 | 2 | 0 | 2 | 0 | 2.26% |   
| 8 | 1 | 0 | 1 | 0 | 3.81% |   
| 9 | 1 | 1 | 0 | 0 | 51.72% |   
| 10 | 3 | 1 | 0 | 2 | 24.08% |   
| 11 | 1 | 1 | 0 | 0 | 97.79% |   
| 12 | 1 | 1 | 0 | 0 | 34.97% |   
| 13 | 2 | 1 | 0 | 1 | 4.62% |   
| 14 | 1 | 1 | 0 | 0 | 32.13% |   
| 15 | 1 | 1 | 0 | 0 | 33.23% |   
| 16 | 3 | 0 | 2 | 1 | 1.00% |   
   
This analysis shows that optimization benefit varies significantly by query and candidate index.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4EKxgBjP+Asa0hxW8ibAl2DIzR3UFAMBf3Gu1VefXEwAAXtsfSqwDVbgKngwAAAAASUVORK5CYII=)  
**30. M11 — Coverage and Low-Benefit Analysis**  
The current coverage/low-benefit analysis distinguishes unique validated recommendations from benchmark experiments.  
Current results:  
Validated recommendations       : 22  
 Positive-benefit experiments     : 19  
 Low-benefit experiments          : 10  
 Index-used low-benefit cases     : 5  
 Index-not-used cases             : 5  
   
Rates:  
Positive-benefit rate            : 82.61%  
 Low-benefit rate                 : 43.48%  
 Index-not-used rate              : 21.74%  
   
The terminology intentionally distinguishes **recommendations** from  **experiments**, because one recommendation can appear in more than one benchmark record.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNBCkLfFDZwwIgHRiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AOH0BedHjjlfAAAAAElFTkSuQmCC)  
**31. Important Findings So Far**  
The implementation has produced several findings that will be relevant to the final evaluation.  
**31.1 Index recommendations can produce substantial improvements**  
Several validated recommendations produced improvements greater than 70%, with the highest observed improvement approximately 97.79%.  
**31.2 Not every recommendation is beneficial**  
Four validation experiments were classified as unsuccessful.  
Six were classified as neutral because the measured benefit did not meet the 5% threshold or did not satisfy all success conditions.  
**31.3 Index usage does not automatically imply meaningful benefit**  
An index can be selected by PostgreSQL while producing only a small improvement.  
This is demonstrated by several low-benefit cases.  
**31.4 A recommendation score is not equivalent to measured performance**  
The Q009 experiments provide evidence that heuristic scores do not perfectly predict measured benefit.  
This is an important limitation and a potential research direction.  
**31.5 Experimental validation is necessary**  
The current results support the original project design decision to validate recommendations through controlled BEFORE/AFTER experiments rather than relying only on heuristic scoring.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsSfYxZo/khWsYQLPJrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA4qjBdKlX6OKAAAAAElFTkSuQmCC)  
**32. Testing Implemented So Far**  
The project contains tests covering:  
connection  
 plan analyzer  
 feature extractor  
 query parser  
 index candidate generator  
 candidate diagnostics  
 recommendation engine  
 recommendation repository  
 benchmark runner  
 index validator  
 recommendation integration  
 full recommendation pipeline  
 full benchmark  
 validation decision  
 benchmark integration  
 validation evidence backfill  
   
The workload runner successfully executed all 15 controlled queries.  
The candidate diagnostics completed successfully after correcting GROUP BY extraction.  
The recommendation pipeline completed successfully and stored recommendations.  
The validation suite completed successfully for the official recommendations.  
The M11 analysis module currently executes successfully against the stored validation dataset.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhwgJWEPcbJpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaIkEMIPgIvAAAAAASUVORK5CYII=)  
**33. Current Repository Structure**  
The current repository contains:  
intelligent-sql-query-profiler/  
 │  
 ├── .gitignore  
 ├── README.md  
 ├── requirements.txt  
 │  
 ├── collector/  
 │   ├── __init__.py  
 │   ├── benchmark_repository.py  
 │   ├── benchmark_runner.py  
 │   ├── feature_extractor.py  
 │   ├── index_candidate_generator.py  
 │   ├── index_validator.py  
 │   ├── plan_analyzer.py  
 │   ├── query_collector.py  
 │   ├── query_parser.py  
 │   ├── recommendation_engine.py  
 │   ├── recommendation_repository.py  
 │   ├── validation_analysis.py  
 │   ├── validation_decision.py  
 │   └── workload_runner.py  
 │  
 ├── config/  
 │   ├── __init__.py  
 │   └── database.py  
 │  
 ├── database/  
 │   ├── schema.sql  
 │   └── workload.sql  
 │  
 ├── docs/  
 │   ├── experiments.md  
 │   └── PROJECT_IMPLEMENTATION_LOG.md  
 │  
 └── tests/  
     ├── __init__.py  
     ├── backfill_validation_evidence.py  
     ├── test_all_index_validations.py  
     ├── test_benchmark_integration.py  
     ├── test_benchmark_runner.py  
     ├── test_candidate_diagnostics.py  
     ├── test_connection.py  
     ├── test_feature_extractor.py  
     ├── test_full_benchmark.py  
     ├── test_full_recommendation_pipeline.py  
     ├── test_index_candidate_generator.py  
     ├── test_index_validator.py  
     ├── test_plan_analyzer.py  
     ├── test_query_parser.py  
     ├── test_recommendation_engine.py  
     ├── test_recommendation_integration.py  
     ├── test_recommendation_repository.py  
     └── test_validation_decision.py  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsScYxpg/h5VMYARvRrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA224BcUMk6pDAAAAAElFTkSuQmCC)  
**34. Git/GitHub Checkpoint**  
A Git repository was initialized for the project.  
The branch was renamed from:  
master  
   
to:  
main  
   
The GitHub remote is:  
git@github.com:wol-98/intelligent-sql-query-profiler.git  
   
The initial project implementation through the M11 validation-analysis stage was committed and pushed to GitHub.  
The .gitignore protects:  
.env  
 .venv/  
 __pycache__/  
 *.pyc  
   
This prevents database credentials, virtual-environment files and Python cache files from being committed.  
This GitHub checkpoint serves as the stable baseline before the next development phase.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhYMMAKlD4OzrxgQU2QtIq6DIzR3UFAMBf3Gu1VefXEwAAXtsfSqADWz4G/HUAAAAASUVORK5CYII=)  
**35. Current Implementation Status**  
**Completed Core System**  
The following functionality is operational:  
PostgreSQL database  
         ↓  
 Controlled workload  
         ↓  
 Query collection  
         ↓  
 SQL parsing  
         ↓  
 Execution-plan analysis  
        ↓  
 Feature extraction  
         ↓  
 Index candidate generation  
         ↓  
 Explainable recommendation scoring  
         ↓  
 Controlled index validation  
         ↓  
 Benchmarking  
         ↓  
 Validation evidence  
         ↓  
 Validation decision  
         ↓  
 M11 evaluation  
   
The project therefore has a working end-to-end optimization prototype.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OMQ0AIAwAwdIgBKl1gjacsGCAiZDcTT9+q6oRETMAAPjF6ify6QYAADdyA9Y0AypN+bdfAAAAAElFTkSuQmCC)  
**36. Current Limitations**  
The current implementation is intentionally still a controlled research prototype.  
**36.1 Heuristic recommendation model**  
The recommendation score is rule-based and has not yet been trained or calibrated against a larger experimental dataset.  
**36.2 Single-column candidate focus**  
The current candidate generator primarily produces single-column B-tree candidates.  
Composite-index generation has not yet been implemented.  
**36.3 Controlled workload size**  
The current workload consists of 15 queries and the current database uses a fixed synthetic dataset.  
Larger workloads and multiple data scales have not yet been systematically evaluated.  
**36.4 Limited query normalization**  
The parser currently extracts structural metadata but does not yet provide a complete query-fingerprinting system.  
**36.5 Dashboard**  
The project plan includes a dashboard, but the complete Streamlit dashboard has not yet been integrated into the current repository baseline.  
**36.6 Advanced statistical evaluation**  
The current M11 analysis calculates descriptive metrics. A more comprehensive statistical analysis of repeated benchmark distributions is still planned.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSfYxKK/kYXEkyk8WcGbCFuCLTOzVXsAAPzFuVZ3dXw9AQDgtesB/v8F8JQadPwAAAAASUVORK5CYII=)  
**37. Planned Advanced Development**  
The following features were identified in the original project scope as possible enhancements and are candidates for the next development phase.  
**Priority 1 — Query Intelligence**  
- query normalization;  
- query fingerprinting;  
- workload frequency analysis;  
- query performance ranking;  
- selectivity analysis;  
- cardinality analysis;  
- execution-plan anomaly detection.  
**Priority 2 — Advanced Index Optimization**  
- composite-index candidate generation;  
- column-order evaluation for composite indexes;  
- index redundancy detection;  
- workload-level index recommendations;  
- indexes affecting multiple queries;  
- cost-aware recommendations.  
**Priority 3 — Recommendation Intelligence**  
- recommendation confidence;  
- improved scoring;  
- historical validation evidence;  
- adaptive recommendation scoring;  
- comparison between heuristic and data-driven models;  
- optional machine-learning prediction of recommendation outcomes.  
**Priority 4 — Experimental Evaluation**  
- larger benchmark suites;  
- multiple data sizes;  
- repeated experiments;  
- statistical significance analysis;  
- performance distributions;  
- recommendation precision;  
- recommendation coverage;  
- false-positive analysis;  
- low-benefit analysis;  
- index overhead analysis.  
**Priority 5 — Product Layer**  
- Streamlit dashboard;  
- query explorer;  
- recommendation explorer;  
- benchmark visualization;  
- execution-plan visualization;  
- validation dashboard;  
- experiment history;  
- database insights;  
- automated optimization reports.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OUQmAABBAsSeILQSjXgcrmkOs4J8IW4ItM7NXZwAA/MW1Vlt1fBwBAOC9+wEukwQ+V/SggAAAAABJRU5ErkJggg==)  
**38. Proposed Next-Phase Architecture**  
The extended architecture will evolve toward:  
                         DATABASE  
                             │  
                             ▼  
                   WORKLOAD COLLECTION  
                             │  
                             ▼  
                    QUERY FINGERPRINT  
                             │  
                             ▼  
                      SQL PARSING  
                             │  
                             ▼  
                   QUERY PROFILING  
                             │  
           ┌─────────────────┼─────────────────┐  
           ▼                 ▼                 ▼  
     PLAN ANALYSIS     SELECTIVITY       CARDINALITY  
           │                 │                 │  
           └─────────────────┼─────────────────┘  
                             ▼  
                    PROBLEM DETECTION  
                             │  
              ┌──────────────┼──────────────┐  
              ▼              ▼              ▼  
        INDEX CANDIDATES  QUERY RANKING  ANOMALIES  
              │              │              │  
              └──────────────┼──────────────┘  
                             ▼  
                   RECOMMENDATION ENGINE  
                             │  
                 ┌───────────┼───────────┐  
                 ▼           ▼           ▼  
              SCORE      CONFIDENCE   COST/BENEFIT  
                 │           │           │  
                 └───────────┼───────────┘  
                             ▼  
                      VALIDATION  
                             │  
                             ▼  
                      BENCHMARKING  
                             │  
                             ▼  
                    DECISION ENGINE  
                             │  
                 ┌───────────┼───────────┐  
                 ▼           ▼           ▼  
             ANALYTICS   DASHBOARD     REPORTS  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhQAQ60PcrIhnxgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseS14EKxPCORkAAAAASUVORK5CYII=)  
**39. Development Principle for the Next Phase**  
The next phase will build on the existing working system rather than replacing it.  
Each enhancement should:  
1. have a clearly defined purpose;  
2. be implemented as an isolated module where practical;  
3. have a test;  
4. be integrated with the existing pipeline;  
5. be experimentally evaluated where applicable;  
6. be documented;  
7. be committed to Git.  
The project will maintain a distinction between:  
Planned  
 Implemented  
 Experimentally validated  
 Future enhancement  
   
so that the final academic report remains accurate and reproducible.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSfYxKK/kYXEkyk8WcGbCFuCLTOzVXsAAPzFuVZ3dXw9AQDgtesB/v8F8JQadPwAAAAASUVORK5CYII=)  
**40. Current Project Baseline**  
At the M11 checkpoint, the project has demonstrated:  
15 controlled SQL queries  
 6 relational database tables  
 ~286,100 synthetic records  
 23 validation experiments  
 22 distinct validated recommendations  
 13 successful experiments  
 6 neutral experiments  
 4 unsuccessful experiments  
 0 unsafe experiments  
 33.19% average measured improvement  
 78.26% index usage  
 100% rows preserved  
 100% plans changed  
   
These results form the current experimental baseline.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhwgJWEPcbJpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaIkEMIPgIvAAAAAASUVORK5CYII=)  
**41. Definition of the Current Prototype**  
The current prototype can be defined as:  
*A PostgreSQL-based SQL performance analysis system that collects controlled query execution information, parses SQL structure, analyzes * *execution plans, extracts optimization features, generates explainable index candidates, validates candidate indexes through controlled BEFORE/AFTER experiments, stores validation evidence, and evaluates recommendation outcomes using project-level metrics.*  
This definition describes functionality that has actually been implemented at the current M11 checkpoint.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAMUlEQVR4nO3WAQkAIBAEsBPMYs4PZhMDWMAA5njYUmxU1UqyAwBAF2cmeZE4AIBO7gentgXapSWpbgAAAABJRU5ErkJggg==)  
**42. Next Development Checkpoint**  
The next development phase will begin only after the M11 baseline has been preserved in GitHub.  
The proposed sequence is:  
M11 Git checkpoint  
         ↓  
 Query fingerprinting  
         ↓  
 Selectivity analysis  
         ↓  
 Cardinality / plan anomaly analysis  
         ↓  
 Composite-index generation  
         ↓  
 Workload-level optimization  
         ↓  
 Cost-benefit recommendation model  
         ↓  
 Recommendation confidence  
         ↓  
 Expanded experimental evaluation  
         ↓  
 Statistical analysis  
         ↓  
 Dashboard integration  
         ↓  
 Experiment history  
         ↓  
 Optional ML/adaptive recommendation study  
         ↓  
 Final integrated prototype  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd49m4v6wg/pwmMYQVvImwJtszMXp0BAPAX91pt1fH1BACA164Hoq8EQMMPmF8AAAAASUVORK5CYII=)  
   
**43. Documentation Principle**  
This implementation log should be updated after each major milestone.  
Each future milestone should record:  
Date  
 Milestone  
 Objective  
 Implementation  
 Files changed  
 Tests performed  
 Experimental results  
 Problems encountered  
 Resolution  
 Git commit  
 Next milestone  
   
This will maintain a continuous project timeline from the original proposal through the final MSc prototype.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANElEQVR4nO3OQQmAABRAsSdYxKY/jbnMIJ7FCt5E2BJsmZmt2gMA4C+Otbqr8+sJAACvXQ85TgYRMv3/cwAAAABJRU5ErkJggg==)  
**End of M11 Implementation Baseline**  
**44. M14.1 Recommendation–Workload–Validation Analytical Dataset**

Date: 17 September 2026

Milestone: M14.1 – Recommendation–Workload–Validation Analytical Dataset

Objective:
Create an analytical dataset linking recommendation records, query-profile information, workload characteristics, fingerprints/templates, and experimentally observed benchmark outcomes.

Implementation:
A dedicated analytical module was added to construct a recommendation evaluation dataset. The module preserves multiple benchmark observations for the same recommendation and does not modify recommendation scores, benchmark records, or database state.

The dataset combines:
- recommendation information;
- query profile information;
- query fingerprints and templates;
- workload-level information;
- benchmark validation evidence;
- evaluation improvement metrics.

Evaluation metric precedence:
1. stored benchmark median improvement when available;
2. benchmark average improvement when the stored median is unavailable.

No missing benchmark median values were fabricated.

Verified results:
- Dataset rows: 25
- Unique recommendations: 24
- Unique benchmark observations: 23
- Unique fingerprints: 15
- Validated rows: 23
- Workload-matched rows: 25
- Rows without benchmark evidence: 2
- Rows with evaluation metric: 23

Files added:
- collector/recommendation_quality_analyzer.py
- tests/test_recommendation_quality_analyzer.py

Tests:
- M14.1 tests: 18/18 passed
- Full project suite at the subsequent M14 checkpoint: 106/106 passed

Experimental status:
Implemented and analytically validated.

Git commit:
Pending final M14 Git checkpoint.

Next milestone:
M14.2 Recommendation Quality and Workload-Outcome Analysis.


**45. M14.2 Recommendation Quality & Workload-Outcome Analysis**

Date: 17 September 2026

Milestone: M14.2 – Recommendation Quality & Workload-Outcome Analysis

Objective:
Evaluate the relationship between recommendation scores, workload characteristics, and experimentally observed index-performance outcomes.

Implementation:
A dedicated analytical module was added to calculate descriptive recommendation-quality metrics, score/outcome relationships, workload/outcome relationships, recommendation-priority outcomes, workload-priority outcomes, and validation-result distributions.

The analysis uses the experimentally observed evaluation improvement values from M14.1 and does not modify the recommendation scoring model.

Verified results:
- Evaluated observations: 23
- Successful: 13
- Neutral: 6
- Unsuccessful: 4
- Unsafe: 0
- Overall success rate: 56.52%
- Average improvement: 33.19%
- Median improvement across evaluation observations: 23.17%
- Low-benefit outcomes: 6
- Negative-benefit outcomes: 4
- Index used: 18
- Index not used: 5
- Rows preserved: 23/23 (100%)

Observed relationships:
- Recommendation score vs improvement, Pearson: 0.232
- Recommendation score vs improvement, Spearman: 0.341
- Workload execution-time share vs improvement, Pearson: -0.102
- Workload execution-time share vs improvement, Spearman: -0.448

Recommendation-priority results:
- High-priority observations: 10
- High-priority successful observations: 9
- High-priority success rate: 90.00%

Workload-priority results:
- Critical workload observations: 3
- Critical workload successful observations: 1
- Critical workload success rate: 33.33%

Interpretation:
The original recommendation score showed a positive but limited association with observed improvement in the current experimental dataset. Workload execution-time share did not show a direct positive association with measured index improvement. The results indicate that workload importance and index effectiveness are distinct analytical dimensions.

The findings support retaining empirical validation as a necessary component of the prototype rather than treating heuristic recommendation scores or workload cost as proof of index benefit.

Files added:
- collector/recommendation_quality_analysis.py
- tests/test_recommendation_quality_analysis.py

Tests:
- M14.2 tests: 13/13 passed
- Full project suite after integration: 106/106 passed

Experimental status:
Implemented and analytically validated.

Git commit:
Pending final M14 Git checkpoint.

Next milestone:
M14.3 Score-Only vs Workload-Aware Recommendation Prioritization.


**46. M14.3 Score-Only vs Workload-Aware Recommendation Prioritization**

Date: 17 September 2026

Milestone: M14.3 – Recommendation Prioritization Comparison

Objective:
Compare prioritization based solely on the existing recommendation score with prioritization incorporating workload importance.

Strategy A:
Existing recommendation score only.

Strategy B:
Workload priority, execution-time share, then the original recommendation score.

Implementation:
A dedicated analytical comparison module was implemented to produce both rankings using the same evaluated observations.

A methodological review identified outcome leakage in the initial ranking implementation because validation status and observed improvement had been used as ranking tie-breakers.

Resolution:
The ranking functions were corrected so that validation status and observed improvement are excluded from rank assignment.

The final ranking rules are:

Score-only:
1. recommendation score;
2. recommendation ID as deterministic tie-breaker.

Workload-aware:
1. workload priority;
2. execution-time share;
3. original recommendation score;
4. recommendation ID as deterministic tie-breaker.

Validation outcomes are used only after ranking to evaluate the resulting prioritization strategies.

Verified results:
- Evaluated observations: 23
- Pearson rank correlation: -0.210
- Spearman rank correlation: -0.210
- Observations moved upward: 10
- Observations moved downward: 12
- Unchanged: 1
- Average absolute rank shift: 9.22
- Maximum absolute rank shift: 16

Top-K comparison:

Top-3:
- Score-only: 2 successful, 66.67% success rate, 1 neutral, 0 unsuccessful
- Workload-aware: 1 successful, 33.33% success rate, 0 neutral, 2 unsuccessful

Top-5:
- Score-only: 4 successful, 80.00% success rate, 1 neutral, 0 unsuccessful
- Workload-aware: 2 successful, 40.00% success rate, 1 neutral, 2 unsuccessful

Top-10:
- Score-only: 9 successful, 90.00% success rate, 1 neutral, 0 unsuccessful
- Workload-aware: 4 successful, 40.00% success rate, 2 neutral, 4 unsuccessful

Critical workload placement:
- Critical observations: 3
- Score-only ranks: 13, 14, 17
- Workload-aware ranks: 1, 2, 3
- Workload-aware Top-3 placement: 3/3
- Score-only Top-3 placement: 0/3

Interpretation:
The workload-aware strategy changes prioritization substantially and places all three Critical-workload observations in its Top-3. However, the current validation observations do not demonstrate that workload-aware prioritization produces greater index effectiveness. The comparison therefore distinguishes workload prioritization from empirical index-performance effectiveness rather than establishing universal superiority of either strategy.

Files added:
- collector/recommendation_prioritization_comparison.py
- tests/test_recommendation_prioritization_comparison.py

Tests:
- M14.3 tests: 9/9 passed

Experimental status:
Implemented, methodologically corrected, and experimentally evaluated.

Git commit:
Pending final M14 Git checkpoint.

Next milestone:
M14.4 Integrated Research Evaluation Report.


**47. M14.4 Integrated Research Evaluation Report**

Date: 17 September 2026

Milestone: M14.4 – Integrated Research Evaluation

Objective:
Integrate the M14.1 analytical dataset, M14.2 recommendation-quality analysis, workload analysis, and M14.3 prioritization comparison into a consolidated research evaluation report.

Implementation:
A dedicated reporting module was added to combine the analytical outputs into a reproducible integrated evaluation.

The report contains:
- experimental summary;
- score/workload relationships;
- score-only versus workload-aware comparison;
- Critical-workload placement;
- research interpretation;
- methodological limitations.

The report explicitly distinguishes descriptive observations from general conclusions and records limitations concerning sample size, repeated benchmark observations, unavailable stored benchmark median fields, workload importance, PostgreSQL planner behavior, hardware/environment, cache state, query mix, and benchmark protocol.

Verified results:
- Evaluated observations: 23
- Successful: 13
- Neutral: 6
- Unsuccessful: 4
- Overall success rate: 56.52%
- Average improvement: 33.19%
- Median improvement: 23.17%
- Score vs improvement, Pearson: 0.232
- Score vs improvement, Spearman: 0.341
- Time share vs improvement, Pearson: -0.102
- Time share vs improvement, Spearman: -0.448
- M14.3 ranking Spearman correlation: -0.210
- Critical workload observations: 3
- Workload-aware Critical Top-3 placement: 3/3
- Score-only Critical Top-3 placement: 0/3

Tests:
- M14.4 tests: 7/7 passed
- Complete project test suite: 106/106 passed

Final M14 status:
INTEGRATED ANALYTICAL EVALUATION COMPLETE

Files added:
- collector/research_evaluation_report.py
- tests/test_research_evaluation_report.py

Experimental status:
Implemented, integrated, tested, and experimentally evaluated.

Git commit:
Pending final M14 Git checkpoint.

Next milestone:
Final M14 Git review, implementation-log update verification, commit, and push.


**48. M14 Verification Checkpoint**

Date: 17 September 2026

The complete project test suite was executed after the M14 implementation and methodological correction.

Command:
python -m unittest discover -s tests -p "test_*.py"

Result:
106 tests run
106 tests passed
0 failures
0 errors

M14.3:
9/9 tests passed.

M14.4:
7/7 tests passed.

The project is therefore at a verified M14 analytical checkpoint. No database modification was introduced by the M14 analytical modules.

Git commit: 6f1896c Add integrated recommendation quality analysis
---

# 49. M15 — Query-Pattern-Aware Composite Index Generation

## 49.1 Objective

M15 extends the index candidate generator from primarily single-column recommendations to query-pattern-aware composite B-tree candidate generation.

The objective is to identify columns that occur together in query structures and generate controlled, deterministic composite candidates while keeping candidate generation explainable.

M15 does not modify recommendation scoring, workload-aware prioritization, or benchmark validation.

## 49.2 Implementation

Composite candidate generation is implemented in:

collector/index_candidate_generator.py

The generator analyzes resolved WHERE, GROUP BY, and ORDER BY columns. Columns are combined only when they resolve to the same physical table. Unresolved references are ignored rather than guessed.

## 49.3 Supported Query Patterns

M15 supports the following composite patterns:

1. Multiple WHERE columns
2. WHERE + GROUP BY
3. WHERE + ORDER BY
4. Multiple GROUP BY columns when WHERE is absent
5. Multiple ORDER BY columns when WHERE and GROUP BY are absent

JOIN columns remain separate single-column candidates.

## 49.4 Candidate Width and Ordering

Composite candidates are limited to a maximum of three columns.

Column ordering is deterministic and follows the query structure, with WHERE columns forming the leading portion when applicable.

The implementation does not generate exhaustive permutations of column order.

## 49.5 Safeguards

Existing candidate-generation safeguards remain active, including:

- table and column resolution;
- existing-index detection;
- direct index coverage checks;
- candidate deduplication;
- exact duplicate suppression;
- prefix/redundancy analysis;
- candidate metadata generation.

Cross-table composite indexes are not generated.

## 49.6 Recommendation Metadata

Composite candidates continue through the existing recommendation pipeline and retain candidate metadata including:

- table name;
- column information;
- candidate type;
- source type;
- column count;
- reason.

The recommendation scoring formula remains unchanged.

## 49.7 Test Coverage

M15 added dedicated tests covering:

- multiple WHERE columns;
- WHERE + GROUP BY;
- WHERE + ORDER BY;
- multiple GROUP BY columns;
- multiple ORDER BY columns;
- maximum composite width;
- aggregate alias exclusion;
- JOIN-column exclusion.

The candidate-generator suite now contains 58 tests.

## 49.8 Verification

M15 verification completed successfully:

- Python syntax compilation passed;
- candidate-generator tests: 58 passed;
- full project test suite: 179 passed;
- git diff --check: clean.

## 49.9 Git Checkpoint

M15 was committed and pushed to GitHub.

Commit:

833d205 Add query-pattern-aware composite index generation

Repository state:

origin/main is up to date and the working tree is clean.

## 49.10 Methodological Boundary

M15 is limited to candidate generation.

It does not:

- change the recommendation scoring formula;
- use benchmark outcomes to generate candidates;
- change workload-aware prioritization;
- automatically create permanent indexes;
- claim that generated composite indexes will improve performance;
- perform exhaustive column-order optimization.

Composite candidates therefore remain recommendations requiring experimental validation.

## 49.11 Contribution to the Research Prototype

M15 advances the prototype from primarily single-column candidate generation toward query-structure-aware index optimization.

It provides a foundation for future experimental investigation of composite-index effectiveness, column ordering, workload-level optimization, index cost-benefit analysis, and recommendation confidence.

---

# 50. M15 — Verification Checkpoint

M15 is complete at the implementation level.

Implemented:
Query-pattern-aware composite index candidate generation.

Tested:
8 dedicated M15 tests;
58 candidate-generator tests;
179 full-project tests.

Verified:
Python syntax;
regression compatibility;
whitespace cleanliness.

Committed:
833d205

Pushed:
origin/main

Repository:
clean working tree and up to date with origin/main.

The project is ready to proceed from the stable M15 Git checkpoint.

**Current implementation checkpoint:** M16.2 — Composite Index Effectiveness & Column-Order Evaluation
# 51. M16.1 — Experimental Composite Column-Order Layer

## 51.1 Objective

M16.1 introduces a controlled experimental layer for generating alternative
column-order variants from M15 composite index candidates.

The purpose is to investigate whether different column orderings of the same
composite candidate produce different measured query-performance outcomes.

M16.1 is experimental only and does not modify the M15 recommendation
generation process.

## 51.2 Implementation

The experimental column-order layer is implemented in:

```text
collector/composite_order_experiment.py
````

The module:

* accepts only composite candidates;
* supports two- and three-column candidates;
* preserves the original candidate ordering;
* generates one controlled alternative ordering by reversing the
  original column order;
* does not generate exhaustive permutations;
* does not execute database queries;
* does not create database indexes;
* does not use benchmark outcomes;
* does not use recommendation scores;
* does not modify recommendation generation.

## 51.3 Experimental Design

For each eligible composite candidate, the experiment contains:

1. the original M15 column ordering;
2. one alternative reversed ordering;
3. the same table;
4. the same query;
5. the same experimental protocol.

The original and alternative variants are subsequently evaluated against
the same baseline during M16.2.

The design intentionally avoids exhaustive permutation generation in order
to keep the experimental layer controlled and computationally manageable.

## 51.4 Test Coverage

M16.1 added dedicated tests covering:

* composite-candidate eligibility;
* invalid candidate rejection;
* two-column candidates;
* three-column candidates;
* invalid column counts;
* alternative-order generation;
* duplicate-column handling;
* preservation of candidate metadata;
* experiment construction;
* batch experiment generation.

M16.1 dedicated tests:

```text
12/12 passed
```

## 51.5 Verification

M16.1 verification completed successfully:

* Python implementation verified;
* dedicated tests: 12 passed;
* full project test suite at the M16.1 checkpoint: 191 passed;
* experimental logic remained separate from recommendation generation.

## 51.6 Git Checkpoint

M16.1 was committed and pushed to GitHub.

Commit:

```text
d654d28 Add composite index column-order experiment
```

---

# 52. M16.2 — Composite Index Effectiveness & Column-Order Evaluation

## 52.1 Objective

M16.2 experimentally evaluates whether column ordering within a composite
B-tree index affects measured query performance.

The evaluation compares the original M15 column ordering with a controlled
alternative ordering for the same composite candidate.

Both variants are compared against the same query baseline.

M16.2 is an experimental evaluation layer and does not modify M15
candidate-generation logic or the recommendation scoring formula.

## 52.2 Composite Test-Index Support

Controlled composite indexes are created through the dedicated composite
test-index helper in:

```text
collector/index_validator.py
```

The helper validates the table and column identifiers and creates a
temporary B-tree composite index for experimental validation.

The established single-column test-index path remains unchanged.

Experimental indexes are removed after the corresponding experiment.

## 52.3 Experimental Evaluator

The M16.2 evaluator is implemented in:

```text
collector/composite_order_evaluator.py
```

The evaluator follows a controlled three-stage process:

```text
Baseline
   ↓
Original Composite Index
   ↓
Alternative Composite Index
```

For each experiment, it:

* establishes a common baseline;
* benchmarks the query;
* creates the original composite index;
* analyzes the table;
* benchmarks the query;
* records execution and plan evidence;
* checks index usage;
* removes the original index;
* creates the alternative composite index;
* analyzes the table;
* benchmarks the query;
* records equivalent evidence;
* checks index usage;
* removes the alternative index;
* calculates improvement for both variants;
* calculates the order-effect difference;
* verifies row preservation.

The evaluator does not store these experimental results in the
`benchmark_results` table.

## 52.4 Experimental Recommendations

Four composite recommendations were selected for controlled
column-order experiments:

| Recommendation | Original Order               | Alternative Order            |
| -------------- | ---------------------------- | ---------------------------- |
| Rec32          | `customer_id, status`        | `status, customer_id`        |
| Rec33          | `order_date, total_amount`   | `total_amount, order_date`   |
| Rec34          | `status, customer_id`        | `customer_id, status`        |
| Rec35          | `segment, customer_id, name` | `name, customer_id, segment` |

## 52.5 Recommendation 32

Query:

```sql
SELECT *
FROM orders
WHERE customer_id = 845
  AND status = 'Completed';
```

Observed results:

| Metric             | Original | Alternative |
| ------------------ | -------: | ----------: |
| Execution time     | 0.117 ms |    0.113 ms |
| Improvement        |   97.16% |      97.27% |
| Index used         |      Yes |         Yes |
| Rows preserved     |      Yes |         Yes |
| Plan changed       |      Yes |         Yes |
| Shared buffer hits |        3 |           3 |
| Shared reads       |        0 |           0 |

Order effect:

```text
+0.10 percentage points
```

The two column orderings produced almost identical measured performance
in this experiment.

## 52.6 Recommendation 33

Query:

```sql
SELECT *
FROM orders
WHERE order_date >= (
    SELECT MAX(order_date) - INTERVAL '90 days'
    FROM orders
)
AND total_amount > 1000;
```

Observed baseline execution time:

```text
13.925 ms
```

Observed results:

| Metric             | Original | Alternative |
| ------------------ | -------: | ----------: |
| Execution time     | 2.768 ms |   13.962 ms |
| Improvement        |   80.13% |      -0.26% |
| Index used         |      Yes |          No |
| Rows preserved     |      Yes |         Yes |
| Plan changed       |      Yes |         Yes |
| Shared buffer hits |     3364 |         788 |
| Shared reads       |        0 |           0 |

Order effect:

```text
-80.39 percentage points
```

The original ordering produced a substantial measured improvement, while
the reversed ordering produced essentially no improvement and was not used
by the query plan.

## 52.7 Recommendation 34

Query:

```sql
SELECT
    customer_id,
    SUM(total_amount) AS total_spent
FROM orders
WHERE status = 'Completed'
GROUP BY customer_id;
```

Observed baseline execution time:

```text
17.088 ms
```

Observed results:

| Metric             |  Original | Alternative |
| ------------------ | --------: | ----------: |
| Execution time     | 13.984 ms |   17.034 ms |
| Improvement        |    16.88% |      -1.25% |
| Index used         |       Yes |          No |
| Rows preserved     |       Yes |         Yes |
| Plan changed       |       Yes |         Yes |
| Shared buffer hits |     12603 |         394 |
| Shared reads       |         0 |           0 |

Order effect:

```text
-18.13 percentage points
```

The original ordering produced a measurable improvement, whereas the
alternative ordering did not provide a measured benefit and was not used
by the query plan.

## 52.8 Recommendation 35

Query:

```sql
SELECT
    c.customer_id,
    c.name,
    COUNT(o.order_id) AS number_of_orders,
    SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
WHERE c.segment = 'Corporate'
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 20;
```

Observed baseline execution time:

```text
25.844 ms
```

Observed results:

| Metric             |  Original | Alternative |
| ------------------ | --------: | ----------: |
| Execution time     | 26.012 ms |   26.450 ms |
| Improvement        |    -0.65% |      -2.35% |
| Index used         |       Yes |         Yes |
| Rows preserved     |       Yes |         Yes |
| Plan changed       |       Yes |         Yes |
| Shared buffer hits |       420 |         460 |
| Shared reads       |         0 |           0 |

Order effect:

```text
-1.69 percentage points
```

Neither column ordering produced a meaningful measured improvement over
the baseline in this experiment.

## 52.9 Consolidated M16.2 Analysis

The analytical layer is implemented in:

```text
collector/composite_order_analysis.py
```

Dedicated tests are implemented in:

```text
tests/test_composite_order_analysis.py
```

The four controlled experiments produced the following consolidated
results:

| Metric                                |    Result |
| ------------------------------------- | --------: |
| Experiments                           |         4 |
| Mean order effect                     | -25.03 pp |
| Median order effect                   |  -9.91 pp |
| Minimum order effect                  | -80.39 pp |
| Maximum order effect                  |  +0.10 pp |
| Negligible effects                    |         1 |
| Moderate effects                      |         1 |
| Substantial effects                   |         2 |
| Original-order average improvement    |    48.38% |
| Alternative-order average improvement |    23.35% |
| Original-order median improvement     |    48.50% |
| Alternative-order median improvement  |    -0.76% |
| Original index usage                  |      100% |
| Alternative index usage               |       50% |
| Rows preserved by both variants       |      100% |

The order-effect measure is calculated as the observed improvement of the
original ordering minus the observed improvement of the alternative
ordering.

The four observed order effects were:

| Recommendation | Order Effect | Classification |
| -------------- | -----------: | -------------- |
| Rec32          |     +0.10 pp | Negligible     |
| Rec33          |    -80.39 pp | Substantial    |
| Rec34          |    -18.13 pp | Substantial    |
| Rec35          |     -1.69 pp | Moderate       |

The classifications are descriptive thresholds introduced for the M16.2
analysis and are not PostgreSQL standards.

## 52.10 Research Finding

The four controlled experiments indicate that composite-index column order
can affect query performance, but the magnitude of the effect is
query-dependent.

The observed effects ranged from negligible to substantial.

Recommendation 32 showed almost no difference between the two tested
orders, whereas Recommendations 33 and 34 showed substantial differences.
Recommendation 35 showed a smaller difference, while neither ordering
produced a meaningful improvement over the baseline.

The experiments therefore do not establish a universal optimal
column-ordering rule.

The results also demonstrate that index usage alone is not sufficient
evidence of meaningful performance improvement. Recommendation 35 provides
an example in which both variants were used while both produced slightly
negative improvement relative to the baseline.

## 52.11 Methodological Boundary

M16.2 remains an experimental evaluation layer.

It does not:

* modify M15 candidate generation;
* modify the recommendation scoring formula;
* use validation outcomes to generate candidates;
* automatically select a permanent column ordering;
* claim a universal column-ordering rule;
* create permanent database indexes.

The findings are limited to the tested queries, database state, data
distribution, PostgreSQL planner behavior, caching state, and experimental
protocol.

The results should therefore be interpreted as controlled observations
within the project environment rather than as a general rule for all
PostgreSQL workloads.

## 52.12 Reproducibility

The consolidated M16.2 analysis can be reproduced using:

```text
m16_2_analysis_runner.py
```

The individual controlled experiments were executed using:

```text
recommendation_32_experimental_runner.py
recommendation_33_experimental_runner.py
recommendation_34_experimental_runner.py
recommendation_35_experimental_runner.py
```

The analytical component does not alter the underlying M15
recommendation-generation logic.

## 52.13 Test Coverage

M16.2 analytical tests:

```text
7/7 passed
```

The complete project regression suite after M16.2 implementation:

```text
214/214 passed
```

Python syntax compilation for the analytical module passed successfully.

Git whitespace verification using:

```text
git diff --check
```

also completed successfully.

---

# 53. M16.2 — Verification Checkpoint

M16.2 experimental evaluation and analytical consolidation are complete.

Implemented:

* controlled composite column-order experiment layer;
* composite test-index creation support;
* controlled original/alternative benchmark evaluation;
* order-effect calculation;
* experimental result classification;
* consolidated M16.2 analysis.

Tested:

* M16.1 dedicated tests: 12/12 passed;
* M16.2 analytical tests: 7/7 passed;
* full project test suite: 214/214 passed.

Verified:

* controlled original and alternative column-order experiments;
* row preservation;
* index usage;
* plan changes;
* buffer evidence;
* consolidated analytical statistics;
* Python syntax compilation;
* Git whitespace cleanliness.

M16.2 is ready for the Git checkpoint.
## M17 — Index Cost & Maintenance Impact Analysis

### M17.1 — Index Cost Metadata

Implemented `collector/index_cost_analyzer.py` and
`tests/test_index_cost_analyzer.py`.

The module retrieves PostgreSQL index metadata including:

- index type
- indexed columns
- column count
- uniqueness
- primary-key status
- validity
- index size
- table size
- index/table storage ratio

The implementation is analytical and does not create or remove indexes,
execute workloads, or modify recommendation logic.

Real database validation created a temporary B-tree index on
`orders(customer_id)`.

Observed:

- Index size: 606,208 bytes (592 kB)
- Table size: 3,227,648 bytes (3152 kB)
- Index/table ratio: 18.7817%

The experimental index was removed successfully.

### M17.2 — Index Maintenance Experiment

Implemented:

- `collector/index_maintenance_experiment.py`
- `tests/test_index_maintenance_experiment.py`
- `m17_2_real_runner.py`

The experiment compares controlled INSERT workloads on a temporary table
without and with an experimental B-tree index.

The revised experiment uses:

- 10,000 rows per iteration
- 2 warm-up iterations
- 5 measured iterations
- mean, median, minimum, maximum and standard deviation

Real experiment results:

- Baseline mean: 82.9513 ms
- Indexed mean: 146.4019 ms
- Mean overhead: 76.4914%
- Baseline median: 88.0415 ms
- Indexed median: 91.0569 ms
- Median overhead: approximately 3.43%
- Indexed maximum: 374.3128 ms
- Indexed standard deviation: 127.4194 ms

The indexed condition showed higher measured write time, but the large
374.3128 ms observation substantially affected the mean. The result is
therefore treated as workload-specific experimental evidence rather than a
general index-maintenance cost estimate.

The M17.2 analytical layer preserves both mean and median measures and
explicitly records variability.

### Validation

Full project test suite:

- 252 tests passed
- 0 failures

M17 does not currently modify recommendation scores, candidate generation,
or recommendation priorities.

### M17.3 — Read Benefit vs Cost Analysis

Implemented:

- `collector/index_benefit_cost_analyzer.py`
- `tests/test_index_benefit_cost_analyzer.py`
- `m17_3_real_analysis.py`

The M17.3 analytical layer combines two evidence streams:

1. Controlled index cost measurements from M17.1 and M17.2.
2. Existing validated read-performance observations from the M14
   recommendation-quality dataset.

The two evidence streams are intentionally not treated as measurements of the
same index.

#### Read-benefit evidence

The real M17.3 analysis reused the established recommendation-quality
pipeline and produced:

- Evaluated observations: 23
- Successful: 13
- Neutral: 6
- Unsuccessful: 4
- Average improvement: 33.19%
- Median improvement: 23.17%
- Positive-benefit observations: 19
- Index-used rate: 78.26%

The existing M14 evaluation metric is preserved: median improvement is used
when available, with the stored improvement percentage as the fallback when
median benchmark fields are NULL.

#### Cost evidence

M17.3 reused the real M17.1 and M17.2 measurements:

- Experimental index: `m17_1_idx_orders_customer_id`
- Table: `orders`
- Indexed column: `customer_id`
- Index size: 606,208 bytes
- Table size: 3,227,648 bytes
- Index/table ratio: 18.7817%
- Mean maintenance overhead: 76.4914%
- Median maintenance overhead: 3.43%

The M17.2 mean is substantially affected by variability in the indexed write
measurements. Both mean and median are therefore preserved.

#### Methodological decision

M17.3 does not calculate a per-recommendation cost-benefit ratio.

The historical read-benefit observations were not measured together with the
M17.1 storage and M17.2 maintenance experiment for the same experimental
index. Assigning those cost measurements to historical recommendations would
therefore create an unsupported relationship.

The analytical layer consequently reports the read-benefit and cost evidence
as separate but related evidence streams.

#### Design impact

M17.3 is analytical only.

It does not:

- change candidate generation;
- change recommendation scoring;
- change recommendation priorities;
- create or remove indexes;
- execute new benchmark experiments;
- write new benchmark results.

The purpose of M17.3 is to establish the evidence base for the subsequent
M17.4 cost-aware recommendation analysis.

#### Validation

Python compilation completed successfully.

Full project test suite:

- 252 tests passed
- 0 failures

M17.3 real analysis completed successfully against the current project
database and produced the documented read-benefit and cost evidence.

## M17.4 — Cost-Aware Recommendation Analysis

### Objective

Implement an analytical layer that evaluates whether
recommendation read-benefit evidence can be meaningfully
considered alongside index storage and maintenance costs.

### Implementation

Added:

- `collector/cost_aware_recommendation_analyzer.py`
- `tests/test_cost_aware_recommendation_analyzer.py`
- `m17_4_real_analysis.py`

The analyzer provides:

- evidence-completeness classification;
- explicit detection of read evidence;
- explicit detection of same-index cost linkage;
- cost-aware evidence classification;
- historical recommendation analysis;
- cost-aware summary generation;
- methodological reporting.

### Methodological Boundary

Historical recommendation observations are not assigned
M17.1/M17.2 cost measurements unless the cost evidence
belongs to the same experimental index.

No unsupported cost-benefit ratio or cost-adjusted
recommendation score is generated.

M17.4 does not modify:

- recommendation scores;
- candidate generation;
- recommendation priorities;
- workload prioritization;
- benchmark execution;
- `benchmark_results`.

### Real Analysis

The real M17.4 analysis produced:

- Recommendation observations: 29
- Read evidence available: 23
- No read evidence: 6
- Same-index cost linked: 0
- Complete evidence: 0
- Partial evidence: 0
- Limited evidence: 23
- Insufficient evidence: 6

Cost-aware classifications:

- Benefit with low cost: 0
- Benefit with measurable cost: 0
- Low benefit with cost: 0
- Negative benefit with cost: 0
- Mixed evidence: 0

### Research Finding

The current project contains historical read-performance
evidence and controlled index-cost evidence, but no
recommendation observations currently have same-index linked
storage and maintenance measurements.

Therefore, no complete cost-aware classification is assigned
to the historical recommendation set.

This result establishes an evidence boundary rather than
indicating an implementation failure.

### Validation

M17.4 validation completed with:

- 13 M17.4 tests passed;
- 265 full-project tests passed;
- Python compilation successful;
- real M17.4 analysis completed successfully.

### Design Decision

M17.4 remains an analytical layer. The existing
recommendation engine is deliberately unchanged.

A future cost-aware optimization mechanism should only be
introduced after controlled experiments provide linked
read-benefit, storage-cost, and maintenance-cost evidence
for the same index/workload context.

## M18 — Linked Index Cost-Benefit Validation

M18 extends the cost analysis established in M17 by linking read
performance benefit, index storage cost, and write-side maintenance cost
within the same controlled experimental index and workload.

### M18 Research Question

> When read performance and index costs are measured for the same
> experimental index and workload, can the project quantify the observed
> read/storage/write trade-off?

M17 established separate evidence streams for index storage, write-side
maintenance, and read-performance outcomes. However, those measurements
were not linked to the same experimental index and workload. M18 closes
that evidence gap.

M18 remains an experimental and analytical milestone. It does not change
the production recommendation engine.

### M18.1 — Linked Cost-Benefit Experiment Design

M18.1 established the experiment definition and measurement contract for
linked cost-benefit evaluation.

Implementation:

- `collector/linked_cost_benefit_experiment.py`
- `tests/test_linked_cost_benefit_experiment.py`

The experiment definition requires:

- experiment identifier;
- experimental index name;
- table name;
- indexed columns;
- read query;
- read iterations and warmups;
- write iterations and warmups;
- index type;
- controlled write table.

The read query uses a `{table}` placeholder so that the same experiment
definition can safely render against its isolated experiment table.

The linked measurement contract requires evidence for:

1. baseline and indexed read performance;
2. index and table storage;
3. baseline and indexed write performance.

All evidence must remain linked through the same experiment identifier
and experimental index.

M18.1 is design and validation only. It does not access PostgreSQL,
create or drop indexes, benchmark queries, modify recommendation scores,
or modify `benchmark_results`.

### M18.2 — Linked Read/Write Benchmark

M18.2 implemented the real linked benchmark.

Implementation:

- `collector/linked_cost_benefit_benchmark.py`
- `collector/m18_2_real_experiment.py`
- `tests/test_linked_cost_benefit_benchmark.py`

The benchmark uses an isolated experiment table created from the source
table. The experimental index is created and removed within the controlled
experiment.

The measurement sequence is:

1. baseline read;
2. create experimental index;
3. indexed read;
4. measure index and table storage;
5. remove index for baseline write;
6. measure controlled write workload;
7. recreate the same index;
8. measure indexed write workload;
9. remove the experimental index;
10. remove the experiment table.

The controlled write workload uses INSERT batches with a batch size of
1,000 rows. Write timing includes the INSERT and COMMIT operation.

The completed M18.2 experiment was:

- Experiment: `M18_001`
- Index: `m18_001_idx_orders_customer_id`
- Table: `orders`
- Column: `customer_id`
- Index type: B-tree
- Read iterations: 10
- Read warmups: 2
- Write iterations: 5
- Write warmups: 2

Observed read results:

- baseline average: 4.1082 ms;
- indexed average: 0.1541 ms;
- average improvement: 96.25%;
- median improvement: 96.38%;
- average absolute savings: 3.9541 ms;
- rows preserved: yes;
- index used: yes;
- plan changed from Seq Scan to Index Scan;
- shared buffer hits changed from 448 to 6.

Observed storage:

- index size: 606,208 bytes;
- index size: 592 kB;
- experiment table size: 3,670,016 bytes;
- table size: 3,584 kB;
- index/table ratio: 16.52%.

Observed write results:

- baseline average: 147.6142 ms;
- indexed average: 159.5491 ms;
- average absolute overhead: 11.9349 ms;
- average overhead: 8.09%;
- baseline median: 152.8535 ms;
- indexed median: 152.8794 ms;
- median overhead: 0.017%.

The difference between mean and median write overhead demonstrates that
write-side measurements can be sensitive to run-to-run variability.
Mean and median are therefore retained separately rather than collapsing
the evidence into a single cost number.

### M18.3 — Linked Cost-Benefit Analysis

M18.3 added the analytical layer for a single linked experiment.

Implementation:

- `collector/linked_cost_benefit_analyzer.py`
- `tests/test_linked_cost_benefit_analyzer.py`
- `collector/m18_3_real_analysis.py`

The analyzer calculates:

- absolute read savings;
- read improvement percentage;
- storage ratio;
- write overhead;
- read analysis;
- storage analysis;
- write analysis;
- linked cost-benefit evidence.

M18.3 is analytical only. It does not access PostgreSQL, create or drop
indexes, change recommendation scores, generate candidates, or modify
`benchmark_results`.

The completed M18.3 analysis confirmed the M18.2 measurements and
preserved the distinction between average and median write overhead.

No single read/storage/write cost-benefit ratio was introduced because
the measurements represent different dimensions and units. M18 therefore
retains the trade-off as multidimensional evidence.

### M18.4 — Cross-Workload Cost-Benefit Evaluation

M18.4 extends the linked experiment from one workload to multiple
controlled workload patterns.

Implementation:

- `collector/cross_workload_experiment.py`
- `collector/cross_workload_cost_benefit_analyzer.py`
- `collector/m18_4_cross_workload.py`
- `tests/test_cross_workload_experiment.py`
- `tests/test_cross_workload_cost_benefit_analyzer.py`
- `tests/test_m18_4_cross_workload.py`

Three fresh experiments were executed so that the completed M18.2
experiment `M18_001` was not reused.

The M18.4 experiments were:

| Experiment | Workload pattern | Experimental index |
|---|---|---|
| `M18_004` | Q001 selective equality lookup | `orders(customer_id)` |
| `M18_005` | Q009 join plus category filter | `products(category_id)` |
| `M18_006` | Q015 grouping and ordering by customer | `orders(customer_id)` |

All three experiments completed successfully with linked read, storage,
and write evidence.

#### M18.4 Read Results

| Experiment | Average read improvement | Median read improvement |
|---|---:|---:|
| `M18_004` | 96.15% | 96.29% |
| `M18_005` | 0.83% | 1.40% |
| `M18_006` | 97.80% | 97.80% |

All three experiments preserved rows, used the experimental index, and
reported a plan change.

The results demonstrate substantial workload dependence. In particular,
`M18_005` used the experimental index but produced only a 0.83% average
read improvement. Index usage therefore does not by itself establish
meaningful performance benefit.

#### M18.4 Storage Results

| Experiment | Index/table storage ratio |
|---|---:|
| `M18_004` | 18.78% |
| `M18_005` | 25.00% |
| `M18_006` | 16.52% |

Across the three experiments:

- mean storage ratio: 20.10%;
- median storage ratio: 18.78%;
- minimum: 16.52%;
- maximum: 25.00%.

#### M18.4 Write Results

| Experiment | Mean write overhead | Median write overhead |
|---|---:|---:|
| `M18_004` | 61.95% | -1.52% |
| `M18_005` | 17.49% | 26.84% |
| `M18_006` | 88.67% | 123.83% |

Across the three experiments:

- mean write overhead: 56.03%;
- median write overhead: 61.95%;
- minimum mean overhead: 17.49%;
- maximum mean overhead: 88.67%.

The difference between mean and median in `M18_004` illustrates the
importance of retaining both measures. These values should not be
interpreted as a universal write-cost estimate.

### M18 Findings

M18 provides linked experimental evidence showing that index
cost-benefit behavior varies across workload patterns.

The principal observations are:

1. Selective equality lookup can obtain substantial read benefit from an
   appropriate index.
2. Grouping and ordering workloads can also obtain substantial read
   benefit from an appropriate index.
3. Join/filter workloads may show little measurable read improvement
   even when the experimental index is used.
4. Index storage represents a measurable additional footprint.
5. Write-side overhead can vary considerably between workloads.
6. Mean and median write measurements can diverge substantially.
7. Index usage alone is insufficient evidence of meaningful performance
   benefit.
8. Read benefit, storage footprint, and write overhead should remain
   separate dimensions rather than being collapsed into an arbitrary
   single cost-benefit ratio.

### M18 Limitations

M18 is an experimental prototype rather than a production-scale
benchmarking study.

The main limitations are:

- only three cross-workload experiments were performed in M18.4;
- each experiment used five measured write iterations;
- database caching, planner behavior, system load, and execution
  environment can affect measurements;
- mean and median write overhead can differ substantially;
- the aggregate statistics are descriptive of the tested experiments and
  should not be interpreted as universal estimates;
- the tested workloads do not represent every possible PostgreSQL
  workload;
- M18 does not establish a universal optimal index decision rule.

### M18 Architectural Boundary

M18 remains separate from the production recommendation engine.

M18 does not modify:

- recommendation scoring;
- candidate index generation;
- recommendation priority;
- `benchmark_results`;
- production index configuration.

Its purpose is to provide additional empirical evidence for future
cost-aware recommendation research.

### M18 Validation

The complete project test suite passed with:

- **318 tests passed**;
- **0 failures**.

M18.4 real execution completed all three controlled experiments and
produced linked cross-workload analysis.

### M18 Status

**M18 — Linked Index Cost-Benefit Validation: LOCKED**

M18.1, M18.2, M18.3, and M18.4 are complete and documented.

---

## M21 Final Verification Record — 2026-09-23

The M21 dynamic structural SQL optimization family was validated through the
implemented milestones M21.1-M21.18 and final integration checks.

### M21.14 — Alternative-query benchmarking

Alternative-query benchmarking is implemented with safety-aware handling of
benchmarkable SQL rewrite candidates. The benchmark layer distinguishes
measured evidence from simulated evidence and does not treat simulated
benchmark results as measured production evidence.

### M21.15 — Five-section dynamic optimization blueprint

The dynamic optimization endpoint returns the five-section M21 blueprint:

1. Structural Performance Evaluation
2. Matrix Comparison
3. Optimized Structural SQL Code
4. Indexing Blueprint
5. Architectural Recommendations and Trade-offs

The live validation confirmed that unavailable structural rewrites remain
explicitly unavailable and that insufficient performance evidence is reported
as such.

### M21.16 — Interactive SQL Optimization Studio

The React/Tailwind dashboard provides a dynamic SQL Optimization Studio
connected to the M21 blueprint endpoint.

Dashboard lint and production build completed successfully.

### M21.17 — Interactive analytics and cross-filtering

Interactive Analytics was added as a dedicated dashboard page without replacing
the existing evidence/reporting pages.

The page consumes:

- workloads
- benchmarks
- cost-benefit evidence
- composite-index evidence
- query intelligence
- production decisions
- provenance

The live analytics data-path verification returned:

- 15 workloads
- 23 benchmarks
- 2 cost-benefit records
- 4 composite-index records
- 16 query records
- 28 production decisions
- 28 provenance records

Recommendation linkage verification found 28 recommendation IDs across the
connected workload, query, decision and provenance relationships.

### M21.18 — End-to-end validation, safety review and documentation

Full Python regression:

- 1075 tests passed
- 1 existing Starlette/AnyIO deprecation warning

Dashboard validation:

- ESLint passed with 0 errors and 0 warnings
- Vite production build passed
- git diff --check passed

Live reporting API verification:

- /api/overview — 200
- /api/workloads — 200
- /api/benchmarks — 200
- /api/cost-benefit — 200
- /api/composite-indexes — 200
- /api/queries — 200
- /api/decisions — 200
- /api/provenance — 200

Dynamic SQL safety verification:

- valid SELECT blueprint — 200
- malformed SQL — 422
- missing schema — 422
- missing table — 422
- missing column — 422
- UPDATE — 422
- DELETE — 422
- CREATE TABLE — 422
- multi-statement SQL — 422

The dynamic endpoint therefore remains read-oriented and rejects unsupported
statement types and multi-statement input before entering the optimization
pipeline.

The final valid blueprint test produced candidate recommendations while
retaining INSUFFICIENT performance evidence where no measured alternative
performance evidence existed. No global-optimality claim was emitted.

Git checkpoint:

- c329c11 — feat(M21): implement interactive analytics
- branch: m21-structural-optimization
- remote synchronized
- working tree clean at the time of verification

M21 evidence principle:

Optimization candidates remain distinct from validated performance claims.
Measured, simulated, insufficient and unavailable evidence states are kept
explicit throughout the dynamic optimization workflow.
