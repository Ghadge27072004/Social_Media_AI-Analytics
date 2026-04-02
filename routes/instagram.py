# routes/instagram.py
from fastapi import APIRouter, HTTPException, Query
from services.instagram_scraper import get_instagram_profile, get_instagram_insights

router = APIRouter()


@router.get("/profile")
async def instagram_profile(username: str = Query(...)):
    try:
        data = await get_instagram_profile(username)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def instagram_insights(username: str = Query(...)):
    try:
        data = await get_instagram_insights(username)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
