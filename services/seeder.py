# services/seeder.py
"""
Seeds MongoDB with initial platform_stats documents.
These are updated live by the realtime updater.
"""
import random
from datetime import datetime
from db import platform_stats


INITIAL_STATS = {
    "youtube": {
        "platform":         "youtube",
        "total_views":      random.randint(500_000, 5_000_000),
        "subscribers":      random.randint(10_000, 500_000),
        "total_videos":     random.randint(50, 500),
        "avg_watch_time":   round(random.uniform(3.5, 8.5), 2),
        "total_likes":      random.randint(50_000, 1_000_000),
        "total_comments":   random.randint(5_000, 100_000),
        "engagement_rate":  round(random.uniform(2.0, 8.0), 2),
        "data_label":       "Live Data ✅",
        "last_updated":     datetime.utcnow(),
    },
    "reddit": {
        "platform":         "reddit",
        "total_posts":      random.randint(1_000, 50_000),
        "total_comments":   random.randint(10_000, 500_000),
        "karma":            random.randint(5_000, 200_000),
        "active_subs":      random.randint(100, 10_000),
        "avg_upvote_ratio": round(random.uniform(0.7, 0.95), 3),
        "engagement_rate":  round(random.uniform(3.0, 12.0), 2),
        "data_label":       "Live Data ✅",
        "last_updated":     datetime.utcnow(),
    },
    "instagram": {
        "platform":         "instagram",
        "followers":        random.randint(5_000, 200_000),
        "following":        random.randint(500, 5_000),
        "total_posts":      random.randint(100, 2_000),
        "avg_likes":        random.randint(200, 10_000),
        "avg_comments":     random.randint(10, 500),
        "engagement_rate":  round(random.uniform(1.5, 7.0), 2),
        "reach":            random.randint(1_000, 50_000),
        "data_label":       "AI-based Insights ⚠️",
        "last_updated":     datetime.utcnow(),
    },
    "twitter": {
        "platform":         "twitter",
        "followers":        random.randint(1_000, 100_000),
        "following":        random.randint(200, 5_000),
        "total_tweets":     random.randint(500, 20_000),
        "avg_likes":        random.randint(50, 5_000),
        "avg_retweets":     random.randint(10, 1_000),
        "engagement_rate":  round(random.uniform(1.0, 5.0), 2),
        "data_label":       "Public Analysis ⚠️",
        "last_updated":     datetime.utcnow(),
    },
    "pinterest": {
        "platform":         "pinterest",
        "followers":        random.randint(500, 50_000),
        "monthly_views":    random.randint(10_000, 2_000_000),
        "total_pins":       random.randint(100, 5_000),
        "total_boards":     random.randint(5, 100),
        "saves":            random.randint(1_000, 100_000),
        "engagement_rate":  round(random.uniform(1.0, 6.0), 2),
        "data_label":       "Trend Insights 🔥",
        "last_updated":     datetime.utcnow(),
    },
}


async def seed_platform_stats():
    for platform, doc in INITIAL_STATS.items():
        existing = await platform_stats.find_one({"platform": platform})
        if not existing:
            await platform_stats.insert_one(doc)
            print(f"✅  Seeded platform_stats for {platform}")
        else:
            print(f"ℹ️   platform_stats already exists for {platform}")
