from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlglot import parse_one

from api.services.alternative_benchmark import AlternativeBenchmarkEngine
from api.services.blueprint_generator import DynamicBlueprintGenerator
from api.services.integrated_candidate_orchestrator import (
    IntegratedCandidateOrchestrator,
)
from api.services.structural_analysis_enricher import (
    StructuralAnalysisEnricher,
)
from api.services.structural_sql_analyzer import StructuralSQLAnalyzer
from api.services.structural_sql_validator import validate_sql
from collector.query_parser import parse_query


router = APIRouter(
    prefix="/api/v2/optimization",
    tags=["M21 Dynamic Optimization"],
)


class DynamicOptimizationRequest(BaseModel):
    raw_sql: str = Field(
        ...,
        description="The user-submitted SQL query",
    )
    target_schema: str = Field(default="public")
    enforce_safety_guardrails: bool = Field(default=True)


@router.post("/studio/blueprint")
async def get_optimization_blueprint(
    request: DynamicOptimizationRequest,
) -> Dict[str, Any]:
    """
    M21.16 endpoint backed by the current M21 validation,
    structural-analysis, candidate-generation, and benchmark contracts.

    The endpoint does not invent SQL rewrites. An alternative is
    benchmarked only when an executable optimized SQL statement is
    actually available.
    """
    try:
        # ---------------------------------------------------------
        # 1. Validate submitted SQL
        # ---------------------------------------------------------
        validation = validate_sql(request.raw_sql)

        if validation.status.value != "VALID":
            raise HTTPException(
                status_code=422,
                detail=validation.model_dump(),
            )

        # ---------------------------------------------------------
        # 2. Parse query metadata using the existing collector
        #    parser used by the index recommendation pipeline.
        # ---------------------------------------------------------
        parsed_metadata = parse_query(request.raw_sql)

        # ---------------------------------------------------------
        # 3. Build SQLGlot AST and structural analysis.
        # ---------------------------------------------------------
        expression = parse_one(
            request.raw_sql,
            dialect="postgres",
        )

        structural_analyzer = StructuralSQLAnalyzer()

        structural_analysis = structural_analyzer.analyze(
            expression,
            query_type=validation.query_type,
            tables=parsed_metadata.get("tables", []),
        )

        # ---------------------------------------------------------
        # 4. Generate unified M21.13 candidates.
        #
        # The current collector index generator accepts execution-plan
        # features but deliberately does not consume them. Therefore
        # the dynamic SQL route supplies an empty feature set until
        # dynamic plan acquisition is wired into the route.
        # ---------------------------------------------------------
        structural_enricher = StructuralAnalysisEnricher()

        orchestrator = IntegratedCandidateOrchestrator(
            structural_enricher=structural_enricher,
        )

        candidates = orchestrator.generate_unified_candidates(
            raw_sql=request.raw_sql,
            parsed_metadata=parsed_metadata,
            features={},
            analysis=structural_analysis,
        )

        # ---------------------------------------------------------
        # 5. Benchmark only genuinely executable alternatives.
        #
        # At the current project stage, structural candidates normally
        # have no executable optimized_sql, so they remain explicitly
        # unbenchmarkable. No raw_sql-vs-raw_sql benchmark is performed.
        #
        # Dry-run evidence is intentionally not forwarded as measured
        # benchmark evidence to the current blueprint generator.
        # ---------------------------------------------------------
        benchmark_result = None

        benchmark_engine = AlternativeBenchmarkEngine(
            dry_run=True,
        )

        for candidate in candidates:
            result = benchmark_engine.benchmark_candidate(
                candidate,
            )

            if result.get("evidence_status") == "MEASURED":
                benchmark_result = result
                break

        # ---------------------------------------------------------
        # 6. Compile the current five-section blueprint.
        # ---------------------------------------------------------
        blueprint_generator = DynamicBlueprintGenerator()

        return blueprint_generator.build_blueprint(
            request.raw_sql,
            parsed_metadata,
            candidates,
            benchmark_result,
            structural_analysis=structural_analysis,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Optimization pipeline failed: "
                f"{exc}"
            ),
        ) from exc
