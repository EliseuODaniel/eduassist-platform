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


def infer_request_slice(request: Any) -> str:
    if _support_shadow_slice(request):
        return 'support'
    if _workflow_shadow_slice(request):
        return 'workflow'
    if _protected_shadow_slice(request):
        return 'protected'
    return 'public'


class CrewAIEngine(ResponseEngine):
    name = 'crewai'
    ready = False

    def __init__(self, *, fallback_engine: ResponseEngine | None = None) -> None:
        self._fallback_engine = fallback_engine

    async def _call_remote_pilot(self, *, request: Any, settings: Any, slice_name: str) -> dict[str, Any] | None:
        pilot_url = str(getattr(settings, 'crewai_pilot_url', '') or '').strip()
        if not pilot_url:
            return None
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
        return payload if isinstance(payload, dict) else None

    async def respond(self, *, request: Any, settings: Any, engine_mode: str | None = None) -> Any:
        from ..graph import build_orchestration_graph, to_preview
        from ..models import MessageResponse
        from ..runtime import (
            _build_suggested_replies,
            _conversation_context_payload,
            _effective_conversation_id,
            _fetch_actor_context,
            _fetch_conversation_context,
            _fetch_public_school_profile,
            _map_request,
            _persist_conversation_turn,
            _persist_operational_trace,
            _user_context_from_actor,
        )

        slice_name = infer_request_slice(request)
        try:
            payload = await self._call_remote_pilot(request=request, settings=settings, slice_name=slice_name)
        except Exception:
            logger.exception('crewai_primary_http_failed')
            payload = None
        answer_text = ''
        if isinstance(payload, dict):
            metadata = payload.get('metadata')
            if isinstance(metadata, dict):
                answer = metadata.get('answer')
                if isinstance(answer, dict) and isinstance(answer.get('answer_text'), str):
                    answer_text = str(answer['answer_text'])
        if not answer_text:
            from ..runtime import generate_message_response

            logger.warning('crewai_engine_primary_fallback_to_langgraph')
            return await generate_message_response(
                request=request,
                settings=settings,
                engine_name='crewai_stub',
                engine_mode=str(engine_mode or getattr(settings, 'orchestrator_engine', self.name) or self.name),
            )

        actor = await _fetch_actor_context(settings=settings, telegram_chat_id=getattr(request, 'telegram_chat_id', None))
        effective_user = _user_context_from_actor(actor) if actor else request.user
        effective_conversation_id = _effective_conversation_id(request)
        conversation_context = await _fetch_conversation_context(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
        )
        context_payload = _conversation_context_payload(conversation_context)
        school_profile = await _fetch_public_school_profile(settings=settings)
        graph = build_orchestration_graph(settings.graph_rag_enabled)
        state = graph.invoke({'request': _map_request(request, effective_user)})
        preview = to_preview(state)
        suggested_replies = _build_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=context_payload,
        )
        await _persist_conversation_turn(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            actor=actor,
            user_message=request.message,
            assistant_message=answer_text,
        )
        await _persist_operational_trace(
            settings=settings,
            conversation_external_id=effective_conversation_id,
            channel=request.channel.value,
            engine_name=self.name,
            engine_mode=str(engine_mode or self.name),
            actor=actor,
            preview=preview,
            school_profile=school_profile,
            conversation_context=context_payload,
            public_plan=None,
            request_message=request.message,
            message_text=answer_text,
            citations_count=0,
            suggested_reply_count=len(suggested_replies),
            visual_asset_count=0,
            answer_verifier_valid=True,
            answer_verifier_reason='',
            answer_verifier_fallback_used=False,
            deterministic_fallback_available=False,
            answer_verifier_judge_used=False,
        )
        return MessageResponse(
            message_text=answer_text,
            mode=preview.mode,
            classification=preview.classification,
            retrieval_backend=preview.retrieval_backend,
            selected_tools=preview.selected_tools,
            citations=[],
            visual_assets=[],
            suggested_replies=suggested_replies,
            calendar_events=[],
            needs_authentication=preview.needs_authentication,
            graph_path=preview.graph_path,
            risk_flags=preview.risk_flags,
            reason=preview.reason,
        )

    async def shadow_compare(self, *, request: Any, settings: Any) -> ShadowRunResult:
        pilot_url = str(getattr(settings, 'crewai_pilot_url', '') or '').strip()
        if pilot_url:
            slice_name = infer_request_slice(request)
            try:
                payload = await self._call_remote_pilot(request=request, settings=settings, slice_name=slice_name)
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
