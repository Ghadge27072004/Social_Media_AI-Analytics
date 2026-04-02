# routes/chatbot_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ai_engine.chatbot import (
    chat as do_chat,
    get_or_create_session,
    clear_session as do_clear_session
)

router = APIRouter()


class ChatRequest(BaseModel):
    message:    str
    session_id: Optional[str] = "default"
    platform:   Optional[str] = "general"


class ClearSessionRequest(BaseModel):
    session_id: str


@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        return do_chat(req.message, req.session_id, req.platform)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    try:
        session = get_or_create_session(session_id)
        return session.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    try:
        do_clear_session(session_id)
        return {"message": f"Session {session_id} cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))