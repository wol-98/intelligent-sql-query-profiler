from datetime import datetime, timezone
from typing import List, Dict, Any
from api.schemas.structural_optimization import OptimizationCandidate

class DynamicBlueprintGenerator:
    def build_blueprint(self, raw_sql: str, parsed_metadata: Dict[str, Any], candidates: List[OptimizationCandidate], benchmark_result: Dict[str, Any] = None) -> Dict[str, Any]:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sections": [
                self._format_query_summary(raw_sql, parsed_metadata),
                self._format_structural_analysis(parsed_metadata),
                self._format_recommendations(candidates),
                self._format_benchmark_evidence(benchmark_result),
                self._format_cost_benefit_verdict(candidates, benchmark_result),
            ],
        }

    def _format_query_summary(self, raw_sql: str, metadata: dict) -> dict:
        return {
            "section": "1. Query Summary",
            "submitted_sql": raw_sql.strip(),
            "tables": metadata.get("tables", [])
        }

    def _format_structural_analysis(self, metadata: dict) -> dict:
        notes = []
        if metadata.get("join_columns"): notes.append("Join dependencies")
        if metadata.get("aggregate_functions"): notes.append("Aggregations")
        if metadata.get("has_subquery"): notes.append("Subqueries")

        return {
            "section": "2. Structural Analysis",
            "complexity_note": "Moderate-to-high complexity." if notes else "Simple query.",
            "detected_layers": notes
        }

    def _format_recommendations(self, candidates: List[OptimizationCandidate]) -> dict:
        formatted = []
        for c in candidates:
            formatted.append({
                "title": c.title,
                "rationale": c.rationale,
                "sql_code": c.optimized_sql,
                "index_ddl": c.index_ddl
            })
        return {
            "section": "3. Recommendations",
            "candidate_count": len(candidates),
            "candidates": formatted
        }

    def _format_benchmark_evidence(self, benchmark_result: dict) -> dict:
        if not benchmark_result:
            return {"section": "4. Benchmark Evidence", "status": "not yet benchmarked"}
        if benchmark_result.get("status") == "BASELINE_TIMEOUT":
            return {"section": "4. Benchmark Evidence", "status": "Abort: Baseline exceeded timeout safety threshold."}

        return {
            "section": "4. Benchmark Evidence",
            "status": "mock data" if benchmark_result.get("is_mock_data") else "measured",
            "original_avg_ms": benchmark_result.get("original_avg_ms"),
            "alternative_avg_ms": benchmark_result.get("alternative_avg_ms"),
            "improvement_percentage": benchmark_result.get("improvement_percentage"),
        }

    def _format_cost_benefit_verdict(self, candidates: List[OptimizationCandidate], benchmark_result: dict) -> dict:
        if benchmark_result and benchmark_result.get("improvement_percentage", 0) > 10:
            verdict = f"Recommended — measured improvement of {benchmark_result['improvement_percentage']}%."
        elif benchmark_result and benchmark_result.get("status") == "BASELINE_TIMEOUT":
            verdict = "Optimization aborted due to baseline timeout. Treat alternatives as theoretical architectural recommendations."
        elif candidates:
            verdict = f"{len(candidates)} candidate(s) identified; benchmarking recommended."
        else:
            verdict = "No optimization opportunities identified."

        return {
            "section": "5. Cost/Benefit Verdict",
            "verdict": verdict
        }
