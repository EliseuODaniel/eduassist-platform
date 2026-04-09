from __future__ import annotations

from .service_settings import Settings


_STACK_LOCAL_OVERRIDES: dict[str, dict[str, object]] = {
    'langgraph': {
        'strict_framework_isolation_enabled': True,
        'feature_flag_answer_experience_enabled': True,
        'feature_flag_context_repair_enabled': True,
        'feature_flag_final_polish_enabled': True,
        'feature_flag_final_polish_public_enabled': True,
        'feature_flag_final_polish_protected_enabled': True,
        'candidate_chooser_enabled': True,
        'public_response_cache_enabled': True,
    },
    'python_functions': {
        'strict_framework_isolation_enabled': True,
        'feature_flag_answer_experience_enabled': True,
        'feature_flag_context_repair_enabled': True,
        'feature_flag_final_polish_enabled': True,
        'feature_flag_final_polish_public_enabled': True,
        'feature_flag_final_polish_protected_enabled': True,
        'candidate_chooser_enabled': True,
        'public_response_cache_enabled': True,
    },
    'llamaindex': {
        'strict_framework_isolation_enabled': True,
        'feature_flag_answer_experience_enabled': True,
        'feature_flag_context_repair_enabled': True,
        'feature_flag_final_polish_enabled': True,
        'feature_flag_final_polish_public_enabled': True,
        'feature_flag_final_polish_protected_enabled': True,
        'candidate_chooser_enabled': True,
        'public_response_cache_enabled': True,
    },
}


def build_stack_local_settings(*, base_settings: Settings, stack_name: str) -> Settings:
    overrides = _STACK_LOCAL_OVERRIDES.get(stack_name, {})
    if not overrides:
        return base_settings
    return base_settings.model_copy(update=overrides)


def stack_runtime_overrides(stack_name: str) -> dict[str, object]:
    return dict(_STACK_LOCAL_OVERRIDES.get(stack_name, {}))
