"""
Dynamic Optimization Blueprint Generator  (M21.15)
------------------------------------------------------
Formats the findings into the 5-section optimization report.
"""

from datetime import datetime, timezone

def _format_query_summary(query_record: dict, original_sql: str) -> dict:
    return {
        "section": "1. Query Summary",
        "query_type": query_record.get("query_type"),
        "tables": query_record.get("tables"),
        "submitted_sql": original_sql.strip(),
        "fingerprint": query_record.get("fingerprint"),
    }

def _format_structural_analysis(query_record: dict) -> dict:
    return {
        "section": "2. Structural Analysis",
        "predicate_count": query_record.get("predicate_count"),
        "predicate_logic": query_record.get("predicate_logic"),
        "where_predicates": query_record.get("where_predicates"),
        "join_columns_resolved": query_record.get("join_columns_resolved"),
        "group_by_columns": query_record.get("group_by_columns"),
        "order_by_columns": query_record.get("order_by_columns"),
        "aggregate_functions": query_record.get("aggregate_functions"),
        "has_subquery": query_record.get("has_subquery"),
        "complexity_note": _describe_complexity(query_record),
    }

def _describe_complexity(query_record: dict) -> str:
    join_count = len(query_record.get("join_columns_resolved", [])) // 2
    notes = []
    if join_count:
        notes.append(f"{join_count} join(s)")
    if query_record.get("aggregate_functions"):
        notes.append("aggregation")
    if query_record.get("has_subquery"):
        notes.append("subquery")
    if not notes:
        return "Simple, single-table query."
    return "Moderate-to-high complexity: " + ", ".join(notes) + "."

def _format_recommendations(combined_candidates: list) -> dict:
    return {
        "section": "3. Recommendations",
        "candidate_count": len(combined_candidates),
        "candidates": [
            {
                "type": c.get("type"),
                "priority": c.get("priority"),
                "reasoning": c.get("reasoning"),
                "sql": c.get("sql"),
                "flags": c.get("flags", []),
            }
            for c in combined_candidates
        ],
    }

def _format_benchmark_evidence(benchmark_result: dict | None) -> dict:
    if not benchmark_result:
        return {
            "section": "4. Benchmark Evidence",
            "status": "not yet benchmarked",
        }
    if benchmark_result.get("status") == "BASELINE_TIMEOUT":
        return {
            "section": "4. Benchmark Evidence",
            "status": "Abort: Baseline exceeded timeout safety threshold."
        }
        
    return {
        "section": "4. Benchmark Evidence",
        "status": "mock data — not from live DB" if benchmark_result.get("is_mock_data") else "measured",
        "original_avg_ms": benchmark_result.get("original_avg_ms"),
        "alternative_avg_ms": benchmark_result.get("alternative_avg_ms"),
        "improvement_percentage": benchmark_result.get("improvement_percentage"),
    }

def _format_cost_benefit_verdict(combined_candidates: list, benchmark_result: dict | None) -> dict:
    high_priority_count = sum(1 for c in combined_candidates if c.get("priority") == "high")
    flagged_count = sum(1 for c in combined_candidates if c.get("flags"))

    if not combined_candidates:
        verdict = "No optimization opportunities identified for this query as written."
    elif benchmark_result and benchmark_result.get("status") == "BASELINE_TIMEOUT":
        verdict = "Optimization aborted due to baseline timeout. Treat alternatives as theoretical architectural recommendations."
    elif benchmark_result and benchmark_result.get("improvement_percentage", 0) > 10:
        verdict = (
            f"Recommended — measured improvement of "
            f"{benchmark_result['improvement_percentage']}%."
        )
    elif high_priority_count:
        verdict = f"{high_priority_count} high-priority candidate(s) identified; benchmarking recommended before applying."
    else:
        verdict = "Only low-priority candidates found; benefit is likely marginal."

    return {
        "section": "5. Cost/Benefit Verdict",
        "verdict": verdict,
        "flagged_for_review": flagged_count,
    }

def build_blueprint(query_record: dict, original_sql: str, combined_candidates: list, benchmark_result: dict = None) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": [
            _format_query_summary(query_record, original_sql),
            _format_structural_analysis(query_record),
            _format_recommendations(combined_candidates),
            _format_benchmark_evidence(benchmark_result),
            _format_cost_benefit_verdict(combined_candidates, benchmark_result),
        ],
    }

def blueprint_to_text(blueprint: dict) -> str:
    lines = [f"OPTIMIZATION BLUEPRINT — generated {blueprint['generated_at']}", "=" * 70]
    for section in blueprint["sections"]:
        lines.append(f"\n{section['section']}")
        lines.append("-" * len(section["section"]))
        for key, value in section.items():
            if key == "section":
                continue
            lines.append(f"  {key}: {value}")
    return "\n".join(lines)
