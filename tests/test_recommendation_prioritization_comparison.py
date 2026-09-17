"""
Tests for M14.3 Score-Only vs Workload-Aware Prioritization
"""

import unittest

from collector.recommendation_prioritization_comparison import (
    rank_score_only,
    rank_workload_aware,
    calculate_rank_correlation,
    summarize_rank_shifts,
    summarize_ranked_records,
    summarize_critical_workload,
    analyze_prioritization_comparison,
)


def make_record(
    recommendation_id,
    score,
    workload_priority,
    time_share,
    status,
    improvement,
    benchmark_id=None,
):
    return {
        "recommendation_id": recommendation_id,
        "query_profile_id": recommendation_id,
        "table_name": "test_table",
        "column_name": f"column_{recommendation_id}",
        "recommendation_score": score,
        "recommendation_priority": "High",
        "workload_priority": workload_priority,
        "execution_time_share": time_share,
        "execution_frequency_share": 5.0,
        "validation_status": status,
        "improvement_percentage": improvement,
        "median_improvement_percentage": None,
        "benchmark_id": benchmark_id or recommendation_id,
    }


class TestScoreOnlyRanking(unittest.TestCase):

    def test_higher_score_first(self):
        records = [
            make_record(
                1, 40, "Low", 1,
                "SUCCESSFUL", 20
            ),
            make_record(
                2, 80, "Low", 1,
                "SUCCESSFUL", 20
            ),
        ]

        ranked = rank_score_only(records)

        self.assertEqual(
            ranked[0]["recommendation_id"],
            2,
        )

        self.assertEqual(
            ranked[0]["score_only_rank"],
            1,
        )


class TestWorkloadAwareRanking(unittest.TestCase):

    def test_critical_workload_first(self):
        records = [
            make_record(
                1, 90, "Low", 1,
                "SUCCESSFUL", 20
            ),
            make_record(
                2, 40, "Critical", 80,
                "SUCCESSFUL", 20
            ),
        ]

        ranked = rank_workload_aware(records)

        self.assertEqual(
            ranked[0]["recommendation_id"],
            2,
        )

        self.assertEqual(
            ranked[0]["workload_aware_rank"],
            1,
        )

    def test_same_workload_uses_time_share(self):
        records = [
            make_record(
                1, 50, "High", 5,
                "SUCCESSFUL", 20
            ),
            make_record(
                2, 40, "High", 15,
                "SUCCESSFUL", 20
            ),
        ]

        ranked = rank_workload_aware(records)

        self.assertEqual(
            ranked[0]["recommendation_id"],
            2,
        )


class TestRankCorrelation(unittest.TestCase):

    def test_perfect_positive_correlation(self):
        comparison = [
            {
                "score_only_rank": 1,
                "workload_aware_rank": 1,
            },
            {
                "score_only_rank": 2,
                "workload_aware_rank": 2,
            },
            {
                "score_only_rank": 3,
                "workload_aware_rank": 3,
            },
        ]

        result = calculate_rank_correlation(
            comparison
        )

        self.assertAlmostEqual(
            result["pearson"],
            1.0,
        )

        self.assertAlmostEqual(
            result["spearman"],
            1.0,
        )

    def test_rank_correlation_requires_pairs(self):
        result = calculate_rank_correlation([])

        self.assertEqual(result["n"], 0)
        self.assertIsNone(result["pearson"])
        self.assertIsNone(result["spearman"])


class TestRankShifts(unittest.TestCase):

    def test_rank_shift_summary(self):
        comparison = [
            {"rank_shift": 2},
            {"rank_shift": -1},
            {"rank_shift": 0},
        ]

        result = summarize_rank_shifts(
            comparison
        )

        self.assertEqual(result["upward"], 1)
        self.assertEqual(result["downward"], 1)
        self.assertEqual(result["unchanged"], 1)
        self.assertAlmostEqual(
            result["average_absolute_rank_shift"],
            1.0,
        )
        self.assertEqual(
            result["maximum_absolute_rank_shift"],
            2,
        )


class TestOutcomeSummary(unittest.TestCase):

    def test_outcome_counts(self):
        records = [
            make_record(
                1, 90, "Low", 1,
                "SUCCESSFUL", 20
            ),
            make_record(
                2, 80, "Low", 1,
                "NEUTRAL", 2
            ),
            make_record(
                3, 70, "Low", 1,
                "UNSUCCESSFUL", -2
            ),
        ]

        result = summarize_ranked_records(
            records
        )

        self.assertEqual(result["count"], 3)
        self.assertEqual(result["successful"], 1)
        self.assertEqual(result["neutral"], 1)
        self.assertEqual(result["unsuccessful"], 1)
        self.assertAlmostEqual(
            result["success_rate"],
            33.3333333333,
            places=5,
        )
        self.assertEqual(
            result["low_benefit"],
            1,
        )
        self.assertEqual(
            result["negative_benefit"],
            1,
        )


class TestCriticalWorkload(unittest.TestCase):

    def test_critical_observations_are_identified(self):
        records = [
            make_record(
                1, 90, "Critical", 90,
                "SUCCESSFUL", 20
            ),
            make_record(
                2, 80, "Low", 1,
                "SUCCESSFUL", 20
            ),
            make_record(
                3, 70, "Critical", 60,
                "NEUTRAL", 2
            ),
        ]

        result = summarize_critical_workload(
            records
        )

        self.assertEqual(
            result["critical_observation_count"],
            2,
        )

        self.assertEqual(
            result["workload_aware"]["top_3_count"],
            2,
        )


class TestCompleteAnalysis(unittest.TestCase):

    def test_complete_analysis(self):
        records = [
            make_record(
                1, 90, "Low", 1,
                "SUCCESSFUL", 20
            ),
            make_record(
                2, 40, "Critical", 80,
                "SUCCESSFUL", 30
            ),
            make_record(
                3, 30, "Low", 1,
                "UNSUCCESSFUL", -2
            ),
        ]

        result = analyze_prioritization_comparison(
            records,
            k_values=(2,),
        )

        self.assertEqual(
            result["evaluated_rows"],
            3,
        )

        self.assertEqual(
            result["score_only_count"],
            3,
        )

        self.assertEqual(
            result["workload_aware_count"],
            3,
        )

        self.assertIn(
            2,
            result["top_k"],
        )

        self.assertEqual(
            result["top_k"][2]["score_only"]["count"],
            2,
        )

        self.assertEqual(
            result["top_k"][2]["workload_aware"]["count"],
            2,
        )

        self.assertEqual(
            result["critical_workload"]
            ["workload_aware"]["top_3_count"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
