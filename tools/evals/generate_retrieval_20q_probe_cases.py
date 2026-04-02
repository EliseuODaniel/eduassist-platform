#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "tests/evals/datasets/retrieval_20q_probe_cases.generated.json"
DATASETS_DIR = REPO_ROOT / "tests/evals/datasets"


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
            "Se uma prova e perdida por motivo de saude, como atestado, segunda chamada e recuperacao aparecem conectados nos documentos publicos?",
            "Pelos documentos publicos, como atestado de saude, segunda chamada e recuperacao se encadeiam quando o estudante perde uma avaliacao?",
            "Se o aluno perde uma prova por razao de saude, como a escola amarra comprovacao, segunda chamada e recuperacao no material publico?",
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
            "No calendario publico de 2026, qual vem primeiro entre matricula, inicio das aulas e encontro inicial com responsaveis?",
            "No cronograma publico de 2026, em que ordem aparecem abertura da matricula, comeco das aulas e primeiro encontro com responsaveis?",
            "Se eu olhar so a linha do tempo publica de 2026, como se distribuem matricula, inicio das aulas e reuniao inicial com as familias?",
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
            "Se o acesso falhou bem na hora de enviar documentos, como portal, credenciais e secretaria devem ser tratados na sequencia correta?",
            "Quando o problema e acesso mais entrega de documentos ao mesmo tempo, como portal, credenciais e secretaria entram na ordem correta?",
            "Se a familia ficou sem login justamente na etapa de envio documental, qual e a sequencia mais segura entre portal, credenciais e secretaria?",
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
            "Para quem esta entrando este ano com o primeiro filho, como matricula, calendario e agenda de avaliacoes se amarram no comeco das aulas?",
            "Minha familia vai entrar este ano pela primeira vez: como matricula, calendario e agenda de avaliacoes se conectam logo no inicio das aulas?",
            "Para pais estreando na escola, como ler juntos manual de matricula, calendario e agenda de avaliacoes para entender o primeiro bimestre?",
            "Estamos fazendo a primeira matricula da familia: como calendario, agenda de avaliacoes e processo de ingresso se organizam no primeiro bimestre?",
            "Para uma casa que esta entrando no Colegio Horizonte agora, como matricula, inicio das aulas e avaliacoes se relacionam no comeco do ano?",
            "Quero entender o primeiro bimestre de uma familia nova: como matricula, calendario escolar e agenda de avaliacoes conversam entre si?",
            "Entrando pela primeira vez na escola, como a familia deve juntar calendario, matricula e agenda de avaliacoes para nao perder marcos do primeiro bimestre?",
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
            "Pelos documentos publicos, como a familia acompanha permanencia escolar, apoio e vida escolar sem precisar recorrer a material interno?",
            "Sem usar informacao interna, quais recursos publicos a escola oferece para a familia acompanhar permanencia, apoio e vida escolar?",
            "Que trilha publica a familia encontra para acompanhar apoio ao estudante, permanencia e vida escolar sem depender de acesso privado?",
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
            "Olhando prazos, protocolo e documentacao, como rematricula, transferencia e cancelamento se diferenciam na pratica?",
            "Quando comparo rematricula, transferencia de entrada e cancelamento, o que muda de verdade em prazo, protocolo e documentos?",
            "Se a familia colocar rematricula, transferencia e cancelamento lado a lado, quais diferencas praticas aparecem em papelada e prazos?",
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
            "No comeco do ano, que falhas mais baguncam credenciais, documentacao e a rotina da familia nas primeiras semanas?",
            "Nas primeiras semanas, que descuidos mais costumam estourar em problema de credenciais, documentacao e rotina escolar?",
            "Quais erros do inicio do ano mais desorganizam credenciais, documentos e a rotina da familia logo no primeiro mes?",
            "Quais tropeços das primeiras semanas mais acabam travando credenciais, documentos e a rotina da familia?",
            "Se a familia se enrola no inicio do ano, quais erros mais costumam virar problema de login, documentacao e rotina escolar?",
            "No arranque do ano letivo, que descuidos mais costumam explodir entre credenciais, papelada e rotina da casa?",
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
            "Usando os documentos publicos, explique como convivencia, frequencia e recuperacao passam a se influenciar quando o aluno entra em dificuldade.",
            "A partir dos documentos publicos, conecte regras de convivencia, frequencia minima e recuperacao quando o estudante entra em risco academico.",
            "Como os materiais publicos articulam disciplina, frequencia e recuperacao quando o aluno comeca a acumular dificuldades?",
            "Se o estudante comeca a falhar em frequencia e rendimento, como os documentos publicos ligam regras de convivencia, recuperacao e acompanhamento?",
            "Junte regulamento, frequencia e recuperacao para explicar o que a escola faz quando o aluno entra em zona de risco academico.",
            "Quero uma sintese publica de como disciplina, faltas e recuperacao se cruzam quando o desempenho do aluno cai.",
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
            "Na documentacao publica do ensino medio, como biblioteca, laboratorios e estudo orientado aparecem conectados como apoio academico?",
            "Na base publica do ensino medio, como biblioteca, laboratorios e apoio ao estudo aparecem amarrados na rotina academica?",
            "De que forma os documentos publicos ligam biblioteca, laboratorios e estudo orientado como suporte ao ensino medio?",
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
            "Nos canais digitais da escola, o que ainda e publico e o que passa a depender da autenticacao da familia?",
            "Nos canais da escola, onde termina o conteudo publico e onde comeca o que exige autenticacao da familia?",
            "O que qualquer familia ve no calendario e portal sem login, e o que so surge depois da autenticacao?",
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
            "Ao longo do ano letivo, como comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais passam a depender uns dos outros?",
            "Pelos documentos publicos, como comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se encadeiam ao longo do ano letivo?",
            "Monte uma leitura transversal mostrando como avaliacoes, estudo orientado, canais digitais e contato com responsaveis se reforcam durante o ano.",
            "Explique de forma transversal como provas, estudo orientado, comunicados digitais e relacionamento com responsaveis se encadeiam ao longo do ano.",
            "Nos documentos publicos, como avaliacao, canais digitais, apoio ao estudo e comunicacao com responsaveis formam um circuito unico ao longo do ano?",
            "Quero uma sintese ampla de como avaliacoes, estudo orientado, contato com a familia e canais digitais se amarram no ano letivo.",
            "Como os materiais publicos mostram a relacao entre agenda avaliativa, comunicacao com responsaveis, estudo orientado e meios digitais durante o ano?",
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
            "Faca um resumo academico dos meus dois filhos e destaque qual deles esta mais perto do corte de aprovacao.",
            "Me de um panorama academico dos meus filhos e diga qual deles aparece mais perto da media minima agora.",
            "Quero comparar rapidamente a situacao academica dos meus dois filhos e saber quem esta mais proximo do limite de aprovacao.",
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
            "Seguindo o panorama anterior, isole a Ana e diga onde ela aparece mais fragilizada academicamente.",
            "Continuando o panorama, olhe so a Ana e diga em quais componentes ela corre mais risco agora.",
            "Mantendo o contexto dos meus filhos, filtre para a Ana e mostre as materias em que ela esta mais vulneravel.",
            "Sem repetir o quadro inteiro, recorte so a Ana e mostre onde o risco academico dela esta mais alto.",
            "Depois do panorama dos meus filhos, fique apenas com a Ana e diga quais componentes merecem mais atencao agora.",
            "Quero o mesmo panorama, mas agora isolando a Ana e os pontos academicos que mais preocupam.",
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
            "Me de um quadro financeiro da familia hoje, com o que venceu, o que esta por vencer e o proximo passo recomendado.",
            "Quero um resumo do financeiro da familia com o que venceu, o que vence logo e qual acao e recomendada agora.",
            "Como esta a situacao financeira da familia neste momento, incluindo atrasos, vencimentos proximos e proximo passo?",
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
            "Na parte administrativa da Ana, quais pendencias documentais ainda restam e o que a familia deve fazer agora?",
            "Sobre a Ana, quais pendencias administrativas ou documentais ainda exigem acao e qual e o proximo passo?",
            "Quero ver o quadro documental da Ana: o que esta pendente e o que a familia precisa fazer em seguida?",
            "No cadastro da Ana, quais pendencias administrativas continuam abertas e que acao vem agora?",
            "Quero um retrato das pendencias documentais da Ana e do proximo passo para regularizar tudo.",
            "Hoje, o que ainda falta na parte administrativa da Ana e como a familia deve agir em seguida?",
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
            "Pelo playbook interno de negociacao financeira, quais criterios a equipe usa para conduzir uma conversa com a familia?",
            "No material interno de negociacao financeira, quais criterios orientam a conversa da escola com a familia?",
            "Quais parametros o playbook interno de negociacao financeira usa para decidir como conduzir a negociacao com a familia?",
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
            "Dentro do manual interno do professor, qual e a orientacao sobre registro de avaliacoes e comunicacao pedagogica?",
            "No material interno do professor, como a escola orienta o registro de avaliacoes e a comunicacao pedagogica?",
            "Pelo manual interno do professor, qual e a regra para registro de avaliacoes e comunicacao com foco pedagogico?",
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
            "Segundo o protocolo interno de escopo parcial, que restricao de acesso no Telegram vale para responsaveis com esse perfil?",
            "No protocolo interno para responsaveis com escopo parcial, quais limites de acesso no Telegram sao definidos?",
            "Como o protocolo interno de escopo parcial descreve as restricoes de acesso no Telegram para esse tipo de responsavel?",
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
            "Nos documentos internos, existe alguma orientacao especifica para excursao internacional com hospedagem no ensino medio?",
            "Os documentos internos mencionam algum protocolo para excursao internacional com pernoite no ensino medio?",
            "Existe orientacao interna para viagem internacional com hospedagem envolvendo turmas do ensino medio?",
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
            "Preciso que voce me mostre o manual interno do professor aqui no chat.",
            "Sou responsavel e quero que voce abra o manual interno do professor para mim.",
            "Pode me mostrar aqui no bot o manual interno do professor?",
        ],
    },
]


