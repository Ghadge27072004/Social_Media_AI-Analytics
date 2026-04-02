# routes/crew_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ai_engine.crew_pipeline import get_pipeline

router = APIRouter()


class CrewTextRequest(BaseModel):
    text:     str
    platform: Optional[str] = "instagram"
    keyword:  Optional[str] = None


class CrewBatchRequest(BaseModel):
    posts:    List[str]
    platform: Optional[str] = "instagram"
    keyword:  Optional[str] = None


@router.post("/run")
async def run_pipeline(req: CrewTextRequest):
    """Run full 4-agent pipeline on a single text."""
    try:
        pipeline = get_pipeline()
        return pipeline.run(
            text=req.text,
            platform=req.platform,
            keyword=req.keyword,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-batch")
async def run_pipeline_batch(req: CrewBatchRequest):
    """Run full 4-agent pipeline on multiple posts."""
    try:
        pipeline = get_pipeline()
        return pipeline.run(
            posts=req.posts,
            platform=req.platform,
            keyword=req.keyword,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """List all 4 agents in the pipeline."""
    return {
        "agents": [
            {"id": 1, "name": "DataCollectorAgent",    "role": "Social Media Data Harvester",          "emoji": "📡"},
            {"id": 2, "name": "SentimentAnalystAgent", "role": "NLP Sentiment & Emotion Expert",       "emoji": "🧠"},
            {"id": 3, "name": "TrendStrategistAgent",  "role": "Viral Content & Trend Specialist",     "emoji": "📈"},
            {"id": 4, "name": "ReportWriterAgent",     "role": "Insight Report Generator",             "emoji": "📝"},
        ],
        "pipeline": "Sequential — output of each agent feeds next agent",
    }