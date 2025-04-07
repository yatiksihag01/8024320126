import aiohttp
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
NAME = os.getenv("NAME")
ROLL_NO = os.getenv("ROLL_NO")
ACCESS_CODE = os.getenv("ACCESS_CODE")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH_URL = os.getenv("AUTH_URL")

access_token = None
token_type = "Bearer"
token_expiry = datetime.now()

async def fetch_access_token():
    global access_token, token_expiry

    async with aiohttp.ClientSession() as session:
        payload = {
            "email": EMAIL,
            "name": NAME,
            "rollNo": ROLL_NO,
            "accessCode": ACCESS_CODE,
            "clientID": CLIENT_ID,
            "clientSecret": CLIENT_SECRET
        }

        async with session.post(AUTH_URL, json=payload) as response:
            if response.status != 200:
                raise Exception(f"Authorization failed: {response.status}")

            data = await response.json()
            access_token = data["access_token"]
            expires_in = data.get("expires_in")
            token_expiry = datetime.now() + timedelta(seconds=expires_in)

async def get_valid_token():
    if datetime.now() >= token_expiry:
        await fetch_access_token()
    return access_token