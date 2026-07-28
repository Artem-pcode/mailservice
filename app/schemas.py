from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class MailAccountCreate(BaseModel):
    email: EmailStr
    request_password: str = Field(min_length=8, description="Пароль, которым будешь авторизовывать запросы к этому ящику")


class MailAccountOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RevealedPassword(BaseModel):
    email: EmailStr
    real_password: str


class CodeResponse(BaseModel):
    found: bool
    code: str | None = None
    date: datetime | None = None
    timestamp_ago: str | None = None


class LinkResponse(BaseModel):
    found: bool
    link: str | None = None
    date: datetime | None = None
    timestamp_ago: str | None = None