import os
import asyncio
from datetime import datetime, timedelta, timezone

import requests
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHANNELS = ["toporlive", "ecotopor"]


async def main():
    client = TelegramClient(
        StringSession(SESSION),
        API_ID,
        API_HASH
    )

    await client.start()

    since = datetime.now(timezone.utc) - timedelta(hours=12)
    posts = []

    for channel in CHANNELS:
        try:
            entity = await client.get_entity(channel)

            async for message in client.iter_messages(
                entity,
                limit=100
            ):
                if message.date < since:
                    break

                if message.text:
                    posts.append(
                        f"Канал: {channel}\n{message.text}"
                    )

        except Exception as error:
            posts.append(
                f"Не удалось прочитать {channel}: {error}"
            )

    await client.disconnect()

    if not posts:
        text = "За последние 12 часов новых публикаций нет."
    else:
        text = "📰 ДАЙДЖЕСТ\n\n" + "\n\n──────────\n\n".join(posts)

    for part in [
        text[i:i + 4000]
        for i in range(0, len(text), 4000)
    ]:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": part
            },
            timeout=30
        )


if __name__ == "__main__":
    asyncio.run(main())