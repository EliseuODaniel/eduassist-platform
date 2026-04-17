from __future__ import annotations

from ai_orchestrator import (
    graph,
    grounded_answer_experience,
    llamaindex_native_runtime,
    langgraph_public_compound_runtime,
    langgraph_message_workflow,
    langgraph_public_retrieval_runtime,
    public_doc_knowledge,
    public_doc_lane_match_runtime,
    public_profile_runtime,
    public_profile_routes_runtime,
    public_profile_slot_memory_runtime,
    python_functions_native_runtime,
)
import ai_orchestrator.public_feature_runtime as public_feature_runtime
import ai_orchestrator.public_contact_runtime as public_contact_runtime
import ai_orchestrator.public_calendar_runtime as public_calendar_runtime
import ai_orchestrator.public_agentic_answer_runtime as public_agentic_answer_runtime
import ai_orchestrator.public_answer_compose_runtime as public_answer_compose_runtime
import ai_orchestrator.public_commercial_runtime as public_commercial_runtime
import ai_orchestrator.public_concierge_runtime as public_concierge_runtime
import ai_orchestrator.public_curriculum_runtime as public_curriculum_runtime
import ai_orchestrator.public_document_policy_runtime as public_document_policy_runtime
import ai_orchestrator.public_handlers_runtime as public_handlers_runtime
import ai_orchestrator.public_followup_preservation_runtime as public_followup_preservation_runtime
import ai_orchestrator.public_multi_intent_runtime as public_multi_intent_runtime
import ai_orchestrator.public_operations_runtime as public_operations_runtime
import ai_orchestrator.public_organization_runtime as public_organization_runtime
import ai_orchestrator.public_presence_runtime as public_presence_runtime
import ai_orchestrator.public_profile_intent_runtime as public_profile_intent_runtime
import ai_orchestrator.public_profile_glue_runtime as public_profile_glue_runtime
import ai_orchestrator.public_profile_routes_context_runtime as public_profile_routes_context_runtime
import ai_orchestrator.public_profile_routes_feature_runtime as public_profile_routes_feature_runtime
import ai_orchestrator.public_profile_routes_pricing_runtime as public_profile_routes_pricing_runtime
import ai_orchestrator.public_profile_routes_contact_runtime as public_profile_routes_contact_runtime
import ai_orchestrator.public_profile_routes_timeline_runtime as public_profile_routes_timeline_runtime
import ai_orchestrator.public_profile_support_runtime as public_profile_support_runtime
import ai_orchestrator.public_service_routing_runtime as public_service_routing_runtime
import ai_orchestrator.public_timeline_runtime as public_timeline_runtime
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


def test_public_profile_runtime_uses_explicit_contact_and_teacher_imports() -> None:
    assert public_profile_runtime._requested_contact_channel is public_contact_runtime._requested_contact_channel
    assert public_profile_runtime._contact_value is public_contact_runtime._contact_value
    assert (
        public_profile_runtime._is_public_teacher_identity_query
        is public_contact_runtime._is_public_teacher_identity_query
    )
    assert (
        public_profile_runtime._is_public_teacher_directory_follow_up
        is public_contact_runtime._is_public_teacher_directory_follow_up
    )


def test_public_profile_runtime_uses_explicit_timeline_and_date_imports() -> None:
    assert public_profile_runtime._is_public_timeline_query is public_timeline_runtime._is_public_timeline_query
    assert (
        public_profile_runtime._compose_contextual_public_timeline_followup_answer
        is public_timeline_runtime._compose_contextual_public_timeline_followup_answer
    )
    assert public_profile_runtime._format_public_date_text is public_timeline_runtime._format_public_date_text


def test_public_profile_runtime_uses_explicit_calendar_imports() -> None:
    assert (
        public_profile_runtime._handle_public_calendar_events
        is public_calendar_runtime._handle_public_calendar_events
    )


