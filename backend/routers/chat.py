import os
import logging
import re
from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, validator
from backend.services.ai_service import run_ai_query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

# ──────────────────────────────────────────────
# API Key Authentication
# ──────────────────────────────────────────────
API_KEY = os.getenv("API_SECRET_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(key: str = Security(api_key_header)):
    if not API_KEY:
        logger.warning("API_SECRET_KEY not set in environment — endpoint is unprotected")
        return  # allows app to still run in dev if key not set
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return key


class ChatRequest(BaseModel):
    question: str
    conversation_history: list = []

    @validator("question")
    def question_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty")
        if len(v) > 2000:
            raise ValueError("Question too long (max 2000 chars)")
        return v


class ChatResponse(BaseModel):
    answer: str
    tool_calls: list
    sources: list
    conversation: list


def _clean_answer(text: str) -> str:
    """
    Remove only clearly accidental artefacts (raw JSON blocks, fenced code).
    Do NOT strip normal prose — the old regex was eating real answer content.
    """
    # Remove fenced code blocks (```...```)
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove bare JSON objects that look like tool-call leakage {"name": ...}
    text = re.sub(r'\{\s*"name"\s*:[\s\S]*?\}', "", text)
    return text.strip()


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest, _=Depends(verify_api_key)):
    try:
        logger.info(f"Chat question: {req.question[:80]}")
        result = run_ai_query(req.question, req.conversation_history)
        result["answer"] = _clean_answer(result["answer"])
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))