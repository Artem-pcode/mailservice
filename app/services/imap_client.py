import asyncio

from imap_tools import MailBox, MailMessage

from app.config import settings


def _fetch_messages_sync(email: str, real_password: str, limit: int = 50) -> list[MailMessage]:
    with MailBox(settings.IMAP_HOST, port=settings.IMAP_PORT).login(email, real_password) as mailbox:
        return list(mailbox.fetch(limit=limit, reverse=True))


async def fetch_messages(email: str, real_password: str, limit: int = 50) -> list[MailMessage]:
    return await asyncio.to_thread(_fetch_messages_sync, email, real_password, limit)
