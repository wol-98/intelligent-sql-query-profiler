import os
import tempfile
import unittest

from collector.workload_analyzer import (
    load_workload,
    analyze_workload,
)


class TestWorkloadAnalyzer(unittest.TestCase):

    def create_temp_workload(self, content):
        file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".sql",
            delete=False,
            encoding="utf-8",
        )

        file.write(content)
        file.close()

        self.addCleanup(
            lambda: os.remove(file.name)
        )

        return file.name

    def test_load_workload(self):
        workload = """
-- Q001: First query
SELECT * FROM orders WHERE status = 'Pending';

-- Q002: Second query
SELECT * FROM orders WHERE status = 'Completed';
"""

        path = self.create_temp_workload(workload)

        result = load_workload(path)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["query_id"], "Q001")
        self.assertEqual(result[1]["query_id"], "Q002")

    def test_identical_structure_groups_together(self):
        workload = """
-- Q001: Pending orders
SELECT * FROM orders WHERE status = 'Pending';

-- Q002: Completed orders
SELECT * FROM orders WHERE status = 'Completed';

-- Q003: Shipped orders
SELECT * FROM orders WHERE status = 'Shipped';

-- Q004: Cancelled orders
SELECT * FROM orders WHERE status = 'Cancelled';
"""

        path = self.create_temp_workload(workload)

        result = analyze_workload(path)

        self.assertEqual(result["total_queries"], 4)
        self.assertEqual(result["unique_fingerprints"], 1)
        self.assertEqual(result["repeated_groups"], 1)
        self.assertEqual(result["largest_group_size"], 4)

        group = result["groups"][0]

        self.assertEqual(group["frequency"], 4)
        self.assertEqual(
            group["query_ids"],
            ["Q001", "Q002", "Q003", "Q004"],
        )

    def test_numeric_variations_group_together(self):
        workload = """
-- Q001: Customer 100
SELECT * FROM orders WHERE customer_id = 100;

-- Q002: Customer 845
SELECT * FROM orders WHERE customer_id = 845;

-- Q003: Customer 9999
SELECT * FROM orders WHERE customer_id = 9999;
"""

        path = self.create_temp_workload(workload)

        result = analyze_workload(path)

        self.assertEqual(result["total_queries"], 3)
        self.assertEqual(result["unique_fingerprints"], 1)
        self.assertEqual(result["repeated_groups"], 1)
        self.assertEqual(result["largest_group_size"], 3)

    def test_different_structures_remain_separate(self):
        workload = """
-- Q001: Customer filter
SELECT * FROM orders WHERE customer_id = 845;

-- Q002: Status filter
SELECT * FROM orders WHERE status = 'Completed';

-- Q003: Customer and status filter
SELECT * FROM orders
WHERE customer_id = 845
AND status = 'Completed';
"""

        path = self.create_temp_workload(workload)

        result = analyze_workload(path)

        self.assertEqual(result["total_queries"], 3)
        self.assertEqual(result["unique_fingerprints"], 3)
        self.assertEqual(result["repeated_groups"], 0)

    def test_official_workload(self):
        workload_path = "database/workload.sql"

        result = analyze_workload(workload_path)

        self.assertEqual(result["total_queries"], 15)
        self.assertEqual(result["unique_fingerprints"], 15)
        self.assertEqual(result["repeated_groups"], 0)
        self.assertEqual(result["largest_group_size"], 1)


if __name__ == "__main__":
    unittest.main()
