#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_MARKDOWN = REPO_ROOT / 'tests/evals/datasets/system_question_bank.md'
OUTPUT_DIR = REPO_ROOT / 'tests/evals/datasets'


def _slugify(value: str) -> str:
    normalized = re.sub(r'[^a-z0-9]+', '_', value.lower()).strip('_')
    return normalized or 'section'


def _parse_sources(cell: str) -> list[str]:
    sources = re.findall(r'`([^`]+)`', cell)
    if sources:
        return [item.strip() for item in sources if item.strip()]
    return [item.strip() for item in cell.split(',') if item.strip()]


def _parse_markdown_table(lines: list[str], start_index: int) -> tuple[list[dict[str, str]], int]:
    table_lines: list[str] = []
    index = start_index
    while index < len(lines):
        stripped = lines[index].rstrip()
        if stripped.startswith('|'):
            table_lines.append(stripped)
            index += 1
            continue
        if table_lines:
            break
        index += 1
    if len(table_lines) < 3:
        return [], index

    headers = [cell.strip() for cell in table_lines[0].strip('|').split('|')]
    rows: list[dict[str, str]] = []
    for row_line in table_lines[2:]:
        cells = [cell.strip() for cell in row_line.strip('|').split('|')]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells, strict=True)))
    return rows, index


def _parse_question_bank(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding='utf-8').splitlines()
    entries: list[dict[str, Any]] = []
    current_section = 'uncategorized'
    current_section_slug = 'uncategorized'
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if line.startswith('## '):
            current_section = line[3:].strip()
            current_section_slug = _slugify(re.sub(r'^\d+\.\s*', '', current_section))
            index += 1
            continue
        if line.startswith('| ID |'):
            rows, next_index = _parse_markdown_table(lines, index)
            for row in rows:
                entries.append(
                    {
                        'question_id': row.get('ID', '').strip(),
                        'profile': row.get('Perfil', '').strip().lower(),
                        'difficulty': row.get('Dificuldade', '').strip().lower(),
                        'form': row.get('Forma', '').strip().lower(),
                        'sources': _parse_sources(row.get('Fontes', '')),
                        'graph_rag': row.get('GraphRAG', '').strip().lower() == 'sim',
                        'prompt': row.get('Pergunta', '').strip(),
                        'section': current_section,
                        'section_slug': current_section_slug,
                    }
                )
            index = next_index
            continue
        index += 1
    return [entry for entry in entries if entry.get('question_id') and entry.get('prompt')]


def _slice_for_entry(entry: dict[str, Any]) -> str:
    sources = set(str(item).strip().lower() for item in entry.get('sources') or [])
    profile = str(entry.get('profile') or '').strip().lower()
    if {'workflow', 'handoff'} & sources:
        return 'workflow'
    if profile in {'responsavel', 'aluno', 'professor', 'staff'}:
        return 'protected'
    if {'identity', 'policy', 'academic', 'finance', 'admin', 'teacher', 'private_docs'} & sources:
        return 'protected'
    return 'public'


def _user_for_profile(profile: str) -> dict[str, Any]:
    normalized = str(profile or '').strip().lower()
    if normalized == 'responsavel':
        return {
            'role': 'guardian',
            'authenticated': True,
            'linked_student_ids': ['stu-lucas', 'stu-ana'],
            'scopes': ['students:read', 'administrative:read', 'financial:read', 'academic:read'],
        }
    if normalized == 'aluno':
        return {
            'role': 'student',
            'authenticated': True,
            'linked_student_ids': ['stu-lucas'],
            'scopes': ['academic:read'],
        }
    if normalized == 'professor':
        return {
            'role': 'teacher',
            'authenticated': True,
            'scopes': ['teacher:schedule:read', 'calendar:read'],
        }
    if normalized == 'staff':
        return {
            'role': 'staff',
            'authenticated': True,
            'scopes': ['documents:private:read', 'workflow:manage'],
        }
    return {'role': 'anonymous', 'authenticated': False, 'scopes': []}


def _telegram_chat_id_for_profile(profile: str) -> int:
    normalized = str(profile or '').strip().lower()
    if normalized == 'responsavel':
        return 1649845499
    if normalized == 'aluno':
        return 1649845500
    if normalized == 'professor':
        return 1649845501
    if normalized == 'staff':
        return 1649845502
    return 777101


def _bucket_for_entry(question_id: str) -> str:
    number = int(question_id[1:])
    if number <= 24:
        return 'system_question_bank_wave_public_grounding.json'
    if number <= 32:
        return 'system_question_bank_wave_public_graphrag.json'
    if number <= 64:
        return 'system_question_bank_wave_protected_ops.json'
    if number <= 80:
        return 'system_question_bank_wave_teacher_workflow.json'
    return 'system_question_bank_wave_sensitive_external.json'


def _threaded_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    current_thread_id = ''
    current_turn_index = 0
    current_anchor = ''

    for entry in entries:
        form = str(entry.get('form') or '')
        is_followup = 'follow-up' in form or 'followup' in form
        if not is_followup or not current_thread_id:
            current_anchor = str(entry['question_id'])
            current_thread_id = f"system_bank:{entry['section_slug']}:{current_anchor}"
            current_turn_index = 1
        else:
            current_turn_index += 1

        output.append(
            {
                'prompt': entry['prompt'],
                'slice': _slice_for_entry(entry),
                'category': entry['section_slug'],
                'thread_id': current_thread_id,
                'turn_index': current_turn_index,
                'telegram_chat_id': _telegram_chat_id_for_profile(str(entry.get('profile') or '')),
                'expected_keywords': [],
                'forbidden_keywords': [],
                'note': (
                    f"{entry['question_id']}|profile={entry['profile']}|difficulty={entry['difficulty']}"
                    f"|form={entry['form']}|sources={','.join(entry['sources'])}|graph_rag={str(entry['graph_rag']).lower()}"
                ),
                'question_id': entry['question_id'],
                'profile': entry['profile'],
                'difficulty': entry['difficulty'],
                'form': entry['form'],
                'sources': entry['sources'],
                'graph_rag': entry['graph_rag'],
                'user': _user_for_profile(str(entry.get('profile') or '')),
            }
        )
    return output


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    parsed_entries = _parse_question_bank(SOURCE_MARKDOWN)
    threaded = _threaded_entries(parsed_entries)

    catalog_path = OUTPUT_DIR / 'system_question_bank_catalog.json'
    combined_path = OUTPUT_DIR / 'system_question_bank_all.json'
    _write_json(catalog_path, parsed_entries)
    _write_json(combined_path, threaded)

    bucketed: dict[str, list[dict[str, Any]]] = {}
    for entry in threaded:
        bucket_name = _bucket_for_entry(str(entry['question_id']))
        bucketed.setdefault(bucket_name, []).append(entry)

    for bucket_name, items in bucketed.items():
        _write_json(OUTPUT_DIR / bucket_name, items)

    print(catalog_path)
    print(combined_path)
    for bucket_name, items in sorted(bucketed.items()):
        print(f'{bucket_name}: entries={len(items)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
