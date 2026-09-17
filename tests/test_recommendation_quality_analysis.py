"""
Tests for M14.2 Recommendation Quality & Workload-Outcome Analysis
"""

import unittest

from collector.recommendation_quality_analysis import (
    classify_improvement,
    analyze_score_vs_improvement,
    analyze_workload_share_vs_improvement,
    calculate_research_metrics,
    analyze_workload_priority_outcomes,
    analyze_recommendation_priority_outcomes,
    analyze_recommendation_quality,
)


class TestImprovementClassification(unittest.TestCase):

    def test_successful(self):
        self.assertEqual(
            classify_improvement(5.0),
            "SUCCESSFUL"
        )

    def test_low_benefit(self):
        self.assertEqual(
            classify_improvement(2.5),
            "LOW_BENEFIT"
        )

    def test_zero_is_low_benefit(self):
        self.assertEqual(
            classify_improvement(0.0),
            "LOW_BENEFIT"
        )

    def test_negative(self):
        self.assertEqual(
            classify_improvement(-1.0),
            "NEGATIVE_BENEFIT"
        )

    def test_unknown(self):
        self.assertEqual(
            classify_improvement(None),
            "UNKNOWN"
        )


class TestM142Analysis(unittest.TestCase):

    def setUp(self):
        self.dataset = [
            {
                "recommendation_id": 1,
                "recommendation_score": 80.0,
                "recommendation_priority": "High",
                "execution_time_share": 50.0,
                "workload_priority": "Critical",
                "evaluation_improvement_percentage": 20.0,
                "validation_status": "SUCCESSFUL",
                "index_used": True,
                "rows_preserved": True,
            },
            {
                "recommendation_id": 2,
                "recommendation_score": 60.0,
                "recommendation_priority": "Medium",
                "execution_time_share": 20.0,
                "workload_priority": "High",
                "evaluation_improvement_percentage": 3.0,
                "validation_status": "NEUTRAL",
                "index_used": True,
                "rows_preserved": True,
            },
            {
                "recommendation_id": 3,
                "recommendation_score": 40.0,
                "recommendation_priority": "Low",
                "execution_time_share": 5.0,
                "workload_priority": "Moderate",
                "evaluation_improvement_percentage": -2.0,
                "validation_status": "UNSUCCESSFUL",
                "index_used": False,
                "rows_preserved": True,
            },
            {
                "recommendation_id": 4,
                "recommendation_score": 70.0,
                "recommendation_priority": "High",
                "execution_time_share": 1.0,
                "workload_priority": "Low",
                "evaluation_improvement_percentage": 10.0,
                "validation_status": "SUCCESSFUL",
                "index_used": True,
                "rows_preserved": True,
            },
            {
                "recommendation_id": 5,
                "recommendation_score": 50.0,
                "recommendation_priority": "Medium",
                "execution_time_share": 2.0,
                "workload_priority": "Low",
                "evaluation_improvement_percentage": None,
                "validation_status": None,
                "index_used": None,
                "rows_preserved": None,
            },
        ]


    def test_score_correlation(self):
        result = analyze_score_vs_improvement(
            self.dataset
        )

        self.assertEqual(result["n"], 4)
        self.assertIsNotNone(
            result["pearson_correlation"]
        )
        self.assertIsNotNone(
            result["spearman_correlation"]
        )


    def test_workload_share_correlation(self):
        result = analyze_workload_share_vs_improvement(
            self.dataset
        )

        self.assertEqual(result["n"], 4)
        self.assertIsNotNone(
            result["pearson_correlation"]
        )
        self.assertIsNotNone(
            result["spearman_correlation"]
        )


    def test_overall_metrics(self):
        metrics = calculate_research_metrics(
            self.dataset
        )

        self.assertEqual(
            metrics["evaluated_rows"],
            4
        )

        self.assertEqual(
            metrics["successful"],
            2
        )

        self.assertEqual(
            metrics["neutral"],
            1
        )

        self.assertEqual(
            metrics["unsuccessful"],
            1
        )

        self.assertAlmostEqual(
            metrics["success_rate"],
            50.0
        )

        self.assertEqual(
            metrics["low_benefit_count"],
            1
        )

        self.assertEqual(
            metrics["negative_benefit_count"],
            1
        )

        self.assertEqual(
            metrics["index_not_used_count"],
            1
        )


    def test_high_priority_success_rate(self):
        metrics = calculate_research_metrics(
            self.dataset
        )

        self.assertEqual(
            metrics["high_priority_count"],
            2
        )

        self.assertEqual(
            metrics["high_priority_successful"],
            2
        )

        self.assertAlmostEqual(
            metrics["high_priority_success_rate"],
            100.0
        )


    def test_workload_critical_success_rate(self):
        metrics = calculate_research_metrics(
            self.dataset
        )

        self.assertEqual(
            metrics["workload_critical_count"],
            1
        )

        self.assertEqual(
            metrics["workload_critical_successful"],
            1
        )

        self.assertAlmostEqual(
            metrics["workload_critical_success_rate"],
            100.0
        )


    def test_workload_priority_groups(self):
        results = analyze_workload_priority_outcomes(
            self.dataset
        )

        critical = results[0]

        self.assertEqual(
            critical["category"],
            "Critical"
        )

        self.assertEqual(
            critical["evaluated_rows"],
            1
        )

        self.assertEqual(
            critical["successful"],
            1
        )


    def test_recommendation_priority_groups(self):
        results = (
            analyze_recommendation_priority_outcomes(
                self.dataset
            )
        )

        high = results[0]

        self.assertEqual(
            high["category"],
            "High"
        )

        self.assertEqual(
            high["evaluated_rows"],
            2
        )

        self.assertEqual(
            high["successful"],
            2
        )


    def test_full_analysis_structure(self):
        analysis = analyze_recommendation_quality(
            self.dataset
        )

        self.assertIn(
            "metrics",
            analysis
        )

        self.assertIn(
            "score_vs_improvement",
            analysis
        )

        self.assertIn(
            "workload_share_vs_improvement",
            analysis
        )

        self.assertIn(
            "workload_priority_outcomes",
            analysis
        )

        self.assertIn(
            "recommendation_priority_outcomes",
            analysis
        )


if __name__ == "__main__":
    unittest.main()
