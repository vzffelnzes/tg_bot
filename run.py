from config import TOKEN, API_ID, API_HASH
import asyncio
import logging
from telethon import TelegramClient, events, Button
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsBots, ReplyInlineMarkup, \
    ReplyKeyboardMarkup, PeerUser, KeyboardButtonRow, KeyboardButton
from telethon.errors import UserIsBlockedError, PeerIdInvalidError, UserPrivacyRestrictedError
from db.user import User
from db.db_session import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telegram')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

global_init("db/base.db")

# num_client = TelegramClient("tg", API_ID, API_HASH).start()
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=TOKEN)


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    keyboard_buttons = [
        [Button.text("Меню")]
    ]

    await client.send_message(
        event.chat_id,
        "Привет! Это бот для парсинга аудитории в телеграмме, чтобы начать взаимодействовать зайдите в меню",
        buttons=keyboard_buttons
    )


@client.on(events.NewMessage(pattern='/get_user_list (.*)'))
async def get_user_list(event):
    chat_links = event.pattern_match.group(1).split()[:-1]
    category = event.pattern_match.group(1).split()[-1]
    result = {}
    # result = await get_members(chat_links, num_client)

    for chat_link in chat_links:
        try:
            chat = await client.get_entity(chat_link)

            admin_ids = set()
            async for admin in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
                admin_ids.add(admin.id)

            bot_ids = set()
            async for bot in client.iter_participants(chat, filter=ChannelParticipantsBots):
                bot_ids.add(bot.id)

            participants = []
            async for user in client.iter_participants(chat):
                if user.id in admin_ids or user.id in bot_ids or user.is_self:
                    continue

                username = user.username if user.username else f'{user.first_name} {user.last_name}'.strip()
                participants.append(username)

                member = User()
                member.user_id = str(user.id)
                member.nickname = str(user.username)
                member.category = str(category)
                member.first_name = str(user.first_name)
                member.last_name = str(user.last_name)
                db_sess = create_session()
                db_sess.add(member)
                db_sess.commit()

            result[chat_link] = participants

        except Exception as e:
            result[chat_link] = f'Произошла ошибка: {e}'

    await event.reply(str(result))


@client.on(events.NewMessage(pattern='/send_message_to_users (.*)'))
async def send_message_to_users(event):
    args = event.pattern_match.group(1).split(maxsplit=1)
    if len(args) != 2:
        await event.reply('Использование: /send_message_to_users <category> <message>')
        return

    db_session = create_session()

    category, message = args
    users = list(db_session.query(User).filter(User.category == category))
    print(users)
    sent_to = []
    not_sent_to = []

    try:
        for user in users:
            try:
                await client.send_message(user.user_id, message)
                sent_to.append(user.nickname if user.nickname else f'{user.first_name} {user.last_name}'.strip())
            except (UserIsBlockedError, PeerIdInvalidError):
                not_sent_to.append(user.nickname if user.nickname else f'{user.first_name} {user.last_name}'.strip())

    except Exception as e:
        await event.reply(f'Произошла ошибка: {e}')
        return

    response = f'Сообщение было отправлено:\n{sent_to}\n\nНе удалось отправить сообщение:\n{not_sent_to}'
    await event.reply(response)


def main():
    client.run_until_disconnected()


if __name__ == "__main__":
    main()
