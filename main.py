from keep_alive import keep_alive

import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import os
import json
import asyncio
import re

TOKEN = os.getenv("TOKEN")
GOAL_AMOUNT = int(os.getenv("GOAL", 2000))
GFM_URL = os.getenv("GFM_URL")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 1234567890))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def scrape_gfm_total():
    try:
        response = requests.get(GFM_URL)
        if response.status_code != 200:
            print(f"Failed to fetch page, status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        match = re.search(r"€\s?([\d,\.]+)\s*(raised|gesammelt)", text, re.IGNORECASE)
        if not match:
            match = re.search(r"([\d,\.]+)\s*€\s*(raised|gesammelt)", text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(",", "").replace(".", "")
            return int(amount_str)

        print("Donation amount not found in visible text.")
        return None
    except Exception as e:
        print(f"Error scraping GoFundMe: {e}")
        return None

from discord import Embed

def format_bar_embed(current, goal):
    percent = min(100, int((current / goal) * 100))
    filled_blocks = int(percent / 10)
    bar = "█" * filled_blocks + "░" * (10 - filled_blocks)
    
    embed = Embed(
        title="🎯 Donation Progress",
        description=f"**€{current:,} / €{goal:,}**\n`{bar}` {percent}%",
        color=0x00BFFF  # optional: light blue
    )
    embed.set_footer(text="Updated every 5 minutes")
    return embed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    update_progress.start()

@tasks.loop(minutes=5)
async def update_progress():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found")
        return

    total = scrape_gfm_total()
    embed = format_bar_embed(total, GOAL_AMOUNT) if total else "Unable to scrape donation data."

    message = None
    async for msg in channel.history(limit=50):
        if msg.author == bot.user and "🎯 Goal:" in msg.content:
            message = msg
            break

    if message:
    await message.edit(embed=embed)
    else:
    msg = await channel.send(embed=embed)

# Start web server to keep app alive
keep_alive()

# Start bot
bot.run(TOKEN)# main bot file placeholder
