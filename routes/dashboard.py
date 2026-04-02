# routes/dashboard.py
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from db import posts_collection, platform_stats

router = APIRouter()


@router.get("/summary")
async def get_summary():
    """Main dashboard summary — all platforms combined."""
    try:
        total_posts  = await posts_collection.count_documents({})
        since        = datetime.utcnow() - timedelta(hours=24)
        recent_posts = await posts_collection.count_documents({"fetched_at": {"$gte": since}})

        # Per-platform breakdown
        pipeline = [{"$group": {"_id": "$platform", "count": {"$sum": 1}}}]
        by_platform = {}
        async for doc in posts_collection.aggregate(pipeline):
            by_platform[doc["_id"]] = doc["count"]

        # Pull live stats for every platform
        stats_list = []
        async for doc in platform_stats.find({}, {"_id": 0}):
            # Convert datetime to string for JSON
            if "last_updated" in doc and isinstance(doc["last_updated"], datetime):
                doc["last_updated"] = doc["last_updated"].isoformat()
            stats_list.append(doc)

        return {
            "total_posts":    total_posts,
            "posts_last_24h": recent_posts,
            "by_platform":    by_platform,
            "platform_stats": stats_list,
            "last_updated":   datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending(limit: int = Query(10, ge=1, le=50)):
    """Top trending posts by engagement score."""
    try:
        cursor = posts_collection.find({}, {"_id": 0}).sort("engagement_score", -1).limit(limit)
        posts  = []
        async for post in cursor:
            if "fetched_at" in post and isinstance(post["fetched_at"], datetime):
                post["fetched_at"] = post["fetched_at"].isoformat()
            posts.append(post)
        return {"trending": posts, "count": len(posts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platform/{platform}")
async def get_platform_stats(platform: str):
    """Live stats for a single platform."""
    try:
        doc = await platform_stats.find_one({"platform": platform}, {"_id": 0})
        if not doc:
            raise HTTPException(status_code=404, detail=f"No stats for platform: {platform}")
        if "last_updated" in doc and isinstance(doc["last_updated"], datetime):
            doc["last_updated"] = doc["last_updated"].isoformat()
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-posts")
async def get_recent_posts(limit: int = Query(20), platform: str = Query(None)):
    """Recent posts, optionally filtered by platform."""
    try:
        query  = {"platform": platform} if platform else {}
        cursor = posts_collection.find(query, {"_id": 0}).sort("fetched_at", -1).limit(limit)
        posts  = []
        async for post in cursor:
            if "fetched_at" in post and isinstance(post["fetched_at"], datetime):
                post["fetched_at"] = post["fetched_at"].isoformat()
            posts.append(post)
        return {"posts": posts, "count": len(posts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
