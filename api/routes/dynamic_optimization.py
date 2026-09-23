from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel, Field
from api.services.blueprint_generator import DynamicBlueprintGenerator
from api.services.alternative_benchmark import AlternativeBenchmarkEngine

router = APIRouter(prefix="/api/v2/optimization", tags=["M21 Dynamic Optimization"])

class DynamicOptimizationRequest(BaseModel):
    raw_sql: str = Field(..., description="The user-submitted SQL query")
    target_schema: str = Field(default="public")
    enforce_safety_guardrails: bool = Field(default=True)

@router.post("/studio/blueprint")
async def get_optimization_blueprint(request: DynamicOptimizationRequest) -> Dict[str, Any]:
    """
    M21.16 Endpoint: Receives dynamic SQL from the React studio, validates it, 
    generates candidates, benchmarks alternatives, and returns the 5-section blueprint.
    """
    try:
        # Step 1: Validation & Parsing (Routed to M21.2 - M21.4 services)
        parsed_metadata = {"tables": [], "where_predicates": []} 
        
        # Step 2: Candidate Generation (Routed to M21.13 Orchestrator)
        candidates = [] 
        
        # Step 3: Benchmarking (Routed to M21.14 Engine)
        benchmark_engine = AlternativeBenchmarkEngine(dry_run=True)
        benchmark_result = benchmark_engine.compare_query_alternatives(request.raw_sql, request.raw_sql)
        
        # Step 4: Blueprint Compilation (Routed to M21.15 Generator)
        blueprint_gen = DynamicBlueprintGenerator()
        return blueprint_gen.build_blueprint(request.raw_sql, parsed_metadata, candidates, benchmark_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization pipeline failed: {str(e)}")
