import asyncio
import aiohttp
import os
from datetime import datetime
from auth.token_handler import get_valid_token
from cache.storage import users_data, posts_data, user_posts_map
from dotenv import load_dotenv

load_dotenv()

BASE_API_URL = os.getenv("BASE_API_URL")
SYNC_INTERVAL_SECONDS = 60

async def fetch_json(session, url, headers):
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            raise Exception(f"{url} returned error with {response.status}")
        return await response.json()

async def sync_data():
    while True:
        try:
            token = await get_valid_token()
            headers = {"Authorization": f"Bearer {token}"}

            async with aiohttp.ClientSession() as session:
                users_response = await fetch_json(session, f"{BASE_API_URL}/users", headers)
                users_dict = users_response.get("users", {})

                posts_response = await fetch_json(session, f"{BASE_API_URL}/posts", headers)
                comments_response = await fetch_json(session, f"{BASE_API_URL}/comments", headers)

                posts = posts_response.get("posts", [])
                comments = comments_response.get("comments", [])

                users_data.clear()
                user_posts_map.clear()
                for user_id_str, username in users_dict.items():
                    user_id = int(user_id_str)
                    users_data[user_id] = {"id": user_id, "name": username}
                    user_posts_map[user_id] = []

                comment_map = {}
                for comment in comments:
                    postid = comment["postid"]
                    comment_map.setdefault(postid, []).append(comment)

                posts_data.clear()
                for post in posts:
                    post_id = post["id"]
                    user_id = post["userid"]

                    post["comment_count"] = len(comment_map.get(post_id, []))
                    post["timestamp"] = datetime.now().isoformat()

                    posts_data[post_id] = post
                    if user_id in user_posts_map:
                        user_posts_map[user_id].append(post_id)

            print(f"Fetch completed")

        except Exception as e:
            print(f"Fetching failed: {str(e)}")

        await asyncio.sleep(SYNC_INTERVAL_SECONDS)