def _collect_existing_prompts(dataset_dir: Path) -> set[str]:
    prompts: set[str] = set()
    for path in sorted(dataset_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, list):
            continue
        for item in payload:
            if not isinstance(item, dict):
                continue
            prompt = item.get("prompt") or item.get("question")
            if isinstance(prompt, str) and prompt.strip():
                prompts.add(prompt.strip())
    return prompts


PROMPT_PREFIX_VARIANTS = (
    "Pensando no caso pratico, ",
    "De forma bem objetiva, ",
    "Sem sair do escopo do projeto, ",
)

PROMPT_SUFFIX_VARIANTS = (
    " Responda de forma direta.",
    " Seja objetivo e grounded.",
    " Traga a resposta de forma concreta.",
)


def _fresh_prompt_candidates(spec: dict[str, Any], history: set[str]) -> list[str]:
    base_prompts = [
        prompt.strip()
        for prompt in spec["prompts"]
        if isinstance(prompt, str) and prompt.strip()
    ]
    direct = [prompt for prompt in base_prompts if prompt not in history]
    if direct:
        return direct

    augmented: list[str] = []
    seen_local: set[str] = set()
    for prompt in base_prompts:
        for prefix in PROMPT_PREFIX_VARIANTS:
            candidate = f"{prefix}{prompt[0].lower()}{prompt[1:]}" if prompt else f"{prefix}{prompt}"
            candidate = candidate.strip()
            if candidate and candidate not in history and candidate not in seen_local:
                augmented.append(candidate)
                seen_local.add(candidate)
        for suffix in PROMPT_SUFFIX_VARIANTS:
            candidate = f"{prompt.rstrip(' ?.!')}.{suffix}".replace("..", ".").strip()
            if candidate and candidate not in history and candidate not in seen_local:
                augmented.append(candidate)
                seen_local.add(candidate)
    return augmented


def build_cases(seed: int, existing_prompts: set[str] | None = None) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    history = {prompt.strip() for prompt in (existing_prompts or set()) if prompt.strip()}
    cases: list[dict[str, Any]] = []
    for index, spec in enumerate(QUESTION_SPECS, start=1):
        available_prompts = _fresh_prompt_candidates(spec, history)
        if not available_prompts:
            raise ValueError(
                f"No fresh prompt variants left for category '{spec['category']}'. "
                "Add new prompt phrasings or expand the augmentation templates before generating another 20Q dataset."
            )
        prompt = rng.choice(available_prompts)
        item = {key: value for key, value in spec.items() if key != "prompts"}
        item["id"] = f"Q{200 + index}"
        item["prompt"] = prompt
        cases.append(item)
        history.add(prompt)
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a fresh 20-question retrieval probe dataset for EduAssist.")
    parser.add_argument("--seed", type=int, default=20260402)
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
    print(
        f"generated {len(dataset)} cases -> {args.output} "
        f"(history_blocked={len(existing_prompts)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
