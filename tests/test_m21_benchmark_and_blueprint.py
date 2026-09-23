import unittest

from api.schemas.structural_optimization import (
    AlternativeType,
    CandidateStatus,
    OptimizationCandidate,
)
from types import SimpleNamespace
from api.services.alternative_benchmark import AlternativeBenchmarkEngine
from api.services.blueprint_generator import DynamicBlueprintGenerator


class TestM21Integration(unittest.TestCase):
    def test_benchmark_safety_abort(self):
        engine = AlternativeBenchmarkEngine(dry_run=True, timeout_ms=0.0)
        result = engine.compare_query_alternatives("SELECT *", "SELECT 1")

        self.assertEqual(result["status"], "BASELINE_TIMEOUT")
        self.assertEqual(result["evidence_status"], "SIMULATED")
        self.assertTrue(result["is_mock_data"])

    def test_benchmark_rejects_non_read_only_sql(self):
        engine = AlternativeBenchmarkEngine(dry_run=True)

        result = engine.compare_query_alternatives(
            "UPDATE orders SET amount = 10",
            "SELECT * FROM orders",
        )

        self.assertEqual(result["status"], "UNSAFE_SQL")
        self.assertEqual(result["query"], "ORIGINAL")
        self.assertEqual(result["evidence_status"], "INSUFFICIENT")

    def test_benchmark_rejects_multiple_statements(self):
        engine = AlternativeBenchmarkEngine(dry_run=True)

        result = engine.compare_query_alternatives(
            "SELECT * FROM orders; SELECT * FROM customers",
            "SELECT * FROM orders",
        )

        self.assertEqual(result["status"], "UNSAFE_SQL")
        self.assertEqual(result["query"], "ORIGINAL")

    def test_benchmark_rejects_invalid_repetitions(self):
        engine = AlternativeBenchmarkEngine(dry_run=True)

        result = engine.compare_query_alternatives(
            "SELECT * FROM orders",
            "SELECT * FROM orders",
            repetitions=0,
        )

        self.assertEqual(result["status"], "INVALID_INPUT")
        self.assertEqual(result["evidence_status"], "INSUFFICIENT")

    def test_benchmark_returns_simulated_statistics(self):
        engine = AlternativeBenchmarkEngine(
            dry_run=True,
            timeout_ms=1000.0,
        )

        result = engine.compare_query_alternatives(
            "SELECT * FROM orders",
            "SELECT * FROM orders WHERE id > 0",
            repetitions=3,
        )

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["evidence_status"], "SIMULATED")
        self.assertTrue(result["is_mock_data"])
        self.assertEqual(result["repetitions"], 3)

        for key in (
            "original_avg_ms",
            "original_median_ms",
            "original_min_ms",
            "original_max_ms",
            "alternative_avg_ms",
            "alternative_median_ms",
            "alternative_min_ms",
            "alternative_max_ms",
            "improvement_percentage",
        ):
            self.assertIn(key, result)

        self.assertIsNone(result["rows_preserved"])
        self.assertEqual(len(result["original_runs"]), 3)
        self.assertEqual(len(result["alternative_runs"]), 3)

    def test_benchmark_accepts_with_query(self):
        engine = AlternativeBenchmarkEngine(
            dry_run=True,
            timeout_ms=1000.0,
        )

        result = engine.compare_query_alternatives(
            "WITH x AS (SELECT 1) SELECT * FROM x",
            "SELECT 1",
        )

        self.assertEqual(result["status"], "SUCCESS")

    def test_blueprint_generation(self):
        generator = DynamicBlueprintGenerator()

        candidate = OptimizationCandidate(
            candidate_id="123",
            alternative_type=AlternativeType.SQL_REWRITE,
            status=CandidateStatus.CANDIDATE,
            title="Test CTE",
            rationale="Test structural CTE alternative.",
            original_sql="SELECT * FROM orders",
            optimized_sql=(
                "WITH cte AS "
                "(SELECT * FROM orders) "
                "SELECT * FROM cte"
            ),
        )

        benchmark_mock = {
            "status": "SUCCESS",
            "is_mock_data": True,
            "evidence_status": "SIMULATED",
            "improvement_percentage": 25.5,
        }

        blueprint = generator.build_blueprint(
            "SELECT * FROM orders",
            {"tables": ["orders"]},
            [candidate],
            benchmark_mock,
        )

        self.assertEqual(len(blueprint["sections"]), 5)

        self.assertEqual(
            [section["section"] for section in blueprint["sections"]],
            [
                "1. Structural Performance Evaluation",
                "2. Matrix Comparison",
                "3. Optimized Structural SQL Code",
                "4. Indexing Blueprint",
                "5. Architectural Recommendations and Trade-offs",
            ],
        )

        self.assertEqual(
            blueprint["sections"][2]["status"],
            "SIMULATED_NOT_DECISIONAL",
        )

        self.assertEqual(
            blueprint["sections"][4]["evidence_status"],
            "SIMULATED",
        )

        self.assertNotIn(
            "Recommended",
            blueprint["sections"][4]["decision_note"],
        )

    def test_blueprint_does_not_recommend_from_simulated_improvement(self):
        generator = DynamicBlueprintGenerator()

        candidate = OptimizationCandidate(
            candidate_id="124",
            alternative_type=AlternativeType.SQL_REWRITE,
            status=CandidateStatus.CANDIDATE,
            title="Simulated Rewrite",
            rationale="Simulated structural alternative.",
            original_sql="SELECT * FROM orders",
            optimized_sql="SELECT * FROM orders WHERE id > 0",
        )

        benchmark_result = {
            "status": "SUCCESS",
            "is_mock_data": True,
            "evidence_status": "SIMULATED",
            "improvement_percentage": 80.0,
        }

        blueprint = generator.build_blueprint(
            "SELECT * FROM orders",
            {"tables": ["orders"]},
            [candidate],
            benchmark_result,
        )

        self.assertEqual(
            blueprint["sections"][4]["evidence_status"],
            "SIMULATED",
        )
        self.assertIn(
            "simulated",
            blueprint["sections"][4]["decision_note"].lower(),
        )

    def test_benchmark_candidate_rejects_index_candidate(self):
        engine = AlternativeBenchmarkEngine(dry_run=True)

        candidate = SimpleNamespace(
            alternative_type=AlternativeType.INDEX,
            original_sql="SELECT * FROM orders",
            optimized_sql=None,
        )

        result = engine.benchmark_candidate(candidate)

        self.assertEqual(result["status"], "NOT_BENCHMARKABLE")
        self.assertEqual(result["candidate_type"], "INDEX")
        self.assertEqual(result["evidence_status"], "INSUFFICIENT")

    def test_benchmark_candidate_rejects_missing_alternative_sql(self):
        engine = AlternativeBenchmarkEngine(dry_run=True)

        candidate = SimpleNamespace(
            alternative_type=AlternativeType.SQL_REWRITE,
            original_sql="SELECT * FROM orders",
            optimized_sql=None,
        )

        result = engine.benchmark_candidate(candidate)

        self.assertEqual(result["status"], "NOT_BENCHMARKABLE")
        self.assertEqual(result["candidate_type"], "SQL_REWRITE")
        self.assertEqual(result["evidence_status"], "INSUFFICIENT")

    def test_benchmark_candidate_rejects_identical_sql(self):
        engine = AlternativeBenchmarkEngine(dry_run=True)

        candidate = SimpleNamespace(
            alternative_type=AlternativeType.SQL_REWRITE,
            original_sql="SELECT * FROM orders",
            optimized_sql="SELECT * FROM orders",
        )

        result = engine.benchmark_candidate(candidate)

        self.assertEqual(result["status"], "NOT_BENCHMARKABLE")
        self.assertEqual(result["evidence_status"], "INSUFFICIENT")

    def test_benchmark_candidate_runs_sql_rewrite(self):
        engine = AlternativeBenchmarkEngine(
            dry_run=True,
            timeout_ms=1000.0,
        )

        candidate = SimpleNamespace(
            alternative_type=AlternativeType.SQL_REWRITE,
            original_sql="SELECT * FROM orders",
            optimized_sql="SELECT * FROM orders WHERE id > 0",
        )

        result = engine.benchmark_candidate(candidate)

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["evidence_status"], "SIMULATED")
        self.assertTrue(result["is_mock_data"])

if __name__ == "__main__":
    unittest.main()
