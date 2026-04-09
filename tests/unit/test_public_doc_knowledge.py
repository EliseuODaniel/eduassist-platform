from __future__ import annotations

from ai_orchestrator.public_doc_knowledge import (
    compose_public_canonical_lane_answer,
    compose_public_outings_authorizations,
    match_public_canonical_lane,
)
from ai_orchestrator.llamaindex_public_knowledge import (
    compose_public_academic_policy_overview as compose_llamaindex_public_academic_policy_overview,
    compose_public_governance_protocol as compose_llamaindex_public_governance_protocol,
    compose_public_integral_study_support as compose_llamaindex_public_integral_study_support,
    match_public_canonical_lane as match_llamaindex_public_canonical_lane,
    compose_public_teacher_directory_boundary as compose_llamaindex_public_teacher_directory_boundary,
    compose_public_year_three_phases as compose_llamaindex_public_year_three_phases,
)
from ai_orchestrator.python_functions_public_knowledge import (
    compose_public_academic_policy_overview as compose_python_functions_public_academic_policy_overview,
    compose_public_conduct_policy_contextual_answer,
    compose_public_governance_protocol as compose_python_functions_public_governance_protocol,
    compose_public_integral_study_support as compose_python_functions_public_integral_study_support,
    match_public_canonical_lane as match_python_functions_public_canonical_lane,
    compose_public_teacher_directory_boundary as compose_python_functions_public_teacher_directory_boundary,
    compose_public_year_three_phases as compose_python_functions_public_year_three_phases,
)
from ai_orchestrator_specialist.public_doc_knowledge import (
    match_public_canonical_lane as match_specialist_public_canonical_lane,
)


def _sample_profile() -> dict[str, object]:
    return {
        'school_name': 'Colegio Horizonte',
        'academic_policy': {
            'passing_policy': {'passing_average': '7.0'},
            'attendance_policy': {
                'minimum_attendance_percent': '75.0',
                'chronic_absence_guidance': 'A escola aciona acompanhamento quando faltas recorrentes comprometem a rotina.',
            },
        },
        'public_timeline': [
            {
                'topic_key': 'family_meeting',
                'summary': 'Reuniao de familias no inicio do ano.',
                'notes': 'Orienta portal, rotina e credenciais.',
            },
            {
                'topic_key': 'admissions_opening',
                'summary': 'Matriculas abrem em janeiro.',
                'notes': 'Documentos sao enviados pelo portal ou secretaria.',
            },
            {
                'topic_key': 'school_year_closing',
                'summary': 'Fechamento do ano ocorre em dezembro.',
                'notes': 'Consolida calendario, recuperacao e encerramento.',
            },
        ],
    }


def test_teacher_directory_boundary_lane_matches() -> None:
    lane = match_public_canonical_lane('Quero o nome e o telefone do professor de matematica.')
    assert lane == 'public_bundle.teacher_directory_boundary'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    assert 'nao divulga nome' in answer.lower()
    assert 'coordenacao' in answer.lower()
    assert 'proximo passo' in answer.lower()


def test_calendar_week_lane_matches() -> None:
    lane = match_public_canonical_lane('Quais eventos desta semana importam para as familias?')
    assert lane == 'public_bundle.calendar_week'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    assert 'semana' in answer.lower() or 'familias' in answer.lower()


def test_calendar_week_lane_matches_generic_family_prompt() -> None:
    lane = match_public_canonical_lane(
        'Dentro do calendario publico, quais eventos parecem mais importantes para familias e responsaveis?'
    )
    assert lane == 'public_bundle.calendar_week'


def test_timeline_lifecycle_lane_wins_over_calendar_week_for_marcos_entre_prompt() -> None:
    lane = match_public_canonical_lane(
        'Quais sao os marcos entre matricula, inicio do ano letivo e reuniao de responsaveis no calendario publico de 2026?'
    )
    assert lane == 'public_bundle.timeline_lifecycle'


def test_calendar_week_lane_matches_marcos_prompt() -> None:
    lane = match_public_canonical_lane(
        'Quais marcos do calendario publico hoje falam mais diretamente com familias e responsaveis?'
    )
    assert lane == 'public_bundle.calendar_week'


def test_first_month_risks_lane_matches_arranque_prompt() -> None:
    lane = match_public_canonical_lane(
        'No arranque do ano letivo, que descuidos mais costumam explodir entre credenciais, papelada e rotina da casa?'
    )
    assert lane == 'public_bundle.first_month_risks'


def test_transversal_year_lane_matches_agenda_avaliativa_prompt() -> None:
    lane = match_public_canonical_lane(
        'Como os materiais publicos mostram a relacao entre agenda avaliativa, comunicacao com responsaveis, estudo orientado e meios digitais durante o ano?'
    )
    assert lane == 'public_bundle.transversal_year'


