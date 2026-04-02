from __future__ import annotations

from ai_orchestrator.public_doc_knowledge import (
    compose_public_canonical_lane_answer,
    match_public_canonical_lane,
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


def test_academic_policy_overview_lane_matches() -> None:
    lane = match_public_canonical_lane('Qual a politica de avaliacao e recuperacao da escola?')
    assert lane == 'public_bundle.academic_policy_overview'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    assert 'media 7,0' in answer.lower()
