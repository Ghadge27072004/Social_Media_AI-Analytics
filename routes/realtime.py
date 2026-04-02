# routes/realtime.py
"""
Server-Sent Events (SSE) endpoint.
Flutter can listen to /api/realtime/stream and receive live stat updates
without polling — no WebSocket needed.
"""
import asyncio
import json
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from db import platform_stats

router = APIRouter()


async def _stat_generator():
    """Yields platform stats as SSE every 5 seconds."""
    while True:
        try:
            stats = []
            async for doc in platform_stats.find({}, {"_id": 0}):
                if "last_updated" in doc and isinstance(doc["last_updated"], datetime):
                    doc["last_updated"] = doc["last_updated"].isoformat()
                stats.append(doc)

            payload = json.dumps({
                "event":        "stats_update",
                "data":         stats,
                "timestamp":    datetime.utcnow().isoformat(),
            })
            yield f"data: {payload}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        await asyncio.sleep(5)


@router.get("/stream")
async def realtime_stream():
    """
    SSE stream — Flutter connects once, receives updates every 5 sec.
    Usage: EventSource("http://localhost:8000/api/realtime/stream")
    """
    return StreamingResponse(
        _stat_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/snapshot")
async def snapshot():
    """One-shot snapshot of current platform stats (for polling fallback)."""
    stats = []
    async for doc in platform_stats.find({}, {"_id": 0}):
        if "last_updated" in doc and isinstance(doc["last_updated"], datetime):
            doc["last_updated"] = doc["last_updated"].isoformat()
        stats.append(doc)
    return {"stats": stats, "timestamp": datetime.utcnow().isoformat()}
