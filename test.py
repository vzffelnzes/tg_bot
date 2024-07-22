from config import API_ID, API_HASH
from pyrogram import Client, filters, enums
from pyrogram.errors import UserIsBlocked, PeerIdInvalid
from db.user import User
from db.db_session import *
import logging, os, sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telegram')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

global_init("db/base.sqlite3")

app = Client("mybot", api_id=API_ID, api_hash=API_HASH)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Привет! Это бот для парсинга аудитории в телеграмме, что бы добавить пользователей в базу данных напиши /get_user_list <ссылки на чаты> <тематика>. Чтобы разослать сообщене напиши /send_message <тематика> <сообщение>")


@app.on_message(filters.command("get_user_list") & filters.regex(r"(.*)"))
async def get_user_list(client, message):
    chat_links = message.matches[0].group(1).split()[1:-1]
    category = message.matches[0].group(1).split()[-1]
    result = {}

    for chat_link in chat_links:
        aaa = chat_link.split("/")[-1]
        try:
            chat = await app.get_chat(aaa)
            admin_ids = set()
            async for admin in chat.get_members(filter=enums.ChatMembersFilter.ADMINISTRATORS):
                admin_ids.add(admin.user.id)

            bot_ids = set()
            async for bot in chat.get_members(filter=enums.ChatMembersFilter.BOTS):
                bot_ids.add(bot.user.id)

            participants = []
            async for user in chat.get_members():
                if user.user.id in admin_ids or user.user.id in bot_ids or user.user.is_self:
                    continue

                username = user.user.username if user.user.username else f"{user.user.first_name} {user.user.last_name}".strip()
                participants.append(username)

                member = User()
                member.user_id = str(user.user.id)
                member.nickname = str(user.user.username)
                member.category = str(category)
                member.first_name = str(user.user.first_name)
                member.last_name = str(user.user.last_name)
                db_sess = create_session()
                db_sess.add(member)
                db_sess.commit()

            result = "Успешно выполнено."

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            result[chat_link] = f"Произошла ошибка: {e}"

    await message.reply(str(result))


@app.on_message(filters.command("send_message") & filters.regex(r"(.*)"))
async def send_message_to_users(client, message):
    args = message.matches[0].group(1).split()
    if len(args) != 3:
        await message.reply("Использование: /send_message <category> <message>")
        return

    db_session = create_session()
    category, message_text = args[1], args[2]
    users = list(db_session.query(User).filter(User.category == category))
    sent_to = 0
    not_sent_to = 0

    try:
        for user in users:
            try:
                await app.send_message(user.user_id, message_text)
                sent_to += 1 if user.nickname else f"{user.first_name} {user.last_name}".strip()
            except (UserIsBlocked, PeerIdInvalid):
                not_sent_to += 1 if user.nickname else f"{user.first_name} {user.last_name}".strip()

    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")
        return

    response = f"Сообщение было отправлено:\n{sent_to}\n\nНе удалось отправить сообщение:\n{not_sent_to}"
    await message.reply(response)


app.run()