def test_family_new_bundle_matches_house_entering_now_prompt() -> None:
    lane = match_public_canonical_lane(
        'Para uma casa que esta entrando no Colegio Horizonte agora, como matricula, inicio das aulas e avaliacoes se relacionam no comeco do ano?'
    )
    assert lane == 'public_bundle.family_new_calendar_assessment_enrollment'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    lowered = answer.lower()
    assert 'matricula' in lowered
    assert 'calendario' in lowered
    assert 'avaliacoes' in lowered


def test_year_three_phases_matches_distribution_prompt() -> None:
    lane = match_public_canonical_lane(
        'Olhando so a base publica, como o ano se distribui entre admissao, rotina academica e fechamento?'
    )
    assert lane == 'public_bundle.year_three_phases'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    lowered = answer.lower()
    assert 'admiss' in lowered
    assert 'rotina academica' in lowered
    assert 'fechamento' in lowered
    assert 'primeiro' in lowered


def test_year_three_phases_matches_se_eu_dividir_o_ano_prompt() -> None:
    lane = match_public_canonical_lane(
        'Se eu dividir o ano em admissao, rotina academica e fechamento, como isso aparece na linha do tempo publica?'
    )
    assert lane == 'public_bundle.year_three_phases'


def test_bolsas_and_processes_lane_beats_generic_process_compare() -> None:
    lane = match_public_canonical_lane(
        'Como a escola conecta edital de bolsas com rematricula, transferencia e cancelamento?'
    )
    assert lane == 'public_bundle.bolsas_and_processes'


def test_academic_policy_overview_lane_matches() -> None:
    lane = match_public_canonical_lane('Qual a politica de avaliacao e recuperacao da escola?')
    assert lane == 'public_bundle.academic_policy_overview'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    assert 'media 7,0' in answer.lower()


def test_academic_policy_overview_lane_matches_public_docs_conduct_frequency_and_recovery_prompt() -> None:
    lane = match_public_canonical_lane(
        'Nos documentos publicos, como convivencia, frequencia e recuperacao se conectam na pratica?'
    )
    assert lane == 'public_bundle.academic_policy_overview'


def test_python_functions_conduct_lane_matches_bullying_and_exclusion_prompt() -> None:
    lane = match_python_functions_public_canonical_lane(
        'Qual o procedimento da escola com bullying? E permitido? O que gera exclusao de aluno da escola?'
    )
    assert lane == 'public_bundle.conduct_frequency_punctuality'


def test_python_functions_conduct_lane_matches_behavior_prompt() -> None:
    lane = match_python_functions_public_canonical_lane(
        'E sobre bom comportamento? O que define e o que e mal comportamento?'
    )
    assert lane == 'public_bundle.conduct_frequency_punctuality'


def test_shared_and_llamaindex_conduct_lane_match_behavior_prompt() -> None:
    prompt = 'E sobre bom comportamento? O que define e o que e mal comportamento?'
    assert match_public_canonical_lane(prompt) == 'public_bundle.conduct_frequency_punctuality'
    assert match_llamaindex_public_canonical_lane(prompt) == 'public_bundle.conduct_frequency_punctuality'


def test_python_functions_contextual_conduct_answer_handles_expulsion_prompt() -> None:
    answer = compose_public_conduct_policy_contextual_answer(
        'O que gera expulsao de um aluno?',
        profile=_sample_profile(),
    )
    assert answer is not None
    lowered = answer.lower()
    assert 'na base publica atual' in lowered
    assert 'nao publica uma tabela fechada' in lowered
    assert 'coordenacao' in lowered
    assert 'direcao@' not in lowered


def test_shared_and_specialist_conduct_lane_match_exclusion_prompt() -> None:
    prompt = 'Que tipo de comportamento pode levar ao desligamento de um aluno?'
    assert match_public_canonical_lane(prompt) == 'public_bundle.conduct_frequency_punctuality'
    assert match_specialist_public_canonical_lane(prompt) == 'public_bundle.conduct_frequency_punctuality'


def test_shared_and_specialist_conduct_lane_match_safety_prompt() -> None:
    prompt = 'Se um aluno levar explosivo ou algo perigoso, qual e o procedimento institucional?'
    assert match_public_canonical_lane(prompt) == 'public_bundle.conduct_frequency_punctuality'
    assert match_specialist_public_canonical_lane(prompt) == 'public_bundle.conduct_frequency_punctuality'


