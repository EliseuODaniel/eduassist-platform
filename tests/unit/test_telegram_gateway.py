from __future__ import annotations

import asyncio

from telegram_gateway import main as gateway_main


def _reset_gateway_state() -> None:
    gateway_main._RECENT_TELEGRAM_UPDATE_IDS.clear()
    gateway_main._LATEST_TELEGRAM_UPDATE_BY_CHAT.clear()


def test_send_telegram_message_treats_read_timeout_as_delivery_uncertain(monkeypatch) -> None:
    class _FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *_args, **_kwargs):
            raise gateway_main.httpx.ReadTimeout('timeout')

    monkeypatch.setattr(
        gateway_main,
        'get_settings',
        lambda: gateway_main.Settings(
            telegram_bot_token='token',
            telegram_webhook_secret='secret',
            internal_api_token='internal',
        ),
    )
    monkeypatch.setattr(gateway_main.httpx, 'AsyncClient', lambda *args, **kwargs: _FakeClient())

    outcome = asyncio.run(gateway_main._send_telegram_message(123, 'resposta'))
    assert outcome.delivery_uncertain is True
    assert outcome.delivered is False


def test_send_telegram_message_retries_connect_timeout_once(monkeypatch) -> None:
    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {'ok': True, 'result': {'message_id': 99}}

    class _FakeClient:
        def __init__(self):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *_args, **_kwargs):
            self.calls += 1
            if self.calls == 1:
                raise gateway_main.httpx.ConnectTimeout('timeout')
            return _FakeResponse()

    fake_client = _FakeClient()

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(
        gateway_main,
        'get_settings',
        lambda: gateway_main.Settings(
            telegram_bot_token='token',
            telegram_webhook_secret='secret',
            internal_api_token='internal',
        ),
    )
    monkeypatch.setattr(gateway_main.httpx, 'AsyncClient', lambda *args, **kwargs: fake_client)
    monkeypatch.setattr(gateway_main.asyncio, 'sleep', fake_sleep)

    outcome = asyncio.run(gateway_main._send_telegram_message(123, 'resposta'))

    assert outcome.delivered is True
    assert fake_client.calls == 2


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
        return gateway_main.TelegramSendOutcome(delivered=True)

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
        return gateway_main.TelegramSendOutcome(delivered=True)

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
        return gateway_main.TelegramSendOutcome(delivered=True)

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


def test_build_trace_context_is_stable_for_same_update() -> None:
    first = gateway_main._build_trace_context(chat_id=123, text='oi', update_id=456)
    second = gateway_main._build_trace_context(chat_id=123, text='oi', update_id=456)
    assert first == second
    assert first['conversation_external_id'] == 'telegram:123'
    assert first['ingress_service'] == 'telegram-gateway'


def test_orchestrate_message_sends_trace_context(monkeypatch) -> None:
    captured: dict[str, object] = {}

    async def fake_resolve_actor_context(_chat_id: int) -> None:
        return None

    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {'message_text': 'ok'}

    class _FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, _url: str, *, headers=None, json=None):
            captured['headers'] = headers
            captured['json'] = json
            return _FakeResponse()

    monkeypatch.setattr(gateway_main, '_resolve_actor_context', fake_resolve_actor_context)
    monkeypatch.setattr(
        gateway_main,
        'get_settings',
        lambda: gateway_main.Settings(
            telegram_bot_token='token',
            telegram_webhook_secret='secret',
            internal_api_token='internal',
            ai_orchestrator_url='http://runtime:8000',
        ),
    )
    monkeypatch.setattr(gateway_main.httpx, 'AsyncClient', lambda *args, **kwargs: _FakeClient())

    body = asyncio.run(gateway_main._orchestrate_message(chat_id=123, text='oi', update_id=456))

    assert body['message_text'] == 'ok'
    payload = captured['json']
    assert isinstance(payload, dict)
    trace_context = payload.get('trace_context')
    assert isinstance(trace_context, dict)
    assert trace_context['conversation_external_id'] == 'telegram:123'
    assert trace_context['telegram_update_id'] == '456'
