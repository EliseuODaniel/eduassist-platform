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


def test_detect_error_types_flags_multi_intent_partial_collapse() -> None:
    errors = _detect_error_types(
        answer_text='A simulacao para 3 filhos no ensino medio fica em R$ 4.350,00 por mes.',
        expected_keywords=['secretaria', 'mensalidade'],
        forbidden_keywords=[],
        expected_sections=['contacts', 'pricing'],
        rubric_tags=['multi_intent'],
        prompt='Quero os contatos da secretaria e do financeiro junto com mensalidade e bolsa para 3 filhos no ensino medio.',
        previous_answer='',
        status=200,
        turn_index=1,
        note='',
    )
    assert 'multi_intent_partial_collapse' in errors


def test_detect_error_types_flags_partial_scope_loss() -> None:
    errors = _detect_error_types(
        answer_text='Os componentes com menores medias agora sao Fisica e Geografia.',
        expected_keywords=['Ana Oliveira'],
        forbidden_keywords=[],
        expected_sections=['academic'],
        rubric_tags=[],
        prompt='Quero isolar so a Ana Oliveira e os pontos academicos que mais preocupam.',
        previous_answer='',
        status=200,
        turn_index=1,
        note='',
    )
    assert 'partial_scope_loss' in errors


def test_detect_error_types_flags_attendance_metric_misroute() -> None:
    errors = _detect_error_types(
        answer_text='Panorama academico das contas vinculadas: Lucas Oliveira em Fisica 5,9 e Ana Oliveira em Fisica 6,4.',
        expected_keywords=['frequencia', 'faltas'],
        forbidden_keywords=[],
        expected_sections=['academic'],
        rubric_tags=[],
        prompt='Me de um panorama de faltas e frequencia dos meus filhos, apontando quem exige maior atencao agora.',
        previous_answer='',
        status=200,
        turn_index=1,
        note='',
    )
    assert 'attendance_metric_misroute' in errors


def test_detect_error_types_flags_comparative_reasoning_mismatch() -> None:
    errors = _detect_error_types(
        answer_text=(
            'Panorama academico das contas vinculadas:\n'
            '- Lucas Oliveira: Biologia 7,9; Educacao Fisica 6,5; Filosofia 7,1; Fisica 5,9\n'
            '- Ana Oliveira: Biologia 8,0; Educacao Fisica 7,0; Filosofia 7,5; Fisica 6,4\n'
            'Quem hoje aparece mais perto da media minima e Ana Oliveira, principalmente em Educacao Fisica.'
        ),
        expected_keywords=['Lucas Oliveira', 'Ana Oliveira'],
        forbidden_keywords=[],
        expected_sections=['academic'],
        rubric_tags=[],
        prompt='Me de um panorama academico dos meus filhos e diga qual deles aparece mais perto da media minima agora. Responda de forma direta.',
        previous_answer='',
        status=200,
        turn_index=1,
        note='',
    )
    assert 'comparative_reasoning_mismatch' in errors
