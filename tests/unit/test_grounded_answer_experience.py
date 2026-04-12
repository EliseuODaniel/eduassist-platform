from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from ai_orchestrator.grounded_answer_experience import (
    _ANSWER_FOCUS_CACHE,
    _clarify_after_retry_message,
    _looks_like_cross_student_academic_comparison_followup,
    _looks_like_contextual_cross_student_academic_comparison_followup,
    _preserve_deterministic_answer_surface,
    apply_grounded_answer_experience,
)
from ai_orchestrator.conversation_answer_state import AnswerFocusState, resolve_answer_focus
from ai_orchestrator.conversation_answer_state import explicit_subject_from_message
from ai_orchestrator.models import (
    AccessTier,
    ConversationChannel,
    IntentClassification,
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageResponse,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
    UserContext,
)


def _settings() -> SimpleNamespace:
    return SimpleNamespace(
        feature_flag_answer_experience_enabled=True,
        feature_flag_answer_experience_channels='telegram',
        feature_flag_answer_experience_stacks='specialist_supervisor,langgraph,python_functions,llamaindex',
        feature_flag_answer_experience_public_enabled=True,
        feature_flag_answer_experience_protected_enabled=True,
        feature_flag_answer_experience_min_chars=10,
        feature_flag_context_repair_enabled=True,
        feature_flag_context_repair_stacks='specialist_supervisor,langgraph,python_functions,llamaindex',
        feature_flag_context_repair_retry_top_k=6,
        answer_experience_provider=None,
        answer_experience_openai_api_key=None,
        answer_experience_openai_base_url=None,
        answer_experience_openai_model=None,
        answer_experience_google_api_key='test-key',
        answer_experience_google_api_base_url='https://example.test',
        answer_experience_google_model='gemini-2.5-flash',
        llm_provider='google',
        google_api_key='test-key',
        google_api_base_url='https://example.test',
        google_model='gemini-2.5-flash',
        openai_api_key=None,
        openai_base_url='https://api.openai.com/v1',
        openai_model='gpt-5.4',
        database_url='postgresql://test:test@localhost:5432/test',
        qdrant_url='http://localhost:6333',
        qdrant_documents_collection='eduassist_documents',
        document_embedding_model='BAAI/bge-small-en-v1.5',
        retrieval_enable_query_variants=True,
        retrieval_enable_late_interaction_rerank=False,
        retrieval_late_interaction_model='',
        retrieval_candidate_pool_size=8,
        retrieval_cheap_candidate_pool_size=6,
        retrieval_deep_candidate_pool_size=10,
        retrieval_rerank_fused_weight=0.35,
        retrieval_rerank_late_interaction_weight=0.65,
        api_core_url='http://api-core:8000',
        internal_api_token='test-token',
    )


def _request(message: str) -> MessageResponseRequest:
    return MessageResponseRequest(
        message=message,
        telegram_chat_id=123,
        channel=ConversationChannel.telegram,
        user=UserContext(role='guardian', authenticated=True),
    )


def test_clarify_after_retry_abstains_for_out_of_scope_question() -> None:
    request = _request("Qual o melhor filme do ano?")
    message = _clarify_after_retry_message(
        request=request,
        focus=AnswerFocusState(),
        actor={"linked_students": [{"full_name": "Lucas Oliveira"}]},
        conversation_context=None,
    )

    assert message is not None
    lowered = message.casefold()
    assert "fora do escopo da escola" in lowered
    assert "matricula" in lowered


def _response(message_text: str) -> MessageResponse:
    return MessageResponse(
        message_text=message_text,
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.academic,
            access_tier=AccessTier.authenticated,
            confidence=1.0,
            reason='test',
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=['get_student_grades'],
        evidence_pack=MessageEvidencePack(
            strategy='structured_tool',
            summary='Notas estruturadas do aluno.',
            source_count=1,
            support_count=1,
            supports=[
                MessageEvidenceSupport(
                    kind='grade_snapshot',
                    label='Lucas Oliveira',
                    detail='Historia 6,8; Matematica 7,4; Biologia 8,1',
                    excerpt='Historia 6,8; Matematica 7,4; Biologia 8,1',
                )
            ],
        ),
        reason='protected_academic_detail',
    )


def _public_response(
    message_text: str,
    *,
    domain: QueryDomain = QueryDomain.institution,
    mode: OrchestrationMode = OrchestrationMode.structured_tool,
) -> MessageResponse:
    return MessageResponse(
        message_text=message_text,
        mode=mode,
        classification=IntentClassification(
            domain=domain,
            access_tier=AccessTier.public,
            confidence=0.9,
            reason='test',
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=['get_public_school_profile'],
        evidence_pack=MessageEvidencePack(
            strategy='structured_tool',
            summary='Informação pública estruturada.',
            source_count=1,
            support_count=1,
            supports=[
                MessageEvidenceSupport(
                    kind='public_fact',
                    label='Colegio Horizonte',
                    detail='Informação pública institucional.',
                    excerpt='Informação pública institucional.',
                )
            ],
        ),
        reason='public_structured_detail',
    )


def _restricted_no_match_response(message_text: str, *, reason: str) -> MessageResponse:
    return MessageResponse(
        message_text=message_text,
        mode=OrchestrationMode.clarify,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.sensitive,
            confidence=0.9,
            reason=reason,
        ),
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        selected_tools=['search_documents'],
        evidence_pack=MessageEvidencePack(
            strategy='retrieval',
            summary='Consulta a documentos restritos sem correspondencia suficiente.',
            source_count=0,
            support_count=0,
            supports=[],
        ),
        reason=reason,
    )


@pytest.fixture(autouse=True)
def _clear_answer_focus_cache() -> None:
    _ANSWER_FOCUS_CACHE.clear()
    yield
    _ANSWER_FOCUS_CACHE.clear()


def test_answer_experience_rewrites_to_requested_subject(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': [{'sender_type': 'user', 'content': 'quais as notas do lucas?'}]}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'A média parcial de Lucas Oliveira em História é 6,8.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('qual a nota de história do lucas?'),
            response=_response('Lucas Oliveira: História 6,8; Matemática 7,4; Biologia 8,1.'),
            settings=_settings(),
            stack_name='specialist_supervisor',
        )
    )

    assert updated.message_text == 'A média parcial de Lucas Oliveira em História é 6,8.'
    assert updated.answer_experience_applied is True
    assert updated.answer_experience_reason == 'protected_grounded_answer'
    assert updated.used_llm is True
    assert 'grounded_answer_experience' in updated.llm_stages


def test_explicit_subject_from_message_ignores_metalinguistic_ingles() -> None:
    assert explicit_subject_from_message('Por que admissions ta em ingles?') is None


def test_explicit_subject_from_message_ignores_metalinguistic_portugues() -> None:
    assert explicit_subject_from_message('Quero que so fale portugues') is None


def test_answer_experience_builds_family_academic_aggregate_from_clarify(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 5.9, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 6.8, 'max_score': 10},
                        {'subject_name': 'Matematica', 'score': 7.7, 'max_score': 10},
                    ],
                }
            }
        if path.endswith('/ana-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 6.4, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 7.3, 'max_score': 10},
                        {'subject_name': 'Matematica', 'score': 7.4, 'max_score': 10},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('De forma bem objetiva, me de um panorama academico dos meus filhos e diga qual deles aparece mais perto da media minima agora.'),
            response=_response('Para qual aluno você quer consultar isso: Lucas Oliveira ou Ana Oliveira?').model_copy(
                update={'mode': OrchestrationMode.clarify}
            ),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'Panorama academico das contas vinculadas' in updated.message_text
    assert 'Lucas Oliveira' in updated.message_text
    assert 'Ana Oliveira' in updated.message_text
    assert 'Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.' in updated.message_text
    assert updated.mode == OrchestrationMode.structured_tool


def test_answer_experience_repairs_family_academic_reason_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {
                    'role': 'assistant',
                    'content': (
                        'Panorama academico das contas vinculadas:\n'
                        '- Lucas Oliveira: Fisica 5,9/10.\n'
                        '- Ana Oliveira: Fisica 6,4/10.\n'
                        'Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.'
                    ),
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 5.9, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 6.8, 'max_score': 10},
                    ],
                }
            }
        if path.endswith('/ana-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 6.4, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 7.3, 'max_score': 10},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Situacao administrativa do seu cadastro hoje: com pendencias.').model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.authenticated,
                confidence=0.88,
                reason='python_functions_local_protected:institution',
            ),
            'selected_tools': ['get_administrative_status'],
            'reason': 'python_functions_local_protected:institution',
            'candidate_reason': 'python_functions_local_protected:institution',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Qual e o principal motivo desse alerta?'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'Lucas Oliveira' in updated.message_text
    assert 'abaixo da media minima em Fisica' in updated.message_text
    assert updated.answer_experience_reason.endswith(':protected_academic_direct')


def test_answer_experience_repairs_family_academic_next_in_line_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {
                    'role': 'assistant',
                    'content': (
                        'Panorama academico das contas vinculadas:\n'
                        '- Lucas Oliveira: Fisica 5,9/10.\n'
                        '- Ana Oliveira: Fisica 6,4/10.\n'
                        'Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.'
                    ),
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 5.9, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 6.8, 'max_score': 10},
                    ],
                }
            }
        if path.endswith('/ana-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 6.4, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 7.3, 'max_score': 10},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Voce quer consultar Matematica de qual aluno?').model_copy(
        update={
            'mode': OrchestrationMode.clarify,
            'classification': IntentClassification(
                domain=QueryDomain.academic,
                access_tier=AccessTier.authenticated,
                confidence=0.71,
                reason='clarify_after_drift',
            ),
            'reason': 'clarify_after_drift',
            'candidate_reason': 'clarify_after_drift',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('E logo depois dele, quem vem na fila se eu olhar o mesmo criterio?'),
            response=response,
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert 'Logo depois dele vem Ana Oliveira, principalmente em Fisica' in updated.message_text
    assert updated.answer_experience_reason.endswith(':protected_academic_direct')


def test_answer_experience_repairs_attendance_to_family_academic_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {
                    'role': 'assistant',
                    'content': (
                        'Panorama de frequencia das contas vinculadas:\n'
                        '- Lucas Oliveira: 6 faltas.\n'
                        '- Ana Oliveira: 6 faltas.\n'
                        'Quem exige maior atencao agora: Ana Oliveira.'
                    ),
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 5.9, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 6.8, 'max_score': 10},
                    ],
                }
            }
        if path.endswith('/ana-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 6.4, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 7.3, 'max_score': 10},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Para qual aluno você quer consultar isso: Lucas Oliveira ou Ana Oliveira?').model_copy(
        update={
            'mode': OrchestrationMode.clarify,
            'classification': IntentClassification(
                domain=QueryDomain.academic,
                access_tier=AccessTier.authenticated,
                confidence=0.71,
                reason='clarify_after_attendance_drift',
            ),
            'reason': 'clarify_after_attendance_drift',
            'candidate_reason': 'clarify_after_attendance_drift',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Não estou falando de falta agora: academicamente, quem está mais crítico?'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'Panorama academico das contas vinculadas' in updated.message_text
    assert 'Lucas Oliveira' in updated.message_text
    assert 'Ana Oliveira' in updated.message_text
    assert 'Quem hoje exige maior atencao academica e Lucas Oliveira' in updated.message_text
    assert updated.answer_experience_reason.endswith(':protected_academic_direct')


def test_answer_experience_repairs_cross_student_comparison_after_public_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'role': 'assistant', 'content': 'Notas de Lucas Oliveira: Historia 6,8; Fisica 5,9; Matematica 7,7; Portugues 8,3'},
                {
                    'role': 'assistant',
                    'content': (
                        'O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina. '
                        'O caminho publico correto e a coordenacao pedagogica.'
                    ),
                },
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 5.9, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 6.8, 'max_score': 10},
                    ],
                }
            }
        if path.endswith('/ana-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 6.4, 'max_score': 10},
                        {'subject_name': 'Historia', 'score': 7.3, 'max_score': 10},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Lucas Oliveira teve notas em Física e História inferiores às de Ana.').model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.academic,
                access_tier=AccessTier.authenticated,
                confidence=0.9,
                reason='langgraph_local_protected:academic',
            ),
            'reason': 'langgraph_local_protected:academic',
            'candidate_reason': 'langgraph_local_protected:academic',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Voltando aos meus filhos, compara o Lucas com a Ana.'),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'comparando lucas oliveira com ana oliveira' in lowered
    assert 'mais perto da media minima' in lowered or 'média mínima' in lowered
    assert updated.answer_experience_reason.endswith(':protected_academic_direct')