def test_public_profile_runtime_uses_explicit_document_policy_imports() -> None:
    assert public_profile_runtime._is_public_policy_query is public_document_policy_runtime._is_public_policy_query
    assert (
        public_profile_runtime._is_public_document_submission_query
        is public_document_policy_runtime._is_public_document_submission_query
    )
    assert (
        public_profile_runtime._compose_public_document_submission_answer
        is public_document_policy_runtime._compose_public_document_submission_answer
    )
    assert public_profile_runtime._handle_public_policy is public_document_policy_runtime._handle_public_policy


def test_public_profile_runtime_uses_explicit_curriculum_imports() -> None:
    assert (
        public_profile_runtime._extract_public_curriculum_subject_focus
        is public_curriculum_runtime._extract_public_curriculum_subject_focus
    )
    assert public_profile_runtime._is_public_curriculum_query is public_curriculum_runtime._is_public_curriculum_query
    assert public_profile_runtime._match_public_curriculum_component is public_curriculum_runtime._match_public_curriculum_component
    assert public_profile_runtime._handle_public_curriculum is public_curriculum_runtime._handle_public_curriculum


def test_public_profile_runtime_uses_explicit_commercial_imports() -> None:
    assert public_profile_runtime._is_public_scholarship_query is public_commercial_runtime._is_public_scholarship_query
    assert public_profile_runtime._is_public_enrichment_query is public_commercial_runtime._is_public_enrichment_query
    assert public_profile_runtime._compose_public_scholarship_answer is public_commercial_runtime._compose_public_scholarship_answer
    assert public_profile_runtime._compose_public_enrichment_answer is public_commercial_runtime._compose_public_enrichment_answer


def test_public_profile_runtime_uses_explicit_operations_imports() -> None:
    assert public_profile_runtime._parse_public_money is public_operations_runtime._parse_public_money
    assert public_profile_runtime._format_brl is public_operations_runtime._format_brl
    assert (
        public_profile_runtime._compose_public_pricing_projection_answer
        is public_operations_runtime._compose_public_pricing_projection_answer
    )
    assert public_profile_runtime._handle_public_pricing is public_operations_runtime._handle_public_pricing
    assert public_profile_runtime._handle_public_schedule is public_operations_runtime._handle_public_schedule
    assert public_profile_runtime._handle_public_capacity is public_operations_runtime._handle_public_capacity
    assert public_profile_runtime._handle_public_segments is public_operations_runtime._handle_public_segments


def test_public_profile_runtime_uses_explicit_multi_intent_imports() -> None:
    assert public_profile_runtime._compose_public_act_answer is public_multi_intent_runtime._compose_public_act_answer
    assert (
        public_profile_runtime._candidate_public_multi_intent_acts
        is public_multi_intent_runtime._candidate_public_multi_intent_acts
    )
    assert (
        public_profile_runtime._compose_public_multi_intent_answer
        is public_multi_intent_runtime._compose_public_multi_intent_answer
    )


def test_public_profile_runtime_uses_explicit_concierge_imports() -> None:
    assert (
        public_profile_runtime._compose_public_pedagogical_answer
        is public_concierge_runtime._compose_public_pedagogical_answer
    )
    assert public_profile_runtime._compose_concierge_greeting is public_concierge_runtime._compose_concierge_greeting
    assert public_profile_runtime._compose_capability_answer is public_concierge_runtime._compose_capability_answer
    assert (
        public_profile_runtime._compose_service_routing_answer
        is public_concierge_runtime._compose_service_routing_answer
    )
    assert public_profile_runtime._handle_public_acknowledgement is public_concierge_runtime._handle_public_acknowledgement
    assert public_profile_runtime._handle_public_greeting is public_concierge_runtime._handle_public_greeting
    assert (
        public_profile_runtime._handle_public_service_routing
        is public_concierge_runtime._handle_public_service_routing
    )
    assert public_profile_runtime._handle_public_capabilities is public_concierge_runtime._handle_public_capabilities
    assert (
        public_profile_runtime._target_public_feature_for_operating_hours
        is public_concierge_runtime._target_public_feature_for_operating_hours
    )
    assert public_profile_runtime._handle_public_operating_hours is public_concierge_runtime._handle_public_operating_hours
    assert public_profile_runtime._handle_public_features is public_concierge_runtime._handle_public_features


