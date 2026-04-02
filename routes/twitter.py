# routes/twitter.py
from fastapi import APIRouter, HTTPException, Query
from services.twitter_scraper import fetch_tweets, get_twitter_trends

router = APIRouter()


@router.get("/search")
async def search_tweets(
    query: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
):
    try:
        tweets = await fetch_tweets(query, limit)
        return {"query": query, "tweets": tweets, "count": len(tweets), "source": "Public Analysis ⚠️"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def twitter_trends(region: str = Query("India")):
    try:
        trends = await get_twitter_trends(region)
        return {"region": region, "trends": trends, "source": "Public Analysis ⚠️"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
