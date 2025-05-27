import aiohttp
import asyncio
import os
from dotenv import load_dotenv
import discord

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_IDS = ["1376787695069827085"]  # This is your private server's general channel
HEADERS = {
    "authorization": DISCORD_TOKEN
}

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

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
        return f"{message['timestamp']} | {message['author']['username']}: {message['content']}"
    return None

@client.event
async def on_ready():
    print(f"Bot is ready as {client.user}")
    await monitor()

async def monitor():
    async with aiohttp.ClientSession() as session:
        channel = client.get_channel(int(CHANNEL_IDS[0]))  # Your server's channel
        while True:
            for source_channel in CHANNEL_IDS:
                try:
                    messages = await fetch_messages(session, source_channel)
                    for message in reversed(messages):
                        alert = parse_alert(message)
                        if alert:
                            await channel.send(alert)
                except Exception as e:
                    print(f"Error: {e}")
            await asyncio.sleep(10)

client.run(DISCORD_TOKEN)
