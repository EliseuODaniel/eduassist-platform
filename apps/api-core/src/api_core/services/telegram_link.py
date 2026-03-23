from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from api_core.config import get_settings
from api_core.contracts import ActorContext, TelegramLinkChallengeResponse, TelegramLinkConsumeResponse
from api_core.db.models import TelegramAccount, TelegramLinkChallenge, UserTelegramLink
from api_core.services.audit import record_audit_event
from api_core.services.identity import resolve_actor_context


def _hash_challenge_code(code: str) -> str:
    return hashlib.sha256(code.encode('utf-8')).hexdigest()


def create_telegram_link_challenge(session: Session, *, actor: ActorContext) -> TelegramLinkChallengeResponse:
    settings = get_settings()
    now = datetime.now(UTC)

    existing_challenges = session.execute(
        select(TelegramLinkChallenge)
        .where(TelegramLinkChallenge.user_id == actor.user_id)
        .where(TelegramLinkChallenge.consumed_at.is_(None))
        .where(TelegramLinkChallenge.expires_at > now)
    ).scalars()
    for challenge in existing_challenges:
        challenge.consumed_at = now

    raw_code = secrets.token_urlsafe(18)
    challenge = TelegramLinkChallenge(
        user_id=actor.user_id,
        code_hash=_hash_challenge_code(raw_code),
        expires_at=now + timedelta(minutes=settings.telegram_link_ttl_minutes),
        purpose='telegram_link',
    )
    session.add(challenge)
    session.flush()

    record_audit_event(
        session,
        actor_user_id=actor.user_id,
        event_type='telegram_link.challenge_issued',
        resource_type='telegram_link_challenge',
        resource_id=str(challenge.id),
        metadata={'expires_at': challenge.expires_at.isoformat()},
    )

    deep_link = None
    if settings.telegram_bot_username:
        deep_link = f'https://t.me/{settings.telegram_bot_username}?start=link_{raw_code}'

    return TelegramLinkChallengeResponse(
        challenge_code=raw_code,
        expires_at=challenge.expires_at,
        bot_username=settings.telegram_bot_username,
        telegram_deep_link=deep_link,
        telegram_command=f'/start link_{raw_code}',
    )


def consume_telegram_link_challenge(
    session: Session,
    *,
    challenge_code: str,
    telegram_user_id: int | None,
    telegram_chat_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> TelegramLinkConsumeResponse:
    now = datetime.now(UTC)
    challenge = session.execute(
        select(TelegramLinkChallenge)
        .where(TelegramLinkChallenge.code_hash == _hash_challenge_code(challenge_code))
        .where(TelegramLinkChallenge.purpose == 'telegram_link')
    ).scalar_one_or_none()
    if challenge is None:
        raise HTTPException(status_code=404, detail='telegram_link_challenge_not_found')
    if challenge.consumed_at is not None:
        raise HTTPException(status_code=409, detail='telegram_link_challenge_already_consumed')
    if challenge.expires_at <= now:
        raise HTTPException(status_code=410, detail='telegram_link_challenge_expired')

    if telegram_user_id is not None:
        telegram_account = session.execute(
            select(TelegramAccount)
            .where(
                or_(
                    TelegramAccount.telegram_chat_id == telegram_chat_id,
                    TelegramAccount.telegram_user_id == telegram_user_id,
                )
            )
        ).scalars().first()
    else:
        telegram_account = session.execute(
            select(TelegramAccount).where(TelegramAccount.telegram_chat_id == telegram_chat_id)
        ).scalar_one_or_none()
    if telegram_account is None:
        telegram_account = TelegramAccount(
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )
        session.add(telegram_account)
        session.flush()
    else:
        telegram_account.telegram_user_id = telegram_user_id
        telegram_account.telegram_chat_id = telegram_chat_id
        telegram_account.username = username
        telegram_account.first_name = first_name
        telegram_account.last_name = last_name
        telegram_account.is_active = True

    existing_account_link = session.execute(
        select(UserTelegramLink).where(UserTelegramLink.telegram_account_id == telegram_account.id)
    ).scalar_one_or_none()
    if existing_account_link is not None and existing_account_link.user_id != challenge.user_id:
        raise HTTPException(status_code=409, detail='telegram_account_already_linked')

    user_link = session.execute(
        select(UserTelegramLink).where(UserTelegramLink.user_id == challenge.user_id)
    ).scalar_one_or_none()
    if user_link is None:
        user_link = UserTelegramLink(
            user_id=challenge.user_id,
            telegram_account_id=telegram_account.id,
            verification_status='verified',
        )
        session.add(user_link)
    else:
        user_link.telegram_account_id = telegram_account.id
        user_link.verification_status = 'verified'

    challenge.consumed_at = now
    session.flush()

    actor = resolve_actor_context(
        session,
        federated_provider='keycloak',
        federated_subject=_lookup_user_subject(session, challenge.user_id),
    )
    if actor is None:
        actor = resolve_actor_context(session, telegram_chat_id=telegram_chat_id)
    if actor is None:
        raise HTTPException(status_code=404, detail='actor_not_found_after_link')

    record_audit_event(
        session,
        actor_user_id=actor.user_id,
        event_type='telegram_link.completed',
        resource_type='telegram_account',
        resource_id=str(telegram_account.id),
        metadata={
            'telegram_chat_id': telegram_chat_id,
            'telegram_user_id': telegram_user_id,
            'username': username,
        },
    )

    return TelegramLinkConsumeResponse(
        linked=True,
        actor=actor,
        telegram_chat_id=telegram_chat_id,
        telegram_username=username,
    )


def _lookup_user_subject(session: Session, user_id: uuid.UUID) -> str | None:
    from api_core.db.models import FederatedIdentity

    identity = session.execute(
        select(FederatedIdentity.subject)
        .where(FederatedIdentity.user_id == user_id)
        .where(FederatedIdentity.provider == 'keycloak')
    ).scalar_one_or_none()
    return identity
