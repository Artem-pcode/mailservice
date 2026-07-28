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