def test_python_functions_contextual_conduct_answer_handles_severe_incident_prompt() -> None:
    answer = compose_public_conduct_policy_contextual_answer(
        'O que acontece se um aluno tacar bomba na escola?',
        profile=_sample_profile(),
    )
    assert answer is not None
    lowered = answer.lower()
    assert 'nao sao tratadas como comportamento permitido' in lowered
    assert 'registro formal' in lowered or 'escalonamento para a direcao' in lowered
    assert 'direcao@' not in lowered


def test_python_functions_contextual_conduct_answer_handles_behavior_prompt_concisely() -> None:
    answer = compose_public_conduct_policy_contextual_answer(
        'Pelo material publico, como a escola define bom comportamento e o que ela trata como mau comportamento?',
        profile=_sample_profile(),
    )
    assert answer is not None
    lowered = answer.lower()
    assert 'bom comportamento' in lowered
    assert 'bullying' in lowered
    assert 'coordenacao' in lowered
    assert 'direcao@' not in lowered


def test_python_functions_contextual_conduct_answer_keeps_frequency_and_punctuality_bundle() -> None:
    answer = compose_public_conduct_policy_contextual_answer(
        'Pelo material publico, como ficam juntas regras de convivencia, frequencia e pontualidade?',
        profile=_sample_profile(),
    )
    assert answer is not None
    lowered = answer.lower()
    assert 'frequ' in lowered
    assert 'pontual' in lowered
    assert 'conviv' in lowered


def test_inclusion_accessibility_lane_matches() -> None:
    lane = match_public_canonical_lane(
        'Quais evidencias publicas mostram que a escola tenta acolher inclusao, acessibilidade e protecao do estudante como um mesmo compromisso institucional?'
    )
    assert lane == 'public_bundle.inclusion_accessibility'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    lowered = answer.lower()
    assert 'inclus' in lowered
    assert 'acessib' in lowered


def test_integral_study_support_lane_matches() -> None:
    lane = match_public_canonical_lane(
        'Se eu quiser entender o suporte ao aluno alem da sala regular, como periodo integral e estudo orientado se completam no material publico da escola?'
    )
    assert lane == 'public_bundle.integral_study_support'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    lowered = answer.lower()
    assert 'periodo integral' in lowered
    assert 'estudo orientado' in lowered
    assert 'proximo passo' in lowered
    assert 'canal oficial' in lowered


def test_integral_study_support_lane_matches_extended_day_ecosystem_prompt() -> None:
    lane = match_public_canonical_lane(
        'Sem repetir slogans, que arquitetura de rotina escolar aparece quando se combinam turno estendido, oficinas, refeicao, estudo acompanhado e permanencia no contraturno?'
    )
    assert lane == 'public_bundle.integral_study_support'


def test_governance_protocol_lane_matches() -> None:
    lane = match_public_canonical_lane(
        'Quando um assunto foge do cotidiano, como a familia sai da coordenacao e chega a direcao com protocolo formal segundo a base publica?'
    )
    assert lane == 'public_bundle.governance_protocol'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    lowered = answer.lower()
    assert 'direcao' in lowered
    assert 'protocolo' in lowered


def test_governance_protocol_lane_matches_governance_channels_prompt() -> None:
    lane = match_public_canonical_lane(
        'Se uma familia precisa entender por onde um tema caminha dentro da escola, que trilha institucional os documentos publicos sugerem entre secretaria, coordenacao, direcao e canais oficiais?'
    )
    assert lane == 'public_bundle.governance_protocol'


def test_governance_protocol_lane_matches_formal_demands_prompt() -> None:
    lane = match_public_canonical_lane(
        'Na governanca publica da escola, como demandas formais chegam a direcao e viram protocolo?'
    )
    assert lane == 'public_bundle.governance_protocol'


def test_specialist_governance_protocol_lane_matches_formal_demands_prompt() -> None:
    lane = match_specialist_public_canonical_lane(
        'Na governanca publica da escola, como demandas formais chegam a direcao e viram protocolo?'
    )
    assert lane == 'public_bundle.governance_protocol'


def test_governance_protocol_answer_mentions_secretaria_coordenacao_and_direcao() -> None:
    answer = compose_public_canonical_lane_answer('public_bundle.governance_protocol', profile=_sample_profile())
    assert answer is not None
    lowered = answer.lower()
    assert 'secretaria' in lowered
    assert 'coordenacao' in lowered
    assert 'direcao' in lowered
    assert 'protocolo formal' in lowered


def test_support_safety_balance_maps_to_inclusion_accessibility_lane() -> None:
    lane = match_public_canonical_lane(
        'Quero entender como a escola equilibra apoio a necessidades especificas, mediacao de rotina e seguranca institucional sem sair do material publico.'
    )
    assert lane == 'public_bundle.inclusion_accessibility'


