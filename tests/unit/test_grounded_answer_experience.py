from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from ai_orchestrator.grounded_answer_experience import (
    _ANSWER_FOCUS_CACHE,
    apply_grounded_answer_experience,
)
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
    assert updated.mode == OrchestrationMode.structured_tool


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

    async def fake_supplemental(*, settings, request, focus, school_profile=None, actor=None):
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

    async def fake_supplemental(*, settings, request, focus, school_profile=None, actor=None):
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
    assert 'A resposta anterior estava falando de próximas avaliações.' in updated.message_text


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
