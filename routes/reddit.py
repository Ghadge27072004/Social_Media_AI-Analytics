# routes/reddit.py
from fastapi import APIRouter, HTTPException, Query
from services.reddit_service import fetch_reddit_posts, fetch_reddit_comments, search_reddit

router = APIRouter()


@router.get("/posts")
async def get_reddit_posts(
    subreddit: str = Query("india"),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("hot"),
):
    try:
        posts = await fetch_reddit_posts(subreddit, limit, sort)
        return {"subreddit": subreddit, "sort": sort, "posts": posts, "source": "Reddit API ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comments/{post_id}")
async def get_comments(post_id: str, limit: int = Query(20, ge=1, le=100)):
    try:
        comments = await fetch_reddit_comments(post_id, limit)
        return {"post_id": post_id, "comments": comments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search(query: str = Query(...), limit: int = Query(20)):
    try:
        results = await search_reddit(query, limit)
        return {"query": query, "results": results, "source": "Reddit API ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
