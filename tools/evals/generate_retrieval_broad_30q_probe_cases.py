#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evals.generate_retrieval_20q_probe_cases import (
    DATASETS_DIR,
    QUESTION_SPECS as BASE_QUESTION_SPECS,
    _collect_existing_prompts,
    _fresh_prompt_candidates,
)

DEFAULT_OUTPUT = REPO_ROOT / "tests/evals/datasets/retrieval_broad_30q_probe_cases.generated.json"


def _specs_by_thread_id() -> dict[str, list[dict[str, Any]]]:
    mapping: dict[str, list[dict[str, Any]]] = {}
    for spec in BASE_QUESTION_SPECS:
        thread_id = str(spec.get("thread_id") or "")
        mapping.setdefault(thread_id, []).append(deepcopy(spec))
    return mapping


def _single_spec_by_thread(thread_id: str) -> dict[str, Any]:
    rows = _specs_by_thread_id().get(thread_id) or []
    if len(rows) != 1:
        raise ValueError(f"thread_id_not_singleton:{thread_id}:{len(rows)}")
    return rows[0]


def _thread_specs(thread_id: str) -> list[dict[str, Any]]:
    rows = _specs_by_thread_id().get(thread_id) or []
    if not rows:
        raise ValueError(f"thread_id_not_found:{thread_id}")
    return rows


def _first_spec_for_thread(thread_id: str) -> dict[str, Any]:
    rows = _thread_specs(thread_id)
    return rows[0]


