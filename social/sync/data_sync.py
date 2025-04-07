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
                response = await fetch_json(session, f"{BASE_API_URL}/users", headers)
                users_raw = response["users"]

                for user_id_str, user_name in users_raw.items():
                    user_id = int(user_id_str)

                    users_data[user_id] = {
                        "id": user_id,
                        "name": user_name
                    }
                    user_posts_map[user_id] = []

                    posts = await fetch_json(session, f"{BASE_API_URL}/users/{user_id}/posts", headers)
                    posts_raw = posts["posts"]

                    for post in posts_raw:
                        post_id = int(post["id"])

                        comments = await fetch_json(session, f"{BASE_API_URL}/posts/{post_id}/comments", headers)

                        post["comment_count"] = len(comments)
                        post["timestamp"] = datetime.now().isoformat()

                        posts_data[post_id] = post
                        user_posts_map[user_id].append(post_id)

            print(f"Fetch completed: {len(users_data)} users, {len(posts_data)} posts")

        except Exception as e:
            print(f"Fetching failed: {str(e)}")

        await asyncio.sleep(SYNC_INTERVAL_SECONDS)
