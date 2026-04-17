from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from eduassist_observability import detect_runtime_mode


REPO_ROOT = Path(__file__).resolve().parents[4]
ROOT_ENV_FILE = REPO_ROOT / '.env'
_INTERNAL_API_TOKEN_PLACEHOLDERS = {'', 'dev-internal-token', 'change-me-internal-token'}

_LOCAL_SOURCE_SERVICE_URLS = {
    'api-core': 'http://127.0.0.1:8001',
    'ai-orchestrator': 'http://127.0.0.1:8002',
    'ai-orchestrator-langgraph': 'http://127.0.0.1:8006',
    'ai-orchestrator-python-functions': 'http://127.0.0.1:8007',
    'ai-orchestrator-llamaindex': 'http://127.0.0.1:8008',
    'qdrant': 'http://127.0.0.1:6333',
}

_LOCAL_SOURCE_DB_URL = 'postgresql://eduassist:eduassist@127.0.0.1:5432/eduassist'


def _replace_url_host(value: str, *, replacements: dict[str, str]) -> str:
    normalized = str(value or '').strip()
    if not normalized:
        return normalized
    parsed = urlparse(normalized)
    host = (parsed.hostname or '').strip().lower()
    replacement_host = replacements.get(host)
    if replacement_host is None:
        return normalized
    netloc = replacement_host
    if parsed.port is not None:
        netloc = f'{replacement_host}:{parsed.port}'
    if parsed.username:
        auth = parsed.username
        if parsed.password:
            auth = f'{auth}:{parsed.password}'
        netloc = f'{auth}@{netloc}'
    return urlunparse(parsed._replace(netloc=netloc))


def _normalize_local_service_url(value: str, *, env_name: str) -> str:
    override = str(os.getenv(env_name, '') or '').strip()
    normalized = str(value or '').strip()
    if override:
        return override
    if not normalized:
        return normalized
    parsed = urlparse(normalized)
    host = (parsed.hostname or '').strip().lower()
    replacement = _LOCAL_SOURCE_SERVICE_URLS.get(host)
    if not replacement:
        return normalized
    replacement_parsed = urlparse(replacement)
    netloc = replacement_parsed.netloc
    if parsed.username:
        auth = parsed.username
        if parsed.password:
            auth = f'{auth}:{parsed.password}'
        netloc = f'{auth}@{netloc}'
    return urlunparse(parsed._replace(scheme=replacement_parsed.scheme, netloc=netloc))


def _normalize_local_database_url(value: str) -> str:
    override = str(os.getenv('DATABASE_URL_LOCAL', '') or '').strip()
    normalized = str(value or '').strip()
    if override:
        return _replace_url_host(
            override,
            replacements={
                'postgres': '127.0.0.1',
                'localhost': '127.0.0.1',
            },
        )
    if not normalized:
        return _LOCAL_SOURCE_DB_URL
    return _replace_url_host(
        normalized,
        replacements={
            'postgres': '127.0.0.1',
            'localhost': '127.0.0.1',
        },
    )


