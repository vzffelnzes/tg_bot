from config import TOKEN, API_ID, API_HASH
import asyncio
from telethon import TelegramClient, events
import logging


bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=TOKEN)


def main():
    bot.run_until_disconnected()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
