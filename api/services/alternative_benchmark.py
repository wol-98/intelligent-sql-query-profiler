import time
from typing import Dict, Any, List
from api.schemas.structural_optimization import OptimizationCandidate

try:
    import psycopg2
    _HAS_PSYCOPG2 = True
except ImportError:
    _HAS_PSYCOPG2 = False

class AlternativeBenchmarkEngine:
    def __init__(self, connection=None, dry_run: bool = False, timeout_ms: float = 10000.0):
        self.connection = connection
        self.dry_run = dry_run
        self.timeout_ms = timeout_ms

    def _mock_run(self, sql: str) -> Dict[str, Any]:
        time.sleep(0.01)
        mock_ms = round(5 + len(sql) * 0.01, 2)
        return {"execution_time_ms": mock_ms, "plan": None, "mock": True}

    def _run_explain_analyze(self, cursor, sql: str) -> Dict[str, Any]:
        # Enforce statement timeout to prevent runaway user queries
        cursor.execute(f"SET statement_timeout = {int(self.timeout_ms)};")
        cursor.execute(f"EXPLAIN (ANALYZE, FORMAT JSON) {sql}")
        plan_json = cursor.fetchone()[0]
        execution_time_ms = plan_json[0].get("Execution Time", 0)
        return {"execution_time_ms": execution_time_ms, "plan": plan_json}

    def compare_query_alternatives(self, original_sql: str, alternative_sql: str, repetitions: int = 3) -> Dict[str, Any]:
        original_runs = []
        alternative_runs = []

        if self.dry_run or self.connection is None:
            original_runs = [self._mock_run(original_sql) for _ in range(repetitions)]
            
            # M21.14 Safety Abort: Stop if baseline exceeds threshold
            original_avg = sum(r["execution_time_ms"] for r in original_runs) / len(original_runs)
            if original_avg > self.timeout_ms:
                return {"status": "BASELINE_TIMEOUT", "is_mock_data": True}
                
            alternative_runs = [self._mock_run(alternative_sql) for _ in range(repetitions)]
        else:
            if not _HAS_PSYCOPG2:
                raise RuntimeError("psycopg2 is not installed.")
            try:
                cursor = self.connection.cursor()
                for _ in range(repetitions):
                    original_runs.append(self._run_explain_analyze(cursor, original_sql))
                
                original_avg = sum(r["execution_time_ms"] for r in original_runs) / len(original_runs)
                
                # M21.14 Safety Abort for Live Database
                if original_avg > self.timeout_ms:
                    cursor.close()
                    return {"status": "BASELINE_TIMEOUT", "is_mock_data": False}
                
                for _ in range(repetitions):
                    alternative_runs.append(self._run_explain_analyze(cursor, alternative_sql))
                cursor.close()
            except Exception as e:
                return {"status": "ERROR", "message": str(e), "is_mock_data": False}

        alternative_avg = sum(r["execution_time_ms"] for r in alternative_runs) / len(alternative_runs)
        improvement_pct = round((original_avg - alternative_avg) / original_avg * 100, 2) if original_avg > 0 else 0.0

        return {
            "status": "SUCCESS",
            "original_avg_ms": round(original_avg, 3),
            "alternative_avg_ms": round(alternative_avg, 3),
            "improvement_percentage": improvement_pct,
            "repetitions": repetitions,
            "is_mock_data": self.dry_run or self.connection is None
        }
