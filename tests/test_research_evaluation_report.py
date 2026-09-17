"""
Tests for M14.4 Integrated Research Evaluation Report
"""

import unittest

from collector.research_evaluation_report import (
    build_research_summary,
    build_top_k_comparison,
    build_critical_workload_comparison,
    build_validation_evidence_table,
    build_limitations,
    build_interpretation,
    build_research_evaluation,
)


class TestResearchSummary(unittest.TestCase):

    def test_build_summary(self):
        quality = {
            "evaluated_rows": 23,
            "overall": {
                "successful": 13,
                "neutral": 6,
                "unsuccessful": 4,
                "success_rate": 56.52,
                "average_improvement": 33.19,
                "median_improvement": 23.17,
            },
            "relationships": {
                "score_vs_improvement": {
                    "pearson": 0.23,
                    "spearman": 0.34,
                },
                "workload_share_vs_improvement": {
                    "pearson": -0.10,
                    "spearman": -0.45,
                },
            },
            "priority_outcomes": {
                "recommendation": {
                    "high_priority_count": 10,
                    "high_priority_success_rate": 90.0,
                }
            },
        }

        prioritization = {
            "rank_correlation": {
                "spearman": -0.30
            },
            "rank_shifts": {
                "average_absolute_rank_shift": 10.0,
                "maximum_absolute_rank_shift": 15,
            },
        }

        result = build_research_summary(
            quality,
            prioritization,
        )

        self.assertEqual(
            result["evaluated_rows"],
            23,
        )
        self.assertEqual(
            result["successful"],
            13,
        )
        self.assertAlmostEqual(
            result[
                "score_vs_improvement_spearman"
            ],
            0.34,
        )
        self.assertAlmostEqual(
            result["rank_correlation_spearman"],
            -0.30,
        )


