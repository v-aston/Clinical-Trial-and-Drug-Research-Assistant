from fastapi import FastAPI
from app.core.config import settings
from app.api.ingest import router as ingest_router
from app.api.query import router as query_router
from app.api.health import router as health_router

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

app.include_router(ingest_router, prefix="/api/v1", tags=["ingestion"])
app.include_router(query_router, prefix="/api/v1", tags=["query"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])
