from __future__ import annotations

from ai_orchestrator import (
    graph,
    grounded_answer_experience,
    grounded_answer_support_runtime,
    llamaindex_native_runtime,
    langgraph_public_compound_runtime,
    langgraph_message_workflow,
    langgraph_public_retrieval_runtime,
    public_doc_knowledge,
    public_doc_lane_match_runtime,
    public_profile_legacy_runtime,
    public_profile_runtime,
    public_profile_routes_runtime,
    public_profile_slot_memory_runtime,
    python_functions_native_runtime,
)
import ai_orchestrator.public_feature_runtime as public_feature_runtime
import ai_orchestrator.public_service_routing_runtime as public_service_routing_runtime
import ai_orchestrator.workflow_runtime as workflow_runtime
from ai_orchestrator.extracted_module_contracts import refresh_extracted_module_contract
from ai_orchestrator.grounded_answer_support_contract import GROUNDED_ANSWER_SUPPORT_CONTRACT
from ai_orchestrator.graph_classification_contract import GRAPH_CLASSIFICATION_CONTRACT
from ai_orchestrator.graph_execution_contract import GRAPH_EXECUTION_CONTRACT
from ai_orchestrator.llamaindex_native_plan_contract import LLAMAINDEX_NATIVE_PLAN_CONTRACT
from ai_orchestrator.llamaindex_native_support_contract import LLAMAINDEX_NATIVE_SUPPORT_CONTRACT
from ai_orchestrator.public_profile_legacy_contract import PUBLIC_PROFILE_LEGACY_CONTRACT
from ai_orchestrator.public_profile_routes_contract import PUBLIC_PROFILE_ROUTES_CONTRACT
from ai_orchestrator.python_functions_native_plan_contract import PYTHON_FUNCTIONS_NATIVE_PLAN_CONTRACT
from ai_orchestrator_specialist import fast_path_answers
from ai_orchestrator_specialist import local_retrieval
from ai_orchestrator_specialist import local_retrieval_rerank_runtime
from ai_orchestrator_specialist import local_retrieval_search_runtime
from ai_orchestrator_specialist.extracted_module_contracts import (
    refresh_extracted_module_contract as refresh_specialist_extracted_module_contract,
)
from ai_orchestrator_specialist.fast_path_answer_contract import FAST_PATH_ANSWER_CONTRACT
from ai_orchestrator_specialist.local_retrieval_rerank_contract import (
    LOCAL_RETRIEVAL_RERANK_CONTRACT,
)
from ai_orchestrator_specialist.local_retrieval_search_contract import (
    LOCAL_RETRIEVAL_SEARCH_CONTRACT,
)


def test_python_functions_native_plan_contract_symbols_exist() -> None:
    missing = [name for name in PYTHON_FUNCTIONS_NATIVE_PLAN_CONTRACT if not hasattr(python_functions_native_runtime, name)]
    assert not missing


def test_llamaindex_native_plan_contract_symbols_exist() -> None:
    missing = [name for name in LLAMAINDEX_NATIVE_PLAN_CONTRACT if not hasattr(llamaindex_native_runtime, name)]
    assert not missing


def test_llamaindex_native_support_contract_symbols_exist() -> None:
    missing = [name for name in LLAMAINDEX_NATIVE_SUPPORT_CONTRACT if not hasattr(llamaindex_native_runtime, name)]
    assert not missing


def test_graph_classification_contract_symbols_exist() -> None:
    missing = [name for name in GRAPH_CLASSIFICATION_CONTRACT if not hasattr(graph, name)]
    assert not missing


def test_graph_execution_contract_symbols_exist() -> None:
    missing = [name for name in GRAPH_EXECUTION_CONTRACT if not hasattr(graph, name)]
    assert not missing


def test_public_profile_legacy_contract_symbols_exist() -> None:
    missing = [name for name in PUBLIC_PROFILE_LEGACY_CONTRACT if not hasattr(public_profile_runtime, name)]
    assert not missing


