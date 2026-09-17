import unittest

from collector.workload_cost_analyzer import analyze_workload_costs


class TestWorkloadCostAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.analysis = analyze_workload_costs()
        cls.groups = cls.analysis["groups"]

    def test_total_profiles(self):
        self.assertEqual(self.analysis["total_profiles"], 16)

    def test_unique_fingerprints(self):
        self.assertEqual(self.analysis["unique_fingerprints"], 15)

    def test_total_executions(self):
        self.assertEqual(self.analysis["total_executions"], 18)

    def test_total_execution_time_positive(self):
        self.assertGreater(
            self.analysis["total_execution_time_ms"],
            0
        )

    def test_total_rows_processed_positive(self):
        self.assertGreater(
            self.analysis["total_rows_processed"],
            0
        )

    def test_q009_is_rank_one(self):
        top_group = self.groups[0]

        self.assertEqual(top_group["workload_cost_rank"], 1)
        self.assertEqual(top_group["profile_ids"], [10, 17])

    def test_q009_execution_time_share(self):
        top_group = self.groups[0]

        self.assertAlmostEqual(
            top_group["execution_time_share"],
            90.46,
            delta=0.1
        )

    def test_execution_time_shares_sum_to_100(self):
        total_share = sum(
            group["execution_time_share"]
            for group in self.groups
        )

        self.assertAlmostEqual(
            total_share,
            100.0,
            delta=0.01
        )

    def test_execution_frequency_shares_sum_to_100(self):
        total_share = sum(
            group["execution_frequency_share"]
            for group in self.groups
        )

        self.assertAlmostEqual(
            total_share,
            100.0,
            delta=0.01
        )

    def test_groups_sorted_by_total_execution_time(self):
        execution_times = [
            group["total_execution_time_ms"]
            for group in self.groups
        ]

        self.assertEqual(
            execution_times,
            sorted(execution_times, reverse=True)
        )


if __name__ == "__main__":
    unittest.main()
