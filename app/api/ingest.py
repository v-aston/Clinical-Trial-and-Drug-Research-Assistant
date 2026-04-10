from fastapi import APIRouter, HTTPException
from app.db.schemas import IngestRequest, IngestResponse
from app.services.ingest_service import IngestService

router = APIRouter(tags=["ingestion"])
service = IngestService()

@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    try:
        return service.ingest(
            source_type=request.source_type,
            query=request.query,
            max_documents=request.max_documents,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))