def _normalize_local_qdrant_url(value: str) -> str:
    override = str(os.getenv('QDRANT_URL_LOCAL', '') or '').strip()
    normalized = str(value or '').strip()
    if override:
        return _replace_url_host(
            override,
            replacements={
                'qdrant': '127.0.0.1',
                'localhost': '127.0.0.1',
            },
        )
    if not normalized:
        return _LOCAL_SOURCE_SERVICE_URLS['qdrant']
    return _replace_url_host(
        normalized,
        replacements={
            'qdrant': '127.0.0.1',
            'localhost': '127.0.0.1',
        },
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=('/workspace/.env', str(ROOT_ENV_FILE), '.env'),
        env_ignore_empty=True,
        extra='ignore',
    )

    app_env: str = 'development'
    log_level: str = 'INFO'
    port: int = 8000
    llm_model_profile: str | None = 'gemma4e4b_local'
    llm_provider: str = 'openai'
    api_core_url: str = 'http://api-core:8000'
    internal_api_token: str = 'dev-internal-token'
    internal_workload_identity_mode: str = 'token'
    internal_spiffe_allowed_ids: str = ''
    allow_insecure_internal_api_token: bool = False
    openai_api_key: str | None = None
    openai_base_url: str = 'https://api.openai.com/v1'
    openai_model: str = 'gpt-5.4'
    openai_api_mode: str = 'chat_completions'
    google_api_key: str | None = None
    google_api_base_url: str = 'https://generativelanguage.googleapis.com/v1beta'
    google_model: str = 'gemini-2.5-flash'
    database_url: str = 'postgresql://eduassist:eduassist@postgres:5432/eduassist'
    qdrant_url: str = 'http://qdrant:6333'
    qdrant_documents_collection: str = 'school_documents'
    qdrant_document_summaries_collection: str = 'school_document_summaries'
    llamaindex_qdrant_documents_collection: str = 'school_documents_llamaindex'
    llamaindex_qdrant_document_summaries_collection: str = 'school_document_summaries'
    llamaindex_native_timeout_seconds: float = 20.0
    llamaindex_native_prompt_router_ambiguity_only: bool = True
    llamaindex_native_recursive_retriever_enabled: bool = True
    llamaindex_native_summary_stage_enabled: bool = True
    llamaindex_native_summary_stage_top_k: int = 2
    llamaindex_native_selector_ambiguity_only: bool = True
    llamaindex_native_sentence_optimizer_enabled: bool = True
    llamaindex_native_sentence_optimizer_percentile_cutoff: float = 0.55
    llamaindex_native_long_context_reorder_enabled: bool = True
    document_embedding_model: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    warm_retrieval_on_startup: bool = True
    retrieval_enable_query_variants: bool = True
    retrieval_enable_late_interaction_rerank: bool = True
    retrieval_late_interaction_model: str = 'answerdotai/answerai-colbert-small-v1'
    retrieval_enable_cross_encoder_rerank: bool = True
    retrieval_cross_encoder_model: str = 'jinaai/jina-reranker-v2-base-multilingual'
    retrieval_candidate_pool_size: int = 14
    retrieval_cheap_candidate_pool_size: int = 8
    retrieval_deep_candidate_pool_size: int = 22
    retrieval_rerank_fused_weight: float = 0.35
    retrieval_rerank_late_interaction_weight: float = 0.65
    retrieval_rerank_cross_encoder_weight: float = 0.85
    strict_framework_isolation_enabled: bool = False
    graph_rag_enabled: bool = False
    graph_rag_workspace: str = '/workspace/artifacts/graphrag/eduassist-public-benchmark'
    graph_rag_response_type: str = 'List of 3-5 concise bullet points in Brazilian Portuguese'
    graph_rag_local_chat_api_base: str = 'http://host.docker.internal:18080/v1'
    graph_rag_local_embedding_api_base: str = 'http://host.docker.internal:11435/v1'
    graph_rag_local_chat_api_key: str = 'llama.cpp'
    graph_rag_local_embedding_api_key: str = 'ollama'
    orchestrator_engine: str = 'langgraph'
    feature_flag_primary_orchestration_stack: str | None = None
    control_plane_allow_direct_serving: bool = False
    feature_flag_telegram_debug_trace_footer_enabled: bool = False
    feature_flag_final_polish_enabled: bool = True
    feature_flag_final_polish_public_enabled: bool = True
    feature_flag_final_polish_protected_enabled: bool = False
    feature_flag_final_polish_stacks: str = 'langgraph,llamaindex,python_functions'
    feature_flag_final_polish_budget_ms: int = 600
    feature_flag_final_polish_max_delta_ratio: float = 0.25
    feature_flag_final_polish_telegram_only: bool = False
    feature_flag_final_polish_force_llm: bool = False
    feature_flag_final_polish_debug_metadata_enabled: bool = True
    feature_flag_answer_experience_enabled: bool = True
    feature_flag_answer_experience_channels: str = 'telegram'
    feature_flag_answer_experience_stacks: str = 'langgraph,llamaindex,python_functions,specialist_supervisor'
    feature_flag_answer_experience_public_enabled: bool = True
    feature_flag_answer_experience_protected_enabled: bool = True
    feature_flag_answer_experience_min_chars: int = 24
    feature_flag_answer_surface_refiner_enabled: bool = True
    feature_flag_answer_surface_refiner_stacks: str = 'langgraph,llamaindex,python_functions'
    feature_flag_answer_surface_refiner_channels: str = 'telegram,web'
    feature_flag_context_repair_enabled: bool = True
    feature_flag_context_repair_stacks: str = 'langgraph,llamaindex,python_functions,specialist_supervisor'
    feature_flag_context_repair_retry_top_k: int = 6
    semantic_router_history_budget_tokens: int = 180
    semantic_router_candidate_budget_tokens: int = 220
    grounded_public_history_budget_tokens: int = 180
    grounded_public_evidence_budget_tokens: int = 320
    stack_local_llm_history_budget_tokens: int = 220
    stack_local_llm_evidence_budget_tokens: int = 360
    stack_local_llm_calendar_budget_tokens: int = 140
    answer_experience_provider: str | None = None
    answer_experience_openai_api_key: str | None = None
    answer_experience_openai_base_url: str | None = None
    answer_experience_openai_model: str | None = None
    answer_experience_openai_api_mode: str | None = None
    answer_experience_google_api_key: str | None = None
    answer_experience_google_api_base_url: str | None = None
    answer_experience_google_model: str | None = None
    retrieval_aware_routing_enabled: bool = True
    candidate_chooser_enabled: bool = True
    public_response_cache_enabled: bool = True
    public_response_cache_ttl_seconds: float = 300.0
    public_response_semantic_cache_enabled: bool = True
    public_response_semantic_jaccard_threshold: float = 0.84
    serving_policy_llamaindex_summary_stage_required: bool = True
    serving_policy_specialist_public_premium_enabled: bool = False
    specialist_supervisor_pilot_url: str | None = None
    specialist_supervisor_pilot_timeout_seconds: float = 18.0
    orchestrator_experiment_enabled: bool = False
    orchestrator_experiment_primary_engine: str = 'python_functions'
    orchestrator_experiment_slices: str = ''
    orchestrator_experiment_rollout_percent: int = 0
    orchestrator_experiment_slice_rollouts: str = ''
    orchestrator_experiment_telegram_chat_allowlist: str = ''
    orchestrator_experiment_conversation_allowlist: str = ''
    orchestrator_experiment_allowlist_slices: str = ''
    orchestrator_experiment_require_scorecard: bool = False
    orchestrator_experiment_scorecard_path: str = '/workspace/artifacts/framework-native-scorecard.json'
    orchestrator_experiment_min_primary_engine_score: int = 20
    orchestrator_experiment_require_healthy_pilot: bool = False
    orchestrator_experiment_health_ttl_seconds: int = 15
    langgraph_checkpointer_enabled: bool = True
    langgraph_checkpointer_url: str | None = None
    langgraph_checkpointer_schema: str = 'langgraph_checkpoint'
    langgraph_hitl_enabled: bool = False
    langgraph_hitl_default_slices: str = 'support'
    langgraph_hitl_user_traffic_enabled: bool = False
    langgraph_hitl_user_traffic_slices: str = 'support'
    langgraph_orchestrator_url: str = 'http://ai-orchestrator-langgraph:8000'
    python_functions_orchestrator_url: str = 'http://ai-orchestrator-python-functions:8000'
    llamaindex_orchestrator_url: str = 'http://ai-orchestrator-llamaindex:8000'
    router_forward_timeout_seconds: float = 25.0

    @model_validator(mode='after')
    def _apply_llm_model_profile(self) -> 'Settings':
        profile = str(self.llm_model_profile or '').strip().lower()
        if not profile:
            return self

        if profile in {'gemini_flash_lite', 'gemini_2_5_flash_lite', 'gemini-2.5-flash-lite'}:
            self.llm_provider = 'google'
            if not str(self.google_model or '').strip() or self.google_model == 'gemini-2.5-flash':
                self.google_model = 'gemini-2.5-flash-lite'
            if not str(self.answer_experience_provider or '').strip():
                self.answer_experience_provider = 'google'
            if not str(self.answer_experience_google_model or '').strip():
                self.answer_experience_google_model = self.google_model
            return self

        if profile in {'gemma4e4b_local', 'gemma_4_e4b_local', 'gemma-4-e4b-local'}:
            self.llm_provider = 'openai'
            self.openai_api_mode = 'chat_completions'
            if not str(self.openai_api_key or '').strip():
                self.openai_api_key = 'local-llm'
            if not str(self.openai_base_url or '').strip() or self.openai_base_url == 'https://api.openai.com/v1':
                self.openai_base_url = 'http://local-llm-gemma4e4b:8080/v1'
            if not str(self.openai_model or '').strip() or self.openai_model == 'gpt-5.4':
                self.openai_model = 'ggml-org/gemma-4-E4B-it-GGUF:Q4_K_M'
            if not str(self.answer_experience_provider or '').strip():
                self.answer_experience_provider = 'openai'
            if not str(self.answer_experience_openai_api_key or '').strip():
                self.answer_experience_openai_api_key = self.openai_api_key
            if not str(self.answer_experience_openai_base_url or '').strip():
                self.answer_experience_openai_base_url = self.openai_base_url
            if not str(self.answer_experience_openai_model or '').strip():
                self.answer_experience_openai_model = self.openai_model
            if not str(self.answer_experience_openai_api_mode or '').strip():
                self.answer_experience_openai_api_mode = self.openai_api_mode
            return self

        if profile in {'qwen3_4b_instruct_local', 'qwen_3_4b_instruct_local', 'qwen-3-4b-instruct-local'}:
            self.llm_provider = 'openai'
            self.openai_api_mode = 'chat_completions'
            if not str(self.openai_api_key or '').strip():
                self.openai_api_key = 'local-llm'
            if not str(self.openai_base_url or '').strip() or self.openai_base_url == 'https://api.openai.com/v1':
                self.openai_base_url = 'http://local-llm-qwen3-4b:8080/v1'
            if not str(self.openai_model or '').strip() or self.openai_model == 'gpt-5.4':
                self.openai_model = 'Qwen_Qwen3-4B-Instruct-2507-Q5_K_M.gguf'
            if not str(self.answer_experience_provider or '').strip():
                self.answer_experience_provider = 'openai'
            if not str(self.answer_experience_openai_api_key or '').strip():
                self.answer_experience_openai_api_key = self.openai_api_key
            if not str(self.answer_experience_openai_base_url or '').strip():
                self.answer_experience_openai_base_url = self.openai_base_url
            if not str(self.answer_experience_openai_model or '').strip():
                self.answer_experience_openai_model = self.openai_model
            if not str(self.answer_experience_openai_api_mode or '').strip():
                self.answer_experience_openai_api_mode = self.openai_api_mode
            return self

        return self

    @model_validator(mode='after')
    def _apply_source_mode_network_fallbacks(self) -> 'Settings':
        if detect_runtime_mode() != 'source':
            return self
        self.api_core_url = _normalize_local_service_url(self.api_core_url, env_name='API_CORE_URL_LOCAL')
        self.database_url = _normalize_local_database_url(self.database_url)
        self.qdrant_url = _normalize_local_qdrant_url(self.qdrant_url)
        if self.langgraph_checkpointer_url:
            self.langgraph_checkpointer_url = _normalize_local_database_url(self.langgraph_checkpointer_url)
        self.langgraph_orchestrator_url = _normalize_local_service_url(
            self.langgraph_orchestrator_url,
            env_name='AI_ORCHESTRATOR_LANGGRAPH_URL_LOCAL',
        )
        self.python_functions_orchestrator_url = _normalize_local_service_url(
            self.python_functions_orchestrator_url,
            env_name='AI_ORCHESTRATOR_PYTHON_FUNCTIONS_URL_LOCAL',
        )
        self.llamaindex_orchestrator_url = _normalize_local_service_url(
            self.llamaindex_orchestrator_url,
            env_name='AI_ORCHESTRATOR_LLAMAINDEX_URL_LOCAL',
        )
        return self

    @model_validator(mode='after')
    def _validate_internal_api_token(self) -> 'Settings':
        token = str(self.internal_api_token or '').strip()
        if token not in _INTERNAL_API_TOKEN_PLACEHOLDERS:
            return self
        if self.allow_insecure_internal_api_token or self.app_env in {'test'}:
            return self
        raise ValueError(
            'internal_api_token must be set to a non-placeholder value; '
            'set INTERNAL_API_TOKEN or explicitly opt into ALLOW_INSECURE_INTERNAL_API_TOKEN=true for isolated tests.'
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