def test_answer_experience_builds_family_finance_aggregate_from_clarify(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_finance': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_finance': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/financial-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'open_invoice_count': 1,
                    'overdue_invoice_count': 0,
                    'invoices': [
                        {'status': 'open', 'due_date': '2026-04-10', 'amount_due': '1450.00', 'reference_month': '2026-04'},
                    ],
                }
            }
        if path.endswith('/ana-id/financial-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'open_invoice_count': 2,
                    'overdue_invoice_count': 0,
                    'invoices': [
                        {'status': 'open', 'due_date': '2026-03-10', 'amount_due': '1450.00', 'reference_month': '2026-03'},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Resuma a situacao financeira atual da familia, com vencimentos, atrasos e proximos passos. Responda de forma direta.'),
            response=_response('Para qual aluno você quer consultar o financeiro: Lucas Oliveira ou Ana Oliveira?').model_copy(
                update={'mode': OrchestrationMode.clarify}
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'Resumo financeiro das contas vinculadas' in updated.message_text
    assert 'Total de faturas em aberto' in updated.message_text
    assert updated.mode == OrchestrationMode.structured_tool


def test_answer_experience_restores_family_finance_aggregate_from_structured_finance_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_finance': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_finance': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/financial-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'open_invoice_count': 1,
                    'overdue_invoice_count': 0,
                    'invoices': [
                        {'status': 'open', 'due_date': '2026-04-10', 'amount_due': '1450.00', 'reference_month': '2026-04'},
                    ],
                }
            }
        if path.endswith('/ana-id/financial-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'open_invoice_count': 2,
                    'overdue_invoice_count': 0,
                    'invoices': [
                        {'status': 'open', 'due_date': '2026-03-10', 'amount_due': '1450.00', 'reference_month': '2026-03'},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Como estao meus pagamentos?'),
            response=_response('Para qual aluno você quer consultar o financeiro: Lucas Oliveira ou Ana Oliveira?').model_copy(
                update={
                    'classification': IntentClassification(
                        domain=QueryDomain.finance,
                        access_tier=AccessTier.authenticated,
                        confidence=0.9,
                        reason='python_functions_local_protected:finance',
                    ),
                    'reason': 'python_functions_native_structured:finance',
                    'selected_tools': ['get_financial_summary'],
                }
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'resumo financeiro das contas vinculadas' in lowered
    assert 'ana oliveira' in lowered
    assert updated.mode == OrchestrationMode.structured_tool
    assert updated.answer_experience_reason.endswith('protected_finance_direct')


def test_answer_experience_does_not_convert_family_finance_summary_into_attendance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_finance': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_finance': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/financial-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'open_invoice_count': 1,
                    'overdue_invoice_count': 0,
                    'invoices': [{'status': 'open', 'due_date': '2026-04-10', 'amount_due': '1450.00', 'reference_month': '2026-04'}],
                }
            }
        if path.endswith('/ana-id/financial-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'open_invoice_count': 2,
                    'overdue_invoice_count': 0,
                    'invoices': [{'status': 'open', 'due_date': '2026-03-10', 'amount_due': '1450.00', 'reference_month': '2026-03'}],
                }
            }
        raise AssertionError(f'unexpected_path:{path}')

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('De forma bem objetiva, resuma a situacao financeira atual da familia, com vencimentos, atrasos e proximos passos.'),
            response=_response('Panorama de frequencia das contas vinculadas: ...'),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'resumo financeiro das contas vinculadas' in lowered
    assert 'frequencia' not in lowered
    assert updated.answer_experience_reason.endswith(':protected_finance_direct')


def test_answer_experience_does_not_preserve_public_pricing_surface_for_family_finance_request() -> None:
    preserved = _preserve_deterministic_answer_surface(
        request=_request('Paguei parte da mensalidade do Joao e preciso negociar o restante; o que ja aparece e qual o proximo passo?'),
        response=_response(
            'Valores públicos de referência: - Ensino Médio (Manhã): mensalidade R$ 1.450,00 e matrícula R$ 350,00.'
        ).model_copy(
            update={
                'classification': IntentClassification(
                    domain=QueryDomain.finance,
                    access_tier=AccessTier.authenticated,
                    confidence=0.95,
                    reason='python_functions_native_structured:finance',
                ),
                'selected_tools': ['get_financial_summary'],
                'mode': OrchestrationMode.structured_tool,
                'reason': 'python_functions_native_structured:finance',
            }
        ),
        actor={
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        },
        focus=AnswerFocusState(domain='finance', topic='finance', asks_family_aggregate=True),
        conversation_context=None,
    )
    assert preserved is None


def test_family_finance_focus_includes_layman_breakdown_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_finance': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_finance': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/financial-summary'):
            return {'summary': {'student_name': 'Lucas Oliveira', 'open_invoice_count': 1, 'overdue_invoice_count': 0, 'invoices': []}}
        if path.endswith('/ana-id/financial-summary'):
            return {'summary': {'student_name': 'Ana Oliveira', 'open_invoice_count': 2, 'overdue_invoice_count': 0, 'invoices': []}}
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Explique a minha situacao financeira como se eu fosse leigo, separando mensalidade, taxa, atraso e desconto.'),
            response=_response('Resumo financeiro das contas vinculadas:').model_copy(
                update={
                    'classification': IntentClassification(
                        domain=QueryDomain.finance,
                        access_tier=AccessTier.authenticated,
                        confidence=0.95,
                        reason='python_functions_native_structured:finance',
                    ),
                    'selected_tools': ['get_financial_summary'],
                    'reason': 'python_functions_native_structured:finance',
                }
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'mensalidade:' in lowered
    assert 'taxa:' in lowered
    assert 'atraso:' in lowered
    assert 'desconto:' in lowered


def test_cross_student_academic_comparison_followup_rejects_documentation_compare_prompt() -> None:
    assert (
        _looks_like_cross_student_academic_comparison_followup(
            'Compare a documentacao dos meus filhos e diga qual deles ainda tem pendencia.'
        )
        is False
    )


def test_contextual_cross_student_academic_comparison_followup_accepts_short_compare_after_recent_academic_context() -> None:
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'assistant', 'content': 'Notas de Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7.'},
            {'sender_type': 'user', 'content': 'agora me diz se a escola divulga contato direto do professor de matematica'},
        ]
    }
    assert (
        _looks_like_contextual_cross_student_academic_comparison_followup(
            'voltando aos meus filhos, compara o Lucas com a Ana',
            conversation_context=conversation_context,
            mentioned_students=['Lucas Oliveira', 'Ana Oliveira'],
        )
        is True
    )


def test_contextual_cross_student_academic_comparison_followup_rejects_documentation_compare_even_with_recent_context() -> None:
    conversation_context = {
        'recent_messages': [
            {'sender_type': 'assistant', 'content': 'Notas de Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7.'},
        ]
    }
    assert (
        _looks_like_contextual_cross_student_academic_comparison_followup(
            'compare a documentacao do Lucas com a Ana',
            conversation_context=conversation_context,
            mentioned_students=['Lucas Oliveira', 'Ana Oliveira'],
        )
        is False
    )


def test_answer_experience_builds_family_admin_compare_for_documentation_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/administrative-status'):
            return {'summary': {'student_name': 'Lucas Oliveira', 'overall_status': 'complete', 'checklist': []}}
        if path.endswith('/ana-id/administrative-status'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'overall_status': 'pending',
                    'next_step': 'Enviar comprovante atualizado pela secretaria.',
                    'checklist': [{'status': 'pending', 'notes': 'Comprovante de residencia atualizado'}],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Compare a documentacao dos meus filhos e diga qual deles ainda tem pendencia.'),
            response=_response('Ana Oliveira ainda tem pendência documental.').model_copy(
                update={
                    'classification': IntentClassification(
                        domain=QueryDomain.institution,
                        access_tier=AccessTier.authenticated,
                        confidence=0.95,
                        reason='python_functions_native_structured:institution',
                    ),
                    'selected_tools': ['get_student_administrative_status'],
                    'reason': 'python_functions_native_structured:institution',
                }
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'panorama documental das contas vinculadas' in lowered
    assert 'lucas oliveira' in lowered
    assert 'ana oliveira' in lowered
    assert 'quem ainda tem pendencia documental' in lowered


def test_answer_experience_denies_third_party_finance_request_before_public_pricing(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Paguei parte da mensalidade do Joao e preciso negociar o restante; o que ja aparece e qual o proximo passo?'),
            response=_response('Valores públicos de referência: - Ensino Médio (Manhã): mensalidade R$ 1.450,00 e matrícula R$ 350,00.').model_copy(
                update={
                    'classification': IntentClassification(
                        domain=QueryDomain.finance,
                        access_tier=AccessTier.authenticated,
                        confidence=0.95,
                        reason='python_functions_native_structured:finance',
                    ),
                    'selected_tools': ['get_financial_summary'],
                    'reason': 'python_functions_native_structured:finance',
                }
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'o que ja aparece:' in lowered
    assert 'nao posso confirmar nem expor o financeiro' in lowered
    assert 'joao' in lowered
    assert 'lucas oliveira' in lowered
    assert 'regularize primeiro o vinculo com a secretaria' in lowered
    assert 'me diga qual deles' in lowered


def test_answer_experience_builds_family_upcoming_assessments_aggregate(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {'summary': {'student_name': 'Lucas Oliveira', 'class_name': '8º ano'}}
        if path.endswith('/ana-id/academic-summary'):
            return {'summary': {'student_name': 'Ana Oliveira', 'class_name': '7º ano'}}
        if path.endswith('/lucas-id/upcoming-assessments'):
            return {
                'summary': {
                    'assessments': [
                        {'subject_name': 'Historia', 'item_title': 'Avaliacao B1', 'due_date': '2026-04-10'},
                    ]
                }
            }
        if path.endswith('/ana-id/upcoming-assessments'):
            return {
                'summary': {
                    'assessments': [
                        {'subject_name': 'Matematica', 'item_title': 'Lista 2', 'due_date': '2026-04-12'},
                    ]
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Resuma as proximas provas e avaliacoes previstas para Lucas e Ana.'),
            response=_response('Próximas avaliações de Lucas Oliveira: - Historia: Avaliacao B1 em 10/04/2026.').model_copy(
                update={'mode': OrchestrationMode.structured_tool}
            ),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'Próximas avaliações das contas vinculadas' in updated.message_text
    assert 'Lucas Oliveira' in updated.message_text
    assert 'Ana Oliveira' in updated.message_text


def test_answer_experience_builds_public_known_unknown_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=MessageResponseRequest(
                message='Quero saber se a escola publica a quantidade total de professores ou se esse dado nao esta disponivel.',
                telegram_chat_id=999,
                channel=ConversationChannel.telegram,
                user=UserContext(role='anonymous', authenticated=False),
            ),
            response=_public_response('Não tenho esse dado no momento.', mode=OrchestrationMode.clarify),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'nao informam a quantidade total de professores' in updated.message_text.lower()
    assert updated.mode == OrchestrationMode.structured_tool


def test_answer_experience_prefers_public_teacher_directory_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=MessageResponseRequest(
                message='Como falar com o professor de matematica? A escola divulga esse contato ou encaminha para outro setor?',
                telegram_chat_id=999,
                channel=ConversationChannel.telegram,
                user=UserContext(role='anonymous', authenticated=False),
            ),
            response=_public_response('Para falar com um professor de matemática, o contato direto não é divulgado.'),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'nao divulga' in updated.message_text.lower()
    assert 'coordenacao pedagogica' in updated.message_text.lower()


def test_answer_experience_teacher_directory_boundary_beats_service_routing_bundle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=MessageResponseRequest(
                message='De forma bem objetiva, se eu quiser falar com o professor de matematica, a escola divulga esse contato ou manda procurar a coordenacao?',
                telegram_chat_id=999,
                channel=ConversationChannel.telegram,
                user=UserContext(role='anonymous', authenticated=False),
            ),
            response=_public_response('Hoje estes sao os responsaveis e canais mais diretos por assunto:\n- Secretaria: bot, secretaria presencial, email institucional ou portal.'),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'nao divulga' in lowered
    assert 'coordenacao pedagogica' in lowered
    assert '- secretaria:' not in lowered


def test_answer_experience_keeps_teacher_directory_on_short_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quero falar com o professor de matematica.'},
                {'sender_type': 'assistant', 'content': 'A escola nao divulga contato direto de professor.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=MessageResponseRequest(
                message='Ou manda procurar a coordenação?',
                telegram_chat_id=999,
                channel=ConversationChannel.telegram,
                user=UserContext(role='anonymous', authenticated=False),
            ),
            response=_public_response('Hoje estes sao os responsaveis e canais mais diretos por assunto:\n- Secretaria: email institucional.'),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'nao divulga' in lowered
    assert 'coordenacao pedagogica' in lowered


def test_answer_experience_prefers_public_permanence_support_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte', 'academic_policy': {'project_of_life_summary': 'Projeto de vida como eixo de tutoria.'}}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=MessageResponseRequest(
                message='Sem sair do escopo do projeto, que mecanismos publicos ajudam a familia a acompanhar permanencia, apoio e vida escolar sem depender de informacao interna?',
                telegram_chat_id=999,
                channel=ConversationChannel.telegram,
                user=UserContext(role='anonymous', authenticated=False),
            ),
            response=_public_response('Acompanhar a vida escolar do estudante é um processo contínuo.'),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'famil' in lowered
    assert 'apoio' in lowered
    assert 'vida escolar' in lowered


def test_answer_experience_accepts_honest_limitation_on_domain_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'Com a resposta atual, eu não consigo confirmar o valor da próxima fatura do Lucas com segurança.'

    async def fake_plan(**kwargs):
        return {
            'action': 'keep',
            'message': '',
            'retry_query': '',
            'confidence': 0.2,
            'reason': 'no_repair_needed',
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('qual o valor da próxima fatura do lucas?'),
            response=_response('Lucas Oliveira está com História 6,8, Matemática 7,4 e Biologia 8,1.'),
            settings=_settings(),
            stack_name='specialist_supervisor',
        )
    )

    assert 'não consigo confirmar o valor da próxima fatura' in updated.message_text
    assert updated.answer_experience_applied is True


def test_answer_experience_skips_when_candidate_drops_requested_subject(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'Lucas Oliveira está com bom desempenho geral.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = _response('Lucas Oliveira: História 6,8; Matemática 7,4; Biologia 8,1.')
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('qual a nota de história do lucas?'),
            response=original,
            settings=_settings(),
            stack_name='specialist_supervisor',
        )
    )

    assert updated.message_text == original.message_text
    assert updated.answer_experience_eligible is True
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == 'protected_grounded_answer:fallback_to_original'


def test_answer_experience_repairs_clarify_with_supplemental_focus(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Perfeito, seguimos com Lucas Oliveira.'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Lucas Oliveira',
                            'finance_student_name': 'Lucas Oliveira',
                            'active_task': 'finance:billing',
                        }
                    },
                }
            ],
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    async def fake_compose(**kwargs):
        return 'Lucas Oliveira está com 1 fatura em aberto. A mais próxima é de R$ 1.450,00 e vence em 10/04/2026.'

    async def fake_supplemental(*, settings, request, focus, school_profile=None, actor=None, conversation_context=None):
        assert focus.student_name == 'Lucas Oliveira'
        return {
            'focused_draft': 'Lucas Oliveira está com 1 fatura em aberto. A mais próxima é de R$ 1.450,00 e vence em 10/04/2026.',
            'evidence_lines': ['Financeiro | aberto=1 | vencido=0'],
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._build_supplemental_focus', fake_supplemental)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)
    response = _response('Você pode informar qual aluno deseja consultar?').model_copy(
        update={'mode': OrchestrationMode.clarify}
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('e a próxima fatura?'),
            response=response,
            settings=_settings(),
            stack_name='specialist_supervisor',
        )
    )

    assert 'R$ 1.450,00' in updated.message_text
    assert updated.answer_experience_applied is True
    assert updated.answer_experience_reason == 'clarify_repair_grounded_answer:supplemental_focus_direct'


def test_answer_experience_blocks_cross_domain_grade_leak(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'Para justificar as faltas do Lucas, você pode entregar o atestado na secretaria da escola. Sobre a nota de História do Lucas, a avaliação B1 foi 6.70/10.00.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = _response('Para justificar as faltas do Lucas, você pode entregar o atestado na secretaria da escola.')
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('é atestado de ficar dormindo, serve?'),
            response=original,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'não serve como justificativa válida' in updated.message_text
    assert 'nota de História' not in updated.message_text


def test_answer_experience_clarifies_unknown_student_instead_of_reusing_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Lucas Oliveira',
                            'active_task': 'academic:grades',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True, 'can_view_finance': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True, 'can_view_finance': True},
            ]
        }

    async def fake_plan(**kwargs):
        return {'action': 'keep', 'message': '', 'retry_query': '', 'confidence': 0.2, 'reason': 'bad_keep'}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('qual a nota da laura?'),
            response=_response('Notas de Lucas Oliveira:\n- História: média parcial 6,8'),
            settings=_settings(),
            stack_name='specialist_supervisor',
        )
    )

    assert 'Laura' in updated.message_text
    assert 'Lucas Oliveira' in updated.message_text
    assert updated.mode == OrchestrationMode.clarify


