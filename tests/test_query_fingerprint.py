import unittest
from collector.query_parser import QueryFingerprinter, parse_query

class TestQueryFingerprint(unittest.TestCase):
    
    def test_normalize_string_literals(self):
        """Test that different string literals produce the same template."""
        q1 = "SELECT * FROM orders WHERE status = 'Pending';"
        q2 = "SELECT * FROM orders WHERE status = 'Completed';"
        
        norm1 = QueryFingerprinter.normalize_query(q1)
        norm2 = QueryFingerprinter.normalize_query(q2)
        
        self.assertEqual(norm1, "SELECT * FROM ORDERS WHERE STATUS = '?';")
        self.assertEqual(norm1, norm2)

    def test_normalize_numeric_literals(self):
        """Test that different numeric literals produce the same template."""
        q1 = "SELECT * FROM products WHERE price > 100"
        q2 = "SELECT * FROM products WHERE price > 500.50"
        
        norm1 = QueryFingerprinter.normalize_query(q1)
        norm2 = QueryFingerprinter.normalize_query(q2)
        
        self.assertEqual(norm1, "SELECT * FROM PRODUCTS WHERE PRICE > ?")
        self.assertEqual(norm1, norm2)

    def test_generate_fingerprint_match(self):
        """Test that matching structures yield the exact same SHA-256 hash."""
        q1 = "SELECT customer_id FROM customers WHERE segment = 'Retail' AND city = 'Mumbai';"
        q2 = "SELECT customer_id FROM customers WHERE segment = 'Corporate' AND city = 'Delhi';"
        
        hash1, _ = QueryFingerprinter.generate_fingerprint(q1)
        hash2, _ = QueryFingerprinter.generate_fingerprint(q2)
        
        self.assertEqual(hash1, hash2)

    def test_parse_query_integration(self):
        """Test that the main parser successfully includes the new fingerprint metadata."""
        q = "SELECT * FROM orders WHERE total_amount > 1000;"
        metadata = parse_query(q)
        
        self.assertIn("fingerprint", metadata)
        self.assertIn("normalized_template", metadata)
        self.assertEqual(metadata["normalized_template"], "SELECT * FROM ORDERS WHERE TOTAL_AMOUNT > ?;")

if __name__ == '__main__':
    unittest.main()
