"""Alternative-query benchmarking for M21.14.

The engine compares an original query with a structural alternative using
controlled, read-only EXPLAIN ANALYZE execution. Benchmark results distinguish
measured evidence from simulated evidence and execution failures.
"""

import re
import time
from statistics import mean, median
from typing import Any, Dict, List, Optional

try:
    import psycopg2
    _HAS_PSYCOPG2 = True
except ImportError:
    psycopg2 = None
    _HAS_PSYCOPG2 = False

class AlternativeBenchmarkEngine:
    """Benchmark an original query against an alternative query safely."""

    _FORBIDDEN_KEYWORDS = re.compile(
        r"\b(?:INSERT|UPDATE|DELETE|MERGE|CREATE|ALTER|DROP|TRUNCATE|"
        r"GRANT|REVOKE|CALL|DO|VACUUM|COPY)\b",
        re.IGNORECASE,
    )
    def benchmark_candidate(self, candidate) -> Dict[str, Any]:
        """Benchmark a candidate only when executable alternative SQL exists.

        Index-only candidates and structural candidates without rewritten SQL
        remain explicitly unbenchmarkable until a later transformation stage
        provides executable alternative SQL.
        """
        alternative_type = getattr(candidate, "alternative_type", None)
        original_sql = getattr(candidate, "original_sql", None)
        optimized_sql = getattr(candidate, "optimized_sql", None)

        if alternative_type is None:
            return {
                "status": "NOT_BENCHMARKABLE",
                "reason": "Candidate does not define an alternative type.",
                "evidence_status": "INSUFFICIENT",
            }

        if getattr(alternative_type, "value", alternative_type) != "SQL_REWRITE":
            return {
                "status": "NOT_BENCHMARKABLE",
                "reason": (
                    "Only SQL_REWRITE candidates can be benchmarked by "
                    "the alternative-query benchmark engine."
                ),
                "candidate_type": getattr(
                    alternative_type,
                    "value",
                    str(alternative_type),
                ),
                "evidence_status": "INSUFFICIENT",
            }

        if not optimized_sql:
            return {
                "status": "NOT_BENCHMARKABLE",
                "reason": (
                    "No executable alternative SQL is available for "
                    "benchmarking."
                ),
                "candidate_type": "SQL_REWRITE",
                "evidence_status": "INSUFFICIENT",
            }

        if not original_sql:
            return {
                "status": "NOT_BENCHMARKABLE",
                "reason": "Original SQL is missing from the candidate.",
                "candidate_type": "SQL_REWRITE",
                "evidence_status": "INSUFFICIENT",
            }

        if optimized_sql.strip() == original_sql.strip():
            return {
                "status": "NOT_BENCHMARKABLE",
                "reason": (
                    "Alternative SQL is identical to the original SQL; "
                    "there is no query-structure alternative to benchmark."
                ),
                "candidate_type": "SQL_REWRITE",
                "evidence_status": "INSUFFICIENT",
            }

        return self.compare_query_alternatives(
            original_sql,
            optimized_sql,
        )
    _START_KEYWORD = re.compile(r"^(SELECT|WITH)\b", re.IGNORECASE)

    def __init__(
        self,
        connection=None,
        dry_run: bool = False,
        timeout_ms: float = 10000.0,
    ):
        self.connection = connection
        self.dry_run = dry_run
        self.timeout_ms = float(timeout_ms)

    def _validate_benchmark_sql(self, sql: str) -> Optional[str]:
        """Return an error when SQL is not suitable for benchmarking."""
        if not isinstance(sql, str) or not sql.strip():
            return "SQL must be a non-empty string."

        stripped = sql.strip()
        without_trailing_semicolon = (
            stripped[:-1].strip() if stripped.endswith(";") else stripped
        )

        if ";" in without_trailing_semicolon:
            return "Multiple SQL statements are not allowed in a benchmark."

        if not self._START_KEYWORD.match(without_trailing_semicolon):
            return "Only SELECT or WITH statements are allowed for benchmarking."

        if self._FORBIDDEN_KEYWORDS.search(without_trailing_semicolon):
            return "Benchmark SQL contains a non-read-only SQL operation."

        return None

    def _run_explain_analyze(self, cursor, sql: str) -> Dict[str, Any]:
        cursor.execute(f"SET statement_timeout = {int(self.timeout_ms)};")
        try:
            cursor.execute(f"EXPLAIN (ANALYZE, FORMAT JSON) {sql}")
            plan_json = cursor.fetchone()[0]
        finally:
            try:
                cursor.execute("RESET statement_timeout")
            except Exception:
                pass

        execution_time_ms = float(plan_json[0].get("Execution Time", 0.0))
        plan = plan_json[0].get("Plan", {})
        actual_rows = plan.get("Actual Rows")
        actual_loops = plan.get("Actual Loops", 1) or 1
        rows_returned = (
            actual_rows * actual_loops if actual_rows is not None else None
        )

        return {
            "execution_time_ms": execution_time_ms,
            "rows_returned": rows_returned,
            "plan": plan_json,
            "execution_status": "SUCCESS",
            "evidence_status": "MEASURED",
            "mock": False,
        }

    def _mock_run(self, sql: str) -> Dict[str, Any]:
        time.sleep(0.01)
        mock_ms = round(5 + len(sql) * 0.01, 2)
        return {
            "execution_time_ms": mock_ms,
            "rows_returned": None,
            "plan": None,
            "execution_status": "SUCCESS",
            "evidence_status": "SIMULATED",
            "mock": True,
        }

    @staticmethod
    def _is_timeout_exception(exc: Exception) -> bool:
        pgcode = getattr(exc, "pgcode", None)
        message = str(exc).lower()
        return (
            pgcode == "57014"
            or "statement timeout" in message
            or "canceling statement" in message
            or "query canceled" in message
        )

    def _rollback(self) -> None:
        if self.connection is not None:
            try:
                self.connection.rollback()
            except Exception:
                pass

    @staticmethod
    def _statistics(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        timings = [float(run["execution_time_ms"]) for run in runs]
        return {
            "avg_ms": round(mean(timings), 3),
            "median_ms": round(median(timings), 3),
            "min_ms": round(min(timings), 3),
            "max_ms": round(max(timings), 3),
        }

    @staticmethod
    def _rows_preserved(
        original_runs: List[Dict[str, Any]],
        alternative_runs: List[Dict[str, Any]],
    ) -> Optional[bool]:
        original_rows = [run.get("rows_returned") for run in original_runs]
        alternative_rows = [run.get("rows_returned") for run in alternative_runs]
        if any(value is None for value in original_rows + alternative_rows):
            return None
        return median(original_rows) == median(alternative_rows)

    def _benchmark_live_runs(
        self,
        cursor,
        sql: str,
        repetitions: int,
        label: str,
    ) -> Dict[str, Any]:
        runs: List[Dict[str, Any]] = []
        for _ in range(repetitions):
            try:
                runs.append(self._run_explain_analyze(cursor, sql))
            except Exception as exc:
                timed_out = self._is_timeout_exception(exc)
                self._rollback()
                return {
                    "status": f"{label}_TIMEOUT" if timed_out else f"{label}_ERROR",
                    "error": str(exc),
                    "runs": runs,
                    "is_mock_data": False,
                    "evidence_status": "INSUFFICIENT",
                }

        return {
            "status": "SUCCESS",
            "runs": runs,
            "is_mock_data": False,
            "evidence_status": "MEASURED",
        }

    def compare_query_alternatives(
        self,
        original_sql: str,
        alternative_sql: str,
        repetitions: int = 3,
    ) -> Dict[str, Any]:
        if repetitions < 1:
            return {
                "status": "INVALID_INPUT",
                "error": "repetitions must be at least 1.",
                "evidence_status": "INSUFFICIENT",
            }

        for label, sql in (
            ("ORIGINAL", original_sql),
            ("ALTERNATIVE", alternative_sql),
        ):
            error = self._validate_benchmark_sql(sql)
            if error:
                return {
                    "status": "UNSAFE_SQL",
                    "query": label,
                    "error": error,
                    "evidence_status": "INSUFFICIENT",
                }

        if self.dry_run or self.connection is None:
            original_runs = [
                self._mock_run(original_sql) for _ in range(repetitions)
            ]
            original_stats = self._statistics(original_runs)

            if original_stats["avg_ms"] > self.timeout_ms:
                return {
                    "status": "BASELINE_TIMEOUT",
                    "is_mock_data": True,
                    "evidence_status": "SIMULATED",
                    "original_runs": original_runs,
                    "original_avg_ms": original_stats["avg_ms"],
                    "original_median_ms": original_stats["median_ms"],
                }

            alternative_runs = [
                self._mock_run(alternative_sql) for _ in range(repetitions)
            ]
            evidence_status = "SIMULATED"
        else:
            if not _HAS_PSYCOPG2:
                raise RuntimeError(
                    "psycopg2 is not installed — required for live benchmarking."
                )

            cursor = self.connection.cursor()
            try:
                baseline = self._benchmark_live_runs(
                    cursor, original_sql, repetitions, "BASELINE"
                )
                if baseline["status"] != "SUCCESS":
                    return baseline

                original_runs = baseline["runs"]
                original_stats = self._statistics(original_runs)

                alternative = self._benchmark_live_runs(
                    cursor, alternative_sql, repetitions, "ALTERNATIVE"
                )
                if alternative["status"] != "SUCCESS":
                    return {
                        **alternative,
                        "original_runs": original_runs,
                        "original_avg_ms": original_stats["avg_ms"],
                        "original_median_ms": original_stats["median_ms"],
                    }

                alternative_runs = alternative["runs"]
                evidence_status = "MEASURED"
            finally:
                cursor.close()

            # EXPLAIN ANALYZE is read-only, so release the benchmark transaction.
            self._rollback()

        original_stats = self._statistics(original_runs)
        alternative_stats = self._statistics(alternative_runs)

        improvement_pct = (
            round(
                (
                    original_stats["median_ms"]
                    - alternative_stats["median_ms"]
                )
                / original_stats["median_ms"]
                * 100,
                2,
            )
            if original_stats["median_ms"] > 0
            else 0.0
        )

        return {
            "status": "SUCCESS",
            "evidence_status": evidence_status,
            "is_mock_data": evidence_status == "SIMULATED",
            "repetitions": repetitions,
            "original_avg_ms": original_stats["avg_ms"],
            "original_median_ms": original_stats["median_ms"],
            "original_min_ms": original_stats["min_ms"],
            "original_max_ms": original_stats["max_ms"],
            "alternative_avg_ms": alternative_stats["avg_ms"],
            "alternative_median_ms": alternative_stats["median_ms"],
            "alternative_min_ms": alternative_stats["min_ms"],
            "alternative_max_ms": alternative_stats["max_ms"],
            "improvement_percentage": improvement_pct,
            "rows_preserved": self._rows_preserved(
                original_runs, alternative_runs
            ),
            "original_runs": original_runs,
            "alternative_runs": alternative_runs,
        }
