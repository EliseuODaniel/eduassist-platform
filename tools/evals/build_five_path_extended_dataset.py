#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_RANDOM = REPO_ROOT / "tests/evals/datasets/five_path_random_probe_cases.json"
SOURCE_ORCHESTRATOR = REPO_ROOT / "tests/evals/datasets/orchestrator_cases.json"
OUTPUT_DATASET = REPO_ROOT / "tests/evals/datasets/five_path_extended_probe_cases.json"

SELECTED_ORCHESTRATOR_CASE_IDS = [
    "public_institutional_greeting",
    "public_assistant_identity",
    "public_assistant_capabilities",
    "public_service_routing",
    "public_bullying_routing",
    "public_bullying_routing_followup",
    "public_bullying_phone_followup",
    "public_faq_admissions",
    "public_phone_and_fax_multi_attribute",
    "public_school_website",
    "public_parent_meeting_calendar_event",
    "public_director_name",
    "public_director_email_followup_seed",
    "public_director_email_followup",
    "public_approval_kpi",
    "public_negative_requirements_abstention",
    "public_confessional_gap",
    "public_structure_after_greeting_seed",
    "public_structure_after_greeting_followup",
    "guardian_access_scope_query",
    "guardian_actor_identity_query",
    "guardian_academic_student_summary",
    "guardian_academic_followup_same_student",
    "guardian_finance_student_summary",
    "guardian_finance_overdue_empty_state",
    "guardian_finance_identifier_seed",
    "guardian_finance_invoice_identifier_followup",
    "guardian_finance_and_documentation_combined",
    "guardian_profile_update_guidance",
    "guardian_profile_update_phone_followup",
    "guardian_profile_update_documents_followup",
    "guardian_profile_update_next_step_followup",
    "support_institutional_request_workflow",
    "support_institutional_request_update",
    "support_workflow_status_followup",
    "support_workflow_summary_followup",
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _slice_for_case(case_id: str, expected: dict[str, Any], message: str) -> str:
    access_tier = str(expected.get("access_tier") or "").strip().lower()
    domain = str(expected.get("domain") or "").strip().lower()
    normalized = str(message or "").strip().lower()
    if "visit" in case_id or any(term in normalized for term in {"agendar", "visita", "remarcar", "cancelar"}):
        return "workflow"
    if domain == "support" or case_id.startswith("support_"):
        return "support"
    if access_tier in {"authenticated", "sensitive"} or domain in {"academic", "finance"} or case_id.startswith("guardian_"):
        return "protected"
    return "public"


def _category_for_case(expected: dict[str, Any]) -> str:
    domain = str(expected.get("domain") or "institution").strip().lower()
    if domain in {"calendar", "institution", "academic", "finance", "support"}:
        return domain
    return "general"


def _build_from_orchestrator_cases() -> list[dict[str, Any]]:
    raw_cases = _load_json(SOURCE_ORCHESTRATOR)
    by_id = {str(item.get("case_id")): item for item in raw_cases if isinstance(item, dict)}
    thread_turns: dict[str, int] = {}
    entries: list[dict[str, Any]] = []
    for case_id in SELECTED_ORCHESTRATOR_CASE_IDS:
        item = by_id.get(case_id)
        if not item:
            raise SystemExit(f"missing_orchestrator_case:{case_id}")
        request = item.get("request") or {}
        expected = item.get("expected") or {}
        message = str(request.get("message") or "").strip()
        if not message:
            raise SystemExit(f"missing_message:{case_id}")
        thread_id = str(request.get("conversation_id") or f"ext:{case_id}")
        turn_index = thread_turns.get(thread_id, 0) + 1
        thread_turns[thread_id] = turn_index
        expected_keywords = [str(value).strip() for value in expected.get("message_contains") or [] if str(value).strip()]
        forbidden_keywords = [str(value).strip() for value in expected.get("message_excludes") or [] if str(value).strip()]
        entries.append(
            {
                "prompt": message,
                "slice": _slice_for_case(case_id, expected, message),
                "category": _category_for_case(expected),
                "thread_id": thread_id,
                "turn_index": turn_index,
                "telegram_chat_id": request.get("telegram_chat_id"),
                "expected_keywords": expected_keywords,
                "forbidden_keywords": forbidden_keywords,
                "note": case_id,
            }
        )
    return entries


def main() -> int:
    base_entries = _load_json(SOURCE_RANDOM)
    if not isinstance(base_entries, list):
        raise SystemExit("five_path_random_probe_cases_must_be_a_list")
    extended_entries = list(base_entries) + _build_from_orchestrator_cases()
    OUTPUT_DATASET.write_text(
        json.dumps(extended_entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT_DATASET)
    print(f"entries={len(extended_entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
