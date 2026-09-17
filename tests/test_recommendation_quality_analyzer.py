"""
Tests for M14.1 Recommendation Quality Analyzer
"""

import unittest

from collector.query_parser import QueryFingerprinter

from collector.recommendation_quality_analyzer import (
    build_workload_lookup,
    calculate_workload_priority,
    get_evaluation_improvement,
    build_recommendation_evaluation_dataset,
    summarize_evaluation_dataset,
)


# =========================================================
# TEST WORKLOAD LOOKUP
# =========================================================

class TestWorkloadLookup(unittest.TestCase):

    def test_workload_lookup_by_fingerprint(self):

        workload_analysis = {
            "groups": [
                {
                    "fingerprint": "abc123",
                    "workload_cost_rank": 1,
                    "execution_time_share": 90.0,
                    "execution_frequency_share": 20.0,
                    "total_executions": 3,
                    "total_execution_time_ms": 1000.0,
                    "total_rows_processed": 5000,
                }
            ]
        }

        lookup = build_workload_lookup(
            workload_analysis
        )

        self.assertIn(
            "abc123",
            lookup
        )

        self.assertEqual(
            lookup["abc123"]["workload_cost_rank"],
            1
        )

        self.assertEqual(
            lookup["abc123"]["execution_time_share"],
            90.0
        )


# =========================================================
# TEST WORKLOAD PRIORITY
# =========================================================

class TestWorkloadPriority(unittest.TestCase):

    def test_critical_priority(self):

        self.assertEqual(
            calculate_workload_priority(
                90.0,
                20.0
            ),
            "Critical"
        )

    def test_high_priority(self):

        self.assertEqual(
            calculate_workload_priority(
                20.0,
                5.0
            ),
            "High"
        )

    def test_moderate_priority_by_time(self):

        self.assertEqual(
            calculate_workload_priority(
                5.0,
                5.0
            ),
            "Moderate"
        )

    def test_moderate_priority_by_frequency(self):

        self.assertEqual(
            calculate_workload_priority(
                2.0,
                10.0
            ),
            "Moderate"
        )

    def test_low_priority(self):

        self.assertEqual(
            calculate_workload_priority(
                2.0,
                5.0
            ),
            "Low"
        )

    def test_unknown_priority(self):

        self.assertEqual(
            calculate_workload_priority(
                None,
                None
            ),
            "Unknown"
        )


# =========================================================
# TEST EVALUATION IMPROVEMENT
# =========================================================

class TestEvaluationImprovement(unittest.TestCase):

    def test_uses_median_when_available(self):

        record = {
            "median_improvement_percentage": 25.0,
            "improvement_percentage": 20.0,
        }

        self.assertEqual(
            get_evaluation_improvement(record),
            25.0
        )

    def test_falls_back_to_average_improvement(self):

        record = {
            "median_improvement_percentage": None,
            "improvement_percentage": 20.0,
        }

        self.assertEqual(
            get_evaluation_improvement(record),
            20.0
        )

    def test_returns_none_when_no_improvement_exists(self):

        record = {
            "median_improvement_percentage": None,
            "improvement_percentage": None,
        }

        self.assertIsNone(
            get_evaluation_improvement(record)
        )


# =========================================================
# TEST DATASET CONSTRUCTION
# =========================================================

