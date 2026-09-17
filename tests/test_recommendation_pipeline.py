import unittest

from collector.recommendation_pipeline import (
    generate_recommendations,
)
from collector.workload_cost_analyzer import (
    analyze_workload_costs,
)


class TestRecommendationPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.analysis = analyze_workload_costs()

        cls.query = """
        SELECT
            oi.order_id,
            p.product_name,
            oi.quantity,
            oi.unit_price
        FROM order_items oi
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE p.category_id = 1;
        """

        # Q009 execution-plan features.
        cls.features = {
            "filters": [
                {
                    "table": "products",
                    "condition": "(category_id = 1)",
                    "rows_removed": 948,
                }
            ],
            "scan_nodes": [
                {
                    "table": "order_items",
                    "node_type": "Seq Scan",
                },
                {
                    "table": "products",
                    "node_type": "Seq Scan",
                },
            ],
            "has_index_condition": False,
        }

        cls.recommendations = generate_recommendations(
            cls.query,
            cls.features,
        )

    def test_recommendations_are_generated(self):
        self.assertGreater(
            len(self.recommendations),
            0,
        )

    def test_q009_products_category_candidate_exists(self):
        matches = [
            recommendation
            for recommendation in self.recommendations
            if (
                recommendation["table_name"]
                == "products"
                and recommendation["column_name"]
                == "category_id"
            )
        ]

        self.assertEqual(
            len(matches),
            1,
        )

    def test_original_recommendation_score_preserved(self):
        matches = [
            recommendation
            for recommendation in self.recommendations
            if (
                recommendation["table_name"]
                == "products"
                and recommendation["column_name"]
                == "category_id"
            )
        ]

        self.assertEqual(
            matches[0]["score"],
            60,
        )

    def test_workload_rank_attached(self):
        matches = [
            recommendation
            for recommendation in self.recommendations
            if (
                recommendation["table_name"]
                == "products"
                and recommendation["column_name"]
                == "category_id"
            )
        ]

        self.assertEqual(
            matches[0]["workload_cost_rank"],
            1,
        )

    def test_workload_priority_attached(self):
        matches = [
            recommendation
            for recommendation in self.recommendations
            if (
                recommendation["table_name"]
                == "products"
                and recommendation["column_name"]
                == "category_id"
            )
        ]

        self.assertEqual(
            matches[0]["workload_priority"],
            "Critical",
        )

    def test_execution_time_share_attached(self):
        matches = [
            recommendation
            for recommendation in self.recommendations
            if (
                recommendation["table_name"]
                == "products"
                and recommendation["column_name"]
                == "category_id"
            )
        ]

        self.assertAlmostEqual(
            matches[0]["execution_time_share"],
            90.46,
            delta=0.1,
        )

    def test_fingerprint_attached(self):
        for recommendation in self.recommendations:
            self.assertIn(
                "fingerprint",
                recommendation,
            )

            self.assertTrue(
                recommendation["fingerprint"]
            )

    def test_normalized_template_attached(self):
        for recommendation in self.recommendations:
            self.assertIn(
                "normalized_template",
                recommendation,
            )

            self.assertTrue(
                recommendation["normalized_template"]
            )

    def test_workload_priority_is_separate_from_score_priority(self):
        matches = [
            recommendation
            for recommendation in self.recommendations
            if (
                recommendation["table_name"]
                == "products"
                and recommendation["column_name"]
                == "category_id"
            )
        ]

        result = matches[0]

        self.assertEqual(
            result["priority"],
            "Medium",
        )

        self.assertEqual(
            result["workload_priority"],
            "Critical",
        )

    def test_workload_metrics_are_positive(self):
        for recommendation in self.recommendations:

            self.assertGreaterEqual(
                recommendation["total_executions"],
                0,
            )

            self.assertGreaterEqual(
                recommendation["total_execution_time_ms"],
                0,
            )

            self.assertGreaterEqual(
                recommendation["total_rows_processed"],
                0,
            )


if __name__ == "__main__":
    unittest.main()
