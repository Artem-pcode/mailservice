from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.models import MailAccount
from app.schemas import CodeResponse, LinkResponse
from app.security import decrypt_real_password, verify_request_password, hash_request_password
from app.services.imap_client import fetch_messages
from app.services.matcher import (
    find_login_code,
    find_recovery_code,
    find_removal_link,
    find_verification_link,
)

router = APIRouter(prefix="/fetch", tags=["fetch"], dependencies=[Depends(verify_api_key)])

import secrets
_DUMMY_HASH = hash_request_password(secrets.token_urlsafe(16))


async def _authorize_and_get_account(email, request_password, db):
    account = await db.scalar(select(MailAccount).where(MailAccount.email == email))
    hash_to_check = account.request_password_hash if account else _DUMMY_HASH
    password_ok = verify_request_password(request_password, hash_to_check)
    if account is None or not account.is_active or not password_ok:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Неверный email или request_password")
    return account


async def _get_messages(account: MailAccount) -> list:
    real_password = decrypt_real_password(account.encrypted_real_password)
    return await fetch_messages(account.email, real_password)


@router.get("/recovery-code", response_model=CodeResponse)
async def fetch_recovery_code(email: str, request_password: str, db: AsyncSession = Depends(get_db)):
    account = await _authorize_and_get_account(email, request_password, db)
    messages = await _get_messages(account)
    result = find_recovery_code(messages)
    if result is None:
        return CodeResponse(found=False)
    return CodeResponse(found=True, **result)


@router.get("/login-code", response_model=CodeResponse)
async def fetch_login_code(email: str, request_password: str, db: AsyncSession = Depends(get_db)):
    account = await _authorize_and_get_account(email, request_password, db)
    messages = await _get_messages(account)
    result = find_login_code(messages)
    if result is None:
        return CodeResponse(found=False)
    return CodeResponse(found=True, **result)


@router.get("/removal-link", response_model=LinkResponse)
async def fetch_removal_link(email: str, request_password: str, db: AsyncSession = Depends(get_db)):
    account = await _authorize_and_get_account(email, request_password, db)
    messages = await _get_messages(account)
    result = find_removal_link(messages)
    if result is None:
        return LinkResponse(found=False)
    return LinkResponse(found=True, **result)


@router.get("/verification-link", response_model=LinkResponse)
async def fetch_verification_link(email: str, request_password: str, db: AsyncSession = Depends(get_db)):
    account = await _authorize_and_get_account(email, request_password, db)
    messages = await _get_messages(account)
    result = find_verification_link(messages)
    if result is None:
        return LinkResponse(found=False)
    return LinkResponse(found=True, **result)