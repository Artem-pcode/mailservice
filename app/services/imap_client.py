import asyncio

from imap_tools import MailBox, MailMessage, MailboxLoginError

from app.config import settings


def _fetch_messages_sync(email: str, real_password: str, limit: int = 50) -> list[MailMessage]:
    with MailBox(settings.IMAP_HOST, port=settings.IMAP_PORT).login(email, real_password) as mailbox:
        return list(mailbox.fetch(limit=limit, reverse=True))


async def fetch_messages(email: str, real_password: str, limit: int = 50) -> list[MailMessage]:
    return await asyncio.to_thread(_fetch_messages_sync, email, real_password, limit)


def _is_mailbox_ready_sync(email: str, real_password: str) -> bool:
    """
    Одна попытка логина, без retry — просто проверяет текущее состояние прямо сейчас.
    Используется отдельным эндпоинтом, чтобы клиент сам решал, когда и сколько раз опрашивать.
    """
    try:
        with MailBox(settings.IMAP_HOST, port=settings.IMAP_PORT).login(email, real_password):
            return True
    except MailboxLoginError:
        return False


async def is_mailbox_ready(email: str, real_password: str) -> bool:
    return await asyncio.to_thread(_is_mailbox_ready_sync, email, real_password)