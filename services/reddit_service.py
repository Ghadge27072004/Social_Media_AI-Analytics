# services/reddit_service.py
import asyncio
import praw
from datetime import datetime
from config import get_settings
from db import posts_collection

settings = get_settings()


def _get_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent,
    )


async def fetch_reddit_posts(subreddit: str, limit: int = 20, sort: str = "hot") -> list:
    """Fetch posts from a subreddit (runs sync praw in executor)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_fetch_posts, subreddit, limit, sort)


def _sync_fetch_posts(subreddit: str, limit: int, sort: str) -> list:
    reddit  = _get_reddit_client()
    sub     = reddit.subreddit(subreddit)
    getter  = {"hot": sub.hot, "new": sub.new, "top": sub.top, "rising": sub.rising}.get(sort, sub.hot)
    results = []

    for post in getter(limit=limit):
        if post.stickied:
            continue
        eng_score = round(
            (post.score + post.num_comments * 3) / max(post.upvote_ratio * 100, 1), 4
        )
        doc = {
            "post_id":          post.id,
            "platform":         "reddit",
            "title":            post.title,
            "text":             post.selftext[:1000] if post.selftext else "",
            "author":           str(post.author) if post.author else "[deleted]",
            "subreddit":        subreddit,
            "score":            post.score,
            "upvote_ratio":     post.upvote_ratio,
            "num_comments":     post.num_comments,
            "engagement_score": eng_score,
            "url":              f"https://reddit.com{post.permalink}",
            "thumbnail":        post.thumbnail if post.thumbnail.startswith("http") else "",
            "is_video":         post.is_video,
            "flair":            post.link_flair_text or "",
            "fetched_at":       datetime.utcnow(),
            "created_utc":      datetime.utcfromtimestamp(post.created_utc).isoformat(),
        }
        results.append(doc)
        import pymongo
        from db import client as mongo_client, db as mongo_db
        col = mongo_client[settings.db_name]["posts"]
        col.update_one(
            {"post_id": post.id, "platform": "reddit"},
            {"$set": doc},
            upsert=True,
        )
    return results


async def fetch_reddit_comments(post_id: str, limit: int = 20) -> list:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_fetch_comments, post_id, limit)


def _sync_fetch_comments(post_id: str, limit: int) -> list:
    reddit = _get_reddit_client()
    submission = reddit.submission(id=post_id)
    submission.comments.replace_more(limit=0)
    comments = []
    for comment in list(submission.comments)[:limit]:
        comments.append({
            "comment_id": comment.id,
            "author":     str(comment.author) if comment.author else "[deleted]",
            "body":       comment.body[:500],
            "score":      comment.score,
            "created_utc": datetime.utcfromtimestamp(comment.created_utc).isoformat(),
        })
    return comments


async def search_reddit(query: str, limit: int = 20) -> list:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_search, query, limit)


def _sync_search(query: str, limit: int) -> list:
    reddit  = _get_reddit_client()
    results = []
    for post in reddit.subreddit("all").search(query, limit=limit, sort="relevance"):
        results.append({
            "post_id":      post.id,
            "platform":     "reddit",
            "title":        post.title,
            "subreddit":    str(post.subreddit),
            "score":        post.score,
            "num_comments": post.num_comments,
            "url":          f"https://reddit.com{post.permalink}",
            "created_utc":  datetime.utcfromtimestamp(post.created_utc).isoformat(),
        })
    return results