class TestTopK(unittest.TestCase):

    def test_top_k_rows(self):
        prioritization = {
            "top_k": {
                3: {
                    "score_only": {
                        "count": 3,
                        "successful": 2,
                        "success_rate": 66.67,
                        "neutral": 1,
                        "unsuccessful": 0,
                        "low_benefit": 1,
                        "negative_benefit": 0,
                        "average_improvement": 55.21,
                    },
                    "workload_aware": {
                        "count": 3,
                        "successful": 1,
                        "success_rate": 33.33,
                        "neutral": 0,
                        "unsuccessful": 2,
                        "low_benefit": 0,
                        "negative_benefit": 2,
                        "average_improvement": 24.08,
                    },
                }
            }
        }

        rows = build_top_k_comparison(
            prioritization
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(
            rows[0]["k"],
            3,
        )
        self.assertEqual(
            rows[1]["unsuccessful"],
            2,
        )


class TestCriticalWorkload(unittest.TestCase):

    def test_critical_comparison(self):
        prioritization = {
            "critical_workload": {
                "critical_observation_count": 3,
                "score_only": {
                    "top_3_count": 0,
                    "top_5_count": 0,
                    "top_10_count": 0,
                    "ranks": [15, 16, 17],
                },
                "workload_aware": {
                    "top_3_count": 3,
                    "top_5_count": 3,
                    "top_10_count": 3,
                    "ranks": [1, 2, 3],
                },
            }
        }

        result = build_critical_workload_comparison(
            prioritization
        )

        self.assertEqual(
            result["critical_observations"],
            3,
        )
        self.assertEqual(
            result["workload_aware"]["top_3_count"],
            3,
        )


class TestEvidenceTable(unittest.TestCase):

    def test_evidence_table_falls_back_to_average(self):
        dataset = [
            {
                "recommendation_id": 8,
                "benchmark_id": 1,
                "table_name": "products",
                "column_name": "category_id",
                "recommendation_score": 60,
                "recommendation_priority": "Medium",
                "workload_priority": "Critical",
                "execution_time_share": 90.46,
                "validation_status": "UNSUCCESSFUL",
                "median_improvement_percentage": None,
                "improvement_percentage": -1.33,
                "rows_preserved": True,
                "index_used": True,
                "plan_changed": True,
            },
            {
                "recommendation_id": 99,
                "benchmark_id": None,
                "improvement_percentage": None,
                "median_improvement_percentage": None,
            },
        ]

        result = build_validation_evidence_table(
            dataset
        )

        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(
            result[0]["improvement_percentage"],
            -1.33,
        )


class TestLimitations(unittest.TestCase):

    def test_limitations_are_explicit(self):
        result = build_limitations(
            23,
            23,
        )

        self.assertGreaterEqual(
            len(result),
            5,
        )

        combined = " ".join(result)

        self.assertIn(
            "23",
            combined,
        )

        self.assertIn(
            "causality",
            combined,
        )


class TestInterpretation(unittest.TestCase):

    def test_interpretation_contains_core_findings(self):
        summary = {
            "score_vs_improvement_pearson": 0.23,
        }

        critical = {
            "critical_observations": 3,
            "score_only": {
                "top_3_count": 0,
            },
            "workload_aware": {
                "top_3_count": 3,
            },
        }

        top_k = [
            {
                "k": 3,
                "strategy": "score_only",
                "success_rate": 66.67,
            },
            {
                "k": 3,
                "strategy": "workload_aware",
                "success_rate": 33.33,
            },
        ]

        result = build_interpretation(
            summary,
            critical,
            top_k,
        )

        combined = " ".join(result)

        self.assertIn(
            "Critical-workload",
            combined,
        )
        self.assertIn(
            "empirical validation",
            combined,
        )


class TestCompleteReport(unittest.TestCase):

    def test_complete_report(self):
        quality = {
            "evaluated_rows": 1,
            "overall": {
                "successful": 1,
                "neutral": 0,
                "unsuccessful": 0,
                "success_rate": 100.0,
                "average_improvement": 20.0,
                "median_improvement": 20.0,
            },
            "relationships": {
                "score_vs_improvement": {
                    "pearson": 1.0,
                    "spearman": 1.0,
                },
                "workload_share_vs_improvement": {
                    "pearson": 0.0,
                    "spearman": 0.0,
                },
            },
            "priority_outcomes": {
                "recommendation": {
                    "high_priority_count": 1,
                    "high_priority_success_rate": 100.0,
                }
            },
        }

        prioritization = {
            "rank_correlation": {
                "pearson": 1.0,
                "spearman": 1.0,
            },
            "rank_shifts": {
                "average_absolute_rank_shift": 0.0,
                "maximum_absolute_rank_shift": 0,
            },
            "top_k": {
                1: {
                    "score_only": {
                        "count": 1,
                        "successful": 1,
                        "success_rate": 100.0,
                        "neutral": 0,
                        "unsuccessful": 0,
                        "low_benefit": 0,
                        "negative_benefit": 0,
                        "average_improvement": 20.0,
                    },
                    "workload_aware": {
                        "count": 1,
                        "successful": 1,
                        "success_rate": 100.0,
                        "neutral": 0,
                        "unsuccessful": 0,
                        "low_benefit": 0,
                        "negative_benefit": 0,
                        "average_improvement": 20.0,
                    },
                }
            },
            "critical_workload": {
                "critical_observation_count": 0,
                "score_only": {
                    "top_3_count": 0,
                    "top_5_count": 0,
                    "top_10_count": 0,
                    "ranks": [],
                },
                "workload_aware": {
                    "top_3_count": 0,
                    "top_5_count": 0,
                    "top_10_count": 0,
                    "ranks": [],
                },
            },
        }

        dataset = [
            {
                "recommendation_id": 1,
                "benchmark_id": 1,
                "table_name": "orders",
                "column_name": "customer_id",
                "recommendation_score": 80,
                "recommendation_priority": "High",
                "workload_priority": "Low",
                "execution_time_share": 1.0,
                "validation_status": "SUCCESSFUL",
                "median_improvement_percentage": None,
                "improvement_percentage": 20.0,
                "rows_preserved": True,
                "index_used": True,
                "plan_changed": True,
            }
        ]

        report = build_research_evaluation(
            quality,
            prioritization,
            dataset,
        )

        self.assertIn(
            "summary",
            report,
        )
        self.assertIn(
            "interpretation",
            report,
        )
        self.assertIn(
            "limitations",
            report,
        )
        self.assertEqual(
            len(report["validation_evidence"]),
            1,
        )


if __name__ == "__main__":
    unittest.main()
