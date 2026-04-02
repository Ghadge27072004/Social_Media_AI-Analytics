# routes/youtube.py
from fastapi import APIRouter, HTTPException, Query
from services.youtube_service import (
    fetch_youtube_videos,
    fetch_trending_youtube,
    fetch_video_stats,
)

router = APIRouter()


@router.get("/search")
async def search_youtube(
    query: str = Query(..., description="Search keyword"),
    max_results: int = Query(10, ge=1, le=50),
):
    try:
        videos = await fetch_youtube_videos(query, max_results)
        return {"query": query, "results": videos, "count": len(videos), "source": "YouTube API ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending(region: str = Query("IN")):
    try:
        videos = await fetch_trending_youtube(region)
        return {"region": region, "results": videos, "count": len(videos), "source": "YouTube API ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{video_id}")
async def get_video_stats(video_id: str):
    try:
        stats = await fetch_video_stats(video_id)
        return {"video_id": video_id, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
