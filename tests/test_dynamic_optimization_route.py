import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.routes.dynamic_optimization import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestDynamicOptimizationRoute(unittest.TestCase):
    def test_blueprint_endpoint_returns_five_sections(self):
        payload = {
            "raw_sql": "SELECT * FROM products WHERE price > 100",
            "target_schema": "public",
            "enforce_safety_guardrails": True
        }
        response = client.post("/api/v2/optimization/studio/blueprint", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("generated_at", data)
        self.assertIn("sections", data)
        self.assertEqual(len(data["sections"]), 5)
        self.assertEqual(
            [section["section"] for section in data["sections"]],
            [
                "1. Structural Performance Evaluation",
                "2. Matrix Comparison",
                "3. Optimized Structural SQL Code",
                "4. Indexing Blueprint",
                "5. Architectural Recommendations and Trade-offs",
            ],
        )

if __name__ == '__main__':
    unittest.main()
