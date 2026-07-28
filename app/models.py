from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MailAccount(Base):
    __tablename__ = "mail_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    request_password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_real_password: Mapped[str] = mapped_column(String(512), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    templates: Mapped[list["Template"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("mail_accounts.id", ondelete="CASCADE"))

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sender_pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_pattern: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body_pattern: Mapped[str] = mapped_column(String(1024), nullable=False)
    link_extract_regex: Mapped[str] = mapped_column(String(1024), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account: Mapped["MailAccount"] = relationship(back_populates="templates")