def test_grounded_answer_support_contract_symbols_exist() -> None:
    missing = [
        name for name in GROUNDED_ANSWER_SUPPORT_CONTRACT if not hasattr(grounded_answer_experience, name)
    ]
    assert not missing


def test_public_profile_routes_contract_symbols_exist() -> None:
    missing = [name for name in PUBLIC_PROFILE_ROUTES_CONTRACT if not hasattr(public_profile_runtime, name)]
    assert not missing


def test_specialist_fast_path_contract_symbols_exist() -> None:
    missing = [name for name in FAST_PATH_ANSWER_CONTRACT if not hasattr(fast_path_answers, name)]
    assert not missing


def test_specialist_local_retrieval_search_contract_symbols_exist() -> None:
    missing = [name for name in LOCAL_RETRIEVAL_SEARCH_CONTRACT if not hasattr(local_retrieval, name)]
    assert not missing


def test_specialist_local_retrieval_rerank_contract_symbols_exist() -> None:
    missing = [name for name in LOCAL_RETRIEVAL_RERANK_CONTRACT if not hasattr(local_retrieval, name)]
    assert not missing


def test_contract_refresh_binds_only_declared_python_functions_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_extracted_module_contract(
        native_module=python_functions_native_runtime,
        namespace=namespace,
        contract_names=PYTHON_FUNCTIONS_NATIVE_PLAN_CONTRACT,
        local_extracted_names=frozenset({'maybe_execute_python_functions_native_plan'}),
        contract_label='python_functions_native_plan_runtime',
    )
    assert 'maybe_execute_python_functions_native_plan' not in namespace
    assert namespace['rt'] is python_functions_native_runtime.rt
    assert namespace['build_response_candidate'] is python_functions_native_runtime.build_response_candidate


def test_contract_refresh_binds_only_declared_specialist_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_specialist_extracted_module_contract(
        native_module=fast_path_answers,
        namespace=namespace,
        contract_names=FAST_PATH_ANSWER_CONTRACT,
        local_extracted_names=frozenset({'build_fast_path_answer'}),
        contract_label='fast_path_answer_runtime',
    )
    assert 'build_fast_path_answer' not in namespace
    assert namespace['match_public_canonical_lane'] is fast_path_answers.match_public_canonical_lane


def test_contract_refresh_binds_only_declared_specialist_local_retrieval_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_specialist_extracted_module_contract(
        native_module=local_retrieval,
        namespace=namespace,
        contract_names=LOCAL_RETRIEVAL_SEARCH_CONTRACT,
        local_extracted_names=frozenset({'hybrid_search_impl', 'lexical_search_impl', 'fuse_hits_impl'}),
        contract_label='local_retrieval_search_runtime',
    )
    assert 'hybrid_search_impl' not in namespace
    assert namespace['RetrievalSearchResponse'] is local_retrieval.RetrievalSearchResponse


def test_specialist_local_retrieval_runtime_uses_explicit_contracts() -> None:
    namespace: dict[str, object] = {}
    refresh_specialist_extracted_module_contract(
        native_module=local_retrieval,
        namespace=namespace,
        contract_names=LOCAL_RETRIEVAL_RERANK_CONTRACT,
        local_extracted_names=frozenset(
            {
                '_rerank_text_for_hit',
                '_late_interaction_maxsim',
                '_late_interaction_scores',
                '_normalize_visibility_filter',
                '_normalize_category_filter',
                'get_retrieval_service',
                '_build_embedder',
                '_build_cross_encoder_reranker',
                '_build_late_interaction_embedder',
            }
        ),
        contract_label='local_retrieval_rerank_runtime',
    )
    assert 'get_retrieval_service' not in namespace
    assert local_retrieval_rerank_runtime._normalize_text is local_retrieval._normalize_text


def test_contract_refresh_binds_only_declared_graph_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_extracted_module_contract(
        native_module=graph,
        namespace=namespace,
        contract_names=GRAPH_EXECUTION_CONTRACT,
        local_extracted_names=frozenset({'structured_tool_call', 'get_graph_blueprint'}),
        contract_label='graph_execution_runtime',
    )
    assert 'structured_tool_call' not in namespace
    assert namespace['_append_path'] is graph._append_path


