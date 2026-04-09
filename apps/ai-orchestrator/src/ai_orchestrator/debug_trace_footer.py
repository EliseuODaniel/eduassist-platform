from __future__ import annotations

from typing import Any

from eduassist_observability import canonicalize_evidence_strategy, canonicalize_risk_flags

from .models import ConversationChannel, MessageResponse, MessageResponseRequest
from .service_settings import Settings


def _dedupe_debug_items(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in values:
        normalized = str(raw or '').strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _truncate_debug_list(values: list[str], *, limit: int = 6) -> str:
    if not values:
        return 'none'
    if len(values) <= limit:
        return ', '.join(values)
    hidden = len(values) - limit
    return f"{', '.join(values[:limit])}, +{hidden} more"


def _debug_agents_for_response(*, response: MessageResponse, stack_name: str) -> list[str]:
    candidates: list[str] = []
    for node in response.graph_path:
        token = str(node or '').strip()
        lowered = token.lower()
        if any(
            keyword in lowered
            for keyword in (
                'specialist',
                'planner',
                'manager',
                'judge',
                'composer',
                'critic',
                'router',
                'supervisor',
                'workflow',
                'kernel',
            )
        ):
            candidates.append(token)
    if not candidates:
        candidates.append(stack_name)
    return _dedupe_debug_items(candidates)


def _debug_resources_for_response(response: MessageResponse) -> list[str]:
    resources: list[str] = []
    resources.extend(f'tool:{tool}' for tool in response.selected_tools)
    if response.evidence_pack is not None:
        for support in response.evidence_pack.supports:
            label = str(support.label or support.kind or 'support').strip()
            kind = str(support.kind or 'support').strip()
            resources.append(f'support:{kind}:{label}')
    for citation in response.citations:
        title = str(citation.document_title or '').strip()
        if title:
            resources.append(f'doc:{title}')
    return _dedupe_debug_items(resources)


def _base_debug_trace(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    stack_name: str,
    bundle_mode: str,
) -> dict[str, Any]:
    raw_path_nodes = [str(item).strip() for item in (response.graph_path or []) if str(item).strip()]
    path_nodes = list(raw_path_nodes)
    if stack_name == 'langgraph':
        classify_indexes = [index for index, item in enumerate(path_nodes) if item == 'classify_request']
        if len(classify_indexes) > 1:
            path_nodes = path_nodes[classify_indexes[-1]:]
    if not path_nodes or path_nodes[0] != stack_name:
        path_nodes = [stack_name, *path_nodes]
    agents = _debug_agents_for_response(response=response, stack_name=stack_name)
    resources = _debug_resources_for_response(response)
    evidence_pack = response.evidence_pack
    retrieval: dict[str, Any] = {
        'backend': response.retrieval_backend.value,
        'strategy': canonicalize_evidence_strategy(
            evidence_pack.strategy if evidence_pack is not None else 'none',
            retrieval_backend=response.retrieval_backend.value,
        ),
        'source_count': evidence_pack.source_count if evidence_pack is not None else 0,
        'support_count': evidence_pack.support_count if evidence_pack is not None else 0,
        'citation_count': len(response.citations),
    }
    return {
        'channel': request.channel.value,
        'stack': stack_name,
        'bundle_mode': bundle_mode,
        'path': path_nodes,
        'raw_path': raw_path_nodes,
        'agents': agents,
        'resources': resources,
        'selected_tools': list(response.selected_tools),
        'risk_flags': canonicalize_risk_flags(response.risk_flags),
        'retrieval': retrieval,
        'reason': response.reason,
        'used_llm': bool(getattr(response, 'used_llm', False)),
        'llm_stages': [str(item).strip() for item in (response.llm_stages or []) if str(item).strip()],
        'final_polish_eligible': bool(getattr(response, 'final_polish_eligible', False)),
        'final_polish_applied': bool(getattr(response, 'final_polish_applied', False)),
        'final_polish_mode': str(getattr(response, 'final_polish_mode', '') or ''),
        'final_polish_reason': str(getattr(response, 'final_polish_reason', '') or ''),
        'final_polish_changed_text': bool(getattr(response, 'final_polish_changed_text', False)),
        'final_polish_preserved_fallback': bool(getattr(response, 'final_polish_preserved_fallback', False)),
        'answer_experience_eligible': bool(getattr(response, 'answer_experience_eligible', False)),
        'answer_experience_applied': bool(getattr(response, 'answer_experience_applied', False)),
        'answer_experience_reason': str(getattr(response, 'answer_experience_reason', '') or ''),
        'answer_experience_provider': str(getattr(response, 'answer_experience_provider', '') or ''),
        'answer_experience_model': str(getattr(response, 'answer_experience_model', '') or ''),
        'context_repair_applied': bool(getattr(response, 'context_repair_applied', False)),
        'context_repair_action': str(getattr(response, 'context_repair_action', '') or ''),
        'context_repair_reason': str(getattr(response, 'context_repair_reason', '') or ''),
        'retrieval_retry_applied': bool(getattr(response, 'retrieval_retry_applied', False)),
        'retrieval_retry_reason': str(getattr(response, 'retrieval_retry_reason', '') or ''),
    }


def build_debug_trace_for_bundle(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    bundle: Any,
) -> dict[str, Any]:
    stack_name = str(getattr(getattr(bundle, 'primary', None), 'name', '') or 'unknown')
    bundle_mode = str(getattr(bundle, 'mode', '') or stack_name)
    trace = _base_debug_trace(
        request=request,
        response=response,
        stack_name=stack_name,
        bundle_mode=bundle_mode,
    )
    if isinstance(getattr(bundle, 'experiment', None), dict):
        trace['experiment'] = dict(bundle.experiment)
    return trace


def build_debug_trace_for_stack(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    stack_name: str,
) -> dict[str, Any]:
    return _base_debug_trace(
        request=request,
        response=response,
        stack_name=stack_name,
        bundle_mode=stack_name,
    )


def format_telegram_debug_footer(trace: dict[str, Any]) -> str:
    path = [str(item).strip() for item in trace.get('path', []) if str(item).strip()]
    agents = [str(item).strip() for item in trace.get('agents', []) if str(item).strip()]
    resources = [str(item).strip() for item in trace.get('resources', []) if str(item).strip()]
    retrieval = trace.get('retrieval') if isinstance(trace.get('retrieval'), dict) else {}
    retrieval_parts = [
        f"backend={str(retrieval.get('backend') or 'none')}",
        f"strategy={str(retrieval.get('strategy') or 'none')}",
        f"sources={int(retrieval.get('source_count') or 0)}",
        f"supports={int(retrieval.get('support_count') or 0)}",
        f"citations={int(retrieval.get('citation_count') or 0)}",
    ]
    llm_stages = [str(item).strip() for item in trace.get('llm_stages', []) if str(item).strip()]
    llm_value = 'yes' if bool(trace.get('used_llm')) else 'no'
    if llm_stages:
        llm_value = f"{llm_value} ({', '.join(llm_stages)})"
    polish_mode = str(trace.get('final_polish_mode') or 'skip')
    polish_reason = str(trace.get('final_polish_reason') or 'none')
    polish_value = polish_mode
    if bool(trace.get('final_polish_applied')):
        polish_value = f"{polish_value} (applied)"
    elif bool(trace.get('final_polish_eligible')):
        polish_value = f"{polish_value} (eligible)"
    if bool(trace.get('final_polish_preserved_fallback')):
        polish_value = f"{polish_value}, rollback"
    answer_experience_value = 'off'
    if bool(trace.get('answer_experience_eligible')):
        answer_experience_value = 'eligible'
    if bool(trace.get('answer_experience_applied')):
        answer_experience_value = 'applied'
    answer_experience_provider = str(trace.get('answer_experience_provider') or 'none')
    answer_experience_model = str(trace.get('answer_experience_model') or 'none')
    answer_experience_reason = str(trace.get('answer_experience_reason') or 'none')
    context_repair_action = str(trace.get('context_repair_action') or 'none')
    context_repair_reason = str(trace.get('context_repair_reason') or 'none')
    context_repair_value = 'off'
    if bool(trace.get('context_repair_applied')):
        context_repair_value = 'applied'
    elif context_repair_action != 'none':
        context_repair_value = f'planned:{context_repair_action}'
    retrieval_retry_value = 'yes' if bool(trace.get('retrieval_retry_applied')) else 'no'
    lines = [
        '',
        '[debug]',
        f"stack: {trace.get('stack') or 'unknown'}",
        f"bundle: {trace.get('bundle_mode') or 'unknown'}",
        f"path: {' > '.join(path) if path else 'none'}",
        f"llm: {llm_value}",
        f"final_polish: {polish_value}",
        f"answer_experience: {answer_experience_value} ({answer_experience_provider}/{answer_experience_model})",
        f"context_repair: {context_repair_value}",
        f"retrieval_retry: {retrieval_retry_value}",
        f"agents: {_truncate_debug_list(agents)}",
        f"resources: {_truncate_debug_list(resources)}",
        f"retrieval: {', '.join(retrieval_parts)}",
        f"reason: {str(trace.get('reason') or 'none')}",
        f"final_polish_reason: {polish_reason}",
        f"answer_experience_reason: {answer_experience_reason}",
        f"context_repair_reason: {context_repair_reason}",
    ]
    return '\n'.join(lines)


def append_telegram_debug_footer(text: str, footer: str) -> str:
    combined = f'{text}{footer}'
    max_length = 4096
    if len(combined) <= max_length:
        return combined
    overflow = len(combined) - max_length
    available_footer = max(0, len(footer) - overflow - len('\n[debug truncated]'))
    if available_footer <= 0:
        return text
    return f"{text}{footer[:available_footer]}\n[debug truncated]"


def attach_telegram_debug_trace_for_stack(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    stack_name: str,
    settings: Settings,
) -> MessageResponse:
    if request.channel != ConversationChannel.telegram:
        return response
    if not settings.feature_flag_telegram_debug_trace_footer_enabled:
        return response
    trace = build_debug_trace_for_stack(request=request, response=response, stack_name=stack_name)
    footer = format_telegram_debug_footer(trace)
    return response.model_copy(
        update={
            'message_text': append_telegram_debug_footer(response.message_text, footer),
            'debug_trace': trace,
        }
    )


def attach_telegram_debug_trace_for_bundle(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    bundle: Any,
    settings: Settings,
) -> MessageResponse:
    if request.channel != ConversationChannel.telegram:
        return response
    if not settings.feature_flag_telegram_debug_trace_footer_enabled:
        return response
    trace = build_debug_trace_for_bundle(request=request, response=response, bundle=bundle)
    footer = format_telegram_debug_footer(trace)
    return response.model_copy(
        update={
            'message_text': append_telegram_debug_footer(response.message_text, footer),
            'debug_trace': trace,
        }
    )
