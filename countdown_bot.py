import discord
from discord.ext import tasks
from datetime import datetime, timezone, timedelta
import itertools
import os
import sys
import json

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
DATA_FILE = "data.json"
# =============================================

if not TOKEN:
    print("❌ TOKEN не найден")
    sys.exit(1)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

message_to_edit = None
summer_fired = False

BIG_NUMBERS = {
    "0": "𝟎", "1": "𝟏", "2": "𝟐", "3": "𝟑", "4": "𝟒",
    "5": "𝟓", "6": "𝟔", "7": "𝟕", "8": "𝟖", "9": "𝟗"
}

COLORS = itertools.cycle([0xff4500, 0xffd700, 0x00ffcc, 0x8a2be2, 0xff69b4])

def big(n):
    return "".join(BIG_NUMBERS.get(d, d) for d in str(n))

# Обновляем функцию отсчёта времени для ЛЕТА
def time_until_summer():
    now = datetime.now(TZ)
    # Лето начинается 1 июня
    target = datetime(now.year, 6, 1, tzinfo=TZ)
    if now > target:
        target = datetime(now.year + 1, 6, 1, tzinfo=TZ)  # Если уже после 1 июня, то отсчитываем до следующего года
    delta = target - now
    total = int(delta.total_seconds())

    if total <= 0:
        return 0, 0, 0, 0

    return (
        total // 86400,
        (total % 86400) // 3600,
        (total % 3600) // 60,
        total % 60
    )

def load_message_id():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f).get("message_id")
    return None

def save_message_id(mid):
    with open(DATA_FILE, "w") as f:
        json.dump({"message_id": mid}, f)

@tasks.loop(seconds=10)
async def update_countdown():
    global message_to_edit, summer_fired

    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return

    if not message_to_edit:
        mid = load_message_id()
        if mid:
            try:
                message_to_edit = await channel.fetch_message(mid)
            except:
                pass

        if not message_to_edit:
            message_to_edit = await channel.send
            save_message_id(message_to_edit.id)

    days, hours, minutes, seconds = time_until_summer()

    if days == hours == minutes == seconds == 0 and not summer_fired:
        summer_fired = True
        await channel.send("🎉🌞 **ЛЕТО НАСТУПИЛО!!!** 🌞🎉")

    color = next(COLORS)

    embed = discord.Embed(
        title="☀️ Обратный отсчёт до ЛЕТА ☀️",
        description=( 
            f"🗓 **Дней:** {big(days)}\n"
            f"⏰ **Часов:** {big(hours)}\n"
            f"⏱ **Минут:** {big(minutes)}\n"
            f"⏳ **Секунд:** {big(seconds)}"
        ),
        color=color
    )

    await message_to_edit.edit(embed=embed)

@tasks.loop(minutes=5)
async def update_channel_name():
    channel = client.get_channel(NAME_CHANNEL_ID)
    if not channel:
        return

    days, hours, _, _ = time_until_summer()
    new_name = f"До Лета: {big(days)}д {big(hours)}ч"

    if channel.name != new_name:
        await channel.edit(name=new_name)

@client.event
async def on_ready():
    print(f"✅ {client.user} онлайн")
    update_countdown.start()
    update_channel_name.start()

client.run(TOKEN)
Ы
