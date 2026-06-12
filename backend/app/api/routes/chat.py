from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.embedder import get_model
from app.services.vector_store import query_similar
from app.services.llm_service import chat_with_codebase

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        model = get_model()
        hits = query_similar(request.question, model, n_results=5)

        if not hits:
            raise HTTPException(status_code=400, detail="No codebase loaded. Run /review first.")

        result = chat_with_codebase(request.question, hits)
        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))