def test_external_activity_risk_management_maps_to_outings_lane() -> None:
    lane = match_public_canonical_lane(
        'Numa atividade externa, como a escola costura anuencia da familia, impedimentos de saude e retorno seguro segundo a base publica?'
    )
    assert lane == 'public_bundle.outings_authorizations'


def test_public_outings_answer_explicitly_mentions_public_protocol() -> None:
    answer = compose_public_outings_authorizations()
    assert answer is not None
    lowered = answer.casefold()
    assert 'publico' in lowered
    assert 'protocolo' in lowered


def test_operational_experience_bundle_maps_to_transport_uniform_lane() -> None:
    lane = match_public_canonical_lane(
        'Quero uma leitura integrada de deslocamento, refeicao, identificacao e uniforme na experiencia operacional do aluno.'
    )
    assert lane == 'public_bundle.transport_uniform_bundle'


def test_operational_experience_bundle_maps_to_transport_uniform_lane_without_explicit_uniforme() -> None:
    lane = match_public_canonical_lane(
        'No cotidiano fora da aula, que experiencia operacional do aluno aparece quando a base publica fala de deslocamento, refeicao, identificacao e uso diario de itens institucionais?'
    )
    assert lane == 'public_bundle.transport_uniform_bundle'


def test_family_time_architecture_maps_to_family_new_bundle() -> None:
    lane = match_public_canonical_lane(
        'Se eu montar o ano do ponto de vista da familia, como entrada, encontros com responsaveis, devolutivas e recomposicao academica se encadeiam?'
    )
    assert lane == 'public_bundle.family_new_calendar_assessment_enrollment'


def test_visibility_boundary_answer_mentions_portal_and_login() -> None:
    answer = compose_public_canonical_lane_answer('public_bundle.visibility_boundary', profile=_sample_profile())
    assert answer is not None
    lowered = answer.lower()
    assert 'portal' in lowered
    assert 'login' in lowered


def test_health_emergency_bundle_mentions_second_call_or_reorganizacao() -> None:
    answer = compose_public_canonical_lane_answer('public_bundle.health_emergency_bundle', profile=_sample_profile())
    assert answer is not None
    lowered = answer.lower()
    assert 'segunda chamada' in lowered or 'reorganiz' in lowered


def test_timeline_lifecycle_answer_mentions_operational_sequence() -> None:
    answer = compose_public_canonical_lane_answer('public_bundle.timeline_lifecycle', profile=_sample_profile())
    assert answer is not None
    lowered = answer.lower()
    assert 'primeiro' in lowered
    assert 'inicio das aulas' in lowered
    assert 'responsaveis' in lowered


def test_stack_specific_public_answers_reuse_canonical_academic_policy_bundle() -> None:
    profile = _sample_profile()
    canonical = compose_public_canonical_lane_answer('public_bundle.academic_policy_overview', profile=profile)
    assert canonical is not None
    assert compose_python_functions_public_academic_policy_overview(profile) == canonical
    assert compose_llamaindex_public_academic_policy_overview(profile) == canonical


def test_stack_specific_public_answers_reuse_canonical_governance_bundle() -> None:
    profile = _sample_profile()
    canonical = compose_public_canonical_lane_answer('public_bundle.governance_protocol', profile=profile)
    assert canonical is not None
    assert compose_python_functions_public_governance_protocol(profile) == canonical
    assert compose_llamaindex_public_governance_protocol(profile) == canonical


def test_stack_specific_public_answers_reuse_canonical_year_three_bundle() -> None:
    profile = _sample_profile()
    canonical = compose_public_canonical_lane_answer('public_bundle.year_three_phases', profile=profile)
    assert canonical is not None
    assert compose_python_functions_public_year_three_phases(profile) == canonical
    assert compose_llamaindex_public_year_three_phases(profile) == canonical


def test_stack_specific_public_answers_reuse_canonical_integral_support_bundle() -> None:
    canonical = compose_public_canonical_lane_answer('public_bundle.integral_study_support', profile=_sample_profile())
    assert canonical is not None
    assert compose_python_functions_public_integral_study_support() == canonical
    assert compose_llamaindex_public_integral_study_support() == canonical


def test_stack_specific_public_answers_reuse_canonical_teacher_boundary_bundle() -> None:
    profile = _sample_profile()
    canonical = compose_public_canonical_lane_answer('public_bundle.teacher_directory_boundary', profile=profile)
    assert canonical is not None
    assert compose_python_functions_public_teacher_directory_boundary(profile) == canonical
    assert compose_llamaindex_public_teacher_directory_boundary(profile) == canonical