def test_answer_experience_clarifies_unknown_subject_instead_of_returning_stale_grade(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Lucas Oliveira',
                            'active_task': 'academic:grades',
                            'active_subject': 'Fisica',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True, 'can_view_finance': True},
            ]
        }

    async def fake_plan(**kwargs):
        return {'action': 'keep', 'message': '', 'retry_query': '', 'confidence': 0.1, 'reason': 'bad_keep'}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('e as notas de dança?'),
            response=_response('A média parcial de Lucas Oliveira em Física é 5,8.'),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'Danca' in updated.message_text or 'dança' in updated.message_text.lower()
    assert 'Física' not in updated.message_text
    assert updated.mode == OrchestrationMode.clarify
    assert updated.answer_experience_applied is True


def test_answer_experience_clarifies_subject_without_student_using_linked_names(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True, 'can_view_finance': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True, 'can_view_finance': True},
            ]
        }

    async def fake_plan(**kwargs):
        return {'action': 'keep', 'message': '', 'retry_query': '', 'confidence': 0.2, 'reason': 'bad_keep'}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('e de english'),
                response=_response('Sim, a Língua Inglesa é um dos componentes curriculares oferecidos no Ensino Médio do Colégio Horizonte.').model_copy(
                    update={
                        'classification': IntentClassification(
                            domain=QueryDomain.institution,
                            access_tier=AccessTier.public,
                            confidence=0.4,
                            reason='llamaindex_public_profile',
                    ),
                    'reason': 'llamaindex_public_profile',
                }
            ),
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert updated.mode is OrchestrationMode.clarify
    assert 'Lingua Inglesa' in updated.message_text
    assert 'Lucas Oliveira' in updated.message_text
    assert 'Ana Oliveira' in updated.message_text


def test_answer_experience_prefers_supplemental_focus_for_finance_student_resolution_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'finance_student_name': 'Lucas Oliveira',
                            'academic_student_name': 'Lucas Oliveira',
                            'active_task': 'finance:billing',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    async def fake_compose(**kwargs):
        return 'Não encontrei um aluno chamado Lucas Como.'

    async def fake_supplemental(*, settings, request, focus, school_profile=None, actor=None, conversation_context=None):
        return {
            'focused_draft': 'Lucas Oliveira está com 1 fatura em aberto. A próxima vence em 10/04/2026 no valor de R$ 1.450,00.',
            'evidence_lines': ['Financeiro | aberto=1 | vencido=0'],
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._build_supplemental_focus', fake_supplemental)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    response = _response('Não encontrei um aluno chamado Lucas Como vinculado a esta conta.').model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.finance,
                access_tier=AccessTier.authenticated,
                confidence=1.0,
                reason='test',
            ),
            'selected_tools': ['get_financial_summary'],
            'reason': 'protected_finance_detail',
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('e o financeiro do lucas como está?'),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'R$ 1.450,00' in updated.message_text
    assert updated.answer_experience_reason == 'protected_grounded_answer:supplemental_focus_direct'