EXTRA_SPECS: list[dict[str, Any]] = [
    {
        "category": "protected_teacher_schedule",
        "slice": "protected",
        "expected_keywords": ["turmas", "disciplin"],
        "forbidden_keywords": ["nao posso", "não posso"],
        "thread_id": "retrieval_teacher_schedule_panorama",
        "telegram_chat_id": 1649845501,
        "note": "teacher schedule summary",
        "user": {
            "role": "teacher",
            "authenticated": True,
            "linked_student_ids": [],
            "scopes": ["teacher:schedule:read", "calendar:read"],
        },
        "prompts": [
            "Sou professor e quero um panorama das minhas turmas e disciplinas deste ano.",
            "Quero ver minha alocacao docente atual, com turmas e disciplinas, de forma objetiva.",
            "Mostre minha grade docente do ano juntando turmas e disciplinas que ficaram sob minha responsabilidade.",
            "Preciso revisar rapidamente minhas turmas e disciplinas neste ano letivo. Me entregue isso em resumo.",
            "Como professor autenticado, quero um quadro claro das turmas e disciplinas que atendo neste ano.",
            "Resuma minha alocacao docente atual com foco em turmas e disciplinas.",
        ],
    },
    {
        "category": "protected_teacher_schedule_followup",
        "slice": "protected",
        "expected_keywords": ["ensino medio", "médio"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_teacher_schedule_panorama",
        "telegram_chat_id": 1649845501,
        "note": "teacher schedule follow-up",
        "user": {
            "role": "teacher",
            "authenticated": True,
            "linked_student_ids": [],
            "scopes": ["teacher:schedule:read", "calendar:read"],
        },
        "prompts": [
            "Agora recorte so o que eu tenho no ensino medio.",
            "Mantendo o contexto anterior, quero apenas a parte do ensino medio.",
            "Filtre a minha alocacao e deixe so as turmas do ensino medio.",
            "Continuando a consulta, mostra apenas o trecho da minha rotina no ensino medio.",
            "Agora quero ver so o recorte de ensino medio da minha grade docente.",
            "Sem repetir tudo, isole apenas minhas turmas e disciplinas do ensino medio.",
        ],
    },
    {
        "category": "protected_student_academic_self",
        "slice": "protected",
        "expected_keywords": ["fisica", "física"],
        "forbidden_keywords": ["Ana Oliveira"],
        "thread_id": "retrieval_student_academic_self",
        "telegram_chat_id": 777013,
        "note": "student self academic panorama",
        "user": {
            "role": "student",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas"],
            "scopes": ["academic:read"],
        },
        "prompts": [
            "Sou aluno e quero saber minha melhor disciplina, minha pior e quanto falta para eu fechar a media em fisica.",
            "Como aluno autenticado, me diga qual materia esta melhor, qual esta pior e o que falta para fechar a media em fisica.",
            "Quero um retrato curto do meu desempenho: melhor disciplina, pior disciplina e distancia ate a media em fisica.",
            "Me mostre meu ponto mais forte, meu ponto mais fraco e o quanto falta para eu fechar fisica.",
            "Preciso de um resumo do meu desempenho com foco em melhor materia, pior materia e situacao em fisica.",
            "Sem tabela, diga minha melhor disciplina, a pior e quanto ainda falta para eu fechar a media em fisica.",
        ],
    },
    {
        "category": "restricted_staff_finance_protocol",
        "slice": "restricted",
        "expected_keywords": ["pagamento", "quitacao", "quitação"],
        "forbidden_keywords": ["nao posso compartilhar", "não posso compartilhar"],
        "thread_id": "retrieval_staff_finance_protocol",
        "telegram_chat_id": 888002,
        "note": "staff internal finance protocol",
        "user": {
            "role": "staff",
            "authenticated": True,
            "linked_student_ids": [],
            "scopes": ["documents:private:read", "documents:restricted:read", "workflow:manage"],
        },
        "prompts": [
            "No procedimento interno de pagamento parcial e negociacao, o que o financeiro deve validar antes de prometer quitacao?",
            "Como o protocolo interno orienta a equipe financeira antes de falar em quitacao num caso de pagamento parcial?",
            "Quero o trecho operacional: no fluxo interno de pagamento parcial, o que precisa ser validado antes de prometer quitacao?",
            "Pelo procedimento interno, o que o financeiro confere antes de assumir quitacao em negociacao com pagamento parcial?",
            "Na rotina interna de negociacao financeira, quais validacoes antecedem qualquer promessa de quitacao?",
            "No manual interno da equipe financeira, o que deve ser checado antes de prometer quitacao quando houve pagamento parcial?",
        ],
    },
    {
        "category": "public_external_library_boundary",
        "slice": "public",
        "expected_keywords": ["escola", "escopo"],
        "forbidden_keywords": ["Biblioteca Aurora", "7h30", "18h00"],
        "thread_id": "retrieval_public_external_library_boundary",
        "telegram_chat_id": 777330,
        "note": "external city library boundary",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Qual e o horario de fechamento da biblioteca publica da cidade? Nao estou falando da escola.",
            "Quero saber da biblioteca publica municipal, nao da escola: que horas ela fecha?",
            "Fora do Colegio Horizonte, qual e o horario da biblioteca publica da cidade?",
            "Nao e a biblioteca da escola: me diga o horario da biblioteca publica municipal.",
            "Estou perguntando da biblioteca da cidade, nao da escola. Que horas ela fecha?",
            "Esquece a escola por um momento: a biblioteca publica da cidade fecha que horas?",
        ],
    },
    {
        "category": "public_open_world_out_of_scope",
        "slice": "public",
        "expected_keywords": ["escola"],
        "forbidden_keywords": ["Oscar", "Campeonato", "filme"],
        "thread_id": "retrieval_public_open_world_out_of_scope",
        "telegram_chat_id": 777331,
        "note": "open world out of scope",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Qual e o melhor filme do ano na sua opiniao?",
            "Me recomenda um filme para ver hoje a noite.",
            "Quem vai ganhar o principal premio de cinema este ano?",
            "Quero uma recomendacao de filme, sem relacao com escola.",
            "Me ajuda a escolher um filme para o fim de semana?",
            "Fora do tema escolar, qual filme voce acha que mais vale a pena ver agora?",
        ],
    },
    {
        "category": "protected_boundary_auth_needed",
        "slice": "protected",
        "expected_keywords": ["autentic", "vincul"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_protected_boundary_auth_needed",
        "telegram_chat_id": 777332,
        "note": "anonymous asks for protected grades",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Quero ver minhas notas agora, mas ainda nao fiz login aqui.",
            "Sem autenticar, eu consigo puxar minhas notas por este chat?",
            "Ainda nao vinculei minha conta: da para voce me mostrar minhas notas assim mesmo?",
            "Quero minhas notas sem passar por login. O que acontece nesse caso?",
            "Nao estou autenticado e mesmo assim quero consultar meu boletim aqui pelo bot.",
            "Se eu pedir minhas notas antes de autenticar, voce mostra ou bloqueia?",
        ],
    },
]


