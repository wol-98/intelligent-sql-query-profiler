from collector.composite_order_evaluator import evaluate_order_experiment


experiment = {
    "recommendation_id": 35,
    "query_id": 16,
    "fingerprint": None,
    "table_name": "customers",
    "candidate_type": "composite",
    "source_type": "mixed",
    "column_count": 3,
    "original_columns": [
        "segment",
        "customer_id",
        "name",
    ],
    "alternative_columns": [
        "name",
        "customer_id",
        "segment",
    ],
    "experiment_type": "column_order",
}


query = """
SELECT
    c.customer_id,
    c.name,
    COUNT(o.order_id) AS number_of_orders,
    SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
WHERE c.segment = 'Corporate'
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 20;
"""


result = evaluate_order_experiment(
    experiment=experiment,
    query=query,
    iterations=10,
    warmup_runs=2,
)


print("\n" + "=" * 70)
print("M16.2 — RECOMMENDATION 35")
print("=" * 70)

print(f"\nRecommendation ID: {result['recommendation_id']}")
print(f"Table:              {result['table_name']}")
print(f"Experiment type:    {result['experiment_type']}")

print("\nColumn Orders")
print("-" * 70)
print("Original:    " + ", ".join(result["original_columns"]))
print("Alternative: " + ", ".join(result["alternative_columns"]))

print("\nExecution Time")
print("-" * 70)
print(f"Baseline:     {result['baseline']['execution_time_ms']:.3f} ms")
print(f"Original:     {result['original']['execution_time_ms']:.3f} ms")
print(f"Alternative:  {result['alternative']['execution_time_ms']:.3f} ms")

print("\nImprovement")
print("-" * 70)
print(
    f"Original improvement:    "
    f"{result['original_improvement_percentage']:.2f}%"
)
print(
    f"Alternative improvement: "
    f"{result['alternative_improvement_percentage']:.2f}%"
)
print(
    f"Order effect:            "
    f"{result['improvement_difference_percentage_points']:.2f} "
    f"percentage points"
)

print("\nIndex Usage")
print("-" * 70)
print(f"Original index used:     {result['original']['index_used']}")
print(f"Alternative index used:  {result['alternative']['index_used']}")

print("\nRows Preserved")
print("-" * 70)
print(f"Original:     {result['original_rows_preserved']}")
print(f"Alternative:  {result['alternative_rows_preserved']}")

print("\nPlan Changed")
print("-" * 70)
print(f"Original:     {result['original_plan_changed']}")
print(f"Alternative:  {result['alternative_plan_changed']}")

print("\nBuffer Usage")
print("-" * 70)

print("Baseline:")
print(
    f"  Shared hits:   "
    f"{result['baseline']['average_shared_hit_blocks']}"
)
print(
    f"  Shared reads:  "
    f"{result['baseline']['average_shared_read_blocks']}"
)

print("\nOriginal:")
print(
    f"  Shared hits:   "
    f"{result['original']['average_shared_hit_blocks']}"
)
print(
    f"  Shared reads:  "
    f"{result['original']['average_shared_read_blocks']}"
)

print("\nAlternative:")
print(
    f"  Shared hits:   "
    f"{result['alternative']['average_shared_hit_blocks']}"
)
print(
    f"  Shared reads:  "
    f"{result['alternative']['average_shared_read_blocks']}"
)

print("\n" + "=" * 70)
print("EXPERIMENT COMPLETE")
print("=" * 70)
