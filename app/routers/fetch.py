from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.models import MailAccount
from app.schemas import FetchLinkResponse
from app.security import decrypt_real_password, verify_request_password
from app.services.imap_client import fetch_messages
from app.services.matcher import find_matching_link

router = APIRouter(prefix="/fetch", tags=["fetch"], dependencies=[Depends(verify_api_key)])


async def _authorize_and_get_account(email: str, request_password: str, db: AsyncSession) -> MailAccount:
    account = await db.scalar(select(MailAccount).where(MailAccount.email == email))
    if account is None or not verify_request_password(request_password, account.request_password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Неверный email или request_password")
    return account


@router.get("/template-one", response_model=FetchLinkResponse)
async def fetch_template_one(email: str, request_password: str, db: AsyncSession = Depends(get_db)):
    account = await _authorize_and_get_account(email, request_password, db)
    real_password = decrypt_real_password(account.encrypted_real_password)
    messages = await fetch_messages(email, real_password)

    try:
        link = find_matching_link(messages, template=account.templates[0])
    except NotImplementedError:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="Логика шаблона ещё не реализована")

    return FetchLinkResponse(found=link is not None, link=link)


@router.get("/template-two", response_model=FetchLinkResponse)
async def fetch_template_two(email: str, request_password: str, db: AsyncSession = Depends(get_db)):
    account = await _authorize_and_get_account(email, request_password, db)
    real_password = decrypt_real_password(account.encrypted_real_password)
    messages = await fetch_messages(email, real_password)

    try:
        link = find_matching_link(messages, template=account.templates[0])
    except NotImplementedError:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="Логика шаблона ещё не реализована")

    return FetchLinkResponse(found=link is not None, link=link)


@router.get("/template-three", response_model=FetchLinkResponse)
async def fetch_template_three(email: str, request_password: str, db: AsyncSession = Depends(get_db)):
    account = await _authorize_and_get_account(email, request_password, db)
    real_password = decrypt_real_password(account.encrypted_real_password)
    messages = await fetch_messages(email, real_password)

    try:
        link = find_matching_link(messages, template=account.templates[0])
    except NotImplementedError:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="Логика шаблона ещё не реализована")

    return FetchLinkResponse(found=link is not None, link=link)
