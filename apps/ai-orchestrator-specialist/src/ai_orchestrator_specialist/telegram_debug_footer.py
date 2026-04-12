from __future__ import annotations

from typing import Any

from .models import ConversationChannel, SpecialistSupervisorRequest


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        token = str(value or "").strip()
        if not token or token in seen:
            continue
        seen.add(token)
        ordered.append(token)
    return ordered


def _truncate(values: list[str], *, limit: int = 6) -> str:
    if not values:
        return 'none'
    if len(values) <= limit:
        return ', '.join(values)
    hidden = len(values) - limit
    return f"{', '.join(values[:limit])}, +{hidden} more"


def _trace_context(request: SpecialistSupervisorRequest) -> dict[str, str]:
    payload = request.trace_context if isinstance(request.trace_context, dict) else {}

    def _pick(key: str) -> str:
        return str(payload.get(key) or '').strip()

    conversation_external_id = _pick('conversation_external_id')
    if not conversation_external_id and request.conversation_id:
        conversation_external_id = str(request.conversation_id).strip()
    if not conversation_external_id and request.channel == ConversationChannel.telegram and request.telegram_chat_id is not None:
        conversation_external_id = f'telegram:{request.telegram_chat_id}'

    result = {
        'correlation_id': _pick('correlation_id'),
        'conversation_external_id': conversation_external_id,
        'ingress_service': _pick('ingress_service'),
        'ingress_event_id': _pick('ingress_event_id'),
        'telegram_update_id': _pick('telegram_update_id'),
    }
    return {key: value for key, value in result.items() if value}


def _debug_agents(payload: dict[str, Any]) -> list[str]:
    graph_path = [str(item).strip() for item in payload.get('graph_path', []) if str(item).strip()]
    agents: list[str] = []
    for token in graph_path:
        lowered = token.lower()
        if any(keyword in lowered for keyword in ('specialist', 'planner', 'manager', 'judge', 'router', 'workflow', 'runtime')):
            agents.append(token)
    return _dedupe(agents or ['specialist_supervisor'])


def _debug_resources(payload: dict[str, Any]) -> list[str]:
    resources = [f"tool:{tool}" for tool in payload.get('selected_tools', []) if str(tool).strip()]
    evidence_pack = payload.get('evidence_pack') if isinstance(payload.get('evidence_pack'), dict) else {}
    supports = evidence_pack.get('supports') if isinstance(evidence_pack.get('supports'), list) else []
    for item in supports:
        if not isinstance(item, dict):
            continue
        kind = str(item.get('kind') or 'support').strip()
        label = str(item.get('label') or kind).strip()
        resources.append(f'support:{kind}:{label}')
    citations = payload.get('citations') if isinstance(payload.get('citations'), list) else []
    for item in citations:
        if not isinstance(item, dict):
            continue
        title = str(item.get('document_title') or '').strip()
        if title:
            resources.append(f'doc:{title}')
    return _dedupe(resources)


def _build_trace(payload: dict[str, Any], *, request: SpecialistSupervisorRequest, settings: Any) -> dict[str, Any]:
    evidence_pack = payload.get('evidence_pack') if isinstance(payload.get('evidence_pack'), dict) else {}
    graph_path = [str(item).strip() for item in payload.get('graph_path', []) if str(item).strip()]
    if not graph_path or graph_path[0] != 'specialist_supervisor':
        graph_path = ['specialist_supervisor', *graph_path]
    retrieval_strategy = str(evidence_pack.get('strategy') or payload.get('mode') or 'none')
    return {
        'stack': 'specialist_supervisor',
        'bundle_mode': 'specialist_supervisor',
        'path': graph_path,
        'agents': _debug_agents(payload),
        'resources': _debug_resources(payload),
        'retrieval': {
            'backend': str(payload.get('retrieval_backend') or 'none'),
            'strategy': retrieval_strategy,
            'source_count': int(evidence_pack.get('source_count') or 0),
            'support_count': int(evidence_pack.get('support_count') or 0),
            'citation_count': len(payload.get('citations') or []),
        },
        'trace_context': _trace_context(request),
        'reason': str(payload.get('reason') or 'specialist_local_contract'),
        'used_llm': bool(payload.get('used_llm', False)),
        'llm_stages': [str(item).strip() for item in payload.get('llm_stages', []) if str(item).strip()],
        'final_polish_eligible': bool(payload.get('final_polish_eligible', False)),
        'final_polish_applied': bool(payload.get('final_polish_applied', False)),
        'final_polish_mode': str(payload.get('final_polish_mode') or 'skip'),
        'final_polish_reason': str(payload.get('final_polish_reason') or 'none'),
        'model_profile': str(getattr(settings, 'llm_model_profile', '') or ''),
        'provider': str(getattr(settings, 'llm_provider', '') or ''),
    }


