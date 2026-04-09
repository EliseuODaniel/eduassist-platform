from __future__ import annotations

import asyncio

from telegram_gateway import main as gateway_main


def _reset_gateway_state() -> None:
    gateway_main._RECENT_TELEGRAM_UPDATE_IDS.clear()
    gateway_main._LATEST_TELEGRAM_UPDATE_BY_CHAT.clear()


def test_process_message_suppresses_stale_response(monkeypatch) -> None:
    _reset_gateway_state()
    gateway_main._mark_latest_chat_update(123, 200)
    sent_messages: list[str] = []

    async def fake_orchestrate_message(*, chat_id: int, text: str, update_id: int | None):
        return {'message_text': 'resposta antiga'}

    async def fake_send_telegram_message(chat_id: int, text: str, *, reply_markup=None) -> bool:
        sent_messages.append(text)
        return True

    monkeypatch.setattr(gateway_main, '_orchestrate_message', fake_orchestrate_message)
    monkeypatch.setattr(gateway_main, '_send_telegram_message', fake_send_telegram_message)

    asyncio.run(
        gateway_main._process_telegram_text_message(
            chat_id=123,
            text='pergunta antiga',
            update_id=199,
        )
    )

    assert sent_messages == []


def test_process_message_sends_current_response(monkeypatch) -> None:
    _reset_gateway_state()
    gateway_main._mark_latest_chat_update(123, 200)
    sent_messages: list[str] = []

    async def fake_orchestrate_message(*, chat_id: int, text: str, update_id: int | None):
        return {'message_text': 'resposta atual'}

    async def fake_send_telegram_message(chat_id: int, text: str, *, reply_markup=None) -> bool:
        sent_messages.append(text)
        return True

    monkeypatch.setattr(gateway_main, '_orchestrate_message', fake_orchestrate_message)
    monkeypatch.setattr(gateway_main, '_send_telegram_message', fake_send_telegram_message)

    asyncio.run(
        gateway_main._process_telegram_text_message(
            chat_id=123,
            text='pergunta nova',
            update_id=200,
        )
    )

    assert sent_messages == ['resposta atual']


def test_process_message_retries_orchestrator_once(monkeypatch) -> None:
    _reset_gateway_state()
    gateway_main._mark_latest_chat_update(123, 200)
    sent_messages: list[str] = []
    calls = {'count': 0}

    async def fake_orchestrate_message(*, chat_id: int, text: str, update_id: int | None):
        calls['count'] += 1
        if calls['count'] == 1:
            raise gateway_main.httpx.ReadTimeout('timeout')
        return {'message_text': 'resposta apos retry'}

    async def fake_send_telegram_message(chat_id: int, text: str, *, reply_markup=None) -> bool:
        sent_messages.append(text)
        return True

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(gateway_main, '_orchestrate_message', fake_orchestrate_message)
    monkeypatch.setattr(gateway_main, '_send_telegram_message', fake_send_telegram_message)
    monkeypatch.setattr(gateway_main.asyncio, 'sleep', fake_sleep)

    asyncio.run(
        gateway_main._process_telegram_text_message(
            chat_id=123,
            text='pergunta nova',
            update_id=200,
        )
    )

    assert calls['count'] == 2
    assert sent_messages == ['resposta apos retry']


def test_process_message_falls_back_after_retry_failure(monkeypatch) -> None:
    _reset_gateway_state()
    gateway_main._mark_latest_chat_update(123, 200)
    sent_messages: list[str] = []
    calls = {'count': 0}

    async def fake_orchestrate_message(*, chat_id: int, text: str, update_id: int | None):
        calls['count'] += 1
        raise gateway_main.httpx.ReadTimeout('timeout')

    async def fake_send_telegram_message(chat_id: int, text: str, *, reply_markup=None) -> bool:
        sent_messages.append(text)
        return True

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(gateway_main, '_orchestrate_message', fake_orchestrate_message)
    monkeypatch.setattr(gateway_main, '_send_telegram_message', fake_send_telegram_message)
    monkeypatch.setattr(gateway_main.asyncio, 'sleep', fake_sleep)

    asyncio.run(
        gateway_main._process_telegram_text_message(
            chat_id=123,
            text='pergunta nova',
            update_id=200,
        )
    )

    assert calls['count'] == 2
    assert sent_messages == [
        'Nao consegui consultar a base da escola agora. Tente novamente em instantes ou use o portal institucional.'
    ]
