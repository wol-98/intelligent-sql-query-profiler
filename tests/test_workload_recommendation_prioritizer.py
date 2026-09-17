import unittest

from collector.workload_cost_analyzer import analyze_workload_costs
from collector.workload_recommendation_prioritizer import (
    build_workload_lookup,
    calculate_workload_priority,
)


class TestWorkloadRecommendationPrioritizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.analysis = analyze_workload_costs()
        cls.lookup = build_workload_lookup(cls.analysis)

    def test_lookup_contains_all_fingerprints(self):
        self.assertEqual(
            len(self.lookup),
            self.analysis["unique_fingerprints"]
        )

    def test_q009_is_in_lookup(self):
        q009_group = self.analysis["groups"][0]

        fingerprint = q009_group["fingerprint"]

        self.assertIn(fingerprint, self.lookup)

    def test_q009_workload_rank(self):
        q009_group = self.analysis["groups"][0]

        self.assertEqual(
            q009_group["workload_cost_rank"],
            1
        )

    def test_q009_execution_time_share(self):
        q009_group = self.analysis["groups"][0]

        self.assertAlmostEqual(
            q009_group["execution_time_share"],
            90.46,
            delta=0.1
        )

    def test_q009_priority_is_critical(self):
        q009_group = self.analysis["groups"][0]

        priority = calculate_workload_priority(
            q009_group["execution_time_share"],
            q009_group["execution_frequency_share"],
        )

        self.assertEqual(
            priority,
            "Critical"
        )

    def test_high_cost_priority(self):
        priority = calculate_workload_priority(
            execution_time_share=25.0,
            execution_frequency_share=5.0,
        )

        self.assertEqual(priority, "High")

    def test_moderate_cost_priority(self):
        priority = calculate_workload_priority(
            execution_time_share=7.0,
            execution_frequency_share=5.0,
        )

        self.assertEqual(priority, "Moderate")

    def test_frequency_can_raise_priority(self):
        priority = calculate_workload_priority(
            execution_time_share=1.0,
            execution_frequency_share=15.0,
        )

        self.assertEqual(priority, "Moderate")

    def test_low_workload_priority(self):
        priority = calculate_workload_priority(
            execution_time_share=1.0,
            execution_frequency_share=5.0,
        )

        self.assertEqual(priority, "Low")

    def test_lookup_preserves_workload_metrics(self):
        q009_group = self.analysis["groups"][0]

        fingerprint = q009_group["fingerprint"]
        metrics = self.lookup[fingerprint]

        self.assertEqual(
            metrics["total_executions"],
            q009_group["total_executions"]
        )

        self.assertAlmostEqual(
            metrics["total_execution_time_ms"],
            q009_group["total_execution_time_ms"],
            places=6
        )

        self.assertEqual(
            metrics["total_rows_processed"],
            q009_group["total_rows_processed"]
        )


if __name__ == "__main__":
    unittest.main()
