from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_core.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Role(TimestampMixin, Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'identity'}

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'identity'}

    role_code: Mapped[str] = mapped_column(ForeignKey('identity.roles.code'), nullable=False)
    external_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone_number: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(30), default='active', nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    role: Mapped[Role] = relationship()


class TelegramAccount(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'telegram_accounts'
    __table_args__ = (
        UniqueConstraint('telegram_user_id'),
        UniqueConstraint('telegram_chat_id'),
        {'schema': 'identity'},
    )

    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger)
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100))
    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class UserTelegramLink(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'user_telegram_links'
    __table_args__ = (
        UniqueConstraint('user_id'),
        UniqueConstraint('telegram_account_id'),
        {'schema': 'identity'},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('identity.users.id'), nullable=False)
    telegram_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('identity.telegram_accounts.id'),
        nullable=False,
    )
    verification_status: Mapped[str] = mapped_column(String(30), default='verified', nullable=False)

    user: Mapped[User] = relationship()
    telegram_account: Mapped[TelegramAccount] = relationship()
