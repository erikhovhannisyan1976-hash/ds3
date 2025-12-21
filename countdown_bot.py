import discord
from discord.ext import tasks
from datetime import datetime
import itertools
import os
import sys

# ================= НАСТРОЙКИ =================
TOKEN = os.getenv("TOKEN")  # токен берётся из переменных окружения
CHANNEL_ID = 1452399245624868934
NAME_CHANNEL_ID = 1452409457739829289
# =============================================

if not TOKEN:
    print("❌ ОШИБКА: TOKEN не найден в переменных окружения")
    sys.exit(1)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

message_to_edit = None

BIG_NUMBERS = {
    "0": "𝟎", "1": "𝟏", "2": "𝟐", "3": "𝟑", "4": "𝟒",
    "5": "𝟓", "6": "𝟔", "7": "𝟕", "8": "𝟖", "9": "𝟗"
}

COLORS = itertools.cycle([
    0xff4500, 0xffd700, 0x00ffcc, 0x8a2be2, 0xff69b4
])

EMOJIS = itertools.cycle(["🎉", "✨", "🎆", "🎇"])


def time_until_new_year():
    now = datetime.now()
    new_year = datetime(now.year + 1, 1, 1)
    delta = new_year - now
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes, seconds


def big_number_format(number):
    return "".join(BIG_NUMBERS.get(d, d) for d in str(number))


@tasks.loop(seconds=1)
async def update_countdown():
    global message_to_edit
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return

    days, hours, minutes, seconds = time_until_new_year()
    color = next(COLORS)
    emoji = next(EMOJIS)

    description = (
        f"🗓 Дней: {big_number_format(days)}\n"
        f"⏰ Часов: {big_number_format(hours)}\n"
        f"⏱ Минут: {big_number_format(minutes)}\n"
        f"⏳ Секунд: {big_number_format(seconds)}"
    )

    embed = discord.Embed(
        title=f"{emoji} Обратный отсчёт до Нового года {emoji}",
        description=description,
        color=color
    )
    embed.set_footer(text="Обновление в реальном времени")

    if message_to_edit:
        try:
            await message_to_edit.edit(embed=embed)
        except discord.NotFound:
            message_to_edit = await channel.send(embed=embed)
    else:
        message_to_edit = await channel.send(embed=embed)


@tasks.loop(hours=1)
async def update_channel_name():
    await client.wait_until_ready()
    channel = client.get_channel(NAME_CHANNEL_ID)
    if not channel:
        return

    days, hours, _, _ = time_until_new_year()
    new_name = f"До Нового года: {big_number_format(days)}д {big_number_format(hours)}ч"

    if channel.name != new_name:
        try:
            await channel.edit(name=new_name)
        except discord.HTTPException as e:
            print(f"⚠ Ошибка обновления канала: {e}")


@client.event
async def on_ready():
    print(f"✅ Бот {client.user} запущен и работает")
    update_countdown.start()
    update_channel_name.start()


client.run(TOKEN)
