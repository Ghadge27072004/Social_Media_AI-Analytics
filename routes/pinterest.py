# routes/pinterest.py
from fastapi import APIRouter, HTTPException, Query
from services.pinterest_scraper import get_pinterest_trends, get_pinterest_board_analysis

router = APIRouter()


@router.get("/trends")
async def pinterest_trends(keyword: str = Query(...)):
    try:
        data = await get_pinterest_trends(keyword)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/boards")
async def pinterest_boards(keyword: str = Query(...)):
    try:
        data = await get_pinterest_board_analysis(keyword)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
