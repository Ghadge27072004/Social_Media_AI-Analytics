# routes/ai_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ai_engine.sentiment      import analyze_sentiment, batch_analyze as batch_sentiment
from ai_engine.emotion        import detect_emotion, batch_detect as batch_emotion
from ai_engine.toxicity       import detect_toxicity, batch_detect as batch_toxicity
from ai_engine.hinglish_nlp   import analyze_hinglish, batch_analyze as batch_hinglish
from ai_engine.trend_forecasting import forecast_trend, forecast_viral_potential
from ai_engine.clustering     import cluster_audience

router = APIRouter()


# ── Request models ────────────────────────────────────────────────────────────

class TextRequest(BaseModel):
    text: str

class BatchRequest(BaseModel):
    texts: List[str]

class ForecastRequest(BaseModel):
    keyword: str
    historical_values: Optional[List[float]] = None
    forecast_days: int = 7

class ViralRequest(BaseModel):
    title: str
    description: Optional[str] = ""

class ClusterRequest(BaseModel):
    total_followers: int = 10000
    n_clusters: int = 4


# ── Sentiment ─────────────────────────────────────────────────────────────────

@router.post("/sentiment")
async def sentiment(req: TextRequest):
    try:
        return analyze_sentiment(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment/batch")
async def sentiment_batch(req: BatchRequest):
    try:
        return {"results": batch_sentiment(req.texts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Emotion ───────────────────────────────────────────────────────────────────

@router.post("/emotion")
async def emotion(req: TextRequest):
    try:
        return detect_emotion(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emotion/batch")
async def emotion_batch(req: BatchRequest):
    try:
        return {"results": batch_emotion(req.texts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Toxicity ──────────────────────────────────────────────────────────────────

@router.post("/toxicity")
async def toxicity(req: TextRequest):
    try:
        return detect_toxicity(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/toxicity/batch")
async def toxicity_batch(req: BatchRequest):
    try:
        return {"results": batch_toxicity(req.texts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Hinglish NLP ──────────────────────────────────────────────────────────────

@router.post("/hinglish")
async def hinglish(req: TextRequest):
    try:
        return analyze_hinglish(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hinglish/batch")
async def hinglish_batch(req: BatchRequest):
    try:
        return {"results": batch_hinglish(req.texts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Trend Forecasting ─────────────────────────────────────────────────────────

@router.post("/forecast")
async def forecast(req: ForecastRequest):
    try:
        return forecast_trend(req.keyword, req.historical_values, req.forecast_days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/viral-score")
async def viral_score(req: ViralRequest):
    try:
        return forecast_viral_potential(req.title, req.description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Audience Clustering ───────────────────────────────────────────────────────

@router.post("/cluster")
async def cluster(req: ClusterRequest):
    try:
        return cluster_audience(req.total_followers, req.n_clusters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Combined Full Analysis ────────────────────────────────────────────────────

@router.post("/analyze-full")
async def full_analysis(req: TextRequest):
    """Run all AI models on a single piece of text — one API call."""
    try:
        sentiment_result = analyze_sentiment(req.text)
        emotion_result   = detect_emotion(req.text)
        toxicity_result  = detect_toxicity(req.text)
        hinglish_result  = analyze_hinglish(req.text)
        return {
            "text":      req.text[:200],
            "sentiment": sentiment_result,
            "emotion":   emotion_result,
            "toxicity":  toxicity_result,
            "hinglish":  hinglish_result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
