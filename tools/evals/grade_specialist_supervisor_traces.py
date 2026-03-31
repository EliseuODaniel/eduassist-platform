#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import asyncpg


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = "postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist"
DEFAULT_REPORT = REPO_ROOT / "docs/architecture/specialist-supervisor-trace-grading-report.md"
DEFAULT_JSON_REPORT = REPO_ROOT / "docs/architecture/specialist-supervisor-trace-grading-report.json"


@dataclass(slots=True)
class TraceRow:
    created_at: datetime
    conversation_id: str
    channel: str
    request_payload: dict[str, Any]
    response_payload: dict[str, Any]


def _normalize_text(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _contains_any(text: str, terms: set[str] | tuple[str, ...]) -> bool:
    normalized = _normalize_text(text)
    return any(term in normalized for term in terms)


def _human_handoff_requested(message: str) -> bool:
    normalized = _normalize_text(message)
    markers = {
        "atendente humano",
        "atendimento humano",
        "quero falar com um humano",
        "quero falar com humano",
        "quero falar com o financeiro",
        "quero falar com a secretaria",
        "quero falar com a coordenação",
        "quero falar com a coordenacao",
        "quero falar com atendimento",
        "abre um atendimento",
        "abre um chamado",
        "me encaminha",
        "encaminhe",
    }
    return any(marker in normalized for marker in markers)


def _detect_domains(message: str) -> set[str]:
    normalized = _normalize_text(message)
    domains: set[str] = set()
    if _contains_any(normalized, {"nota", "notas", "falta", "faltas", "boletim", "aprovação", "aprovacao", "disciplina"}):
        domains.add("academic")
    if _contains_any(normalized, {"boleto", "boletos", "fatura", "faturas", "mensalidade", "parcelas", "financeiro"}):
        domains.add("finance")
    if _contains_any(normalized, {"visita", "protocolo", "status", "atendimento", "humano", "secretaria"}):
        domains.add("support")
    if _contains_any(normalized, {"bncc", "biblioteca", "curriculo", "currículo", "escola", "matrícula", "matricula"}):
        domains.add("institution")
    return domains


def _flatten_specialists(response_payload: dict[str, Any]) -> list[str]:
    specialist_ids: list[str] = []
    plan = response_payload.get("plan")
    if isinstance(plan, dict):
        for item in plan.get("specialists") or []:
            if isinstance(item, str) and item:
                specialist_ids.append(item)
    for event in response_payload.get("tool_events") or []:
        if not isinstance(event, dict):
            continue
        if event.get("event") != "tool_end":
            continue
        tool_name = str(event.get("tool") or "").strip()
        if tool_name.endswith("_specialist"):
            specialist_ids.append(tool_name)
    return list(dict.fromkeys(specialist_ids))


def _clarification_is_reasonable(message: str, answer: dict[str, Any], response_payload: dict[str, Any]) -> bool:
    normalized = _normalize_text(message)
    if any(token in normalized for token in {"ou", "também", "tambem", "qual aluno", "qual disciplina"}):
        return True
    memory = response_payload.get("operational_memory") or {}
    if any(memory.get(key) for key in ("pending_kind", "pending_prompt")):
        return True
    answer_text = str(answer.get("message_text") or "")
    return "confirme" in _normalize_text(answer_text) or "me diga" in _normalize_text(answer_text)


def _answer_covers_multi_intent(message: str, answer_text: str, detected_domains: set[str]) -> bool:
    if len(detected_domains) < 2:
        return True
    normalized_answer = _normalize_text(answer_text)
    checks: list[bool] = []
    if "academic" in detected_domains:
        checks.append(any(token in normalized_answer for token in {"acadêmico", "academico", "notas", "faltas", "aprov"}))
    if "finance" in detected_domains:
        checks.append(any(token in normalized_answer for token in {"financeiro", "boleto", "fatura", "mensalidade", "parcel"}))
    if "support" in detected_domains:
        checks.append(any(token in normalized_answer for token in {"protocolo", "fila", "status", "atendimento"}))
    return all(checks) if checks else True


def _grade_trace(row: TraceRow) -> dict[str, Any]:
    request_payload = row.request_payload if isinstance(row.request_payload, dict) else {}
    response_payload = row.response_payload if isinstance(row.response_payload, dict) else {}
    answer = response_payload.get("answer") if isinstance(response_payload.get("answer"), dict) else {}
    judge = response_payload.get("judge") if isinstance(response_payload.get("judge"), dict) else {}
    message = str(request_payload.get("message") or "").strip()
    answer_text = str(answer.get("message_text") or "").strip()
    mode = str(answer.get("mode") or "").strip()
    route = str(response_payload.get("route") or "").strip() or str(answer.get("reason") or "").strip()
    evidence_pack = answer.get("evidence_pack") if isinstance(answer.get("evidence_pack"), dict) else {}
    support_count = int(evidence_pack.get("support_count") or len(evidence_pack.get("supports") or []))
    source_count = int(evidence_pack.get("source_count") or 0)
    specialist_ids = _flatten_specialists(response_payload)
    detected_domains = _detect_domains(message)
    issues: list[str] = []

    grounding_score = float(judge.get("grounding_score") or 0.0)
    completeness_score = float(judge.get("completeness_score") or 0.0)
    if support_count > 0:
        grounding_score = max(grounding_score, 1.0)
    elif specialist_ids:
        grounding_score = max(grounding_score, 0.75)

    if answer_text and mode != "clarify":
        completeness_score = max(completeness_score, 0.85)

    if _human_handoff_requested(message):
        handoff_opened = mode == "handoff" or "protocolo:" in _normalize_text(answer_text)
        if not handoff_opened:
            issues.append("human_handoff_not_opened")

    if len(detected_domains) >= 2 and not _answer_covers_multi_intent(message, answer_text, detected_domains):
        issues.append("multi_intent_partial")

    if mode == "clarify" and not _clarification_is_reasonable(message, answer, response_payload):
        issues.append("clarification_overuse")

    if detected_domains & {"institution", "academic", "finance", "support"} and support_count == 0 and mode not in {"handoff", "deny"}:
        issues.append("grounding_weak")

    normalized_answer = _normalize_text(answer_text)
    if any(token in normalized_answer for token in {"modelo de linguagem", "treinado pelo google", "trained by"}):
        issues.append("persona_leak")

    if any(token in normalized_answer for token in {"nao consegui", "não consegui", "ainda nao consegui", "ainda não consegui"}):
        issues.append("fallback_language")

    base = 55.0 + grounding_score * 25.0 + completeness_score * 15.0
    if answer_text:
        base += 5.0
    penalty_map = {
        "human_handoff_not_opened": 30.0,
        "multi_intent_partial": 20.0,
        "clarification_overuse": 15.0,
        "grounding_weak": 12.0,
        "persona_leak": 18.0,
        "fallback_language": 10.0,
    }
    penalty = sum(penalty_map[item] for item in issues)
    grade = max(0.0, min(100.0, round(base - penalty, 1)))
    return {
        "created_at": row.created_at.isoformat(),
        "conversation_id": row.conversation_id,
        "channel": row.channel,
        "message": message,
        "route": route,
        "mode": mode,
        "answer_text": answer_text,
        "specialists": specialist_ids,
        "detected_domains": sorted(detected_domains),
        "grounding_score": round(grounding_score, 2),
        "completeness_score": round(completeness_score, 2),
        "trace_grade": grade,
        "issues": issues,
    }


def _recommendations(issue_counter: Counter[str]) -> list[str]:
    mapping = {
        "human_handoff_not_opened": "Promover regra mais forte para encaminhamento humano tool-first com fila e protocolo antes de qualquer resposta textual.",
        "multi_intent_partial": "Fortalecer decomposicao e composicao multi-intent para nao perder um dominio pedido no mesmo turno.",
        "clarification_overuse": "Reduzir clarificacao desnecessaria e usar memoria operacional/grounded tools antes de perguntar de novo.",
        "grounding_weak": "Exigir EvidencePack ou specialist_results em perguntas institucionais, academicas, financeiras e de suporte.",
        "persona_leak": "Bloquear regressao de persona e reforcar a identidade do EduAssist no manager e no judge.",
        "fallback_language": "Substituir linguagem de fallback por respostas deterministicamente grounded ou handoff real quando apropriado.",
    }
    ranked = issue_counter.most_common(5)
    return [mapping[item] for item, _count in ranked if item in mapping]


async def _fetch_rows(*, database_url: str, limit: int, hours: int, conversation_id: str | None) -> list[TraceRow]:
    threshold = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hours)
    conn = await asyncpg.connect(database_url)
    try:
        rows = await conn.fetch(
            """
            select
              tc.created_at,
              c.external_thread_id,
              c.channel,
              tc.request_payload,
              tc.response_payload
            from conversation.tool_calls tc
            join conversation.conversations c on c.id = tc.conversation_id
            where tc.tool_name = 'specialist_supervisor.trace'
              and tc.created_at >= $1
              and ($2::text is null or c.external_thread_id = $2)
            order by tc.created_at desc
            limit $3
            """,
            threshold,
            conversation_id,
            limit,
        )
    finally:
        await conn.close()
    result: list[TraceRow] = []
    for row in rows:
        request_payload = row["request_payload"] if isinstance(row["request_payload"], dict) else json.loads(row["request_payload"] or "{}")
        response_payload = row["response_payload"] if isinstance(row["response_payload"], dict) else json.loads(row["response_payload"] or "{}")
        result.append(
            TraceRow(
                created_at=row["created_at"],
                conversation_id=str(row["external_thread_id"]),
                channel=str(row["channel"]),
                request_payload=request_payload,
                response_payload=response_payload,
            )
        )
    return result


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Specialist Supervisor Trace Grading Report", ""]
    lines.append(f"Generated at: {payload['generated_at']}")
    lines.append("")
    lines.append(f"Window: last `{payload['hours']}h`, limit `{payload['limit']}`")
    if payload.get("conversation_id"):
        lines.append(f"Conversation filter: `{payload['conversation_id']}`")
        lines.append("")
    summary = payload["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Traces analyzed: `{summary['count']}`")
    lines.append(f"- Average trace grade: `{summary['trace_grade_avg']}`")
    lines.append(f"- Average grounding score: `{summary['grounding_score_avg']}`")
    lines.append(f"- Average completeness score: `{summary['completeness_score_avg']}`")
    lines.append("")
    lines.append("## Top Issues")
    lines.append("")
    for issue, count in summary["issues"]:
        lines.append(f"- `{issue}`: `{count}`")
    if not summary["issues"]:
        lines.append("- nenhum")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for item in payload["recommendations"]:
        lines.append(f"- {item}")
    if not payload["recommendations"]:
        lines.append("- Nenhuma recomendacao critica nesta janela.")
    lines.append("")
    lines.append("## By Route")
    lines.append("")
    lines.append("| Route | Count | Avg grade |")
    lines.append("| --- | --- | --- |")
    for route, bucket in payload["by_route"].items():
        lines.append(f"| `{route}` | `{bucket['count']}` | `{bucket['trace_grade_avg']}` |")
    lines.append("")
    lines.append("## Recent Traces")
    lines.append("")
    for item in payload["traces"]:
        lines.append(f"### {item['message']}")
        lines.append("")
        lines.append(f"- When: `{item['created_at']}`")
        lines.append(f"- Conversation: `{item['conversation_id']}`")
        lines.append(f"- Route: `{item['route']}`")
        lines.append(f"- Mode: `{item['mode']}`")
        lines.append(f"- Specialists: `{', '.join(item['specialists']) or 'nenhum'}`")
        lines.append(f"- Grade: `{item['trace_grade']}`")
        if item["issues"]:
            lines.append(f"- Issues: `{', '.join(item['issues'])}`")
        lines.append(f"- Answer: {item['answer_text']}")
        lines.append("")
    return "\n".join(lines)


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Grade recent specialist supervisor traces for controlled evolution.")
    parser.add_argument("--database-url", default=DEFAULT_DATABASE_URL)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--conversation-id", default=None)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--json-report", default=str(DEFAULT_JSON_REPORT))
    args = parser.parse_args()

    rows = await _fetch_rows(
        database_url=args.database_url,
        limit=args.limit,
        hours=args.hours,
        conversation_id=args.conversation_id,
    )
    traces = [_grade_trace(row) for row in rows]
    issue_counter: Counter[str] = Counter()
    by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in traces:
        issue_counter.update(item["issues"])
        by_route[item["route"] or "unknown"].append(item)

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "hours": args.hours,
        "limit": args.limit,
        "conversation_id": args.conversation_id,
        "summary": {
            "count": len(traces),
            "trace_grade_avg": round(sum(item["trace_grade"] for item in traces) / max(1, len(traces)), 1),
            "grounding_score_avg": round(sum(item["grounding_score"] for item in traces) / max(1, len(traces)), 2),
            "completeness_score_avg": round(sum(item["completeness_score"] for item in traces) / max(1, len(traces)), 2),
            "issues": issue_counter.most_common(),
        },
        "recommendations": _recommendations(issue_counter),
        "by_route": {
            route: {
                "count": len(items),
                "trace_grade_avg": round(sum(item["trace_grade"] for item in items) / max(1, len(items)), 1),
            }
            for route, items in by_route.items()
        },
        "traces": traces,
    }

    report_path = Path(args.report)
    json_path = Path(args.json_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_markdown(payload), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(_main())
