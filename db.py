# db.py
import motor.motor_asyncio
from config import get_settings

settings = get_settings()

client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
db = client[settings.db_name]

# ── Collections ──────────────────────────────────────────────────────────────
posts_collection        = db["posts"]
users_collection        = db["users"]
analytics_collection    = db["analytics"]
trends_collection       = db["trends"]
alerts_collection       = db["alerts"]
reports_collection      = db["reports"]
competitors_collection  = db["competitors"]
platform_stats          = db["platform_stats"]


async def ping_db():
    try:
        await client.admin.command("ping")
        print("✅  MongoDB connected successfully")
    except Exception as exc:
        print(f"❌  MongoDB connection failed: {exc}")
        raise exc


async def create_indexes():
    """Run once on startup to ensure fast queries."""
    await posts_collection.create_index([("platform", 1), ("fetched_at", -1)])
    await posts_collection.create_index([("engagement_score", -1)])
    await posts_collection.create_index([("post_id", 1)], unique=True, sparse=True)
    await trends_collection.create_index([("keyword", 1), ("platform", 1)])
    await platform_stats.create_index([("platform", 1)], unique=True)
    print("✅  MongoDB indexes ensured")
