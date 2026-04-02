# realtime/updater.py

import random
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db import platform_stats, posts_collection
from config import get_settings

settings = get_settings()
_scheduler = AsyncIOScheduler(timezone="UTC")


# ── Micro-update (every 5 sec) ───────────────────────────────────────────────

async def _micro_update():
    updates = {
        "youtube": {
            "total_views": random.randint(50, 500),
            "subscribers": random.randint(0, 5),
            "total_likes": random.randint(5, 50),
            "total_comments": random.randint(1, 10),
        },
        "reddit": {
            "total_posts": random.randint(0, 3),
            "total_comments": random.randint(2, 20),
            "karma": random.randint(10, 100),
        },
        "instagram": {
            "followers": random.randint(1, 10),
            "avg_likes": random.randint(-5, 15),
        },
        "twitter": {
            "followers": random.randint(0, 8),
            "total_tweets": random.randint(0, 5),
        },
        "pinterest": {
            "monthly_views": random.randint(100, 1000),
            "saves": random.randint(5, 50),
        },
    }

    ts = datetime.utcnow()

    for platform, increments in updates.items():
        await platform_stats.update_one(
            {"platform": platform},
            {
                "$inc": increments,
                "$set": {
                    "last_updated": ts,
                    "engagement_rate": round(random.uniform(1.5, 9.0), 2),
                },
            },
            upsert=True,
        )


# ── Macro-update (every 5 min) ───────────────────────────────────────────────

async def _macro_update():
    try:
        if settings.youtube_api_key:
            from services.youtube_service import fetch_trending_youtube
            await fetch_trending_youtube("IN")
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] 🔄 YouTube refreshed")
    except Exception as e:
        print(f"[Macro] YouTube error: {e}")

    try:
        if settings.reddit_client_id:
            from services.reddit_service import fetch_reddit_posts
            await fetch_reddit_posts("india", 15, "hot")
            await fetch_reddit_posts("technology", 15, "hot")
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] 🔄 Reddit refreshed")
    except Exception as e:
        print(f"[Macro] Reddit error: {e}")


# ── Engagement update (every 30 sec) ─────────────────────────────────────────

async def _recalculate_engagement():
    cursor = posts_collection.find({}).sort("fetched_at", -1).limit(50)

    async for post in cursor:
        delta = random.uniform(-0.05, 0.15)
        new_score = max(0, post.get("engagement_score", 0) + delta)

        await posts_collection.update_one(
            {"_id": post["_id"]},
            {"$set": {"engagement_score": round(new_score, 4)}},
        )


# ── Scheduler start ─────────────────────────────────────────────────────────

def start_scheduler():
    if _scheduler.running:
        return

    _scheduler.add_job(_micro_update, IntervalTrigger(seconds=5), id="micro_update")
    _scheduler.add_job(_macro_update, IntervalTrigger(minutes=5), id="macro_update")
    _scheduler.add_job(_recalculate_engagement, IntervalTrigger(seconds=30), id="engagement_recalc")

    _scheduler.start()
    print("✅ Realtime scheduler started (no errors now 😎)")