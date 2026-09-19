from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.overview import (
    router as overview_router,
)

from api.routes.workloads import router as workloads_router
from api.routes.recommendations import (
    router as recommendations_router,
)


app = FastAPI(
    title=(
        "Intelligent SQL Query Profiler "
        "& Index Optimization Engine"
    ),
    description=(
        "Read-only reporting API for the "
        "M20 Optimization Intelligence Dashboard."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


app.include_router(
    overview_router
)

app.include_router(
    recommendations_router
)
app.include_router(
    workloads_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "m20-reporting-api",
    }
