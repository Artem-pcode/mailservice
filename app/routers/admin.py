from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.models import MailAccount
from app.schemas import RevealedPassword
from app.security import decrypt_real_password

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verify_api_key)])


@router.get("/accounts/{account_id}/reveal", response_model=RevealedPassword)
async def reveal_real_password(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await db.get(MailAccount, account_id)
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Ящик не найден")

    real_password = decrypt_real_password(account.encrypted_real_password)
    return RevealedPassword(email=account.email, real_password=real_password)
