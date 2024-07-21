from config import TOKEN
from pyrogram import Client, filters, enums
from pyrogram.errors import UserIsBlocked, PeerIdInvalid
from test import get_user_list, send_message_to_users
import logging, os, sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telegram')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

app = Client("my_bot", bot_token=TOKEN)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Привет! Это бот для парсинга аудитории в телеграмме, что бы добавить пользователей в базу данных напиши /get_user_list <ссылки на чаты> <тематика>. Чтобы разослать сообщене напиши /send_message <тематика> <сообщение>")


@app.on_message(filters.command("get_user_list") & filters.regex(r"(.*)"))
async def get_user_list(client, message):
    await message.reply(get_user_list(message))


@app.on_message(filters.command("send_message") & filters.regex(r"(.*)"))
async def send_message_to_users(client, message):
    await message.reply(send_message_to_users(message))


app.run()