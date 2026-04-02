#!/usr/bin/env python3
# run.py  —  Start the Social Analytics API
import uvicorn
from config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=(settings.app_env == "development"),
        log_level="info",
    )
