import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SOURCE_CHANNEL_IDS = ["1373261075952058240", "1380380752488502652"]  # Trade With Insight alert channels
TARGET_CHANNEL_ID = "1376787695069827085"  # Big Mully's server #general channel ID

HEADERS = {
    "Authorization": f"Bot {DISCORD_TOKEN}"
}

async def fetch_messages(session, channel_id):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=10"
    async with session.get(url, headers=HEADERS) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Failed to fetch from channel {channel_id}: {response.status}")
            return []

def parse_alert(message):
    content = message["content"].upper()
    if any(keyword in content for keyword in ["BOUGHT", "SOLD"]):
        return {
            "timestamp": message["timestamp"],
            "author": message["author"]["username"],
            "content": message["content"]
        }
    return None

async def send_alert(session, content):
    url = f"https://discord.com/api/v10/channels/{TARGET_CHANNEL_ID}/messages"
    payload = {"content": content}
    async with session.post(url, json=payload, headers=HEADERS) as response:
        if response.status != 200:
            print(f"Failed to send message: {response.status}")

async def monitor():
    async with aiohttp.ClientSession() as session:
        while True:
            for channel_id in SOURCE_CHANNEL_IDS:
                try:
                    messages = await fetch_messages(session, channel_id)
                    for message in reversed(messages):
                        alert = parse_alert(message)
                        if alert:
                            formatted = f"[{alert['timestamp']}] {alert['author']}: {alert['content']}"
                            print(formatted)
                            await send_alert(session, formatted)
                except Exception as e:
                    print(f"Error fetching/parsing messages: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(monitor())
