import unittest
from api.services.alternative_benchmark import AlternativeBenchmarkEngine
from api.services.blueprint_generator import DynamicBlueprintGenerator
from api.schemas.structural_optimization import OptimizationCandidate, AlternativeType, CandidateStatus

class TestM21Integration(unittest.TestCase):
    def test_benchmark_safety_abort(self):
        # Force a timeout abort by setting timeout to 0 ms
        engine = AlternativeBenchmarkEngine(dry_run=True, timeout_ms=0.0)
        result = engine.compare_query_alternatives("SELECT *", "SELECT 1")
        self.assertEqual(result["status"], "BASELINE_TIMEOUT")

    def test_blueprint_generation(self):
        generator = DynamicBlueprintGenerator()
        candidate = OptimizationCandidate(
            candidate_id="123",
            alternative_type=list(AlternativeType)[0],
            status=CandidateStatus.CANDIDATE,
            title="Test CTE",
            rationale="Test Rationale",
            original_sql="SELECT *",
            optimized_sql="WITH cte AS (SELECT *) SELECT * FROM cte"
        )
        
        benchmark_mock = {"status": "SUCCESS", "is_mock_data": True, "improvement_percentage": 25.5}
        
        blueprint = generator.build_blueprint("SELECT *", {"tables": ["t1"]}, [candidate], benchmark_mock)
        
        self.assertEqual(len(blueprint["sections"]), 5)
        self.assertEqual(blueprint["sections"][3]["improvement_percentage"], 25.5)
        self.assertIn("Recommended", blueprint["sections"][4]["verdict"])

if __name__ == '__main__':
    unittest.main()
