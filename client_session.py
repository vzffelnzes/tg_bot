from config import TOKEN, API_ID, API_HASH
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsBots
from telethon.errors import UserIsBlockedError, PeerIdInvalidError, UserPrivacyRestrictedError


num_client = TelegramClient("tg", API_ID, API_HASH).start()


async def get_members(links):
    res = {}

    for link in links:
        try:
            chat = await num_client.get_participants(link)

            participants = []

            async for user in chat:
                username = user.username if user.username else f'{user.first_name} {user.last_name}'.strip()
                participants.append(username)
            res[link] = participants

        except Exception as e:
            res[link] = f'Произошла ошибка: {e}'

    return res

res = get_members("https://t.me/sgnivshiygnome")
print(res)