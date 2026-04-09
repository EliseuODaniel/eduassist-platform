from __future__ import annotations

import re


def _normalize_inline_markdown_bullets(text: str) -> str:
    normalized = str(text or '')
    if '*' not in normalized:
        return normalized
    normalized = re.sub(r'(?:^|\s+)\*\s*\*\*([^*]+)\*\*:\s*', r'\n- \1: ', normalized)
    normalized = re.sub(r'(?:^|\s+)\*\s*([^*\n:][^:\n]{0,80}?):\s*', r'\n- \1: ', normalized)
    normalized = normalized.replace('**', '')
    return normalized


def format_reply_for_channel(*, text: str, channel: str) -> str:
    normalized = str(text or '').replace('\r\n', '\n').replace('\r', '\n')
    normalized = _normalize_inline_markdown_bullets(normalized)
    if channel == 'telegram':
        normalized = normalized.replace('**', '').replace('__', '').replace('`', '')
        normalized = re.sub(r':\s+-\s+(?=[A-ZÀ-Ý][^:\n-]{1,60}:)', ':\n- ', normalized)
        normalized = re.sub(r'\s+-\s+(?=[A-ZÀ-Ý][^:\n-]{1,60}:)', '\n- ', normalized)
        normalized = re.sub(r'^[ \t]*[-*][ \t]+', '- ', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)
        normalized = re.sub(r'[ \t]+\n', '\n', normalized)
        normalized = normalized.strip()
    return normalized