def test_public_profile_runtime_uses_explicit_answer_compose_imports() -> None:
    assert (
        public_profile_runtime._compose_public_profile_answer
        is public_answer_compose_runtime._compose_public_profile_answer
    )


def test_public_profile_runtime_uses_explicit_handlers_imports() -> None:
    assert public_profile_runtime._handle_public_location is public_handlers_runtime._handle_public_location
    assert public_profile_runtime._handle_public_confessional is public_handlers_runtime._handle_public_confessional
    assert public_profile_runtime._handle_public_visit is public_handlers_runtime._handle_public_visit
    assert public_profile_runtime._handle_public_school_name is public_handlers_runtime._handle_public_school_name
    assert (
        public_profile_runtime._public_profile_handler_registry
        is public_handlers_runtime._public_profile_handler_registry
    )
    assert (
        public_profile_runtime.NON_AGENTIC_PUBLIC_COMPOSITION_ACTS
        is public_handlers_runtime.NON_AGENTIC_PUBLIC_COMPOSITION_ACTS
    )


def test_public_profile_runtime_uses_explicit_profile_support_imports() -> None:
    assert public_profile_runtime._select_public_segment is public_profile_support_runtime._select_public_segment
    assert public_profile_runtime._segment_semantic_key is public_profile_support_runtime._segment_semantic_key
    assert public_profile_runtime._public_segment_matches is public_profile_support_runtime._public_segment_matches
    assert public_profile_runtime._extract_grade_reference is public_profile_support_runtime._extract_grade_reference
    assert (
        public_profile_runtime._requested_unpublished_public_segment
        is public_profile_support_runtime._requested_unpublished_public_segment
    )
    assert (
        public_profile_runtime._compose_public_segment_scope_gap
        is public_profile_support_runtime._compose_public_segment_scope_gap
    )
    assert public_profile_runtime._public_service_catalog is public_profile_support_runtime._public_service_catalog
    assert public_profile_runtime._public_feature_inventory is public_profile_support_runtime._public_feature_inventory
    assert public_profile_runtime._capability_summary_lines is public_profile_support_runtime._capability_summary_lines
    assert public_profile_runtime._concierge_topic_examples is public_profile_support_runtime._concierge_topic_examples
    assert (
        public_profile_runtime._compose_concierge_topic_examples
        is public_profile_support_runtime._compose_concierge_topic_examples
    )
    assert public_profile_runtime._requested_public_attribute is public_profile_support_runtime._requested_public_attribute
    assert public_profile_runtime._requested_public_attributes is public_profile_support_runtime._requested_public_attributes
    assert public_profile_runtime._humanize_service_eta is public_profile_support_runtime._humanize_service_eta
    assert (
        public_profile_runtime._compose_assistant_identity_answer
        is public_profile_support_runtime._compose_assistant_identity_answer
    )


def test_public_profile_runtime_uses_explicit_profile_intent_imports() -> None:
    assert public_profile_runtime._is_public_navigation_query is public_profile_intent_runtime._is_public_navigation_query
    assert public_profile_runtime._is_public_capacity_query is public_profile_intent_runtime._is_public_capacity_query
    assert (
        public_profile_runtime._compose_scope_boundary_answer
        is public_profile_intent_runtime._compose_scope_boundary_answer
    )
    assert (
        public_profile_runtime._compose_input_clarification_answer
        is public_profile_intent_runtime._compose_input_clarification_answer
    )
    assert (
        public_profile_runtime._compose_language_preference_answer
        is public_profile_intent_runtime._compose_language_preference_answer
    )
    assert public_profile_runtime._resolve_public_profile_act is public_profile_intent_runtime._resolve_public_profile_act