def test_answer_experience_builds_direct_attendance_justification_focus(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'KEEP'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    response = _response('Você poderia esclarecer melhor a dúvida sobre o atestado?').model_copy(
        update={
            'mode': OrchestrationMode.clarify,
            'classification': IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.public,
                confidence=0.7,
                reason='test',
            ),
            'selected_tools': [],
            'evidence_pack': None,
            'reason': 'clarify',
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('é atestado de ficar dormindo, serve?'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'não serve como justificativa válida' in updated.message_text
    assert updated.answer_experience_reason == 'clarify_repair_grounded_answer:supplemental_focus_direct'


def test_context_repair_returns_clarifying_question_when_missing_required_slot(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'student-lucas', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'student-ana', 'full_name': 'Ana Oliveira'},
            ]
        }

    async def fake_plan(**kwargs):
        return {
            'action': 'clarify',
            'message': 'Você quer consultar Lucas Oliveira ou Ana Oliveira?',
            'retry_query': '',
            'confidence': 0.82,
            'reason': 'missing_student_slot',
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)

    response = _response('Você pode informar qual aluno deseja consultar?').model_copy(
        update={'mode': OrchestrationMode.clarify}
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('e a próxima prova?'),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.mode is OrchestrationMode.clarify
    assert updated.message_text == 'Para qual aluno você quer ver as próximas provas: Lucas Oliveira ou Ana Oliveira?'
    assert updated.context_repair_applied is True
    assert updated.context_repair_action == 'clarify'


def test_context_repair_does_not_override_terminal_semantic_ingress_input_clarification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {'linked_students': [{'student_id': 'student-lucas', 'full_name': 'Lucas Oliveira'}]}

    async def fake_compose(**kwargs):
        return kwargs['draft_text']

    async def fail_plan(**kwargs):
        raise AssertionError('terminal semantic ingress should not invoke context_repair_planner')

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fail_plan)

    response = _public_response('Nao consegui interpretar essa mensagem com seguranca.').model_copy(
        update={
            'reason': 'python_functions_native_semantic_ingress:input_clarification',
            'graph_path': ['python_functions', 'semantic_ingress:input_clarification'],
            'llm_stages': ['semantic_ingress_classifier'],
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Nao foi isso que falei'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.message_text == 'Nao consegui interpretar essa mensagem com seguranca.'
    assert updated.context_repair_applied is False
    assert updated.answer_experience_reason == 'structured_grounded_answer'


def test_context_repair_does_not_override_terminal_semantic_ingress_language_preference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {'linked_students': [{'student_id': 'student-lucas', 'full_name': 'Lucas Oliveira'}]}

    async def fake_compose(**kwargs):
        return kwargs['draft_text']

    async def fail_plan(**kwargs):
        raise AssertionError('terminal semantic ingress should not invoke context_repair_planner')

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fail_plan)

    response = _public_response('Perfeito. A partir daqui eu respondo em portugues.').model_copy(
        update={
            'reason': 'python_functions_native_semantic_ingress:language_preference',
            'graph_path': ['python_functions', 'semantic_ingress:language_preference'],
            'llm_stages': ['semantic_ingress_classifier'],
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Nao foi isso que falei'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'portugues' in updated.message_text.lower() or 'português' in updated.message_text.lower()
    assert updated.context_repair_applied is False
    assert updated.answer_experience_reason == 'structured_grounded_answer:terminal_language_preference_preserved'


def test_terminal_language_preference_preserves_localized_surface_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {'linked_students': [{'student_id': 'student-lucas', 'full_name': 'Lucas Oliveira'}]}

    async def fail_compose(**kwargs):
        raise AssertionError('terminal language_preference should preserve deterministic answer')

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fail_compose)

    response = _public_response(
        'Entendo sua dúvida. No Colegio Horizonte, o termo "admissions" deve ser lido junto com "sales".'
    ).model_copy(
        update={
            'reason': 'langgraph_semantic_ingress:language_preference',
            'graph_path': ['langgraph', 'semantic_ingress:language_preference'],
            'llm_stages': ['semantic_ingress_classifier'],
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Por que admissions ta em ingles?'),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    normalized = updated.message_text.lower()
    assert 'admissions' not in normalized
    assert 'sales' not in normalized
    assert 'matricula e atendimento comercial' in normalized
    assert updated.answer_experience_reason == 'structured_grounded_answer:terminal_language_preference_preserved'


def test_context_repair_runs_second_retrieval_before_giving_up(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': [{'sender_type': 'user', 'content': 'como funciona a recuperação?'}]}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_plan(**kwargs):
        return {
            'action': 'retry_retrieval',
            'message': '',
            'retry_query': 'recuperacao paralela segunda chamada calendario escolar',
            'confidence': 0.71,
            'reason': 'retry_with_enriched_query',
        }

    async def fake_retry(**kwargs):
        response = kwargs['response']
        return response.model_copy(
            update={
                'message_text': 'A recuperação paralela ocorre ao longo do bimestre, e a segunda chamada segue o calendário e as orientações oficiais.',
                'used_llm': True,
                'llm_stages': ['context_repair_planner', 'retrieval_retry_answer'],
                'answer_experience_eligible': True,
                'answer_experience_applied': True,
                'answer_experience_reason': 'context_repair:second_retrieval_retry',
                'context_repair_applied': True,
                'context_repair_action': 'retry_retrieval',
                'context_repair_reason': 'second_retrieval_retry',
                'retrieval_retry_applied': True,
                'retrieval_retry_reason': kwargs['retry_query'],
            }
        )

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._attempt_second_retrieval', fake_retry)

    response = MessageResponse(
        message_text='Não encontrei base suficiente para confirmar isso na resposta atual.',
        mode=OrchestrationMode.hybrid_retrieval,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.9,
            reason='test',
        ),
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        selected_tools=['public_retrieval'],
        evidence_pack=MessageEvidencePack(
            strategy='retrieval',
            summary='Busca inicial fraca.',
            source_count=0,
            support_count=0,
            supports=[],
        ),
        reason='initial_retrieval_weak',
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('e a recuperação, como funciona?').model_copy(update={'user': UserContext(role='anonymous', authenticated=False)}),
            response=response,
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert 'recuperação paralela' in updated.message_text
    assert updated.context_repair_applied is True
    assert updated.context_repair_action == 'retry_retrieval'
    assert updated.retrieval_retry_applied is True


def test_context_repair_retries_on_public_explicit_limitation_with_weak_support(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': [{'sender_type': 'user', 'content': 'como funciona a recuperação paralela?'}]}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_plan(**kwargs):
        return {
            'action': 'retry_retrieval',
            'message': '',
            'retry_query': 'segunda chamada recuperacao paralela calendario orientacoes oficiais',
            'confidence': 0.78,
            'reason': 'retry_on_explicit_limitation',
        }

    async def fake_retry(**kwargs):
        response = kwargs['response']
        return response.model_copy(
            update={
                'message_text': 'A segunda chamada se conecta à recuperação paralela porque ambas seguem as orientações acadêmicas e o calendário oficial.',
                'used_llm': True,
                'llm_stages': ['context_repair_planner', 'retrieval_retry_answer'],
                'answer_experience_eligible': True,
                'answer_experience_applied': True,
                'answer_experience_reason': 'context_repair:second_retrieval_retry',
                'context_repair_applied': True,
                'context_repair_action': 'retry_retrieval',
                'context_repair_reason': 'second_retrieval_retry',
                'retrieval_retry_applied': True,
                'retrieval_retry_reason': kwargs['retry_query'],
            }
        )

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._attempt_second_retrieval', fake_retry)

    response = MessageResponse(
        message_text='A resposta atual não trouxe evidência suficiente para confirmar como a segunda chamada se conecta com a recuperação paralela.',
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.76,
            reason='llamaindex_public_profile',
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=['public_profile'],
        evidence_pack=MessageEvidencePack(
            strategy='structured_tool',
            summary='Busca inicial fraca.',
            source_count=1,
            support_count=1,
            supports=[],
        ),
        reason='llamaindex_public_profile',
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('e a segunda chamada, como isso se conecta?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response,
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert 'segunda chamada' in updated.message_text.lower()
    assert updated.context_repair_applied is True
    assert updated.context_repair_action == 'retry_retrieval'
    assert updated.retrieval_retry_applied is True


def test_answer_experience_uses_finance_status_filter_from_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'finance_student_name': 'Lucas Oliveira',
                            'active_task': 'finance:billing',
                            'finance_status_filter': 'overdue',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    async def fake_api_core_get(*, settings, path, params=None):
        assert path.endswith('/financial-summary')
        return {
            'summary': {
                'invoices': [
                    {'status': 'open', 'amount_due': '1450.00', 'due_date': '2026-04-10', 'reference_month': 'abril/2026'},
                    {'status': 'overdue', 'amount_due': '1450.00', 'due_date': '2026-03-10', 'reference_month': 'março/2026'},
                ],
                'open_invoice_count': 1,
                'overdue_invoice_count': 1,
            }
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Lucas Oliveira está com 1 fatura em aberto.').model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.finance,
                access_tier=AccessTier.authenticated,
                confidence=1.0,
                reason='test',
            ),
            'selected_tools': ['get_financial_summary'],
            'reason': 'protected_finance_detail',
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('e as vencidas dele?'),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'fatura(s) vencida(s)' in updated.message_text
    assert '10/03/2026' in updated.message_text
    assert updated.answer_experience_reason == 'protected_grounded_answer:supplemental_focus_direct'


def test_context_repair_clarifies_after_failed_retry_on_relationship_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': [{'sender_type': 'user', 'content': 'como funciona a recuperação paralela?'}]}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_plan(**kwargs):
        return {
            'action': 'retry_retrieval',
            'message': '',
            'retry_query': 'segunda chamada recuperacao paralela calendario orientacoes oficiais',
            'confidence': 0.66,
            'reason': 'retry_with_enriched_query',
        }

    async def fake_retry(**kwargs):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._attempt_second_retrieval', fake_retry)

    response = MessageResponse(
        message_text='A resposta atual não trouxe evidência suficiente para confirmar como a segunda chamada se conecta com a recuperação paralela.',
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.76,
            reason='weak_public_answer',
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=['public_profile'],
        evidence_pack=MessageEvidencePack(
            strategy='structured_tool',
            summary='Busca inicial fraca.',
            source_count=1,
            support_count=1,
            supports=[],
        ),
        reason='weak_public_answer',
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('e a segunda chamada, como isso se conecta?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.mode is OrchestrationMode.clarify
    assert 'segunda chamada' in updated.message_text.lower()
    assert updated.context_repair_applied is True
    assert updated.context_repair_action == 'clarify'


def test_answer_experience_accepts_short_subject_specific_supplemental_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'academic_student_name': 'Lucas Oliveira',
                            'active_task': 'academic:grades',
                            'active_subject': 'Historia',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        assert path.endswith('/academic-summary')
        return {
            'summary': {
                'grades': [
                    {'subject_name': 'Historia', 'score': '6.7', 'max_score': '10.0'},
                    {'subject_name': 'Historia', 'score': '6.9', 'max_score': '10.0'},
                    {'subject_name': 'Matematica', 'score': '8.7', 'max_score': '10.0'},
                ]
            }
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    original = _response(
        'Notas de Lucas Oliveira:\n- Biologia: 8,4/10\n- História: 6,7/10\n- Matemática: 8,7/10'
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('qual a nota de história do lucas?'),
            response=original,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.message_text == 'Em Historia, Lucas Oliveira está com média parcial de 6,8/10.'
    assert updated.answer_experience_reason == 'protected_grounded_answer:supplemental_focus_direct'


def test_answer_experience_repairs_public_pricing_followup_with_slot_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_grade_year': '3o ano',
                            'public_pricing_quantity': '20',
                            'public_pricing_price_kind': 'enrollment_fee',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '350.00',
                    'notes': 'Valor comercial publico de referencia para 2026.',
                }
            ],
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = _response('Você está perguntando sobre a matrícula para 20 filhos?').model_copy(
        update={
            'mode': OrchestrationMode.clarify,
            'classification': IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.public,
                confidence=0.8,
                reason='test',
            ),
            'selected_tools': [],
            'evidence_pack': None,
            'reason': 'clarify',
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('E para 20 filhos?'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert '20 aluno(s)' in updated.message_text
    assert 'Ensino Medio' in updated.message_text
    assert 'R$ 7.000,00' in updated.message_text
    assert updated.answer_experience_reason == 'clarify_repair_grounded_answer:supplemental_focus_direct'


def test_answer_experience_clarifies_short_ambiguous_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    async def fake_plan(**kwargs):
        return {'action': 'keep', 'message': '', 'retry_query': '', 'confidence': 0.1, 'reason': 'weak_keep'}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('do lucas serve?'),
            response=_response('Notas de Lucas Oliveira:\n- História: 6,8/10\n- Matemática: 7,4/10'),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.mode == OrchestrationMode.clarify
    assert 'nota, as próximas provas ou a frequência de Lucas Oliveira' in updated.message_text
    assert updated.context_repair_action == 'clarify'


def test_answer_experience_repairs_meta_followup_with_previous_topic(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'assistant', 'content': 'Próximas avaliações de Lucas Oliveira:\n- Física: B2 em 10/04/2026'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    async def fake_plan(**kwargs):
        return {'action': 'keep', 'message': '', 'retry_query': '', 'confidence': 0.1, 'reason': 'weak_keep'}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('essa resposta aqui era sobre o que então?'),
            response=_response('A média parcial de Lucas Oliveira em Física é 5,8.'),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.mode == OrchestrationMode.clarify
    assert (
        'A resposta anterior estava falando de próximas avaliações.' in updated.message_text
        or 'A resposta anterior estava falando de próximas provas.' in updated.message_text
    )


def test_answer_experience_answers_grade_timeframe_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                            'active_subject': 'Historia',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        assert path.endswith('/academic-summary')
        return {
            'summary': {
                'grades': [
                    {'subject_name': 'Historia', 'term_code': 'B1', 'item_title': 'Avaliação B1', 'score': '6.7', 'max_score': '10.0'},
                    {'subject_name': 'Historia', 'term_code': 'B1', 'item_title': 'Trabalho B1', 'score': '6.9', 'max_score': '10.0'},
                ]
            }
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('isso é de qual bimestre?'),
            response=_response('A média parcial de Lucas Oliveira em História é 6,8.'),
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert 'No recorte atual, as notas de Lucas Oliveira em Historia são do B1.' == updated.message_text
    assert updated.answer_experience_reason == 'protected_grounded_answer:supplemental_focus_direct'


def test_answer_experience_repair_grade_followup_clarifies_only_grade_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    async def fake_plan(**kwargs):
        return {
            'action': 'retry_retrieval',
            'message': 'bad planner output',
            'retry_query': 'bad',
            'confidence': 0.95,
            'reason': 'bad_retry',
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.plan_context_repair_with_provider', fake_plan)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('não quero justificar, quero saber a nota do lucas'),
            response=_response('Para justificar faltas, a escola aceita atestado médico formal.'),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.mode is OrchestrationMode.clarify
    assert 'boletim completo de Lucas Oliveira' in updated.message_text
    assert 'financeiro' not in updated.message_text.lower()
    assert updated.context_repair_action == 'clarify'


def test_answer_experience_normalizes_english_alias_to_lingua_inglesa(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        assert path.endswith('/academic-summary')
        return {
            'summary': {
                'grades': [
                    {'subject_name': 'Lingua Inglesa', 'score': '8.9', 'max_score': '10.0'},
                    {'subject_name': 'Historia', 'score': '6.7', 'max_score': '10.0'},
                ]
            }
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('quero saber a nota de english do lucas'),
            response=_response('Notas de Lucas Oliveira:\n- História: 6,7/10\n- Língua Inglesa: 8,9/10'),
            settings=_settings(),
            stack_name='specialist_supervisor',
        )
    )

    assert updated.message_text == 'Em Lingua Inglesa, Lucas Oliveira está com média parcial de 8,9/10.'


def test_answer_experience_prefers_concise_unknown_subject_supplemental_focus(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                            'active_subject': 'Fisica',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {
                    'student_id': 'student-lucas',
                    'full_name': 'Lucas Oliveira',
                    'can_view_academic': True,
                    'can_view_finance': True,
                }
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        return {
            'summary': {
                'grades': [
                    {'subject_name': 'Historia', 'score': '6.7', 'max_score': '10.0'},
                    {'subject_name': 'Lingua Inglesa', 'score': '8.9', 'max_score': '10.0'},
                    {'subject_name': 'Matematica', 'score': '7.7', 'max_score': '10.0'},
                ]
            }
        }

    async def fake_compose(**kwargs):
        return 'Peço desculpas pelo erro anterior. Verifiquei novamente e não encontrei notas para a disciplina de Dança no registro de Lucas Oliveira. As notas disponíveis são: História, Inglês e Matemática.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('não é física, é aulas de dança, as notas'),
            response=_response('A média parcial de Lucas Oliveira em Física é 5,8.'),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.message_text == 'Não encontrei a disciplina Danca para Lucas Oliveira neste registro. As disciplinas disponíveis aqui incluem: Historia, Lingua Inglesa, Matematica.'


def test_answer_experience_repairs_public_temporal_followup_for_started_classes(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {
                    'sender_type': 'assistant',
                    'content': 'As aulas para o Ensino Fundamental II e Ensino Médio começam em 2 de fevereiro de 2026.',
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Entao as aulas ja comecaram').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response(
                'Não, as aulas ainda não começaram. Elas estão previstas para 2 de fevereiro de 2026. Hoje é 5 de abril de 2026.',
                domain=QueryDomain.calendar,
            ),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.message_text.startswith('Sim.')
    assert '2 de fevereiro de 2026' in updated.message_text
    assert updated.answer_experience_reason.endswith('public_temporal_followup')


def test_answer_experience_blocks_false_promise_for_public_notification(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {
                    'sender_type': 'assistant',
                    'content': 'A cerimônia interna de conclusão do Ensino Fundamental II está prevista para 12 de dezembro de 2026.',
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Me avisa a data da formatura quando chegar perto').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response(
                'Claro! A cerimônia interna de conclusão do Ensino Fundamental II está prevista para 12 de dezembro de 2026.',
                domain=QueryDomain.calendar,
            ),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'nao consigo te avisar automaticamente' in updated.message_text.lower()
    assert '12 de dezembro de 2026' in updated.message_text


def test_answer_experience_repairs_parking_capacity_misroute(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Quantas vagas tem no estacionamento da escola?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response(
                'Se você quer se candidatar para dar aula em Colegio Horizonte, o caminho mais direto hoje é talentos@colegiohorizonte.edu.br.',
                domain=QueryDomain.institution,
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'estacionamento' in updated.message_text.lower()
    assert 'talentos@' not in updated.message_text.lower()


def test_answer_experience_repairs_parking_followup_after_public_pricing_context(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Mensalidade do ensino medio'},
                {
                    'sender_type': 'assistant',
                    'content': 'Para Ensino Medio no turno Manha, a mensalidade pública de referência é R$ 1.450,00 e a taxa de matrícula é R$ 350,00.',
                },
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_quantity': '200',
                            'public_pricing_price_kind': 'enrollment_fee',
                        }
                    },
                }
            ],
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('E no estacionamento?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response(
                'Para 200 aluno(s) em Ensino Medio, usando o valor público de referência de taxa de matrícula, a simulação fica 200 x R$ 350,00 = R$ 70.000,00.',
                domain=QueryDomain.institution,
                mode=OrchestrationMode.clarify,
            ),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'estacionamento' in updated.message_text.lower()
    assert '70.000,00' not in updated.message_text


def test_answer_experience_repairs_school_capacity_followup_after_pricing_context(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Mensalidade do ensino medio'},
                {'sender_type': 'assistant', 'content': 'A mensalidade do Ensino Médio é R$ 1.450,00 e a matrícula é R$ 350,00.'},
                {'sender_type': 'user', 'content': 'E se eu matricular meus 200 filhos?'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Quantas vagas tem?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response(
                'Se voce quer se candidatar para dar aula em Colegio Horizonte, o caminho mais direto hoje e email talentos@colegiohorizonte.edu.br.',
                domain=QueryDomain.institution,
            ),
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert 'vagas para alunos' in updated.message_text.lower() or 'capacidade total da escola' in updated.message_text.lower()


def test_answer_experience_uses_recent_calendar_context_for_event_distance_followup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {
                    'sender_type': 'assistant',
                    'content': 'A cerimônia interna de conclusão do Ensino Fundamental II está prevista para 12 de dezembro de 2026, no fim da tarde.',
                },
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Ta longe ainda').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response(
                'A formatura esta prevista para 6 de outubro de 2025; essa data ja passou.',
                domain=QueryDomain.calendar,
            ),
            settings=_settings(),
            stack_name='specialist_supervisor',
        )
    )

    assert '12 de dezembro de 2026' in updated.message_text
    assert '6 de outubro de 2025' not in updated.message_text


def test_answer_experience_prefers_recent_event_topic_for_notification_followup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {
                    'sender_type': 'assistant',
                    'content': 'A cerimônia interna de conclusão do Ensino Fundamental II está prevista para 12 de dezembro de 2026, no fim da tarde.',
                },
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Vão me avisar?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response(
                'Hoje é 6 de abril de 2026. Posso ajudar se você disser a que aviso se refere.',
                domain=QueryDomain.calendar,
                mode=OrchestrationMode.clarify,
            ),
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert '12 de dezembro de 2026' in updated.message_text
    assert '6 de abril de 2026' not in updated.message_text


def test_answer_experience_public_pricing_followup_mentions_requested_grade_year(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quanto seria a matricula para 20 filhos no ensino medio?'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'focus_kind': 'public',
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_grade_year': '3o ano',
                            'public_pricing_quantity': '20',
                            'public_pricing_price_kind': 'enrollment_fee',
                        }
                    },
                }
            ],
        }

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '350.00',
                }
            ],
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('3o').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response(
                'Para 20 aluno(s) em Ensino Medio, usando o valor público de referência de taxa de matrícula, a simulação fica 20 x R$ 350,00 = R$ 7.000,00.',
                domain=QueryDomain.institution,
                mode=OrchestrationMode.clarify,
            ),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert '3o ano do Ensino Medio' in updated.message_text
    assert 'dar aula' not in updated.message_text.lower()


def test_answer_experience_repairs_public_capacity_even_when_llm_polish_is_not_eligible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Mensalidade do ensino medio'},
                {'sender_type': 'assistant', 'content': 'A mensalidade do Ensino Médio é R$ 1.450,00 e a matrícula é R$ 350,00.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = MessageResponse(
        message_text='talentos@colegiohorizonte.edu.br',
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.9,
            reason='test',
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=[],
        evidence_pack=None,
        reason='public_profile',
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Quantas vagas tem?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'vagas para alunos' in updated.message_text.lower() or 'capacidade total da escola' in updated.message_text.lower()
    assert 'talentos@' not in updated.message_text.lower()


def test_answer_experience_repairs_generic_school_capacity_even_without_pricing_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Quantas vagas tem?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response(
                'Posso te explicar vagas para trabalhar, estacionamento ou alunos, se você quiser.',
                domain=QueryDomain.institution,
                mode=OrchestrationMode.clarify,
            ),
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert 'numero fechado de vagas para alunos' in updated.message_text.lower()
    assert 'trabalhar' not in updated.message_text.lower()


def test_answer_experience_repairs_public_pricing_followup_without_general_polish_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'public:pricing',
                            'public_pricing_segment': 'Ensino Medio',
                            'public_pricing_grade_year': '3o ano',
                            'public_pricing_quantity': '20',
                            'public_pricing_price_kind': 'enrollment_fee',
                        }
                    },
                }
            ]
        }

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '350.00',
                }
            ],
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = MessageResponse(
        message_text='R$ 350,00',
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.public,
            confidence=0.8,
            reason='test',
        ),
        retrieval_backend=RetrievalBackend.none,
        selected_tools=[],
        evidence_pack=None,
        reason='public_profile',
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('3o').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert '3o ano do Ensino Medio' in updated.message_text
    assert 'R$ 7.000,00' in updated.message_text


def test_answer_experience_preserves_restricted_document_no_match_without_student_clarify(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    original = (
        'Consultei os documentos internos disponiveis, mas nao encontrei uma orientacao restrita especifica para: '
        '"No manual interno do professor, como ficam registro de avaliacoes e comunicacao pedagogica?".'
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('No manual interno do professor, como ficam registro de avaliacoes e comunicacao pedagogica?'),
            response=_restricted_no_match_response(
                original,
                reason='langgraph_restricted_document_no_match',
            ),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False


def test_answer_experience_preserves_public_process_compare_lane(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'Valores públicos de referência para 2026.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = (
        'Na rematricula, a vaga continua na escola; na transferencia, a vaga e encerrada para migracao; '
        'no cancelamento, a matricula e encerrada sem continuidade.'
    )
    response = _public_response(original).model_copy(
        update={
            'reason': 'langgraph_public_canonical_lane:public_bundle.process_compare',
            'candidate_chosen': 'deterministic',
            'candidate_reason': 'public_canonical_lane:public_bundle.process_compare',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Compare rematricula, transferencia e cancelamento destacando o que muda na pratica.').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == 'structured_grounded_answer:preserve_process_compare'


@pytest.mark.parametrize(
    ("prompt", "reason", "original", "expected_reason"),
    [
        (
            'Quero uma sintese publica de como disciplina, faltas e recuperacao se cruzam quando o desempenho do aluno cai. Traga a resposta de forma concreta.',
            'langgraph_public_canonical_lane:public_bundle.conduct_frequency_recovery',
            'Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar. '
            'Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico. '
            'Em termos operacionais, primeiro a familia regulariza a justificativa da ausencia, depois confere a segunda chamada e, por fim, acompanha a recuperacao prevista para o aluno.',
            'structured_grounded_answer:preserve_public_canonical_lane',
        ),
        (
            'Sem sair do escopo do projeto, de que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio?',
            'python_functions_native_canonical_lane:public_bundle.facilities_study_support',
            'Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo. '
            'No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno. '
            'Na pratica, biblioteca, laboratorios e estudo orientado funcionam como tres apoios complementares: pesquisa e leitura, experimentacao e producao, e organizacao da rotina de estudo.',
            'structured_grounded_answer:preserve_public_canonical_lane',
        ),
        (
            'Compare a orientacao publica e a interna sobre acessos diferentes entre responsaveis e destaque o que muda de linguagem e de acao.',
            'langgraph_public_canonical_lane:public_bundle.access_scope_compare',
            'Quando a pergunta compara a orientacao publica com a interna sobre acessos diferentes entre responsaveis, a mudanca principal aparece em linguagem e em acao. '
            'Na linguagem publica do Colegio Horizonte, a escola orienta por canais oficiais e evita detalhar permissao interna por perfil de responsavel. '
            'Ja na orientacao interna, a linguagem fica operacional: a equipe verifica vinculo, escopo autorizado, diferenca de acesso entre perfis e registro antes de liberar qualquer consulta sensivel. '
            'Na pratica, a camada publica explica o caminho e manda confirmar com secretaria ou coordenacao; a camada interna decide quem pode acessar o que e qual setor valida excecoes.',
            'structured_grounded_answer:preserve_public_canonical_lane',
        ),
    ],
)
def test_answer_experience_preserves_additional_public_canonical_lanes(
    monkeypatch: pytest.MonkeyPatch,
    prompt: str,
    reason: str,
    original: str,
    expected_reason: str,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'Parafraseei demais e nao deveria vencer aqui.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    response = _public_response(original).model_copy(
        update={
            'reason': reason,
            'candidate_chosen': 'deterministic',
            'candidate_reason': reason.replace('_native_', '_').replace('langgraph_', '').replace('python_functions_', ''),
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request(prompt).model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == expected_reason


def test_answer_experience_preserves_public_pricing_projection_when_response_already_complete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'Para 3 filhos, a taxa de matrícula total fica R$ 1.050,00.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = (
        'Para 3 filhos no Ensino Médio (Manhã), a taxa de matrícula total fica R$ 1.050,00 '
        'e a mensalidade pública de referência por mês fica 3 x R$ 1.450,00 = R$ 4.350,00.'
    )
    response = _public_response(original).model_copy(
        update={
            'reason': 'python_functions_native_pricing_projection',
            'candidate_chosen': 'deterministic',
            'candidate_reason': 'python_functions_native_pricing_projection',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Quanto eu pagaria de matricula e por mes para 3 filhos usando a referencia publica atual?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == 'structured_grounded_answer:preserve_pricing_projection'


def test_answer_experience_preserves_protected_finance_surface_for_negotiation_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {'linked_students': [{'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_finance': True}]}

    async def fake_compose(**kwargs):
        return 'Valores publicos de referencia de mensalidade e matricula.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = (
        'Resumo financeiro das contas vinculadas:\n'
        '- Lucas Oliveira: 1 em aberto, 0 vencida(s), proximo vencimento 15 de abril de 2026 (350.00).\n'
        '- Proximo passo recomendado: acompanhar esse vencimento e, se a ideia for negociar o restante, acionar o financeiro pelo canal oficial.\n'
        '- Mensalidade: mostra as cobrancas recorrentes do aluno neste recorte.\n'
        '- Taxa: aponta cobrancas avulsas ou taxas administrativas quando existirem.\n'
        '- Atraso: indica se ja existe fatura vencida pressionando o quadro atual.\n'
        '- Desconto: sinaliza abatimentos registrados neste panorama.'
    )
    response = _response(original).model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.finance,
                access_tier=AccessTier.authenticated,
                confidence=0.97,
                reason='python_functions_local_protected:finance',
            ),
            'selected_tools': ['get_financial_summary'],
            'reason': 'python_functions_native_structured:finance',
            'candidate_chosen': 'deterministic',
            'candidate_reason': 'python_functions_native_structured:finance',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Paguei parte da mensalidade do Lucas e quero entender o que ja aparece e como negociar o restante.'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == 'protected_grounded_answer:preserve_protected_finance_surface'


def test_answer_experience_preserves_process_compare_for_stack_specific_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'Valores públicos de referência.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = (
        'Na rematricula, a vaga continua na escola; na transferencia, a vaga e encerrada para migracao; '
        'no cancelamento, a matricula e encerrada sem continuidade.'
    )
    response = _public_response(original).model_copy(
        update={
            'reason': 'python_functions_native_canonical_lane:public_bundle.process_compare',
            'candidate_chosen': 'deterministic',
            'candidate_reason': 'deterministic_candidate_selected',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Compare rematricula, transferencia e cancelamento destacando o que muda na pratica.').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == 'structured_grounded_answer:preserve_process_compare'


def test_answer_experience_prefers_canonical_timeline_lane_for_public_sequence_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'No calendario publico atual, a reuniao de pais acontece em 28 de marco de 2026.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    response = _public_response(
        'No calendario publico atual, a reuniao de pais acontece em 28 de marco de 2026.'
    ).model_copy(
        update={
            'reason': 'python_functions_native_canonical_lane:public_bundle.timeline_lifecycle',
            'candidate_reason': 'public_canonical_lane:public_bundle.timeline_lifecycle',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request(
                'Quais sao os marcos entre matricula, inicio do ano letivo e reuniao de responsaveis no calendario publico de 2026?'
            ).model_copy(update={'user': UserContext(role='anonymous', authenticated=False)}),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'matricula' in lowered or 'matrícula' in lowered
    assert 'inicio das aulas' in lowered or 'aulas' in lowered
    assert 'responsaveis' in lowered


def test_answer_experience_preserves_restricted_internal_document_no_match_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def unexpected_context(*, settings, request):
        raise AssertionError('should not fetch conversation context for restricted no-match preserve')

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', unexpected_context)

    response = MessageResponse(
        message_text=(
            'Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional '
            'com hospedagem para o ensino medio nos documentos internos disponiveis.'
        ),
        mode=OrchestrationMode.structured_tool,
        classification=IntentClassification(
            domain=QueryDomain.institution,
            access_tier=AccessTier.authenticated,
            confidence=0.95,
            reason='restricted',
        ),
        retrieval_backend=RetrievalBackend.qdrant_hybrid,
        selected_tools=['search_documents'],
        evidence_pack=MessageEvidencePack(
            strategy='hybrid_retrieval',
            summary='Busca restrita sem resultado focal.',
            source_count=0,
            support_count=0,
            supports=[],
        ),
        reason='llamaindex_restricted_doc_no_match',
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request(
                'Existe orientacao interna para viagem internacional com hospedagem envolvendo turmas do ensino medio?'
            ),
            response=response,
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert updated.message_text == response.message_text
    assert updated.answer_experience_applied is False


def test_answer_experience_preserves_restricted_doc_no_match_surface_from_reason_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def unexpected_context(*, settings, request):
        raise AssertionError('should not fetch conversation context for restricted no-match preserve')

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', unexpected_context)

    response = _restricted_no_match_response(
        'Não encontrei uma orientação específica sobre procedimentos internos para viagens internacionais com hospedagem para alunos do ensino médio nos documentos disponíveis. Para obter essa informação, o ideal é consultar diretamente o setor responsável por esse tipo de protocolo na escola.',
        reason='langgraph_restricted_doc_no_match',
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Ha procedimento interno de viagem internacional com hospedagem para alunos do ensino medio. Seja objetivo e grounded.'),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.message_text == response.message_text
    assert updated.answer_experience_applied is False


def test_answer_experience_upgrades_public_pricing_focus_for_matricula_e_por_mes_wording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'tuition_reference': [
                {
                    'segment': 'Ensino Medio',
                    'shift_label': 'Manha',
                    'monthly_amount': '1450.00',
                    'enrollment_fee': '350.00',
                }
            ],
        }

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'KEEP'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    response = _public_response(
        'Para 3 aluno(s), se eu usar a taxa publica de matricula hoje publicada em Ensino Medio, a simulacao fica 3 x R$ 350,00 = R$ 1.050,00.'
    ).model_copy(
        update={
            'reason': 'python_functions_native_public_compound',
            'candidate_reason': 'python_functions_native_public_compound',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request(
                'Se eu projetar 3 filhos no colegio, qual e o valor de matricula e quanto fica por mes na base publica?'
            ).model_copy(update={'user': UserContext(role='anonymous', authenticated=False)}),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'matricula' in lowered or 'matrícula' in lowered
    assert 'mensalidade' in lowered
    assert 'por mes' in lowered
    assert 'r$ 4.350,00' in lowered


def test_answer_experience_preserves_llamaindex_process_compare_on_telegram(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'Valores públicos de referência.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = (
        'Na rematricula, a vaga continua na escola; na transferencia, a vaga e encerrada para migracao; '
        'no cancelamento, a matricula e encerrada sem continuidade.'
    )
    response = _public_response(original).model_copy(
        update={
            'reason': 'llamaindex_public_canonical_lane:public_bundle.process_compare',
            'candidate_chosen': 'deterministic',
            'candidate_reason': 'public_canonical_lane:public_bundle.process_compare',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Compare rematricula, transferencia e cancelamento destacando o que muda na pratica.').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response,
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == 'structured_grounded_answer:preserve_process_compare'


def test_answer_experience_preserves_authenticated_access_scope_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    async def fake_compose(**kwargs):
        return 'Não encontrei Academico entre os alunos vinculados.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = (
        'Sua conta esta autenticada e vinculada a Lucas Oliveira e Ana Oliveira. '
        'Voce consegue consultar dados academicos e financeiros desses alunos neste Telegram.'
    )
    response = _response(original).model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.authenticated,
                confidence=1.0,
                reason='test',
            ),
            'reason': 'python_functions_native_authenticated_account_scope',
            'candidate_chosen': 'deterministic',
            'candidate_reason': 'python_functions_native_authenticated_account_scope',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == 'protected_grounded_answer:preserve_access_scope'


def test_answer_experience_preserves_public_service_routing_bundle(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'O atendimento geralmente acontece pelos canais institucionais.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = (
        'Hoje estes sao os responsaveis e canais mais diretos por assunto:\n'
        '- Atendimento comercial / Admissoes: bot, setor de admissoes ou WhatsApp comercial.\n'
        '- Financeiro: email financeiro@colegiohorizonte.edu.br e telefone (11) 3333-4203.\n'
        '- Direcao geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.'
    )
    response = _public_response(original).model_copy(
        update={
            'reason': 'python_functions_native_public_compound',
            'candidate_chosen': 'deterministic',
            'candidate_reason': 'deterministic_candidate_selected',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request(
                'Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola?'
            ).model_copy(update={'user': UserContext(role='anonymous', authenticated=False)}),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == 'structured_grounded_answer:preserve_service_routing'


def test_answer_experience_repairs_public_service_routing_quem_responde_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'service_catalog': [
                {'service_key': 'atendimento_admissoes', 'request_channel': 'bot, admissions ou WhatsApp comercial'},
                {'service_key': 'financeiro_escolar', 'request_channel': 'email financeiro@colegiohorizonte.edu.br'},
                {'service_key': 'solicitacao_direcao', 'request_channel': 'protocolo institucional'},
            ],
            'leadership_team': [
                {'title': 'Diretora geral', 'name': 'Helena Martins', 'contact_channel': 'direcao@colegiohorizonte.edu.br'}
            ],
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = _public_response('Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.').model_copy(
        update={
            'reason': 'python_functions_native_public_compound',
            'candidate_reason': 'python_functions_native_public_compound',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request(
                'Se eu precisar tratar desconto, financeiro e um assunto com a direcao, quem responde por cada frente?'
            ).model_copy(update={'user': UserContext(role='anonymous', authenticated=False)}),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'atendimento comercial / admissoes' in lowered
    assert 'financeiro' in lowered
    assert 'direcao' in lowered
    assert updated.answer_experience_reason.endswith(':public_direct_answer')


def test_answer_experience_repairs_public_service_routing_menu_geral_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'service_catalog': [
                {'service_key': 'atendimento_admissoes', 'request_channel': 'bot, admissions ou WhatsApp comercial'},
                {'service_key': 'financeiro_escolar', 'request_channel': 'email financeiro@colegiohorizonte.edu.br'},
                {'service_key': 'solicitacao_direcao', 'request_channel': 'protocolo institucional'},
            ],
            'leadership_team': [
                {'title': 'Diretora geral', 'name': 'Helena Martins', 'contact_channel': 'direcao@colegiohorizonte.edu.br'}
            ],
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = _public_response('Diretora geral: Helena Martins. Canal institucional: direcao@colegiohorizonte.edu.br.').model_copy(
        update={
            'reason': 'python_functions_native_public_compound',
            'candidate_reason': 'python_functions_native_public_compound',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request(
                'Nao me manda menu geral: quais setores e canais realmente resolvem bolsa, financeiro e direcao?'
            ).model_copy(update={'user': UserContext(role='anonymous', authenticated=False)}),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'financeiro' in lowered
    assert 'direcao' in lowered
    assert 'admissoes' in lowered or 'bolsas' in lowered
    assert updated.answer_experience_reason.endswith(':public_direct_answer')


def test_answer_experience_repairs_public_service_routing_followup_from_authenticated_misroute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola?'},
                {'sender_type': 'assistant', 'content': 'Hoje estes sao os responsaveis e canais mais diretos por assunto:\n- Atendimento comercial / Admissoes: bot, admissions ou WhatsApp comercial.\n- Financeiro: email financeiro@colegiohorizonte.edu.br.\n- Direcao: protocolo institucional.'},
            ]
        }

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'service_catalog': [
                {'service_key': 'atendimento_admissoes', 'request_channel': 'bot, admissions ou WhatsApp comercial'},
                {'service_key': 'financeiro_escolar', 'request_channel': 'email financeiro@colegiohorizonte.edu.br'},
                {'service_key': 'solicitacao_direcao', 'request_channel': 'protocolo institucional'},
            ],
            'leadership_team': [
                {'title': 'Diretora geral', 'name': 'Helena Martins', 'contact_channel': 'direcao@colegiohorizonte.edu.br'}
            ],
        }

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = _response('Nao encontrei Bolsas entre os alunos vinculados.').model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.authenticated,
                confidence=0.7,
                reason='structured_grounded_answer:context_repair_clarify',
            ),
            'mode': OrchestrationMode.clarify,
            'reason': 'structured_grounded_answer:context_repair_clarify',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Agora reduz para uma linha por setor, sem explicar o resto da escola.'),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'atendimento comercial / admissoes' in lowered
    assert 'financeiro' in lowered
    assert 'direcao' in lowered
    assert updated.answer_experience_reason.endswith(':public_direct_answer')


def test_answer_experience_repairs_public_timeline_order_followup_from_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quais sao os marcos entre matricula, inicio do ano letivo e reuniao de responsaveis no calendario publico de 2026?'},
                {'sender_type': 'assistant', 'content': 'Primeiro entra a matricula, depois comecam as aulas e, na sequencia, vem a reuniao inicial com as familias.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {'linked_students': [{'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'}]}

    async def fake_timeline(settings):
        return {
            'entries': [
                {'topic_key': 'admissions_opening', 'summary': 'Matricula comecou em 10/01/2026.'},
                {'topic_key': 'school_year_start', 'summary': 'Inicio das aulas em 02/02/2026.'},
                {'topic_key': 'family_meeting', 'summary': 'Primeira reuniao com responsaveis em 05/02/2026.'},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_timeline', fake_timeline)

    response = _public_response('Posso corrigir a resposta anterior, mas preciso que você me diga só o foco certo agora.')
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Nao quero o calendario inteiro. Quero so esse recorte em ordem.').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=response.model_copy(
                update={
                    'mode': OrchestrationMode.clarify,
                    'reason': 'structured_grounded_answer:context_repair_clarify',
                }
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'matricula' in lowered
    assert 'inicio das aulas' in lowered
    assert 'reuniao com responsaveis' in lowered or 'reunião com responsáveis' in updated.message_text.casefold()
    assert updated.answer_experience_reason.endswith(':public_direct_answer')


@pytest.mark.parametrize("stack_name", ["python_functions", "llamaindex"])
def test_answer_experience_repairs_public_calendar_reset_after_protected_digression(
    monkeypatch: pytest.MonkeyPatch,
    stack_name: str,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quando comecam as aulas?'},
                {'sender_type': 'assistant', 'content': 'No calendario publico atual, as aulas comecam em 2 de fevereiro de 2026.'},
                {'sender_type': 'user', 'content': 'E as notas da Ana?'},
                {'sender_type': 'assistant', 'content': 'Em Educacao Fisica, Ana Oliveira esta com media parcial de 7,0/10.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {'linked_students': [{'student_id': 'ana-id', 'full_name': 'Ana Oliveira'}]}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr(
        'ai_orchestrator.grounded_answer_experience.compose_public_timeline_lifecycle_bundle',
        lambda: '1) Matricula e ingresso. 2) Inicio das aulas. 3) Reuniao com responsaveis. No calendario publico, as aulas entram nesse fluxo.',
    )

    response = _public_response('Entendido. O Colegio Horizonte e uma escola laica que oferece Ensino Fundamental II e Ensino Medio.')
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Nao, quero so o calendario publico').model_copy(
                update={'user': UserContext(role='guardian', authenticated=True)}
            ),
            response=response.model_copy(
                update={
                    'classification': IntentClassification(
                        domain=QueryDomain.calendar,
                        access_tier=AccessTier.public,
                        confidence=0.82,
                        reason='structured_grounded_answer:calendar_reset_followup',
                    ),
                    'mode': OrchestrationMode.structured_tool,
                    'reason': 'structured_grounded_answer:calendar_reset_followup',
                }
            ),
            settings=_settings(),
            stack_name=stack_name,
        )
    )

    lowered = updated.message_text.casefold()
    assert 'inicio das aulas' in lowered
    assert 'calendario publico' in lowered or 'calendário público' in updated.message_text.casefold()
    assert updated.answer_experience_reason.endswith(':public_direct_answer')


def test_answer_experience_repairs_student_switch_academic_risk_followup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Agora isola so historia.'},
                {'sender_type': 'assistant', 'content': 'Em Historia, Lucas Oliveira está com média parcial de 6,8/10.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        if path == '/v1/students/ana-id/academic-summary':
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Historia', 'score': 7.3, 'max_score': 10},
                        {'subject_name': 'Fisica', 'score': 6.4, 'max_score': 10},
                        {'subject_name': 'Matematica', 'score': 7.4, 'max_score': 10},
                    ],
                }
            }
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Em Historia, Ana Oliveira está com média parcial de 7,3/10.')
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('E da Ana, quais os pontos academicos que mais preocupam?'),
            response=response,
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'ana oliveira' in lowered
    assert 'fisica' in lowered
    assert 'historia' in lowered
    assert updated.answer_experience_reason.endswith(':protected_academic_direct')


def test_answer_experience_repairs_componentes_merecem_mais_atencao_followup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Faca um resumo academico dos meus dois filhos e destaque qual deles esta mais perto do corte de aprovacao.'},
                {'sender_type': 'assistant', 'content': 'Quem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        if path == '/v1/students/ana-id/academic-summary':
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Historia', 'score': 7.3, 'max_score': 10},
                        {'subject_name': 'Fisica', 'score': 6.4, 'max_score': 10},
                        {'subject_name': 'Matematica', 'score': 7.4, 'max_score': 10},
                    ],
                }
            }
        raise AssertionError(f'unexpected_path:{path}')

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Fique apenas com a Ana e diga quais componentes merecem mais atencao agora.'),
            response=_response('A Ana Oliveira precisa de atenção na documentação escolar.'),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'ana oliveira' in lowered
    assert 'fisica' in lowered
    assert 'historia' in lowered
    assert 'documenta' not in lowered
    assert updated.answer_experience_reason.endswith(':protected_academic_direct')


def test_answer_focus_ignores_generic_qual_disciplina_stub_in_family_aggregate_prompt() -> None:
    focus = resolve_answer_focus(
        request_message='Sem me dar tabela, qual dos meus filhos esta academicamente pior hoje e em qual disciplina isso fica mais claro?',
        actor={
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        },
        conversation_context=None,
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.asks_family_aggregate is True
    assert focus.unknown_subject_name is None


def test_answer_focus_prefers_focus_marked_student_over_multiple_mentions() -> None:
    focus = resolve_answer_focus(
        request_message='Sem repetir o Lucas, corta so para a Ana e me diga qual componente dela acende mais alerta agora.',
        actor={
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        },
        conversation_context={
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                            'active_subject': 'Educacao Fisica',
                        }
                    },
                }
            ],
        },
    )

    assert focus.domain == 'academic'
    assert focus.topic == 'grades'
    assert focus.student_name == 'Ana Oliveira'
    assert focus.subject_name is None
    assert focus.needs_disambiguation is False


def test_answer_experience_repairs_focus_marked_alert_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Sem me dar tabela, qual dos meus filhos esta academicamente pior hoje e em qual disciplina isso fica mais claro?'},
                {'sender_type': 'assistant', 'content': 'Panorama academico das contas vinculadas:\n- Lucas Oliveira: Fisica 5,9; Historia 6,8; Matematica 7,7\n- Ana Oliveira: Fisica 6,4; Historia 7,3; Matematica 7,4\nQuem hoje exige maior atencao academica e Lucas Oliveira, principalmente em Fisica.'},
            ],
            'recent_tool_calls': [
                {
                    'tool_name': 'orchestration.trace',
                    'request_payload': {
                        'slot_memory': {
                            'active_task': 'academic:grades',
                            'academic_student_name': 'Lucas Oliveira',
                            'active_subject': 'Educacao Fisica',
                        }
                    },
                }
            ],
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        if path == '/v1/students/ana-id/academic-summary':
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'grades': [
                        {'subject_name': 'Fisica', 'score': 6.4, 'max_score': 10},
                        {'subject_name': 'Geografia', 'score': 7.0, 'max_score': 10},
                        {'subject_name': 'Educacao Fisica', 'score': 7.0, 'max_score': 10},
                    ],
                }
            }
        raise AssertionError(f'unexpected_path:{path}')

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Sem repetir o Lucas, corta so para a Ana e me diga qual componente dela acende mais alerta agora.'),
            response=_response('Você quer consultar Educacao Fisica de qual aluno: Lucas Oliveira ou Ana Oliveira?').model_copy(
                update={'mode': OrchestrationMode.clarify}
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'ana oliveira' in lowered
    assert 'lucas oliveira' not in lowered
    assert 'fisica' in lowered
    assert updated.answer_experience_reason.endswith(':protected_academic_direct')


def test_answer_experience_repairs_admin_finance_combo_regularization_followup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro.'},
                {'sender_type': 'assistant', 'content': 'Hoje ainda existe bloqueio administrativo ou documental neste recorte. Financeiro: Ana Oliveira: 2 em aberto, 0 vencidas.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        if path == '/v1/students/ana-id/administrative-status':
            return {'summary': {'overall_status': 'pending', 'next_step': 'Enviar comprovante de residencia atualizado pelo portal autenticado.'}}
        if path == '/v1/students/ana-id/financial-summary':
            return {'summary': {'student_name': 'Ana Oliveira', 'open_invoice_count': 2, 'overdue_invoice_count': 0, 'invoices': [{'status': 'open', 'amount_due': '1450.00', 'due_date': '2026-03-10'}]}}
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Para regularizar a situação da Ana, o próximo passo é enviar um comprovante de residência atualizado.').model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.authenticated,
                confidence=0.9,
                reason='test',
            ),
            'selected_tools': ['get_student_administrative_status'],
            'reason': 'protected_institution_detail',
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Agora recorta so a Ana e o proximo passo para regularizar.'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'ana oliveira' in lowered
    assert 'documentacao' in lowered or 'cadastro escolar' in lowered or 'status atual' in lowered
    assert 'financeiro' in lowered
    assert updated.answer_experience_reason.endswith(':protected_finance_direct')


def test_answer_experience_repairs_admin_finance_direct_block_followup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro.'},
                {'sender_type': 'assistant', 'content': 'Hoje ainda existe bloqueio administrativo ou documental neste recorte. Financeiro: Ana Oliveira: 2 em aberto, 0 vencidas.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        if path == '/v1/students/ana-id/administrative-status':
            return {'summary': {'overall_status': 'pending', 'next_step': 'Enviar comprovante de residencia atualizado pelo portal autenticado.'}}
        if path == '/v1/students/ana-id/financial-summary':
            return {'summary': {'student_name': 'Ana Oliveira', 'open_invoice_count': 2, 'overdue_invoice_count': 0}}
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Ana Oliveira está com 2 fatura(s) em aberto.').model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.finance,
                access_tier=AccessTier.authenticated,
                confidence=0.9,
                reason='test',
            ),
            'selected_tools': ['get_student_financial_summary'],
            'reason': 'protected_institution_detail',
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Se nada estiver bloqueando, fala isso de forma direta.'),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'bloqueio' in lowered
    assert 'ana oliveira' in lowered
    assert updated.answer_experience_reason.endswith(':protected_finance_direct')


def test_answer_experience_admin_finance_direct_block_followup_keeps_combo_student(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Minha documentacao ou cadastro da Ana esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro.'},
                {'sender_type': 'assistant', 'content': 'Hoje ainda existe bloqueio administrativo ou documental no recorte de Ana Oliveira. Financeiro: Ana Oliveira: 2 em aberto, 0 vencidas.'},
                {'sender_type': 'user', 'content': 'E o Lucas, como esta a frequencia dele?'},
                {'sender_type': 'assistant', 'content': 'Lucas Oliveira tem 1 falta recente em Fisica.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        if path == '/v1/students/ana-id/administrative-status':
            return {'summary': {'overall_status': 'complete', 'next_step': ''}}
        if path == '/v1/students/ana-id/financial-summary':
            return {'summary': {'student_name': 'Ana Oliveira', 'open_invoice_count': 0, 'overdue_invoice_count': 0}}
        if path == '/v1/students/lucas-id/administrative-status':
            return {'summary': {'overall_status': 'pending', 'next_step': 'Nao deveria ser usado.'}}
        if path == '/v1/students/lucas-id/financial-summary':
            return {'summary': {'student_name': 'Lucas Oliveira', 'open_invoice_count': 1, 'overdue_invoice_count': 1}}
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Lucas Oliveira está com 1 fatura(s) em aberto.').model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.finance,
                access_tier=AccessTier.authenticated,
                confidence=0.9,
                reason='test',
            ),
            'selected_tools': ['get_student_financial_summary'],
            'reason': 'protected_institution_detail',
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Se nada estiver bloqueando, fala isso de forma direta.'),
            response=response,
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    lowered = updated.message_text.casefold()
    assert 'ana oliveira' in lowered
    assert 'nao ha bloqueio administrativo ou financeiro' in lowered
    assert 'lucas oliveira' not in lowered


def test_answer_experience_repair_followup_mentions_provas_explicitly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quais as proximas provas do Lucas?'},
                {'sender_type': 'assistant', 'content': 'Próximas avaliações de Lucas Oliveira: História em 14/04/2026.'},
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = _response('A resposta anterior estava falando de próximas avaliações.').model_copy(
        update={
            'mode': OrchestrationMode.clarify,
            'classification': IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.authenticated,
                confidence=0.8,
                reason='test',
            ),
            'reason': 'clarify',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Essa resposta era sobre o que entao?'),
            response=response,
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert 'provas' in updated.message_text.casefold()


def test_answer_experience_preserves_public_integral_study_support_lane(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return None

    async def fake_compose(**kwargs):
        return 'Texto reescrito sem o fechamento operacional.'

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience.compose_grounded_answer_experience_with_provider', fake_compose)

    original = (
        'Fora da sala regular, o material publico mostra que periodo integral e estudo orientado se completam como camadas de apoio ao estudante. '
        'O proximo passo e validar pelo canal oficial se a familia precisa de permanencia ampliada, apoio de estudo ou ambos, '
        'para confirmar rotina, refeicoes, horarios e disponibilidade no contraturno.'
    )
    response = _public_response(original).model_copy(
        update={
            'reason': 'langgraph_public_canonical_lane:public_bundle.integral_study_support',
            'candidate_chosen': 'deterministic',
            'candidate_reason': 'public_canonical_lane:public_bundle.integral_study_support',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request(
                'Como periodo integral e estudo orientado se conectam no apoio ao estudante segundo a base publica?'
            ).model_copy(update={'user': UserContext(role='anonymous', authenticated=False)}),
            response=response,
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert updated.message_text == original
    assert updated.answer_experience_applied is False
    assert updated.answer_experience_reason == 'structured_grounded_answer:preserve_integral_study_support'


def test_answer_experience_builds_family_attendance_aggregate_from_clarify(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'attendance': [
                        {'subject_name': 'Fisica', 'present_count': 8, 'late_count': 1, 'absent_count': 3, 'absent_minutes': 150},
                        {'subject_name': 'Historia', 'present_count': 10, 'late_count': 0, 'absent_count': 1, 'absent_minutes': 50},
                    ],
                }
            }
        if path.endswith('/ana-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'attendance': [
                        {'subject_name': 'Biologia', 'present_count': 11, 'late_count': 0, 'absent_count': 0, 'absent_minutes': 0},
                        {'subject_name': 'Matematica', 'present_count': 9, 'late_count': 1, 'absent_count': 1, 'absent_minutes': 50},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Me de um panorama de faltas e frequencia dos meus filhos, apontando quem exige maior atencao agora.'),
            response=_response('Para qual aluno você quer consultar isso: Lucas Oliveira ou Ana Oliveira?').model_copy(
                update={'mode': OrchestrationMode.clarify}
            ),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    assert 'Panorama de faltas e frequencia das contas vinculadas:' in updated.message_text
    assert 'Lucas Oliveira' in updated.message_text
    assert 'Quem exige maior atencao agora: Lucas Oliveira.' in updated.message_text
    assert updated.mode == OrchestrationMode.structured_tool


def test_answer_experience_builds_family_attendance_aggregate_from_two_children_wording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'attendance': [
                        {'subject_name': 'Fisica', 'present_count': 8, 'late_count': 1, 'absent_count': 3, 'absent_minutes': 150},
                    ],
                }
            }
        if path.endswith('/ana-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'attendance': [
                        {'subject_name': 'Biologia', 'present_count': 11, 'late_count': 0, 'absent_count': 0, 'absent_minutes': 0},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Faca um resumo de frequencia dos meus dois filhos e destaque quem inspira mais atencao por faltas.'),
            response=_response('Para qual aluno você quer consultar isso: Lucas Oliveira ou Ana Oliveira?').model_copy(
                update={'mode': OrchestrationMode.clarify}
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'Panorama de faltas e frequencia das contas vinculadas:' in updated.message_text
    assert 'Quem exige maior atencao agora: Lucas Oliveira.' in updated.message_text
    assert updated.answer_experience_reason.endswith('protected_attendance_direct')


def test_answer_experience_builds_family_attendance_aggregate_from_more_attention_wording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'attendance': [
                        {'subject_name': 'Fisica', 'present_count': 8, 'late_count': 1, 'absent_count': 3, 'absent_minutes': 150},
                    ],
                }
            }
        if path.endswith('/ana-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Ana Oliveira',
                    'attendance': [
                        {'subject_name': 'Biologia', 'present_count': 11, 'late_count': 0, 'absent_count': 0, 'absent_minutes': 0},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Me mostre a frequencia dos meus dois filhos e diga quem exige mais atenção agora.'),
            response=_response('Para qual aluno você quer consultar isso: Lucas Oliveira ou Ana Oliveira?').model_copy(
                update={'mode': OrchestrationMode.clarify}
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'Panorama de faltas e frequencia das contas vinculadas:' in updated.message_text
    assert 'Quem exige maior atencao agora: Lucas Oliveira.' in updated.message_text
    assert updated.answer_experience_reason.endswith('protected_attendance_direct')


def test_answer_experience_rewrites_principal_attendance_alert(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'attendance': [
                        {'subject_name': 'Fisica', 'present_count': 19, 'late_count': 7, 'absent_count': 6, 'absent_minutes': 120},
                        {'subject_name': 'Historia', 'present_count': 20, 'late_count': 0, 'absent_count': 1, 'absent_minutes': 20},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('No recorte atual, Lucas Oliveira tem 19 presença(s), 6 falta(s) e 7 atraso(s) registrados.').model_copy(
        update={
            'reason': 'python_functions_native_structured:academic',
            'candidate_reason': 'python_functions_native_structured:academic',
            'classification': IntentClassification(
                domain=QueryDomain.academic,
                access_tier=AccessTier.authenticated,
                confidence=1.0,
                reason='test',
            ),
            'selected_tools': ['get_student_attendance'],
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Hoje, qual e o principal alerta de frequencia do Lucas olhando as faltas registradas?'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'O principal alerta de frequencia de Lucas Oliveira hoje aparece em Fisica' in updated.message_text
    assert 'maior combinacao de faltas e atrasos' in updated.message_text
    assert updated.answer_experience_reason.endswith('protected_attendance_direct')


def test_answer_experience_rewrites_attendance_alert_with_chamam_atencao_wording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params=None):
        if path == '/v1/students/lucas-id/academic-summary':
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'attendance': [
                        {'subject_name': 'Biologia', 'present_count': 3, 'late_count': 0, 'absent_count': 1},
                        {'subject_name': 'Historia', 'present_count': 8, 'late_count': 0, 'absent_count': 0},
                    ],
                }
            }
        raise AssertionError(f'unexpected_path:{path}')

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('No recorte atual, Lucas Oliveira tem 19 presença(s), 6 falta(s) e 7 atraso(s) registrados.').model_copy(
        update={
            'reason': 'python_functions_native_structured:academic',
            'candidate_reason': 'python_functions_native_structured:academic',
            'classification': IntentClassification(
                domain=QueryDomain.academic,
                access_tier=AccessTier.authenticated,
                confidence=1.0,
                reason='test',
            ),
            'selected_tools': ['get_student_attendance'],
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('No Lucas, quais faltas ou ausencias mais chamam atencao agora e como isso bate na frequencia dele?'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'O principal alerta de frequencia de Lucas Oliveira hoje aparece em Biologia' in updated.message_text
    assert 'Proximo passo:' in updated.message_text
    assert updated.answer_experience_reason.endswith('protected_attendance_direct')


def test_answer_experience_repairs_attendance_next_step_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {
                    'role': 'assistant',
                    'content': (
                        'Panorama de faltas e frequencia das contas vinculadas:\n'
                        '- Lucas Oliveira: 6 falta(s), 7 atraso(s), 19 presenca(s), 120 minuto(s) de ausencia. '
                        'Ponto mais sensivel: Fisica (6 falta(s), 7 atraso(s)).\n'
                        'Quem exige maior atencao agora: Lucas Oliveira. O ponto mais sensivel aparece em Fisica.'
                    ),
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
            ]
        }

    async def fake_api_core_get(*, settings, path, params):
        if path.endswith('/lucas-id/academic-summary'):
            return {
                'summary': {
                    'student_name': 'Lucas Oliveira',
                    'attendance': [
                        {'subject_name': 'Fisica', 'present_count': 19, 'late_count': 7, 'absent_count': 6, 'absent_minutes': 120},
                        {'subject_name': 'Historia', 'present_count': 20, 'late_count': 0, 'absent_count': 1, 'absent_minutes': 20},
                    ],
                }
            }
        return {}

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._api_core_get', fake_api_core_get)

    response = _response('Situacao administrativa do seu cadastro hoje: com pendencias.').model_copy(
        update={
            'classification': IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.authenticated,
                confidence=0.84,
                reason='llamaindex_local_protected:institution',
            ),
            'selected_tools': ['get_student_administrative_status'],
            'reason': 'llamaindex_local_protected:institution',
            'candidate_reason': 'llamaindex_local_protected:institution',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Sem repetir os numeros todos, o que eu deveria acompanhar primeiro?'),
            response=response,
            settings=_settings(),
            stack_name='llamaindex',
        )
    )

    assert 'O proximo passo para Lucas Oliveira e acompanhar primeiro Fisica' in updated.message_text
    assert updated.answer_experience_reason.endswith(':protected_attendance_direct')


def test_answer_experience_repairs_restricted_outings_public_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {
                    'role': 'assistant',
                    'content': (
                        'Nao encontrei uma orientacao restrita especifica sobre excursao ou viagem internacional '
                        'com hospedagem para o ensino medio nos documentos internos disponiveis.'
                    ),
                }
            ]
        }

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = _response('Voce quer consultar isso para qual aluno?').model_copy(
        update={
            'mode': OrchestrationMode.clarify,
            'classification': IntentClassification(
                domain=QueryDomain.institution,
                access_tier=AccessTier.authenticated,
                confidence=0.77,
                reason='clarify_after_restricted_no_match',
            ),
            'selected_tools': ['search_documents'],
            'reason': 'clarify_after_restricted_no_match',
            'candidate_reason': 'clarify_after_restricted_no_match',
        }
    )

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Entao me resuma em dois passos praticos o que existe de publico sobre esse tipo de saida ou protocolo.'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert updated.message_text.startswith('Primeiro, confirme pelo canal oficial')
    assert 'Depois, envie a autorizacao da familia no prazo' in updated.message_text
    assert updated.answer_experience_reason.endswith(':public_direct_answer')


def test_answer_experience_restores_public_academic_policy_lane(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'academic_policy': {
                'passing_policy': {'passing_average': 7.0},
                'attendance_policy': {'minimum_attendance_percent': 75.0},
            },
        }

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = _public_response(
        'Hoje eu nao encontrei Escola entre os alunos vinculados. Você quer consultar Lucas Oliveira ou Ana Oliveira?'
    ).model_copy(
        update={
            'reason': 'python_functions_native_canonical_lane:public_bundle.academic_policy_overview',
            'candidate_reason': 'python_functions_native_canonical_lane:public_bundle.academic_policy_overview',
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Pela politica publica da escola, como se juntam avaliacao, recuperacao, promocao, media e frequencia minima?'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    assert 'fluxo academico' in updated.message_text
    assert 'media 7,0/10 e frequencia minima de 75,0%' in updated.message_text
    assert updated.answer_experience_reason.endswith('public_direct_answer')


def test_answer_experience_restores_public_conduct_policy_lane(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return None

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'conduct_frequency_punctuality': {
                'summary': 'A escola orienta convivencia respeitosa, registro de ocorrencias e encaminhamento pela coordenacao.'
            },
            'governance': {
                'summary': 'Casos formais podem seguir secretaria, coordenacao e direcao.'
            },
        }

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira', 'can_view_academic': True},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira', 'can_view_academic': True},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    response = _public_response(
        'O rascunho atual não contém informações públicas suficientes para responder com segurança.'
    ).model_copy(
        update={
            'reason': 'python_functions_native_canonical_lane:public_bundle.conduct_frequency_punctuality',
            'candidate_reason': 'python_functions_native_canonical_lane:public_bundle.conduct_frequency_punctuality',
        }
    )
    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Nos documentos publicos da escola, qual e o procedimento para casos de bullying e quando um caso pode virar exclusao disciplinar?'),
            response=response,
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'bullying' in lowered
    assert 'exclus' in lowered
    assert 'coordenacao' in lowered
    assert 'canais oficiais' in lowered or 'registro formal' in lowered
    assert 'exclus' in lowered
    assert 'rascunho atual' not in lowered
    assert updated.answer_experience_reason.endswith('public_direct_answer')


def test_answer_experience_restores_public_admissions_opening_date(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_timeline(settings):
        return {
            'entries': [
                {
                    'topic_key': 'admissions_opening_2026',
                    'summary': 'O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025.',
                    'event_date': '2025-10-06',
                }
            ]
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_timeline', fake_timeline)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Quando abre a matricula de 2026?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response('Valores publicos de referencia de mensalidade e matricula.').model_copy(
                update={'reason': 'python_functions_native_contextual_public_answer'}
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'matricula de 2026 abre em 6 de outubro de 2025' in lowered
    assert updated.answer_experience_reason.endswith('public_direct_answer')


def test_answer_experience_restores_public_admissions_opening_for_authenticated_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_timeline(settings):
        return {
            'entries': [
                {
                    'topic_key': 'admissions_opening_2026',
                    'summary': 'O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025.',
                    'event_date': '2025-10-06',
                }
            ]
        }

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_timeline', fake_timeline)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Quando abre a matricula de 2026?'),
            response=_public_response('Valores publicos de referencia de mensalidade e matricula.').model_copy(
                update={
                    'classification': IntentClassification(
                        domain=QueryDomain.institution,
                        access_tier=AccessTier.authenticated,
                        confidence=0.9,
                        reason='python_functions_local_protected:institution',
                    ),
                    'reason': 'python_functions_native_structured:institution',
                    'selected_tools': ['get_administrative_status'],
                }
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'matricula de 2026 abre em 6 de outubro de 2025' in lowered
    assert updated.answer_experience_reason.endswith('public_direct_answer')


def test_answer_experience_restores_public_school_year_start_date(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_timeline(settings):
        return {
            'entries': [
                {
                    'topic_key': 'school_year_start_2026',
                    'summary': 'As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.',
                    'event_date': '2026-02-02',
                }
            ]
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_timeline', fake_timeline)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('E quando comecam as aulas?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response('Valores publicos de referencia de mensalidade e matricula.').model_copy(
                update={'reason': 'python_functions_native_contextual_public_answer'}
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'as aulas comecam em 2 de fevereiro de 2026' in lowered
    assert updated.answer_experience_reason.endswith('public_direct_answer')


def test_answer_experience_restores_public_capabilities_menu(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_capabilities(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'public_topics': ['matricula, secretaria, financeiro e visitas'],
            'protected_topics': ['notas, faltas e pagamentos'],
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_assistant_capabilities', fake_capabilities)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Quais opcoes de assuntos eu tenho aqui?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response('Preciso que voce especifique melhor o tema.').model_copy(
                update={'reason': 'python_functions_native_structured:unknown'}
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'matricula' in lowered
    assert 'secretaria' in lowered
    assert 'financeiro' in lowered
    assert updated.answer_experience_reason.endswith('public_direct_answer')


def test_answer_experience_restores_public_capabilities_menu_for_authenticated_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_context(*, settings, request):
        return {'recent_messages': []}

    async def fake_profile(settings):
        return {'school_name': 'Colegio Horizonte'}

    async def fake_capabilities(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'public_topics': ['matricula, secretaria, financeiro e visitas'],
            'protected_topics': ['notas, faltas e pagamentos'],
        }

    async def fake_actor(*, settings, request):
        return {
            'linked_students': [
                {'student_id': 'lucas-id', 'full_name': 'Lucas Oliveira'},
                {'student_id': 'ana-id', 'full_name': 'Ana Oliveira'},
            ]
        }

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_assistant_capabilities', fake_capabilities)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Quais opcoes de assuntos eu tenho aqui?'),
            response=_public_response('Preciso que voce especifique melhor o tema.').model_copy(
                update={
                    'classification': IntentClassification(
                        domain=QueryDomain.institution,
                        access_tier=AccessTier.authenticated,
                        confidence=0.9,
                        reason='python_functions_local_protected:institution',
                    ),
                    'reason': 'python_functions_native_structured:institution',
                    'selected_tools': ['get_administrative_status'],
                }
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'matricula' in lowered
    assert 'secretaria' in lowered
    assert 'financeiro' in lowered
    assert updated.answer_experience_reason.endswith('public_direct_answer')


def test_answer_experience_restores_visit_reschedule_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quero agendar uma visita na quinta a tarde.'},
                {'sender_type': 'assistant', 'content': 'Posso seguir com a visita e depois te devolver o protocolo.'},
            ]
        }

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'service_catalog': [
                {
                    'service_key': 'visita_institucional',
                    'request_channel': 'bot, admissions ou whatsapp comercial',
                    'typical_eta': 'confirmacao em ate 1 dia util',
                }
            ],
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('Se eu precisar remarcar, como faco?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response('Para remarcar, por favor, acesse o portal autenticado da escola.').model_copy(
                update={'reason': 'python_functions_native_structured:unknown'}
            ),
            settings=_settings(),
            stack_name='python_functions',
        )
    )

    lowered = updated.message_text.lower()
    assert 'remarcar a visita' in lowered
    assert 'protocolo' in lowered
    assert updated.answer_experience_reason.endswith('public_direct_answer')


def test_answer_experience_restores_visit_resume_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, settings, request):
        return {
            'recent_messages': [
                {'sender_type': 'user', 'content': 'Quero agendar uma visita na quinta a tarde.'},
                {'sender_type': 'assistant', 'content': 'Posso seguir com a visita e depois te devolver o protocolo.'},
                {'sender_type': 'user', 'content': 'Certo, e se eu cancelar mesmo?'},
                {'sender_type': 'assistant', 'content': 'Se cancelar, eu encerro esse pedido e voce pode voltar quando quiser.'},
            ]
        }

    async def fake_profile(settings):
        return {
            'school_name': 'Colegio Horizonte',
            'service_catalog': [
                {
                    'service_key': 'visita_institucional',
                    'request_channel': 'bot, admissions ou whatsapp comercial',
                    'typical_eta': 'confirmacao em ate 1 dia util',
                }
            ],
        }

    async def fake_actor(*, settings, request):
        return None

    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_conversation_context', fake_context)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_public_school_profile', fake_profile)
    monkeypatch.setattr('ai_orchestrator.grounded_answer_experience._fetch_actor_context', fake_actor)

    updated = asyncio.run(
        apply_grounded_answer_experience(
            request=_request('E se eu quiser retomar depois, por onde volto?').model_copy(
                update={'user': UserContext(role='anonymous', authenticated=False)}
            ),
            response=_public_response('Para retomar depois, voce pode voltar a Biblioteca Aurora no horario de atendimento.').model_copy(
                update={'reason': 'langgraph_structured:institution'}
            ),
            settings=_settings(),
            stack_name='langgraph',
        )
    )

    lowered = updated.message_text.lower()
    assert 'retomar a visita' in lowered
    assert 'novo pedido' in lowered or 'canal institucional' in lowered
    assert updated.answer_experience_reason.endswith('public_direct_answer')
