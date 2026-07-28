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


class TemplateCreate(BaseModel):
    name: str
    sender_pattern: str
    subject_pattern: str | None = None
    body_pattern: str
    link_extract_regex: str


class TemplateOut(TemplateCreate):
    id: int
    account_id: int

    model_config = {"from_attributes": True}


class FetchLinkResponse(BaseModel):
    found: bool
    link: str | None = None