def test_public_profile_runtime_uses_explicit_profile_glue_imports() -> None:
    assert (
        public_profile_runtime._compose_public_feature_schedule_follow_up
        is public_profile_glue_runtime._compose_public_feature_schedule_follow_up
    )
    assert public_profile_runtime._matches_public_contact_rule is public_profile_glue_runtime._matches_public_contact_rule
    assert public_profile_runtime._localize_pt_br_surface_labels is public_profile_glue_runtime._localize_pt_br_surface_labels
    assert public_profile_runtime._recent_messages_mention is public_profile_glue_runtime._recent_messages_mention
    assert public_profile_runtime._recent_user_message_mentions is public_profile_glue_runtime._recent_user_message_mentions


def test_public_profile_runtime_uses_explicit_agentic_answer_imports() -> None:
    assert (
        public_profile_runtime._compose_public_profile_answer_agentic
        is public_agentic_answer_runtime._compose_public_profile_answer_agentic
    )
    assert (
        public_profile_runtime._maybe_langgraph_open_documentary_candidate
        is public_agentic_answer_runtime._maybe_langgraph_open_documentary_candidate
    )


def test_public_profile_runtime_uses_explicit_followup_preservation_imports() -> None:
    assert (
        public_profile_runtime._should_prefer_raw_public_followup_message
        is public_followup_preservation_runtime._should_prefer_raw_public_followup_message
    )
    assert (
        public_profile_runtime._must_preserve_contextual_public_followup_message
        is public_followup_preservation_runtime._must_preserve_contextual_public_followup_message
    )
    assert (
        public_profile_runtime._contextualize_public_followup_message
        is public_followup_preservation_runtime._contextualize_public_followup_message
    )
    assert (
        public_profile_runtime._should_preserve_deterministic_public_answer
        is public_followup_preservation_runtime._should_preserve_deterministic_public_answer
    )


def test_public_profile_runtime_uses_explicit_organization_imports() -> None:
    assert public_profile_runtime._compose_public_leadership_answer is public_organization_runtime._compose_public_leadership_answer
    assert public_profile_runtime._handle_public_highlight is public_organization_runtime._handle_public_highlight
    assert public_profile_runtime._handle_public_kpi is public_organization_runtime._handle_public_kpi
    assert (
        public_profile_runtime._compose_public_teacher_directory_answer
        is public_organization_runtime._compose_public_teacher_directory_answer
    )


def test_public_profile_runtime_uses_explicit_presence_imports() -> None:
    assert public_profile_runtime._compose_public_comparative_answer is public_presence_runtime._compose_public_comparative_answer
    assert public_profile_runtime._handle_public_web_presence is public_presence_runtime._handle_public_web_presence
    assert public_profile_runtime._handle_public_social_presence is public_presence_runtime._handle_public_social_presence
    assert public_profile_runtime._handle_public_careers is public_presence_runtime._handle_public_careers


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


def test_public_profile_routes_runtime_uses_explicit_contact_and_timeline_imports() -> None:
    assert (
        public_profile_routes_runtime._handle_public_contacts
        is public_profile_routes_contact_runtime._handle_public_contacts_impl
    )
    assert (
        public_profile_routes_runtime._handle_public_timeline
        is public_profile_routes_timeline_runtime._handle_public_timeline_impl
    )


def test_public_profile_routes_runtime_uses_explicit_feature_and_pricing_imports() -> None:
    assert (
        public_profile_routes_runtime._compose_public_feature_answer
        is public_profile_routes_feature_runtime._compose_public_feature_answer_impl
    )
    assert (
        public_profile_routes_runtime._compose_public_pricing_projection_answer
        is public_profile_routes_pricing_runtime._compose_public_pricing_projection_answer_impl
    )


def test_public_profile_routes_runtime_uses_explicit_context_imports() -> None:
    assert (
        public_profile_routes_runtime._build_public_profile_context
        is public_profile_routes_context_runtime._build_public_profile_context_impl
    )
