"""
Alternative-Query Benchmark  (M21.14)
----------------------------------------
Compares original vs alternative query structures with a strict timeout 
safety abort to prevent runaway queries from locking the database.
"""

import time

try:
    import psycopg2
    _HAS_PSYCOPG2 = True
except ImportError:
    _HAS_PSYCOPG2 = False

def _run_explain_analyze(cursor, sql: str, timeout_ms: int = 10000) -> dict:
    cursor.execute(f"SET statement_timeout = {timeout_ms};")
    cursor.execute(f"EXPLAIN (ANALYZE, FORMAT JSON) {sql}")
    plan_json = cursor.fetchone()[0]
    execution_time_ms = plan_json[0].get("Execution Time", 0)
    return {
        "execution_time_ms": execution_time_ms,
        "plan": plan_json,
    }

def _mock_run(sql: str) -> dict:
    time.sleep(0.01)
    mock_ms = round(5 + len(sql) * 0.01, 2)
    return {"execution_time_ms": mock_ms, "plan": None, "mock": True}

def compare_query_alternatives(original_sql: str, alternative_sql: str, connection=None, repetitions: int = 3, dry_run: bool = False, timeout_ms: int = 10000) -> dict:
    if dry_run or connection is None:
        original_runs = [_mock_run(original_sql) for _ in range(repetitions)]
        
        # M21.14 Safety Abort
        original_avg = sum(r["execution_time_ms"] for r in original_runs) / len(original_runs)
        if original_avg > timeout_ms:
            return {"status": "BASELINE_TIMEOUT", "is_mock_data": True}
            
        alternative_runs = [_mock_run(alternative_sql) for _ in range(repetitions)]
    else:
        if not _HAS_PSYCOPG2:
            raise RuntimeError("psycopg2 is not installed.")

        cursor = connection.cursor()
        
        # Baseline execution
        original_runs = []
        try:
            for _ in range(repetitions):
                original_runs.append(_run_explain_analyze(cursor, original_sql, timeout_ms))
        except Exception as e:
            cursor.close()
            return {"status": "BASELINE_TIMEOUT", "error": str(e), "is_mock_data": False}
            
        original_avg = sum(r["execution_time_ms"] for r in original_runs) / len(original_runs)
        if original_avg > timeout_ms:
            cursor.close()
            return {"status": "BASELINE_TIMEOUT", "is_mock_data": False}
            
        # Alternative execution
        alternative_runs = []
        try:
            for _ in range(repetitions):
                alternative_runs.append(_run_explain_analyze(cursor, alternative_sql, timeout_ms))
        except Exception as e:
            cursor.close()
            return {"status": "ALTERNATIVE_ERROR", "error": str(e), "is_mock_data": False}
            
        cursor.close()

    alternative_avg = sum(r["execution_time_ms"] for r in alternative_runs) / len(alternative_runs)
    improvement_pct = round((original_avg - alternative_avg) / original_avg * 100, 2) if original_avg > 0 else 0.0

    return {
        "status": "SUCCESS",
        "original_avg_ms": round(original_avg, 3),
        "alternative_avg_ms": round(alternative_avg, 3),
        "improvement_percentage": improvement_pct,
        "repetitions": repetitions,
        "is_mock_data": dry_run or connection is None,
        "original_runs": original_runs,
        "alternative_runs": alternative_runs,
    }
