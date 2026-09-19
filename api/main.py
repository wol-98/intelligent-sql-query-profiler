from fastapi import FastAPI

from api.routes.overview import (
    router as overview_router,
)

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


app.include_router(
    overview_router
)

app.include_router(
    recommendations_router
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "m20-reporting-api",
    }
