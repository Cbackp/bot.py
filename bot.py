
import os
import discord
from discord.ext import commands
import requests
from datetime import datetime, timedelta


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


def convert_to_morocco_time(utc_time_str):

    try:
      
        if len(utc_time_str.split(":")) == 2:
            utc_time = datetime.strptime(utc_time_str, "%H:%M")
        else:
            utc_time = datetime.strptime(utc_time_str, "%H:%M:%S")
        morocco_time = utc_time + timedelta(hours=1) 
        return morocco_time.strftime("%H:%M")
    except Exception:
        return utc_time_str or "TBD"


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")


@bot.command()
async def today(ctx):
    today_date = datetime.utcnow().strftime("%Y-%m-%d")

    url = f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={today_date}&s=Soccer"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            await ctx.send(f"Error fetching matches (status {resp.status_code}).")
            return

        data = resp.json()
        events = data.get("events") or []

        if not events:
            await ctx.send("There are no soccer matches today.")
            return

       
        events_sorted = sorted(events, key=lambda e: (e.get("strTime") or ""))
        lines = []
        for event in events_sorted:
            league = event.get("strLeague") or "Unknown League"
            home = event.get("strHomeTeam") or "Unknown"
            away = event.get("strAwayTeam") or "Unknown"
            utc_time = event.get("strTime") or ""
            local_time = convert_to_morocco_time(utc_time)
            lines.append(f"🏟 **{league}**\n**{home}** vs **{away}** — {local_time} Morocco Time 🇲🇦")


        
        message = "**⚽ Today's Soccer Matches (Morocco Time):**\n\n" + "\n\n".join(lines)
        await ctx.send(message)

    except Exception as e:
        await ctx.send("An error occurred while fetching matches.")
        print("Error in /today:", e)


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    print("ERROR: DISCORD_TOKEN environment variable not set. Exiting.")
    raise SystemExit("DISCORD_TOKEN not set")

bot.run(DISCORD_TOKEN)


