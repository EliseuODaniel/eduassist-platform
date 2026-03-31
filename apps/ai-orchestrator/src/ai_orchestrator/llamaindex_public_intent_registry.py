from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LlamaIndexPublicIntentRule:
    intent_id: str
    priority: int
    conversation_act: str
    answer_mode: str
    any_of: tuple[str, ...] = ()
    all_of: tuple[str, ...] = ()
    none_of: tuple[str, ...] = ()
    required_tools: tuple[str, ...] = ()
    secondary_acts: tuple[str, ...] = ()
    requested_attribute: str | None = None
    requested_channel: str | None = None
    focus_hint: str | None = None
    unpublished_key: str | None = None
    use_conversation_context: bool = True


LLAMAINDEX_PUBLIC_INTENT_RULES: tuple[LlamaIndexPublicIntentRule, ...] = (
    LlamaIndexPublicIntentRule(
        intent_id='documentary_proposal',
        priority=100,
        conversation_act='highlight',
        answer_mode='documentary',
        any_of=(
            'com base nos documentos',
            'cite as fontes',
            'cite os documentos',
            'mostre as fontes',
            'proposta pedagogica',
            'proposta pedagógica',
        ),
        focus_hint='proposta pedagogica, diferenciais, curriculo, apoio pedagogico e evidencias documentais publicas',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='value_proposition',
        priority=95,
        conversation_act='highlight',
        answer_mode='profile',
        any_of=(
            'por que deveria',
            'porque deveria',
            'por que escolher',
            'porque escolher',
            'vale a pena',
            'diferenciais',
            'motivos para escolher',
        ),
        all_of=('colegio',),
        focus_hint='diferenciais do colegio, proposta pedagogica, infraestrutura, acompanhamento pedagogico, biblioteca, esportes e vida escolar',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='value_proposition_school',
        priority=94,
        conversation_act='highlight',
        answer_mode='profile',
        any_of=(
            'meus filhos nessa escola',
            'meus filhos nesse colegio',
            'meus filhos nesse colégio',
        ),
        focus_hint='por que escolher o colegio, proposta pedagogica, estrutura, seguranca, biblioteca, esportes e apoio academico',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='scholarship_policy',
        priority=92,
        conversation_act='pricing',
        answer_mode='profile',
        any_of=('bolsa', 'desconto', '50%', '50 por cento', 'meia bolsa'),
        focus_hint='bolsas, descontos, percentuais, criterios, elegibilidade, edital e documentos exigidos',
        requested_attribute='scholarship_policy',
        requested_channel='admissions',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='minimum_age',
        priority=91,
        conversation_act='segments',
        answer_mode='unpublished',
        any_of=('idade minima', 'idade mínima', 'idade para estudar', 'idade para matricular'),
        unpublished_key='minimum_age',
        requested_attribute='minimum_age',
        requested_channel='admissions',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='classroom_count',
        priority=90,
        conversation_act='features',
        answer_mode='unpublished',
        any_of=('quantas salas', 'quantidade de salas', 'numero de salas', 'número de salas'),
        unpublished_key='classroom_count',
        requested_attribute='classroom_count',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='student_count',
        priority=89,
        conversation_act='kpi',
        answer_mode='unpublished',
        any_of=('quantos alunos', 'quantidade de alunos', 'numero de alunos', 'número de alunos'),
        unpublished_key='total_students',
        requested_attribute='student_count',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='library_book_count',
        priority=88,
        conversation_act='features',
        answer_mode='unpublished',
        any_of=('quantos livros', 'quantidade de livros', 'numero de livros', 'número de livros'),
        all_of=('biblioteca',),
        unpublished_key='library_book_count',
        requested_attribute='library_collection_size',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='cafeteria_menu',
        priority=87,
        conversation_act='features',
        answer_mode='unpublished',
        any_of=('cardapio', 'cardápio'),
        all_of=('cantina',),
        unpublished_key='cafeteria_menu',
        requested_attribute='cafeteria_menu',
        requested_channel='secretaria',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='leadership_name',
        priority=86,
        conversation_act='leadership',
        answer_mode='profile',
        any_of=('diretor', 'diretora', 'direcao', 'direção', 'lideranca', 'liderança'),
        requested_attribute='leadership',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='shift_offers',
        priority=85,
        conversation_act='schedule',
        answer_mode='profile',
        any_of=('turno', 'turnos', 'matutino', 'vespertino', 'noturno', 'turmas'),
        none_of=('intervalo', 'recreio'),
        focus_hint='turnos, segmentos, horarios de aula e oferta por periodo',
        requested_attribute='shift_offers',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='interval_schedule',
        priority=84,
        conversation_act='schedule',
        answer_mode='profile',
        any_of=('intervalo', 'intervalos', 'recreio'),
        focus_hint='horarios de intervalo e recreio por segmento',
        requested_attribute='interval_schedule',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='institutional_facilities',
        priority=83,
        conversation_act='features',
        answer_mode='profile',
        any_of=(
            'biblioteca',
            'cantina',
            'laboratorio',
            'laboratório',
            'quadra',
            'sala de professores',
            'piscina',
            'kart',
            'tenis',
            'tênis',
        ),
        focus_hint='infraestrutura, espacos e atividades oficialmente mencionados',
        requested_attribute='feature_inventory',
    ),
    LlamaIndexPublicIntentRule(
        intent_id='institutional_schedule',
        priority=82,
        conversation_act='operating_hours',
        answer_mode='profile',
        any_of=('horario', 'horário', 'atende', 'funciona'),
        focus_hint='horarios publicos de atendimento, biblioteca e canais oficiais',
        requested_attribute='operating_hours',
    ),
)
