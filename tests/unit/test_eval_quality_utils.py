from __future__ import annotations

from tools.evals.eval_quality_utils import _contains_forbidden_keywords, _detect_error_types


def test_forbidden_keywords_ignore_punctuation_only_false_positive() -> None:
    answer = 'O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina.'
    assert not _contains_forbidden_keywords(answer, ['@'])


def test_forbidden_keywords_still_detect_raw_at_symbol() -> None:
    answer = 'Se precisar, escreva para contato@colegio.example.'
    assert _contains_forbidden_keywords(answer, ['@'])


def test_detect_error_types_flags_public_explanatory_misroute() -> None:
    errors = _detect_error_types(
        answer_text='Se quiser, eu posso abrir um protocolo com a direcao para tratar esse caso individualmente.',
        expected_keywords=['integral', 'estudo orientado'],
        forbidden_keywords=[],
        prompt='Se eu quiser entender o suporte ao aluno alem da sala regular, como periodo integral e estudo orientado se completam no material publico da escola?',
        previous_answer='',
        status=200,
        turn_index=1,
        note='',
    )
    assert 'public_explanatory_misroute' in errors


def test_detect_error_types_flags_generic_profile_leak() -> None:
    errors = _detect_error_types(
        answer_text='O Colegio Horizonte e uma instituicao laica com proposta pedagogica forte, foco em projeto de vida e diferenciais de tecnologia para o ensino fundamental II e o ensino medio.',
        expected_keywords=['direcao', 'protocolo'],
        forbidden_keywords=[],
        prompt='Quando um assunto foge do cotidiano, como a familia sai da coordenacao e chega a direcao com protocolo formal segundo a base publica?',
        previous_answer='',
        status=200,
        turn_index=1,
        note='',
    )
    assert 'generic_profile_leak' in errors


def test_detect_error_types_flags_ungrounded_general_knowledge() -> None:
    errors = _detect_error_types(
        answer_text='Em geral, escolas costumam exigir uniforme e alguma orientacao de transporte conforme a rotina.',
        expected_keywords=['transporte', 'uniforme'],
        forbidden_keywords=[],
        prompt='Para visualizar a rotina fora da sala, como transporte, uniforme e alimentacao aparecem combinados nas orientacoes publicas?',
        previous_answer='',
        status=200,
        turn_index=1,
        note='',
    )
    assert 'ungrounded_general_knowledge' in errors
