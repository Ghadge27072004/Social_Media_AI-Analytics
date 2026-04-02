# main.py  (UPDATED — replace your existing main.py with this)
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import ping_db, create_indexes
from config import get_settings

from routes.youtube        import router as youtube_router
from routes.reddit         import router as reddit_router
from routes.dashboard      import router as dashboard_router
from routes.instagram      import router as instagram_router
from routes.twitter        import router as twitter_router
from routes.pinterest      import router as pinterest_router
from routes.ai_routes      import router as ai_router
from routes.realtime       import router as realtime_router
from routes.chatbot_routes import router as chatbot_router   # NEW
from routes.crisis_routes  import router as crisis_router    # NEW
from routes.crew_routes    import router as crew_router      # NEW

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀  Starting Social Analytics API …")
    await ping_db()
    await create_indexes()
    from services.seeder import seed_platform_stats
    await seed_platform_stats()
    from realtime.updater import start_scheduler
    start_scheduler()
    yield
    print("🛑  Shutdown complete.")


app = FastAPI(
    title="Social Media Analytics API",
    description=(
        "AI-powered analytics for YouTube, Reddit, "
        "Instagram, Twitter/X & Pinterest — "
        "with CrewAI Pipeline, AI Chatbot & Crisis Alert System"
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Existing Routers ──────────────────────────────────────────────────────────
app.include_router(youtube_router,   prefix="/api/youtube",   tags=["YouTube"])
app.include_router(reddit_router,    prefix="/api/reddit",    tags=["Reddit"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(instagram_router, prefix="/api/instagram", tags=["Instagram"])
app.include_router(twitter_router,   prefix="/api/twitter",   tags=["Twitter/X"])
app.include_router(pinterest_router, prefix="/api/pinterest", tags=["Pinterest"])
app.include_router(ai_router,        prefix="/api/ai",        tags=["AI Engine"])
app.include_router(realtime_router,  prefix="/api/realtime",  tags=["Realtime"])

# ── New Routers ───────────────────────────────────────────────────────────────
app.include_router(chatbot_router,   prefix="/api/chatbot",   tags=["AI Chatbot"])
app.include_router(crisis_router,    prefix="/api/crisis",    tags=["Crisis Alert"])
app.include_router(crew_router,      prefix="/api/crew",      tags=["CrewAI Pipeline"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "status":  "online",
        "app":     "Social Analytics API",
        "version": "2.0.0",
        "docs":    "/docs",
        "new_features": [
            "POST /api/chatbot/chat",
            "POST /api/crisis/analyze",
            "POST /api/crisis/scan-batch",
            "POST /api/crew/run",
            "POST /api/crew/run-batch",
        ],
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}