def _broad_specs() -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = [
        _single_spec_by_thread("retrieval_public_docs_credentials"),
        _single_spec_by_thread("retrieval_public_family_new_bundle"),
        _single_spec_by_thread("retrieval_public_discipline_recovery"),
        _single_spec_by_thread("retrieval_public_facilities_study"),
        _single_spec_by_thread("retrieval_public_service_routing"),
        _single_spec_by_thread("retrieval_public_teacher_directory"),
        _single_spec_by_thread("retrieval_public_pricing_projection"),
        _single_spec_by_thread("retrieval_public_governance_protocol"),
        _single_spec_by_thread("retrieval_public_known_unknown_total_teachers"),
        _single_spec_by_thread("retrieval_protected_access_scope"),
        *_thread_specs("retrieval_protected_family_panorama"),
        *_thread_specs("retrieval_protected_attendance_panorama"),
        _single_spec_by_thread("retrieval_protected_finance_panorama"),
        _single_spec_by_thread("retrieval_protected_admin_docs"),
        _single_spec_by_thread("retrieval_protected_admin_finance_combo"),
        _first_spec_for_thread("retrieval_protected_upcoming_assessments"),
        _single_spec_by_thread("retrieval_restricted_finance_playbook"),
        _single_spec_by_thread("retrieval_restricted_teacher_manual"),
        _single_spec_by_thread("retrieval_restricted_scope_protocol"),
        _single_spec_by_thread("retrieval_restricted_no_match"),
        _single_spec_by_thread("retrieval_restricted_denied"),
        *[deepcopy(item) for item in EXTRA_SPECS],
    ]
    if len(selected) != 30:
        raise ValueError(f"broad_spec_count_must_be_30:{len(selected)}")
    return selected


def build_cases(seed: int, existing_prompts: set[str] | None = None) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    history = {prompt.strip() for prompt in (existing_prompts or set()) if prompt.strip()}
    specs = [deepcopy(spec) for spec in _broad_specs()]

    # keep follow-up adjacency, but shuffle blocks around them
    units: list[list[dict[str, Any]]] = []
    index = 0
    while index < len(specs):
        current = specs[index]
        thread_id = str(current.get("thread_id") or "")
        unit = [current]
        index += 1
        while index < len(specs) and thread_id and str(specs[index].get("thread_id") or "") == thread_id:
            unit.append(specs[index])
            index += 1
        units.append(unit)
    rng.shuffle(units)

    cases: list[dict[str, Any]] = []
    running_index = 1
    for unit in units:
        for spec in unit:
            available_prompts = _fresh_prompt_candidates(spec, history)
            if not available_prompts:
                raise ValueError(
                    f"No fresh prompt variants left for broad eval category '{spec['category']}'."
                )
            prompt = rng.choice(available_prompts)
            item = {key: value for key, value in spec.items() if key != "prompts"}
            item["id"] = f"B{running_index:03d}"
            item["prompt"] = prompt
            cases.append(item)
            history.add(prompt)
            running_index += 1
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a broad 30Q cross-stack probe dataset for EduAssist.")
    parser.add_argument("--seed", type=int, default=20260415)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--datasets-dir",
        type=Path,
        default=DATASETS_DIR,
        help="Directory whose existing JSON datasets are scanned to forbid exact prompt overlap.",
    )
    args = parser.parse_args()

    existing_prompts = _collect_existing_prompts(args.datasets_dir)
    dataset = build_cases(seed=args.seed, existing_prompts=existing_prompts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(dataset)} broad cases -> {args.output} (history_blocked={len(existing_prompts)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
