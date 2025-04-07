import asyncio
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Query

from cache.storage import user_posts_map, posts_data, users_data
from sync.data_sync import sync_data

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sync_data())


@app.get("/users")
async def get_top_users() -> List[Dict]:
    user_comment_counts = []

    for user_id, post_ids in user_posts_map.items():
        total_comments = sum(posts_data[pid]["comment_count"] for pid in post_ids if pid in posts_data)
        user = users_data.get(user_id)
        if user:
            user_comment_counts.append({
                "id": user_id,
                "name": user["name"],
                "total_comment_count": total_comments
            })

    # Sort by total_comment_count in descending order
    sorted_users = sorted(user_comment_counts, key=lambda x: x["total_comment_count"], reverse=True)
    return sorted_users[:5]


@app.get("/posts")
async def get_top_or_latest_posts(type: str = Query(..., pattern="^(latest|popular)$")) -> List[Dict]:
    if not posts_data:
        raise HTTPException(status_code=404, detail="No posts found")

    all_posts = list(posts_data.values())

    if type == "latest":
        sorted_posts = sorted(all_posts, key=lambda p: p["timestamp"], reverse=True)
        return sorted_posts[:5]

    elif type == "popular":
        max_comments = max(post["comment_count"] for post in all_posts)
        return [post for post in all_posts if post["comment_count"] == max_comments]
