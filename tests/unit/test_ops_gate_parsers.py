from __future__ import annotations

from tools.ops.promotion_gate import _parse_json_excerpt as parse_promotion_json_excerpt
from tools.ops.release_readiness import _parse_json_excerpt as parse_release_json_excerpt


def test_promotion_gate_parser_handles_make_prefixed_json() -> None:
    excerpt = (
        "python3 tools/ops/telegram_webhook.py edge-readiness\n"
        "{\n"
        '  "ok": true,\n'
        '  "edge_mode": "quick_tunnel"\n'
        "}\n"
    )
    parsed = parse_promotion_json_excerpt({"stdout_excerpt": excerpt})
    assert parsed == {"ok": True, "edge_mode": "quick_tunnel"}


def test_release_readiness_parser_handles_make_prefixed_json() -> None:
    excerpt = (
        "make promotion-gate-check\n"
        "{\n"
        '  "ok": true,\n'
        '  "summary": "all green"\n'
        "}\n"
    )
    parsed = parse_release_json_excerpt(excerpt)
    assert parsed == {"ok": True, "summary": "all green"}