class TestEvaluationDataset(unittest.TestCase):

    def setUp(self):

        query_text = (
            "SELECT * FROM products "
            "WHERE category_id = 1;"
        )

        fingerprinter = QueryFingerprinter()

        fingerprint, normalized_template = (
            fingerprinter.generate_fingerprint(
                query_text
            )
        )

        self.workload_analysis = {
            "groups": [
                {
                    "fingerprint": fingerprint,
                    "normalized_template": normalized_template,
                    "workload_cost_rank": 1,
                    "execution_time_share": 90.46,
                    "execution_frequency_share": 16.67,
                    "total_executions": 3,
                    "total_execution_time_ms": 1492.131,
                    "total_rows_processed": 15914,
                }
            ]
        }

        self.records = [
            {
                "recommendation_id": 8,
                "query_profile_id": 10,
                "table_name": "products",
                "column_name": "category_id",
                "index_type": "B-tree",
                "recommendation_score": 60.0,
                "priority": "Medium",
                "reasoning": "Test recommendation",

                "query_hash": "hash",
                "query_text": (
                    "SELECT * FROM products "
                    "WHERE category_id = 1;"
                ),
                "query_type": "SELECT",
                "execution_count": 1,
                "total_execution_time_ms": 10.0,
                "average_execution_time_ms": 10.0,
                "rows_processed": 52,

                "benchmark_id": 1,
                "execution_time_before_ms": 32.0,
                "execution_time_after_ms": 32.5,
                "improvement_percentage": -1.5,
                "median_before_ms": None,
                "median_after_ms": None,
                "median_improvement_percentage": None,
                "rows_before": 7957,
                "rows_after": 7957,
                "rows_preserved": True,
                "index_used": True,
                "index_node_type": "Bitmap Index Scan",
                "plan_changed": True,
                "validation_status": "UNSUCCESSFUL",
                "validation_reason": "No performance benefit",
            }
        ]

    def test_dataset_contains_record(self):

        dataset = (
            build_recommendation_evaluation_dataset(
                self.workload_analysis,
                self.records
            )
        )

        self.assertEqual(
            len(dataset),
            1
        )

    def test_fingerprint_is_string(self):

        dataset = (
            build_recommendation_evaluation_dataset(
                self.workload_analysis,
                self.records
            )
        )

        self.assertIsInstance(
            dataset[0]["fingerprint"],
            str
        )

    def test_normalized_template_is_present(self):

        dataset = (
            build_recommendation_evaluation_dataset(
                self.workload_analysis,
                self.records
            )
        )

        self.assertIsNotNone(
            dataset[0]["normalized_template"]
        )

    def test_workload_information_is_attached(self):

        dataset = (
            build_recommendation_evaluation_dataset(
                self.workload_analysis,
                self.records
            )
        )

        row = dataset[0]

        self.assertTrue(
            row["workload_match"]
        )

        self.assertEqual(
            row["workload_cost_rank"],
            1
        )

        self.assertEqual(
            row["workload_priority"],
            "Critical"
        )

    def test_evaluation_improvement_fallback(self):

        dataset = (
            build_recommendation_evaluation_dataset(
                self.workload_analysis,
                self.records
            )
        )

        self.assertEqual(
            dataset[0][
                "evaluation_improvement_percentage"
            ],
            -1.5
        )

    def test_validation_information_is_attached(self):

        dataset = (
            build_recommendation_evaluation_dataset(
                self.workload_analysis,
                self.records
            )
        )

        row = dataset[0]

        self.assertEqual(
            row["benchmark_id"],
            1
        )

        self.assertTrue(
            row["rows_preserved"]
        )

        self.assertTrue(
            row["index_used"]
        )

        self.assertTrue(
            row["plan_changed"]
        )

        self.assertEqual(
            row["validation_status"],
            "UNSUCCESSFUL"
        )

    def test_multiple_benchmarks_remain_separate(self):

        second_record = dict(
            self.records[0]
        )

        second_record["benchmark_id"] = 13
        second_record[
            "improvement_percentage"
        ] = -2.5

        dataset = (
            build_recommendation_evaluation_dataset(
                self.workload_analysis,
                [
                    self.records[0],
                    second_record
                ]
            )
        )

        self.assertEqual(
            len(dataset),
            2
        )

        self.assertEqual(
            dataset[0]["benchmark_id"],
            1
        )

        self.assertEqual(
            dataset[1]["benchmark_id"],
            13
        )


# =========================================================
# TEST SUMMARY
# =========================================================

class TestDatasetSummary(unittest.TestCase):

    def test_summary_counts(self):

        dataset = [
            {
                "recommendation_id": 1,
                "benchmark_id": 10,
                "fingerprint": "fp1",
                "workload_match": True,
                "evaluation_improvement_percentage": 10.0,
            },
            {
                "recommendation_id": 1,
                "benchmark_id": 11,
                "fingerprint": "fp1",
                "workload_match": True,
                "evaluation_improvement_percentage": -2.0,
            },
            {
                "recommendation_id": 2,
                "benchmark_id": None,
                "fingerprint": "fp2",
                "workload_match": True,
                "evaluation_improvement_percentage": None,
            },
        ]

        summary = summarize_evaluation_dataset(
            dataset
        )

        self.assertEqual(
            summary["dataset_rows"],
            3
        )

        self.assertEqual(
            summary["unique_recommendations"],
            2
        )

        self.assertEqual(
            summary["unique_benchmarks"],
            2
        )

        self.assertEqual(
            summary["unique_fingerprints"],
            2
        )

        self.assertEqual(
            summary["validated_rows"],
            2
        )

        self.assertEqual(
            summary["workload_matched_rows"],
            3
        )

        self.assertEqual(
            summary["rows_without_benchmark"],
            1
        )

        self.assertEqual(
            summary["rows_with_evaluation_improvement"],
            2
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    unittest.main()