def format_telegram_debug_footer(trace: dict[str, Any]) -> str:
    retrieval = trace.get('retrieval') if isinstance(trace.get('retrieval'), dict) else {}
    llm_value = 'yes' if bool(trace.get('used_llm')) else 'no'
    llm_stages = [str(item).strip() for item in trace.get('llm_stages', []) if str(item).strip()]
    if llm_stages:
        llm_value = f"{llm_value} ({', '.join(llm_stages)})"
    polish_value = str(trace.get('final_polish_mode') or 'skip')
    if bool(trace.get('final_polish_applied')):
        polish_value = f'{polish_value} (applied)'
    elif bool(trace.get('final_polish_eligible')):
        polish_value = f'{polish_value} (eligible)'
    trace_context = trace.get('trace_context') if isinstance(trace.get('trace_context'), dict) else {}
    lines = [
        '[debug]',
        f"stack: specialist_supervisor",
        f"bundle: specialist_supervisor",
        f"corr: {trace_context.get('correlation_id') or 'none'}",
        f"conversation: {trace_context.get('conversation_external_id') or 'none'}",
        f"ingress: {trace_context.get('ingress_service') or 'none'}:{trace_context.get('ingress_event_id') or 'none'}",
        f"path: {' > '.join(trace.get('path', [])) or 'specialist_supervisor'}",
        f"llm: {llm_value}",
        f"final_polish: {polish_value}",
        f"retrieval: backend={retrieval.get('backend') or 'none'}, strategy={retrieval.get('strategy') or 'none'}, sources={int(retrieval.get('source_count') or 0)}, supports={int(retrieval.get('support_count') or 0)}, citations={int(retrieval.get('citation_count') or 0)}",
        f"reason: {trace.get('reason') or 'none'}",
        f"profile: {trace.get('model_profile') or 'default'}",
        f"provider: {trace.get('provider') or 'auto'}",
        f"agents: {_truncate(trace.get('agents', []))}",
        f"resources: {_truncate(trace.get('resources', []))}",
    ]
    return '\n'.join(lines)


def append_telegram_debug_footer(text: str, footer: str) -> str:
    base = str(text or '').rstrip()
    debug = str(footer or '').strip()
    if not debug:
        return base
    if not base:
        return debug
    if debug in base:
        return base
    return f'{base}\n{debug}'


def attach_telegram_debug_footer(payload: dict[str, Any], *, request: SpecialistSupervisorRequest, settings: Any) -> dict[str, Any]:
    if request.channel != ConversationChannel.telegram:
        return payload
    if not bool(getattr(settings, 'feature_flag_telegram_debug_trace_footer_enabled', False)):
        return payload
    text = str(payload.get('message_text') or '')
    if not text.strip():
        return payload
    trace = _build_trace(payload, request=request, settings=settings)
    footer = format_telegram_debug_footer(trace)
    updated = dict(payload)
    updated['message_text'] = append_telegram_debug_footer(text, footer)
    return updated
