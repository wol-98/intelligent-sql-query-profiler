import unittest

from api.schemas.structural_optimization import (
    AlternativeType,
    CandidateStatus,
    OptimizationCandidate,
)

from api.services.integrated_candidate_orchestrator import (
    IntegratedCandidateOrchestrator,
)


class MockStructuralEnricher:
    def generate_candidates(self, analysis, original_sql):
        return [
            OptimizationCandidate(
                candidate_id="CAND-0001",
                alternative_type=AlternativeType.SQL_REWRITE,
                status=CandidateStatus.CANDIDATE,
                title="Nested-query SQL rewrite candidate",
                rationale="Nested query identified for later validation.",
                original_sql=original_sql,
                optimized_sql=None,
            )
        ]


class TestIntegratedCandidateOrchestrator(unittest.TestCase):
    def setUp(self):
        self.structural_enricher = MockStructuralEnricher()

        def mock_index_generator(features, metadata):
            return [
                {
                    "table_name": "orders",
                    "column_name": "customer_id",
                    "index_type": "B-tree",
                    "reason": "Filter condition",
                    "source": "customer_id",
                    "candidate_type": "single",
                    "source_type": "where",
                    "column_count": 1,
                },
                {
                    "table_name": "orders",
                    "column_name": "customer_id, status",
                    "index_type": "B-tree",
                    "reason": "Composite filter/order pattern",
                    "source": "customer_id, status",
                    "candidate_type": "composite",
                    "source_type": "where_order",
                    "column_count": 2,
                },
            ]

        self.orchestrator = IntegratedCandidateOrchestrator(
            structural_enricher=self.structural_enricher,
            index_generator=mock_index_generator,
        )

    def test_generate_unified_candidates(self):
        raw_sql = (
            "SELECT * FROM orders "
            "WHERE customer_id = 10 "
            "AND status = 'Pending'"
        )

        candidates = self.orchestrator.generate_unified_candidates(
            raw_sql=raw_sql,
            parsed_metadata={
                "tables": ["orders"],
            },
            features={},
            analysis=object(),
        )

        self.assertEqual(len(candidates), 3)

        structural = candidates[0]
        self.assertEqual(
            structural.alternative_type,
            AlternativeType.SQL_REWRITE,
        )
        self.assertIsNone(structural.optimized_sql)

        index_one = candidates[1]
        self.assertEqual(
            index_one.alternative_type,
            AlternativeType.INDEX,
        )
        self.assertIsNone(index_one.optimized_sql)
        self.assertIn(
            "CREATE INDEX",
            index_one.index_ddl,
        )
        self.assertIn(
            "orders",
            index_one.index_ddl,
        )
        self.assertIn(
            "customer_id",
            index_one.index_ddl,
        )

        index_two = candidates[2]
        self.assertEqual(
            index_two.alternative_type,
            AlternativeType.INDEX,
        )
        self.assertIn(
            "customer_id, status",
            index_two.index_ddl,
        )


if __name__ == "__main__":
    unittest.main()
