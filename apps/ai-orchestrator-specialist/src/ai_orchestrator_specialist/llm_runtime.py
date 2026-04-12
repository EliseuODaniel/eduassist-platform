from __future__ import annotations

import os
from typing import Any

from agents import RunConfig, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel


def resolve_llm_provider(settings: Any) -> str:
    configured = str(getattr(settings, "llm_provider", "auto") or "auto").strip().lower()
    has_openai = bool(getattr(settings, "openai_api_key", None))
    has_google = bool(getattr(settings, "google_api_key", None))
    if configured == "openai":
        return "openai" if has_openai else "unconfigured"
    if configured in {"google", "gemini", "litellm"}:
        return "gemini_litellm" if has_google else "unconfigured"
    if has_openai:
        return "openai"
    if has_google:
        return "gemini_litellm"
    return "unconfigured"


def effective_llm_model_name(settings: Any) -> str:
    provider = resolve_llm_provider(settings)
    if provider == "openai":
        return str(getattr(settings, "openai_model", "gpt-5.4") or "gpt-5.4")
    google_model = str(getattr(settings, "google_model", "gemini-2.5-flash") or "gemini-2.5-flash").strip()
    if google_model.endswith("-preview"):
        google_model = google_model.removesuffix("-preview")
    if "/" in google_model:
        return google_model
    return f"gemini/{google_model}"


def model_name_for_role(settings: Any, *, role: str) -> str:
    provider = resolve_llm_provider(settings)
    explicit_override = str(getattr(settings, f"{role}_model", "") or "").strip()
    if explicit_override:
        if provider == "gemini_litellm" and "/" not in explicit_override:
            return f"gemini/{explicit_override.removesuffix('-preview')}"
        return explicit_override
    if provider == "openai":
        if role in {"planner", "judge", "guardrail"}:
            return str(
                getattr(settings, "openai_fast_model", None)
                or getattr(settings, "openai_model", "gpt-5.4")
                or "gpt-5.4"
            )
        return str(
            getattr(settings, "openai_reasoning_model", None)
            or getattr(settings, "openai_model", "gpt-5.4")
            or "gpt-5.4"
        )
    if role in {"planner", "judge", "guardrail"}:
        google_override = getattr(settings, "google_fast_model", None)
    else:
        google_override = getattr(settings, "google_reasoning_model", None)
    google_model = str(
        google_override or getattr(settings, "google_model", "gemini-2.5-flash") or "gemini-2.5-flash"
    ).strip()
    if google_model.endswith("-preview"):
        google_model = google_model.removesuffix("-preview")
    return google_model if "/" in google_model else f"gemini/{google_model}"


def agent_model(settings: Any) -> str | LitellmModel:
    provider = resolve_llm_provider(settings)
    if provider == "openai":
        openai_api_key = str(getattr(settings, "openai_api_key", "") or "").strip()
        openai_base_url = str(getattr(settings, "openai_base_url", "") or "").strip()
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        if openai_base_url:
            os.environ["OPENAI_BASE_URL"] = openai_base_url
        return effective_llm_model_name(settings)
    if provider == "gemini_litellm":
        google_api_key = str(getattr(settings, "google_api_key", "") or "").strip()
        if google_api_key:
            os.environ.setdefault("GEMINI_API_KEY", google_api_key)
        return LitellmModel(
            model=effective_llm_model_name(settings),
            api_key=google_api_key or None,
        )
    raise RuntimeError("specialist_supervisor_llm_unconfigured")


def agent_model_for_role(settings: Any, *, role: str) -> str | LitellmModel:
    provider = resolve_llm_provider(settings)
    role_model_name = model_name_for_role(settings, role=role)
    if provider == "openai":
        openai_api_key = str(getattr(settings, "openai_api_key", "") or "").strip()
        openai_base_url = str(getattr(settings, "openai_base_url", "") or "").strip()
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        if openai_base_url:
            os.environ["OPENAI_BASE_URL"] = openai_base_url
        return role_model_name
    if provider == "gemini_litellm":
        google_api_key = str(getattr(settings, "google_api_key", "") or "").strip()
        if google_api_key:
            os.environ.setdefault("GEMINI_API_KEY", google_api_key)
        return LitellmModel(
            model=role_model_name,
            api_key=google_api_key or None,
        )
    raise RuntimeError("specialist_supervisor_llm_unconfigured")


def run_config(settings: Any, *, conversation_id: str) -> RunConfig:
    tracing_disabled = resolve_llm_provider(settings) != "openai"
    set_tracing_disabled(tracing_disabled)
    return RunConfig(
        tracing_disabled=tracing_disabled,
        workflow_name="EduAssist Specialist Supervisor",
        group_id=conversation_id,
        trace_metadata={
            "path": "specialist_supervisor",
            "provider": resolve_llm_provider(settings),
            "model": effective_llm_model_name(settings),
        },
    )
