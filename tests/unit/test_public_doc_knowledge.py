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


def test_academic_policy_overview_lane_matches() -> None:
    lane = match_public_canonical_lane('Qual a politica de avaliacao e recuperacao da escola?')
    assert lane == 'public_bundle.academic_policy_overview'
    answer = compose_public_canonical_lane_answer(lane, profile=_sample_profile())
    assert answer is not None
    assert 'media 7,0' in answer.lower()
