#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "tests/evals/datasets/retrieval_20q_probe_cases.generated.json"


QUESTION_SPECS: list[dict[str, Any]] = [
    {
        "category": "public_policy_bridge",
        "slice": "public",
        "expected_keywords": ["atestado", "segunda chamada"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_policy_bridge",
        "telegram_chat_id": 777201,
        "note": "public section-aware policy bridge",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Se um estudante faltar a uma avaliacao por motivo de saude, como os documentos publicos ligam atestado, segunda chamada e recuperacao?",
            "Quando a ausencia por saude coincide com prova, como a escola conecta comprovacao, segunda chamada e recuperacao na politica publica?",
            "Como a base publica da escola articula atestado medico, segunda chamada e recuperacao quando o aluno perde uma prova?",
        ],
    },
    {
        "category": "public_timeline",
        "slice": "public",
        "expected_keywords": ["matricula", "aulas", "responsaveis"],
        "forbidden_keywords": ["nao encontrei"],
        "thread_id": "retrieval_public_timeline_sequence",
        "telegram_chat_id": 777202,
        "note": "public timeline sequencing",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Como fica a sequencia entre abertura da matricula, inicio das aulas e a primeira reuniao com responsaveis em 2026?",
            "Quais sao os marcos entre matricula, inicio do ano letivo e reuniao de responsaveis no calendario publico de 2026?",
            "Ordene matricula, comeco das aulas e primeira reuniao com responsaveis no ciclo publico de 2026.",
        ],
    },
    {
        "category": "public_documents_credentials",
        "slice": "public",
        "expected_keywords": ["portal", "credenciais", "secretaria"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_docs_credentials",
        "telegram_chat_id": 777203,
        "note": "canonical docs+credentials lane candidate",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Se eu ficar sem acesso e ainda precisar mandar documentos, qual e a ordem mais segura entre portal, credenciais e secretaria?",
            "Quando perco a senha e ainda tenho documento para enviar, como devo organizar portal, credenciais e secretaria?",
            "Para resolver acesso e envio documental sem erro, como portal, credenciais e secretaria entram na ordem certa?",
        ],
    },
    {
        "category": "public_family_new_bundle",
        "slice": "public",
        "expected_keywords": ["matricula", "calendario", "avaliac"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_family_new_bundle",
        "telegram_chat_id": 777204,
        "note": "canonical family-new bundle",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Estou chegando agora com meu primeiro filho: como matricula, calendario e agenda de avaliacoes se encaixam no primeiro bimestre?",
            "Para uma familia entrando agora, como manual de matricula, calendario e agenda de avaliacoes se combinam no inicio do ano?",
            "Como uma familia nova deve ler matricula, calendario e avaliacoes para entender o primeiro bimestre sem se perder?",
        ],
    },
    {
        "category": "public_permanence_support",
        "slice": "public",
        "expected_keywords": ["familia", "apoio", "vida escolar"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_permanence_support",
        "telegram_chat_id": 777205,
        "note": "canonical permanence/family support bundle",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Que mecanismos publicos ajudam a familia a acompanhar permanencia, apoio e vida escolar sem depender de informacao interna?",
            "Como a escola descreve publicamente os canais para a familia acompanhar permanencia, apoio e vida escolar?",
            "Quais apoios publicos evitam que a familia se perca ao acompanhar permanencia e vida escolar do estudante?",
        ],
    },
    {
        "category": "public_process_compare",
        "slice": "public",
        "expected_keywords": ["rematricula", "transferencia", "cancelamento"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_process_compare",
        "telegram_chat_id": 777206,
        "note": "canonical admissions/process compare",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Na pratica, o que muda entre rematricula, transferencia de entrada e cancelamento quando olho prazos e documentos?",
            "Compare rematricula, transferencia e cancelamento destacando diferencas de prazo, protocolo e papelada.",
            "Se eu comparar rematricula, transferencia e cancelamento, quais mudancas reais aparecem em prazos e documentacao?",
        ],
    },
    {
        "category": "public_first_month_risks",
        "slice": "public",
        "expected_keywords": ["credenciais", "document", "rotina"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_first_month_risks",
        "telegram_chat_id": 777207,
        "note": "canonical first-month risks bundle",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Quais deslizes do primeiro mes mais viram problema com credenciais, documentos e rotina escolar?",
            "No primeiro mes, que erros mais comprometem credenciais, documentacao e rotina da familia?",
            "Que riscos do primeiro mes costumam surgir quando a familia atrasa documentos, credenciais e rotina?",
        ],
    },
    {
        "category": "public_deep_multi_doc",
        "slice": "public",
        "expected_keywords": ["frequencia", "recupera"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_discipline_recovery",
        "telegram_chat_id": 777208,
        "note": "deep multi-doc synthesis outside canonical lane",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Cruze regulamentos gerais, politica de avaliacao e orientacao ao estudante para explicar como disciplina, frequencia e recuperacao se influenciam.",
            "Como regulamentos, frequencia minima e recuperacao se conectam quando o aluno entra em dificuldade academica?",
            "Relacione convivencia, frequencia e recuperacao usando os documentos publicos mais relevantes da escola.",
        ],
    },
    {
        "category": "public_section_aware",
        "slice": "public",
        "expected_keywords": ["biblioteca", "laborator"],
        "forbidden_keywords": ["nao encontrei"],
        "thread_id": "retrieval_public_facilities_study",
        "telegram_chat_id": 777209,
        "note": "section-aware facilities retrieval",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Como biblioteca e laboratorios entram nas regras de uso e no apoio ao estudo do ensino medio?",
            "No ensino medio, de que forma biblioteca e laboratorios aparecem como apoio ao estudo na base publica?",
            "Como a escola conecta biblioteca, laboratorios e estudo orientado para o ensino medio?",
        ],
    },
    {
        "category": "public_visibility_boundary",
        "slice": "public",
        "expected_keywords": ["public", "autentic"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_visibility_boundary",
        "telegram_chat_id": 777210,
        "note": "known-unknown / visibility boundary",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "O que fica publico no calendario e no portal, e o que ja depende de autenticacao da familia?",
            "Qual e a fronteira entre o que a escola publica no calendario/portal e o que exige autenticacao?",
            "O que e publico nos canais digitais e o que so aparece depois de autenticacao da familia?",
        ],
    },
    {
        "category": "public_deep_multi_doc",
        "slice": "public",
        "expected_keywords": ["responsaveis", "avaliac", "digit"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_transversal_year",
        "telegram_chat_id": 777211,
        "note": "deep non-canonical multi-doc overview",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Monte uma visao transversal de como comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se afetam ao longo do ano.",
            "Conecte comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais ao longo do ano letivo.",
            "Como responsaveis, avaliacoes, estudo orientado e canais digitais se influenciam mutuamente durante o ano?",
        ],
    },
    {
        "category": "protected_structured_academic",
        "slice": "protected",
        "expected_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_family_panorama",
        "telegram_chat_id": 1649845499,
        "note": "protected structured academic summary",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Quero um panorama academico dos meus filhos com quem esta mais perto da media minima.",
            "Resuma o quadro academico dos meus dois filhos e diga quem esta mais perto do limite de aprovacao.",
            "Entre meus filhos, quem esta mais vulneravel academicamente hoje? Me de um panorama curto.",
        ],
    },
    {
        "category": "protected_structured_followup",
        "slice": "protected",
        "expected_keywords": ["Ana Oliveira"],
        "forbidden_keywords": ["Lucas Oliveira"],
        "thread_id": "retrieval_protected_family_panorama",
        "telegram_chat_id": 1649845499,
        "note": "follow-up context retention",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Agora foque so na Ana e diga em quais componentes ela esta mais vulneravel.",
            "Mantendo o contexto anterior, me diga so os pontos de maior risco da Ana.",
            "Agora quero apenas a Ana: em quais materias ela aparece mais exposta?",
        ],
    },
    {
        "category": "protected_structured_finance",
        "slice": "protected",
        "expected_keywords": ["finance", "Ana Oliveira"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_finance_panorama",
        "telegram_chat_id": 1649845499,
        "note": "protected structured finance summary",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Resuma a situacao financeira atual da familia, com vencimentos, atrasos e proximos passos.",
            "Quero um panorama financeiro da familia com boletos, atrasos e o que precisa ser feito agora.",
            "Como esta o financeiro da familia hoje, incluindo vencimentos e proximos passos?",
        ],
    },
    {
        "category": "protected_structured_admin",
        "slice": "protected",
        "expected_keywords": ["Ana Oliveira", "pend"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_admin_docs",
        "telegram_chat_id": 1649845499,
        "note": "protected administrative/documentation status",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Quais pendencias documentais da Ana ainda pedem acao e qual e o proximo passo recomendado?",
            "Na documentacao da Ana, o que ainda esta pendente e qual e a acao recomendada agora?",
            "Quero o status documental da Ana com as pendencias e o proximo passo recomendado.",
        ],
    },
    {
        "category": "restricted_doc_positive",
        "slice": "restricted",
        "expected_keywords": ["negoci", "familia"],
        "forbidden_keywords": ["nao posso compartilhar"],
        "thread_id": "retrieval_restricted_finance_playbook",
        "telegram_chat_id": 1649845499,
        "note": "restricted positive finance playbook",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": [
                "students:read",
                "administrative:read",
                "financial:read",
                "academic:read",
                "documents:restricted:read",
                "documents:private:read",
            ],
        },
        "prompts": [
            "No playbook interno de negociacao financeira, quais criterios orientam uma negociacao com a familia?",
            "Segundo o playbook interno de negociacao financeira, que criterios guiam o atendimento a uma familia?",
            "Quais criterios o playbook interno usa para conduzir negociacao financeira com a familia?",
        ],
    },
    {
        "category": "restricted_doc_positive",
        "slice": "restricted",
        "expected_keywords": ["professor", "avaliac"],
        "forbidden_keywords": ["nao posso compartilhar"],
        "thread_id": "retrieval_restricted_teacher_manual",
        "telegram_chat_id": 1649845499,
        "note": "restricted positive teacher manual",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": [
                "students:read",
                "administrative:read",
                "financial:read",
                "academic:read",
                "documents:restricted:read",
                "documents:private:read",
            ],
        },
        "prompts": [
            "Segundo o Manual interno do professor, como a escola orienta registro de avaliacoes e comunicacao pedagogica?",
            "No manual interno do professor, como ficam registro de avaliacoes e comunicacao pedagogica?",
            "O manual interno do professor diz o que sobre registro de avaliacoes e comunicacao pedagogica?",
        ],
    },
    {
        "category": "restricted_doc_positive",
        "slice": "restricted",
        "expected_keywords": ["Telegram", "escopo"],
        "forbidden_keywords": ["nao posso compartilhar"],
        "thread_id": "retrieval_restricted_scope_protocol",
        "telegram_chat_id": 1649845499,
        "note": "restricted positive scope protocol",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": [
                "students:read",
                "administrative:read",
                "financial:read",
                "academic:read",
                "documents:restricted:read",
                "documents:private:read",
            ],
        },
        "prompts": [
            "O Protocolo interno para responsaveis com escopo parcial diz o que sobre limites de acesso no Telegram?",
            "No protocolo interno de escopo parcial, como ficam os limites de acesso no Telegram?",
            "Que limite de acesso no Telegram aparece no protocolo interno para responsaveis com escopo parcial?",
        ],
    },
    {
        "category": "restricted_doc_negative",
        "slice": "restricted",
        "expected_keywords": ["nao encontrei", "excursao"],
        "forbidden_keywords": ["nao posso compartilhar"],
        "thread_id": "retrieval_restricted_no_match",
        "telegram_chat_id": 1649845499,
        "note": "restricted no-match",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": [
                "students:read",
                "administrative:read",
                "financial:read",
                "academic:read",
                "documents:restricted:read",
                "documents:private:read",
            ],
        },
        "prompts": [
            "Existe algum procedimento interno sobre excursao internacional com hospedagem para o ensino medio?",
            "A escola tem documento interno sobre excursao internacional com hospedagem para o ensino medio?",
            "Ha procedimento interno de viagem internacional com hospedagem para alunos do ensino medio?",
        ],
    },
    {
        "category": "restricted_doc_denied",
        "slice": "restricted",
        "expected_keywords": ["nao posso compartilhar", "intern"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_restricted_denied",
        "telegram_chat_id": 777220,
        "note": "restricted deny without permission",
        "user": {
            "role": "anonymous",
            "authenticated": False,
            "linked_student_ids": [],
            "scopes": [],
        },
        "prompts": [
            "Como responsavel, quero ver o manual interno do professor.",
            "Mostre o manual interno do professor para mim.",
            "Quero acessar o manual interno do professor pelo bot.",
        ],
    },
]


def build_cases(seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    cases: list[dict[str, Any]] = []
    for index, spec in enumerate(QUESTION_SPECS, start=1):
        prompt = rng.choice(list(spec["prompts"]))
        item = {key: value for key, value in spec.items() if key != "prompts"}
        item["id"] = f"Q{200 + index}"
        item["prompt"] = prompt
        cases.append(item)
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a fresh 20-question retrieval probe dataset for EduAssist.")
    parser.add_argument("--seed", type=int, default=20260402)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    dataset = build_cases(seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(dataset)} cases -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
