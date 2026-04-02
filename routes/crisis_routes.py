# routes/crisis_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ai_engine.crisis_alert import analyze_crisis, batch_crisis_scan
from db import alerts_collection

router = APIRouter()


class CrisisTextRequest(BaseModel):
    text: str


class CrisisBatchRequest(BaseModel):
    posts:           List[str]
    threshold_level: Optional[int] = 1


@router.post("/analyze")
async def analyze_crisis(req: CrisisTextRequest):
    try:
        return analyze_crisis(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan-batch")
async def scan_batch(req: CrisisBatchRequest):
    try:
        return batch_crisis_scan(req.posts, req.threshold_level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def crisis_history(limit: int = 20):
    try:
        cursor  = alerts_collection.find({}, {"_id": 0}).sort("saved_at", -1).limit(limit)
        results = await cursor.to_list(length=limit)
        return {"alerts": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))