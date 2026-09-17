import unittest

from collector.workload_cost_analyzer import analyze_workload_costs
from collector.workload_aware_recommendations import (
    build_workload_lookup,
    calculate_workload_priority,
    enrich_recommendations_with_workload,
    rank_workload_aware_recommendations,
)


class TestWorkloadAwareRecommendations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.analysis = analyze_workload_costs()

    def test_q009_recommendation_is_enriched(self):
        q009_group = self.analysis["groups"][0]

        recommendation = {
            "query_text": (
                "SELECT "
                "oi.order_id, "
                "p.product_name, "
                "oi.quantity, "
                "oi.unit_price "
                "FROM order_items oi "
                "JOIN products p "
                "ON oi.product_id = p.product_id "
                "WHERE p.category_id = 1;"
            ),
            "table_name": "products",
            "column_name": "category_id",
            "score": 60,
            "priority": "Medium",
        }

        enriched = enrich_recommendations_with_workload(
            [recommendation],
            self.analysis,
        )

        self.assertEqual(len(enriched), 1)

        result = enriched[0]

        self.assertEqual(
            result["workload_cost_rank"],
            1,
        )

        self.assertAlmostEqual(
            result["execution_time_share"],
            90.46,
            delta=0.1,
        )

        self.assertEqual(
            result["workload_priority"],
            "Critical",
        )

    def test_original_score_is_preserved(self):
        recommendation = {
            "query_text": (
                "SELECT * FROM orders "
                "WHERE customer_id = 845;"
            ),
            "table_name": "orders",
            "column_name": "customer_id",
            "score": 75,
            "priority": "High",
        }

        enriched = enrich_recommendations_with_workload(
            [recommendation],
            self.analysis,
        )

        self.assertEqual(
            enriched[0]["score"],
            75,
        )

        self.assertEqual(
            enriched[0]["priority"],
            "High",
        )

    def test_workload_priority_is_separate(self):
        recommendation = {
            "query_text": (
                "SELECT "
                "oi.order_id, "
                "p.product_name, "
                "oi.quantity, "
                "oi.unit_price "
                "FROM order_items oi "
                "JOIN products p "
                "ON oi.product_id = p.product_id "
                "WHERE p.category_id = 1;"
            ),
            "table_name": "products",
            "column_name": "category_id",
            "score": 60,
            "priority": "Medium",
        }

        enriched = enrich_recommendations_with_workload(
            [recommendation],
            self.analysis,
        )

        result = enriched[0]

        self.assertEqual(
            result["priority"],
            "Medium",
        )

        self.assertEqual(
            result["workload_priority"],
            "Critical",
        )

    def test_unknown_query_gets_unknown_workload(self):
        recommendation = {
            "query_text": (
                "SELECT * FROM customers "
                "WHERE customer_id = 999999;"
            ),
            "table_name": "customers",
            "column_name": "customer_id",
            "score": 50,
            "priority": "Medium",
        }

        enriched = enrich_recommendations_with_workload(
            [recommendation],
            self.analysis,
        )

        result = enriched[0]

        self.assertIsNone(
            result["workload_cost_rank"]
        )

        self.assertEqual(
            result["workload_priority"],
            "Unknown",
        )

        self.assertEqual(
            result["total_executions"],
            0,
        )

    def test_missing_query_text_gets_unknown_workload(self):
        recommendation = {
            "table_name": "orders",
            "column_name": "customer_id",
            "score": 75,
            "priority": "High",
        }

        enriched = enrich_recommendations_with_workload(
            [recommendation],
            self.analysis,
        )

        result = enriched[0]

        self.assertEqual(
            result["workload_priority"],
            "Unknown",
        )

        self.assertEqual(
            result["score"],
            75,
        )

    def test_rank_prefers_workload_priority(self):
        recommendations = [
            {
                "table_name": "products",
                "column_name": "category_id",
                "score": 95,
                "workload_priority": "Low",
                "execution_time_share": 1.0,
            },
            {
                "table_name": "orders",
                "column_name": "customer_id",
                "score": 60,
                "workload_priority": "Critical",
                "execution_time_share": 90.0,
            },
        ]

        ranked = rank_workload_aware_recommendations(
            recommendations
        )

        self.assertEqual(
            ranked[0]["workload_priority"],
            "Critical",
        )

        self.assertEqual(
            ranked[0]["score"],
            60,
        )

    def test_rank_uses_score_as_final_tiebreaker(self):
        recommendations = [
            {
                "table_name": "orders",
                "column_name": "status",
                "score": 60,
                "workload_priority": "High",
                "execution_time_share": 20.0,
            },
            {
                "table_name": "orders",
                "column_name": "order_date",
                "score": 80,
                "workload_priority": "High",
                "execution_time_share": 20.0,
            },
        ]

        ranked = rank_workload_aware_recommendations(
            recommendations
        )

        self.assertEqual(
            ranked[0]["score"],
            80,
        )

    def test_workload_lookup_has_15_fingerprints(self):
        lookup = build_workload_lookup(
            self.analysis
        )

        self.assertEqual(
            len(lookup),
            15,
        )

    def test_workload_priority_function(self):
        self.assertEqual(
            calculate_workload_priority(
                90.0,
                5.0,
            ),
            "Critical",
        )

        self.assertEqual(
            calculate_workload_priority(
                20.0,
                5.0,
            ),
            "High",
        )

        self.assertEqual(
            calculate_workload_priority(
                7.0,
                5.0,
            ),
            "Moderate",
        )

        self.assertEqual(
            calculate_workload_priority(
                1.0,
                5.0,
            ),
            "Low",
        )

    def test_workload_metrics_are_preserved(self):
        recommendation = {
            "query_text": (
                "SELECT * FROM orders "
                "WHERE customer_id = 845;"
            ),
            "table_name": "orders",
            "column_name": "customer_id",
            "score": 75,
            "priority": "High",
        }

        enriched = enrich_recommendations_with_workload(
            [recommendation],
            self.analysis,
        )

        result = enriched[0]

        self.assertEqual(
            result["total_executions"],
            2,
        )

        self.assertGreater(
            result["total_execution_time_ms"],
            0,
        )

        self.assertGreater(
            result["total_rows_processed"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
