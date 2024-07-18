from config import TOKEN, API_ID, API_HASH
import asyncio
import logging
from telethon import TelegramClient, events

client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=TOKEN)


@client.on(events.NewMessage(pattern='/get_user_list (.+)'))
async def get_user_list(event):
    chat_link = event.pattern_match.group(1)
    try:
        chat = await client.get_entity(chat_link)
        if not chat.admin_rights:
            await event.reply('Я не являюсь администратором этого чата.')
            return
        participants = []
        async for user in client.iter_participants(chat):
            participants.append(user)
        user_list = '\n'.join([f'{user.id}: {user.first_name} {user.last_name}' for user in participants])
        if not user_list:
            user_list = 'В этом чате нет участников.'
        await event.reply(user_list)
    except Exception as e:
        await event.reply(f'Произошла ошибка: {e}')


def main():
    client.run_until_disconnected()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
