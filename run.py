from config import TOKEN, API_ID, API_HASH
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsBots
from telethon.errors import UserIsBlockedError, PeerIdInvalidError, UserPrivacyRestrictedError

client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=TOKEN)


@client.on(events.NewMessage(pattern='/get_user_list (.*)'))
async def get_user_list(event):
    chat_links = event.pattern_match.group(1).split()
    result = {}

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

            result[chat_link] = participants

        except Exception as e:
            result[chat_link] = f'Произошла ошибка: {e}'

    await event.reply(str(result))


@client.on(events.NewMessage(pattern='/send_message_to_users (.*)'))
async def send_message_to_users(event):
    args = event.pattern_match.group(1).split(maxsplit=1)
    if len(args) < 2:
        await event.reply('Использование: /send_message_to_users <chat_link> <message>')
        return

    chat_link, message = args
    sent_to = []
    not_sent_to = []

    try:
        chat = await client.get_entity(chat_link)

        admin_ids = set()
        async for admin in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
            admin_ids.add(admin.id)

        bot_ids = set()
        async for bot in client.iter_participants(chat, filter=ChannelParticipantsBots):
            bot_ids.add(bot.id)

        async for user in client.iter_participants(chat):
            if user.id in admin_ids or user.id in bot_ids or user.is_self:
                continue
            try:
                await client.send_message(user.id, message)
                sent_to.append(user.username if user.username else f'{user.first_name} {user.last_name}'.strip())
            except (UserIsBlockedError, PeerIdInvalidError):
                not_sent_to.append(user.username if user.username else f'{user.first_name} {user.last_name}'.strip())

    except Exception as e:
        await event.reply(f'Произошла ошибка: {e}')
        return

    response = f'Сообщение было отправлено:\n{sent_to}\n\nНе удалось отправить сообщение:\n{not_sent_to}'
    await event.reply(response)


@client.on(events.NewMessage(pattern='/send_invite_to_users (.*)'))
async def send_invite_to_users(event):
    args = event.pattern_match.group(1).split(maxsplit=1)
    if len(args) < 2:
        await event.reply('Использование: /send_invite_to_users <source_chat_link> <destination_channel_link>')
        return

    source_chat_link, destination_channel_link = args
    invite_link = destination_channel_link  # Предполагается, что это полная ссылка-приглашение
    sent_to = []
    not_sent_to = []

    try:
        source_chat = await client.get_entity(source_chat_link)

        admin_ids = set()
        async for admin in client.iter_participants(source_chat, filter=ChannelParticipantsAdmins):
            admin_ids.add(admin.id)

        bot_ids = set()
        async for bot in client.iter_participants(source_chat, filter=ChannelParticipantsBots):
            bot_ids.add(bot.id)

        async for user in client.iter_participants(source_chat):
            if user.id in admin_ids or user.id in bot_ids or user.is_self:
                continue
            try:
                await client.send_message(user.id, f'Привет! Присоединяйтесь к нашему каналу: {invite_link}')
                sent_to.append(user.username if user.username else f'{user.first_name} {user.last_name}'.strip())
            except (UserIsBlockedError, PeerIdInvalidError, UserPrivacyRestrictedError) as e:
                not_sent_to.append(
                    (user.username if user.username else f'{user.first_name} {user.last_name}'.strip(), str(e)))

    except Exception as e:
        await event.reply(f'Произошла ошибка: {e}')
        return

    response = f'Приглашение отправлено:\n{sent_to}\n\nНе удалось отправить приглашение:\n{not_sent_to}'
    await event.reply(response)


def main():
    client.run_until_disconnected()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
