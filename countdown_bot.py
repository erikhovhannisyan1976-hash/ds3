import discord
from discord.ext import tasks
from datetime import datetime, timezone, timedelta
import itertools
import os
import sys

# ===== KEEP ALIVE (Replit) =====
from flask import Flask
from threading import Thread

app = Flask("")

@app.route("/")
def home():
    return "Bot is alive"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()
# ==============================

# ================= НАСТРОЙКИ =================
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1452399245624868934
NAME_CHANNEL_ID = 1452409457739829289
TZ = timezone(timedelta(hours=3))  # МСК
# =============================================

if not TOKEN:
    print("❌ TOKEN не найден")
    sys.exit(1)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

message_to_edit = None
new_year_fired = False

BIG_NUMBERS = {
    "0": "𝟎", "1": "𝟏", "2": "𝟐", "3": "𝟑", "4": "𝟒",
    "5": "𝟓", "6": "𝟔", "7": "𝟕", "8": "𝟖", "9": "𝟗"
}

COLORS = itertools.cycle([
    0xff4500, 0xffd700, 0x00ffcc, 0x8a2be2, 0xff69b4
])

EMOJIS = itertools.cycle(["🎉", "✨", "🎆", "🎇"])


def big(n):
    return "".join(BIG_NUMBERS.get(d, d) for d in str(n))


def time_until_new_year():
    now = datetime.now(TZ)
    target = datetime(now.year + 1, 1, 1, tzinfo=TZ)

    delta = target - now
    total = int(delta.total_seconds())

    if total <= 0:
        return 0, 0, 0, 0

    days = total // 86400
    hours = (total % 86400) // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60

    return days, hours, minutes, seconds


@tasks.loop(seconds=1)
async def update_countdown():
    global message_to_edit, new_year_fired

    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return

    days, hours, minutes, seconds = time_until_new_year()

    # 🎆 Новый год
    if days == hours == minutes == seconds == 0 and not new_year_fired:
        new_year_fired = True
        await channel.send("🎉🎆 **С НОВЫМ ГОДОМ!!!** 🎆🎉")

    color = next(COLORS)
    emoji = next(EMOJIS)

    embed = discord.Embed(
        title=f"{emoji} Обратный отсчёт до Нового года {emoji}",
        description=(
            f"🗓 Дней: {big(days)}\n"
            f"⏰ Часов: {big(hours)}\n"
            f"⏱ Минут: {big(minutes)}\n"
            f"⏳ Секунд: {big(seconds)}"
        ),
        color=color
    )

    if message_to_edit:
        try:
            await message_to_edit.edit(embed=embed)
        except discord.NotFound:
            message_to_edit = await channel.send(embed=embed)
    else:
        message_to_edit = await channel.send(embed=embed)


@tasks.loop(minutes=5)
async def update_channel_name():
    channel = client.get_channel(NAME_CHANNEL_ID)
    if not channel:
        return

    days, hours, _, _ = time_until_new_year()
    new_name = f"До НГ: {big(days)}д {big(hours)}ч"

    if channel.name != new_name:
        await channel.edit(name=new_name)


@client.event
async def on_ready():
    print(f"✅ {client.user} онлайн")
    update_countdown.start()
    update_channel_name.start()


client.run(TOKEN)
