from __future__ import annotations

import logging
from typing import Any

import httpx

from ..crewai.flow import run_public_shadow_flow
from .base import ResponseEngine, ShadowRunResult

logger = logging.getLogger(__name__)


def _protected_shadow_slice(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '').lower()
    protected_terms = (
        'nota',
        'notas',
        'falta',
        'faltas',
        'frequencia',
        'prova',
        'provas',
        'avaliacao',
        'avaliacoes',
        'financeiro',
        'boleto',
        'pagamento',
        'mensalidade',
        'documentacao',
        'documentos',
        'meus filhos',
        'meu filho',
        'minha filha',
        'estou logado',
        'meu acesso',
        'lucas',
        'ana',
    )
    if any(term in message for term in protected_terms):
        return True
    user = getattr(request, 'user', None)
    if user is not None and bool(getattr(user, 'authenticated', False)):
        return True
    return False


def _support_shadow_slice(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '').lower()
    support_terms = (
        'atendente humano',
        'atendimento humano',
        'quero falar com um humano',
        'preciso falar com um humano',
        'como falo com um atendente',
        'quero falar com o setor',
        'suporte humano',
        'atendente',
        'humano',
        'ticket operacional',
        'atd-',
    )
    return any(term in message for term in support_terms)


def _workflow_shadow_slice(request: Any) -> bool:
    message = str(getattr(request, 'message', '') or '').lower()
    if _support_shadow_slice(request):
        return False
    workflow_terms = (
        'agendar visita',
        'visita',
        'tour',
        'protocolar',
        'protocolo',
        'solicitacao',
        'solicitação',
        'remarcar',
        'reagendar',
        'cancelar a visita',
        'resume meu pedido',
        'status da visita',
        'status do protocolo',
    )
    return any(term in message for term in workflow_terms)


class CrewAIEngine(ResponseEngine):
    name = 'crewai'
    ready = False

    def __init__(self, *, fallback_engine: ResponseEngine | None = None) -> None:
        self._fallback_engine = fallback_engine

    async def respond(self, *, request: Any, settings: Any) -> Any:
        from ..runtime import generate_message_response

        logger.warning('crewai_engine_not_implemented_fallback_to_langgraph')
        return await generate_message_response(
            request=request,
            settings=settings,
            engine_name='crewai_stub',
            engine_mode=str(getattr(settings, 'orchestrator_engine', self.name) or self.name),
        )

    async def shadow_compare(self, *, request: Any, settings: Any) -> ShadowRunResult:
        pilot_url = str(getattr(settings, 'crewai_pilot_url', '') or '').strip()
        if pilot_url:
            if _support_shadow_slice(request):
                slice_name = 'support'
            elif _workflow_shadow_slice(request):
                slice_name = 'workflow'
            else:
                slice_name = 'protected' if _protected_shadow_slice(request) else 'public'
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.post(
                        f'{pilot_url.rstrip("/")}/v1/shadow/{slice_name}',
                        headers={
                            'X-Internal-Api-Token': settings.internal_api_token,
                            'Content-Type': 'application/json',
                        },
                        json={
                            'message': getattr(request, 'message', ''),
                            'conversation_id': getattr(request, 'conversation_id', None),
                            'telegram_chat_id': getattr(request, 'telegram_chat_id', None),
                            'channel': getattr(getattr(request, 'channel', None), 'value', 'telegram'),
                        },
                    )
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    metadata = payload.get('metadata') if isinstance(payload.get('metadata'), dict) else {}
                    metadata = {'shadow_slice': slice_name, **metadata}
                    return ShadowRunResult(
                        engine_name=str(payload.get('engine_name', self.name) or self.name),
                        executed=bool(payload.get('executed')),
                        reason=str(payload.get('reason', '') or ''),
                        metadata=metadata,
                    )
            except Exception as exc:
                logger.exception('crewai_shadow_http_failed')
                return ShadowRunResult(
                    engine_name=self.name,
                    executed=False,
                    reason='crewai_shadow_http_failed',
                    error=str(exc),
                )

        logger.info('crewai_shadow_public_slice_local_scaffold')
        return await run_public_shadow_flow(request=request, settings=settings)
