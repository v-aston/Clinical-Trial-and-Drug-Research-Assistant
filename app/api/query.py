from fastapi import APIRouter, HTTPException
from app.db.schemas import QueryRequest, QueryResponse
from app.services.query_service import QueryService

router = APIRouter(tags=["query"])
service = QueryService()

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        result = service.answer_question(
            question=request.question,
            top_k=request.top_k,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))