import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_IDS = [
    "1376787695069827085",  # Big Mully's server (your bot's private alert relay)
    "1303807524788502652"   # analyst-sarang alerts from TWI
]

HEADERS = {
    "authorization": DISCORD_TOKEN
}

async def fetch_messages(session, channel_id):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=10"
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

async def monitor():
    async with aiohttp.ClientSession() as session:
        while True:
            for channel_id in CHANNEL_IDS:
                try:
                    messages = await fetch_messages(session, channel_id)
                    for message in reversed(messages):
                        alert = parse_alert(message)
                        if alert:
                            print(f"[{alert['timestamp']}] {alert['author']}: {alert['content']}")
                except Exception as e:
                    print(f"Error fetching/parsing messages: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(monitor())
