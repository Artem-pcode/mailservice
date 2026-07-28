from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.models import MailAccount
from app.schemas import MailAccountCreate, MailAccountOut
from app.security import encrypt_real_password, generate_real_password, hash_request_password
from app.services.mailserver import MailserverError, create_mailbox, delete_mailbox

router = APIRouter(prefix="/accounts", tags=["accounts"], dependencies=[Depends(verify_api_key)])


@router.post("", response_model=MailAccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(payload: MailAccountCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(MailAccount).where(MailAccount.email == payload.email))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Ящик с таким email уже существует")

    real_password = generate_real_password()

    try:
        await create_mailbox(payload.email, real_password)
    except MailserverError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    account = MailAccount(
        email=payload.email,
        request_password_hash=hash_request_password(payload.request_password),
        encrypted_real_password=encrypt_real_password(real_password),
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)

    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await db.get(MailAccount, account_id)
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Ящик не найден")

    try:
        await delete_mailbox(account.email)
    except MailserverError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    await db.delete(account)


@router.get("", response_model=list[MailAccountOut])
async def list_accounts(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(MailAccount))
    return result.all()
