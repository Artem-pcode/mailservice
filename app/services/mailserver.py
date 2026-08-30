import asyncio
import subprocess

from app.config import settings


class MailserverError(RuntimeError):
    pass


def _run_docker_exec(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "exec", settings.MAILSERVER_CONTAINER, *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _create_mailbox_sync(email: str, password: str) -> None:
    result = _run_docker_exec(["setup", "email", "add", email, password])
    if result.returncode != 0:
        raise MailserverError(f"Не удалось создать ящик {email}: {result.stderr.strip()}")


def _delete_mailbox_sync(email: str) -> None:
    result = _run_docker_exec(["setup", "email", "del", email])
    if result.returncode != 0:
        raise MailserverError(f"Не удалось удалить ящик {email}: {result.stderr.strip()}")


async def create_mailbox(email: str, password: str) -> None:
    await asyncio.to_thread(_create_mailbox_sync, email, password)


async def delete_mailbox(email: str) -> None:
    await asyncio.to_thread(_delete_mailbox_sync, email)

import asyncio
import subprocess
import time

from imap_tools import MailBox
from imap_tools.errors import MailboxLoginError

from app.config import settings


class MailserverError(RuntimeError):
    pass


def _run_docker_exec(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "exec", settings.MAILSERVER_CONTAINER, *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _create_mailbox_sync(email: str, password: str) -> None:
    result = _run_docker_exec(["setup", "email", "add", email, password])
    if result.returncode != 0:
        raise MailserverError(f"Не удалось создать ящик {email}: {result.stderr.strip()}")


def _delete_mailbox_sync(email: str) -> None:
    result = _run_docker_exec(["setup", "email", "del", email])
    if result.returncode != 0:
        raise MailserverError(f"Не удалось удалить ящик {email}: {result.stderr.strip()}")


def _wait_until_ready_sync(email: str, password: str, max_retries: int = 15, initial_delay: float = 0.5) -> None:
    delay = initial_delay
    last_error = None
    start_time = time.time()
    max_wait_time = 120
    attempt = 0

    while time.time() - start_time < max_wait_time:
        attempt += 1
        try:
            with MailBox(settings.IMAP_HOST, port=settings.IMAP_PORT).login(email, password) as mailbox:
                return 
        except MailboxLoginError as exc:
            last_error = exc
            if time.time() - start_time + delay > max_wait_time:
                break
            time.sleep(delay)
            delay = min(delay * 1.5, 5.0)

    raise MailserverError(
        f"Ящик {email} создан, но не стал доступен по IMAP за отведённое время: {last_error}"
    )


async def create_mailbox(email: str, password: str) -> None:
    await asyncio.to_thread(_create_mailbox_sync, email, password)
    await asyncio.to_thread(_wait_until_ready_sync, email, password)


async def delete_mailbox(email: str) -> None:
    await asyncio.to_thread(_delete_mailbox_sync, email)