def test_public_doc_lane_match_runtime_uses_explicit_imports() -> None:
    assert public_doc_lane_match_runtime._normalize_space is public_doc_knowledge._normalize_space
    assert (
        public_doc_lane_match_runtime._looks_like_public_conduct_policy_query
        is public_doc_knowledge._looks_like_public_conduct_policy_query
    )


def test_langgraph_public_retrieval_runtime_uses_explicit_imports() -> None:
    assert langgraph_public_retrieval_runtime.LangGraphMessageState is langgraph_message_workflow.LangGraphMessageState
    assert langgraph_public_retrieval_runtime._delegate_runtime is langgraph_message_workflow._delegate_runtime


def test_public_profile_slot_memory_runtime_uses_explicit_imports() -> None:
    assert (
        public_profile_slot_memory_runtime.PublicInstitutionPlan
        is public_profile_runtime.PublicInstitutionPlan
    )
    assert public_profile_slot_memory_runtime.QueryDomain is public_profile_runtime.QueryDomain


def test_langgraph_public_compound_runtime_uses_explicit_imports() -> None:
    assert langgraph_public_compound_runtime.LangGraphMessageState is langgraph_message_workflow.LangGraphMessageState
    assert langgraph_public_compound_runtime._delegate_runtime is langgraph_message_workflow._delegate_runtime


def test_workflow_runtime_uses_explicit_public_feature_and_service_imports() -> None:
    assert workflow_runtime._feature_suggestion_replies is public_feature_runtime._feature_suggestion_replies
    assert (
        workflow_runtime._routing_follow_up_context_message
        is public_service_routing_runtime._routing_follow_up_context_message
    )
    assert (
        workflow_runtime._service_matches_from_message
        is public_service_routing_runtime._service_matches_from_message
    )


def test_public_profile_legacy_runtime_contract_refresh_binds_declared_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_extracted_module_contract(
        native_module=public_profile_runtime,
        namespace=namespace,
        contract_names=PUBLIC_PROFILE_LEGACY_CONTRACT,
        local_extracted_names=frozenset({'_compose_public_profile_answer_legacy'}),
        contract_label='public_profile_legacy_runtime',
    )
    assert '_compose_public_profile_answer_legacy' not in namespace
    assert namespace['_compose_scope_boundary_answer'] is public_profile_runtime._compose_scope_boundary_answer


def test_grounded_answer_support_runtime_contract_refresh_binds_declared_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_extracted_module_contract(
        native_module=grounded_answer_experience,
        namespace=namespace,
        contract_names=GROUNDED_ANSWER_SUPPORT_CONTRACT,
        local_extracted_names=frozenset(
            {
                '_deterministic_public_direct_answer',
                '_deterministic_protected_academic_direct_answer',
                '_deterministic_protected_attendance_direct_answer',
                '_deterministic_protected_finance_direct_answer',
                '_build_supplemental_focus',
                '_preserve_deterministic_answer_surface',
            }
        ),
        contract_label='grounded_answer_support_runtime',
    )
    assert '_build_supplemental_focus' not in namespace
    assert (
        namespace['compose_public_known_unknown_answer']
        is grounded_answer_experience.compose_public_known_unknown_answer
    )


def test_public_profile_routes_runtime_contract_refresh_binds_declared_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_extracted_module_contract(
        native_module=public_profile_runtime,
        namespace=namespace,
        contract_names=PUBLIC_PROFILE_ROUTES_CONTRACT,
        local_extracted_names=frozenset(
            {
                '_compose_public_feature_answer',
                '_try_public_channel_fast_answer',
                '_build_public_profile_context',
                '_handle_public_contacts',
                '_handle_public_timeline',
                '_compose_public_pricing_projection_answer',
            }
        ),
        contract_label='public_profile_routes_runtime',
    )
    assert '_compose_public_feature_answer' not in namespace
    assert namespace['_handle_public_schedule'] is public_profile_runtime._handle_public_schedule
    assert public_profile_routes_runtime._select_public_segment is public_profile_runtime._select_public_segment
