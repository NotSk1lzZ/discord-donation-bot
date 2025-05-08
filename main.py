from keep_alive import keep_alive

import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import os
import asyncio
import re

# Load environment variables from Render dashboard
TOKEN = os.getenv("TOKEN")
GOAL_AMOUNT = int(os.getenv("GOAL", 2000))
GFM_URL = os.getenv("GFM_URL")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 123456789012345678))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 🧠 Scrape GoFundMe total
def scrape_gfm_total():
    try:
        response = requests.get(GFM_URL)
        if response.status_code != 200:
            print(f"❌ Failed to fetch page. Status: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        match = re.search(r"€\s?([\d,\.]+)\s*(raised|gesammelt)", text, re.IGNORECASE)
        if not match:
            match = re.search(r"([\d,\.]+)\s*€\s*(raised|gesammelt)", text, re.IGNORECASE)

        if match:
            amount_str = match.group(1).replace(",", "").replace(".", "")
            return int(amount_str)

        print("❌ Donation amount not found in visible text.")
        return None
    except Exception as e:
        print(f"❗ Error scraping GoFundMe: {e}")
        return None

# 🎯 Format donation progress as a Discord embed
def format_bar_embed(current, goal):
    percent = min(100, int((current / goal) * 100))
    filled_blocks = int(percent / 10)
    bar = "█" * filled_blocks + "░" * (10 - filled_blocks)

    embed = discord.Embed(
        title="🎯 Donation Progress",
        description=f"**€{current:,} / €{goal:,}**\n`{bar}` {percent}%",
        color=0x00BFFF
    )
    embed.set_footer(text="Updated every 1 minute")
    return embed

# ✅ When bot is ready, start the update loop
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")
    print("⏳ Starting update_progress loop...")
    update_progress.start()

# 🔁 This runs every 1 minute
@tasks.loop(minutes=1)
async def update_progress():
    try:
        print("🔁 Running update_progress...")
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print("❌ Channel not found")
            return

        total = scrape_gfm_total() or 0
        embed = format_bar_embed(total, GOAL_AMOUNT)

        message = None
        async for msg in channel.history(limit=50):
            if msg.author == bot.user and msg.embeds:
                message = msg
                break

        if message:
            print("✏️ Editing existing pinned message...")
            await message.edit(embed=embed)
        else:
            print("📌 Sending and pinning new message...")
            msg = await channel.send(embed=embed)
            await msg.pin()

    except Exception as e:
        print(f"❗ Error in update_progress: {e}")

# 🔄 Manual command to trigger update
@bot.command()
async def forceupdate(ctx):
    await ctx.send("🔄 Forcing update...")
    await update_progress()

# 🌐 Keep Render service alive (used with cron-job.org)
keep_alive()

# ▶️ Run the bot
bot.run(TOKEN)
