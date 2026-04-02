# services/youtube_service.py
import httpx
from datetime import datetime
from config import get_settings
from db import posts_collection, platform_stats

settings = get_settings()
YT_BASE = "https://www.googleapis.com/youtube/v3"


async def fetch_youtube_videos(query: str, max_results: int = 10) -> list:
    """Search YouTube and return video details + store in MongoDB."""
    params = {
        "part": "snippet",
        "q": query,
        "maxResults": max_results,
        "type": "video",
        "order": "relevance",
        "key": settings.youtube_api_key,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{YT_BASE}/search", params=params)
        resp.raise_for_status()
        data = resp.json()

    video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
    if not video_ids:
        return []

    # Fetch stats for all videos in one call
    stats_map = await _fetch_video_stats_batch(video_ids)

    results = []
    for item in data.get("items", []):
        vid_id = item["id"]["videoId"]
        snippet = item["snippet"]
        stats = stats_map.get(vid_id, {})

        views       = int(stats.get("viewCount", 0))
        likes       = int(stats.get("likeCount", 0))
        comments    = int(stats.get("commentCount", 0))
        eng_score   = round((likes + comments * 2) / max(views, 1) * 100, 4)

        doc = {
            "post_id":          vid_id,
            "platform":         "youtube",
            "title":            snippet.get("title", ""),
            "description":      snippet.get("description", "")[:500],
            "channel":          snippet.get("channelTitle", ""),
            "thumbnail":        snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "published_at":     snippet.get("publishedAt", ""),
            "views":            views,
            "likes":            likes,
            "comments":         comments,
            "engagement_score": eng_score,
            "url":              f"https://youtube.com/watch?v={vid_id}",
            "fetched_at":       datetime.utcnow(),
            "query":            query,
        }
        results.append(doc)
        # Upsert so we don't duplicate
        await posts_collection.update_one(
            {"post_id": vid_id, "platform": "youtube"},
            {"$set": doc},
            upsert=True,
        )

    return results


async def _fetch_video_stats_batch(video_ids: list) -> dict:
    ids_str = ",".join(video_ids)
    params = {
        "part": "statistics",
        "id": ids_str,
        "key": settings.youtube_api_key,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{YT_BASE}/videos", params=params)
        resp.raise_for_status()
        data = resp.json()
    return {item["id"]: item.get("statistics", {}) for item in data.get("items", [])}


async def fetch_video_stats(video_id: str) -> dict:
    stats_map = await _fetch_video_stats_batch([video_id])
    return stats_map.get(video_id, {})


async def fetch_trending_youtube(region_code: str = "IN") -> list:
    """Fetch YouTube trending videos for a region."""
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "maxResults": 20,
        "key": settings.youtube_api_key,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{YT_BASE}/videos", params=params)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("items", []):
        snippet = item["snippet"]
        stats   = item.get("statistics", {})
        views   = int(stats.get("viewCount", 0))
        likes   = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        doc = {
            "post_id":          item["id"],
            "platform":         "youtube",
            "title":            snippet.get("title", ""),
            "channel":          snippet.get("channelTitle", ""),
            "thumbnail":        snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "published_at":     snippet.get("publishedAt", ""),
            "views":            views,
            "likes":            likes,
            "comments":         comments,
            "engagement_score": round((likes + comments * 2) / max(views, 1) * 100, 4),
            "url":              f"https://youtube.com/watch?v={item['id']}",
            "fetched_at":       datetime.utcnow(),
            "is_trending":      True,
            "region":           region_code,
        }
        results.append(doc)
        await posts_collection.update_one(
            {"post_id": item["id"], "platform": "youtube"},
            {"$set": doc},
            upsert=True,
        )
    return results
