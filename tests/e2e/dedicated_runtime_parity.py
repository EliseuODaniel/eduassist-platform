from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from _common import Settings, assert_condition, internal_headers, request, wait_for_health


STACKS = ("langgraph", "python_functions", "llamaindex", "specialist_supervisor")
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "artifacts" / "dedicated-runtime-parity-report.json"


def _status_requires_auth(stack: str) -> bool:
    return stack == "specialist_supervisor"


def _fetch_status(settings: Settings, stack: str) -> dict[str, Any]:
    headers = internal_headers(settings) if _status_requires_auth(stack) else None
    status, _, payload = request(
        "GET",
        f"{settings.stack_runtime_url(stack)}/v1/status",
        headers=headers,
        timeout=20.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), f"{stack}:status_failed")
    return payload


def _validate_runtime_diagnostics(
    *,
    service_name: str,
    diagnostics: dict[str, Any],
    expect_runtime_mode: str | None,
) -> str:
    runtime_mode = str(diagnostics.get("runtimeMode") or "").strip()
    assert_condition(runtime_mode in {"source", "container"}, f"{service_name}:runtime_mode_missing")
    if expect_runtime_mode:
        assert_condition(runtime_mode == expect_runtime_mode, f"{service_name}:runtime_mode_unexpected:{runtime_mode}")
    assert_condition(bool(diagnostics.get("operationalReadiness")), f"{service_name}:operational_readiness_false")
    blockers = diagnostics.get("blockers")
    assert_condition(not blockers, f"{service_name}:runtime_blockers:{blockers}")
    checks = diagnostics.get("checks")
    assert_condition(isinstance(checks, list) and checks, f"{service_name}:runtime_checks_missing")
    invalid_checks: list[str] = []
    for item in checks:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "").strip()
        kind = str(item.get("kind") or "").strip()
        required = bool(item.get("required"))
        if kind == "service" and required and status in {"missing", "invalid", "mode_mismatch"}:
            invalid_checks.append(f"{item.get('name')}={status}")
    assert_condition(not invalid_checks, f"{service_name}:invalid_runtime_checks:{','.join(invalid_checks)}")
    return runtime_mode


def _fetch_gateway_status(settings: Settings) -> dict[str, Any]:
    status, _, payload = request(
        "GET",
        f"{settings.telegram_gateway_url}/v1/status",
        headers=internal_headers(settings),
        timeout=20.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), "telegram_gateway:status_failed")
    return payload


def _fetch_control_plane_status(settings: Settings) -> dict[str, Any]:
    status, _, payload = request(
        "GET",
        f"{settings.ai_orchestrator_url}/v1/status",
        timeout=20.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), "control_plane:status_failed")
    return payload


def _fetch_control_plane_meta(settings: Settings) -> dict[str, Any]:
    status, _, payload = request(
        "GET",
        f"{settings.ai_orchestrator_url}/meta",
        headers=internal_headers(settings),
        timeout=20.0,
    )
    assert_condition(status == 200 and isinstance(payload, dict), "control_plane:meta_failed")
    return payload


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Checagem de paridade source-vs-docker usando runtimeDiagnostics.")
    parser.add_argument("--stack", choices=("all", *STACKS), default="all")
    parser.add_argument("--expect-runtime-mode", choices=("auto", "source", "container"), default="auto")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    settings = Settings()
    targets = STACKS if args.stack == "all" else (args.stack,)
    expect_runtime_mode = None if args.expect_runtime_mode == "auto" else args.expect_runtime_mode

    print(f"Dedicated runtime parity check starting for: {', '.join(targets)}")
    wait_for_health("api-core", f"{settings.api_core_url}/healthz")
    wait_for_health("telegram-gateway", f"{settings.telegram_gateway_url}/healthz")
    wait_for_health("ai-orchestrator", f"{settings.ai_orchestrator_url}/healthz")

    gateway_status = _fetch_gateway_status(settings)
    gateway_diag = gateway_status.get("runtimeDiagnostics")
    assert_condition(isinstance(gateway_diag, dict), "telegram_gateway:runtime_diagnostics_missing")
    gateway_runtime_mode = _validate_runtime_diagnostics(
        service_name="telegram-gateway",
        diagnostics=gateway_diag,
        expect_runtime_mode=expect_runtime_mode,
    )
    if expect_runtime_mode is None:
        expect_runtime_mode = gateway_runtime_mode

    control_plane_status = _fetch_control_plane_status(settings)
    control_plane_meta = _fetch_control_plane_meta(settings)
    control_plane_diag = control_plane_meta.get("runtimeDiagnostics")
    assert_condition(isinstance(control_plane_diag, dict), "control_plane:runtime_diagnostics_missing")
    _validate_runtime_diagnostics(
        service_name="control-plane",
        diagnostics=control_plane_diag,
        expect_runtime_mode=expect_runtime_mode,
    )
    assert_condition(control_plane_status.get("serviceRole") == "control-plane-router", "control_plane:role_unexpected")
    assert_condition(control_plane_status.get("primaryServingRecommended") is False, "control_plane:primary_flag_unexpected")

    results: list[dict[str, Any]] = []
    for stack in targets:
        wait_for_health(stack, f"{settings.stack_runtime_url(stack)}/healthz")
        status_payload = _fetch_status(settings, stack)
        diagnostics = status_payload.get("runtimeDiagnostics")
        assert_condition(isinstance(diagnostics, dict), f"{stack}:runtime_diagnostics_missing")
        _validate_runtime_diagnostics(
            service_name=stack,
            diagnostics=diagnostics,
            expect_runtime_mode=expect_runtime_mode,
        )
        assert_condition(status_payload.get("serviceRole") == "dedicated-stack-runtime", f"{stack}:role_unexpected")
        assert_condition(status_payload.get("primaryServingRecommended") is True, f"{stack}:primary_flag_unexpected")
        results.append(
            {
                "stack": stack,
                "status": status_payload,
            }
        )
        print(f"[ok] parity {stack}")

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "expected_runtime_mode": expect_runtime_mode,
        "gateway": gateway_status,
        "control_plane": control_plane_status,
        "control_plane_meta": control_plane_meta,
        "results": results,
    }
    _write_report(args.output, report)
    print(f"Dedicated runtime parity check finished successfully. Report: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(1)
