import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import MailAccount, WebSession
from app.security import (
    decrypt_real_password,
    generate_session_token,
    hash_session_token,
    verify_request_password,
)
from app.services.imap_client import fetch_messages
from app.services.matcher import (
    find_all_recovery_codes,
)

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")

_failed_attempts: dict[str, list[float]] = {}


def _is_locked_out(email: str) -> bool:
    now = time.time()
    window_start = now - settings.LOGIN_LOCKOUT_MINUTES * 60
    attempts = [t for t in _failed_attempts.get(email, []) if t > window_start]
    _failed_attempts[email] = attempts
    return len(attempts) >= settings.LOGIN_MAX_ATTEMPTS


def _register_failed_attempt(email: str) -> None:
    _failed_attempts.setdefault(email, []).append(time.time())


def _clear_failed_attempts(email: str) -> None:
    _failed_attempts.pop(email, None)


async def get_current_account(
    session: str | None = Cookie(default=None, alias="session"),
    db: AsyncSession = Depends(get_db),
) -> MailAccount:
    if session is None:
        raise HTTPException(status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})

    token_hash = hash_session_token(session)
    web_session = await db.scalar(select(WebSession).where(WebSession.token_hash == token_hash))

    if web_session is None or web_session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})

    account = await db.get(MailAccount, web_session.account_id)
    if account is None:
        raise HTTPException(status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})

    return account


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    request_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    if _is_locked_out(email):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Слишком много неверных попыток. Попробуй позже."},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    account = await db.scalar(select(MailAccount).where(MailAccount.email == email))

    if account is None or not verify_request_password(request_password, account.request_password_hash):
        _register_failed_attempt(email)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный email или пароль"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    _clear_failed_attempts(email)

    token = generate_session_token()
    web_session = WebSession(
        account_id=account.id,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.SESSION_TTL_MINUTES),
    )
    db.add(web_session)
    await db.flush()

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="strict",
        max_age=settings.SESSION_TTL_MINUTES * 60,
    )
    return response


@router.post("/logout")
async def logout(
    response: Response,
    session: str | None = Cookie(default=None, alias="session"),
    db: AsyncSession = Depends(get_db),
):
    if session:
        token_hash = hash_session_token(session)
        web_session = await db.scalar(select(WebSession).where(WebSession.token_hash == token_hash))
        if web_session:
            await db.delete(web_session)

    redirect = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    redirect.delete_cookie(settings.SESSION_COOKIE_NAME)
    return redirect


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, account: MailAccount = Depends(get_current_account)):
    real_password = decrypt_real_password(account.encrypted_real_password)
    messages = await fetch_messages(account.email, real_password)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "email": account.email,
            "recovery_codes": find_all_recovery_codes(messages),
        },
    )


@router.get("/", response_class=HTMLResponse)
async def root_redirect():
    return RedirectResponse(url="/login")