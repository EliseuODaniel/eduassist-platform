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
FOCUS_ALL = "all"
FOCUS_PROTECTED_SQL = "protected-sql"


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
    {
        "category": "public_service_routing",
        "slice": "public",
        "expected_keywords": ["Financeiro", "Direcao"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_service_routing",
        "telegram_chat_id": 777221,
        "note": "public service directory routing",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Com quem eu falo sobre bolsa, financeiro e direcao? Quero os setores e canais mais diretos.",
            "Qual setor responde por bolsa, financeiro e direcao, e por qual canal eu comeco?",
            "Se eu precisar tratar desconto, financeiro e um assunto com a direcao, quem responde por cada frente?",
            "Como entrar em contato com admissoes, financeiro e direcao quando o assunto mistura bolsa e mensalidade?",
            "Por qual canal eu falo com o setor de bolsas, com o financeiro e com a direcao da escola?",
            "Quem responde por bolsa, financeiro e direcao hoje, e quais canais publicos devo usar?",
        ],
    },
    {
        "category": "public_teacher_directory",
        "slice": "public",
        "expected_keywords": ["nao divulga", "coordenacao"],
        "forbidden_keywords": ["telefone do professor", "@", "11 9"],
        "thread_id": "retrieval_public_teacher_directory",
        "telegram_chat_id": 777222,
        "note": "public teacher contact boundary",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Vocês divulgam o nome ou contato direto do professor de matematica? Se nao, para onde a familia deve ir?",
            "Como falar com o professor de matematica? A escola divulga esse contato ou encaminha para outro setor?",
            "O colegio passa contato direto do professor de matematica ou orienta a familia pela coordenacao?",
            "Se eu quiser falar com o professor de matematica, a escola divulga esse contato ou manda procurar a coordenacao?",
            "Existe canal publico com nome ou contato do professor de matematica, ou isso vai pela coordenacao pedagogica?",
            "Para falar com o professor de matematica, o contato e publico ou a familia precisa passar pela coordenacao?",
        ],
    },
    {
        "category": "public_calendar_week",
        "slice": "public",
        "expected_keywords": ["familias", "responsaveis"],
        "forbidden_keywords": ["nao encontrei"],
        "thread_id": "retrieval_public_calendar_week",
        "telegram_chat_id": 777223,
        "note": "public calendar weekly family events",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Quais eventos publicos para familias e responsaveis aparecem nesta base agora?",
            "No calendario publico atual, quais sao os eventos mais relevantes para familias e responsaveis?",
            "Se eu olhar os eventos publicos voltados a familias e responsaveis, o que aparece primeiro?",
            "Quais marcos do calendario publico hoje falam mais diretamente com familias e responsaveis?",
            "Quero os principais eventos publicos para familias e responsaveis nesta base escolar.",
            "Dentro do calendario publico, quais eventos parecem mais importantes para familias e responsaveis?",
        ],
    },
    {
        "category": "public_year_three_phases",
        "slice": "public",
        "expected_keywords": ["Admissao", "Rotina academica", "Fechamento"],
        "forbidden_keywords": ["nao encontrei"],
        "thread_id": "retrieval_public_year_three_phases",
        "telegram_chat_id": 777224,
        "note": "public year in three phases",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Se eu dividir o ano em admissao, rotina academica e fechamento, como isso aparece na linha do tempo publica?",
            "Como a escola organiza o ano publico nas tres fases de admissao, rotina academica e fechamento?",
            "Na linha do tempo publica, como ficam as tres fases do ano: admissao, rotina academica e fechamento?",
            "Quero uma leitura do ano letivo em tres fases publicas: admissao, rotina academica e fechamento.",
            "Olhando so a base publica, como o ano se distribui entre admissao, rotina academica e fechamento?",
            "Se eu resumir o ano escolar em tres etapas publicas, como aparecem admissao, rotina academica e fechamento?",
        ],
    },
    {
        "category": "public_academic_policy_overview",
        "slice": "public",
        "expected_keywords": ["media", "frequencia"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_academic_policy_overview",
        "telegram_chat_id": 777225,
        "note": "public academic policy overview",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Na escola, como a politica de avaliacao, recuperacao e promocao conversa com media e frequencia minima?",
            "Sem area autenticada: na escola, como politica de avaliacao, recuperacao, promocao, media e frequencia minima aparecem juntas?",
            "Quero um panorama publico da escola sobre politica de avaliacao, recuperacao, promocao, media e frequencia minima.",
            "Na escola, como ficam avaliacao, recuperacao, promocao, media de aprovacao e frequencia minima no material publico?",
            "Pela politica publica da escola, como se juntam avaliacao, recuperacao, promocao, media e frequencia minima?",
            "Sem usar dados privados, como a escola descreve avaliacao, recuperacao, promocao, media e frequencia minima?",
        ],
    },
    {
        "category": "public_conduct_frequency_punctuality",
        "slice": "public",
        "expected_keywords": ["frequencia", "pontualidade"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_conduct_frequency_punctuality",
        "telegram_chat_id": 777226,
        "note": "public conduct frequency punctuality bridge",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Como convivencia, frequencia e pontualidade se ligam na politica publica da escola?",
            "Na base publica, como a escola conecta convivencia, frequencia, pontualidade e risco academico?",
            "Pelo material publico, como ficam juntas regras de convivencia, frequencia e pontualidade?",
            "Quero entender como a escola amarra convivencia, pontualidade e frequencia no regulamento publico.",
            "Nos documentos publicos, como a escola trata pontualidade, frequencia e convivencia como parte do mesmo acompanhamento?",
            "Como a politica publica da escola junta pontualidade, frequencia e convivencia no dia a dia do aluno?",
        ],
    },
    {
        "category": "public_bolsas_and_processes",
        "slice": "public",
        "expected_keywords": ["bolsas", "cancelamento"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_bolsas_and_processes",
        "telegram_chat_id": 777227,
        "note": "public bolsas and process compare",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Como bolsas e descontos se cruzam com rematricula, transferencia e cancelamento no material publico?",
            "Pelos documentos publicos, como ficam juntos bolsas, descontos, rematricula, transferencia e cancelamento?",
            "Quero relacionar bolsas e descontos com rematricula, transferencia e cancelamento sem sair do material publico.",
            "Como a escola conecta edital de bolsas com rematricula, transferencia e cancelamento?",
            "Na pratica, como bolsas e descontos conversam com rematricula, transferencia e cancelamento na base publica?",
            "Se eu juntar bolsas, rematricula, transferencia e cancelamento, que panorama publico a escola oferece?",
        ],
    },
    {
        "category": "public_pricing_projection",
        "slice": "public",
        "expected_keywords": ["matricula", "por mes"],
        "forbidden_keywords": ["nao encontrei"],
        "thread_id": "retrieval_public_pricing_projection",
        "telegram_chat_id": 777228,
        "note": "public pricing projection deterministic",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Quanto eu pagaria de matricula e por mes para 3 filhos usando a referencia publica atual?",
            "Usando a tabela publica, quanto dariam matricula e mensalidade para 3 filhos?",
            "Se eu simular 3 filhos, qual seria o valor de matricula e o total por mes na referencia publica?",
            "Na referencia publica atual, quanto fica a matricula e o total por mes para 3 filhos?",
            "Se eu projetar 3 filhos no colegio, qual e o valor de matricula e quanto fica por mes na base publica?",
            "Pela referencia publica de precos, qual seria a matricula total e o valor mensal para 3 filhos?",
        ],
    },
    {
        "category": "protected_access_scope",
        "slice": "protected",
        "expected_keywords": ["autenticado", "academico", "financeiro"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_access_scope",
        "telegram_chat_id": 1649845499,
        "note": "authenticated account scope",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Qual e exatamente o meu escopo aqui? Quero saber se estou autenticado e quais dados academicos e financeiros consigo ver.",
            "O que eu consigo consultar aqui no Telegram? Quero meu escopo exato entre academico e financeiro.",
            "Quais dados dos meus filhos eu consigo acessar por aqui, e se o meu acesso cobre academico e financeiro?",
            "Estou autenticado como quem e com qual escopo? Quero saber o que consigo ver de academico e financeiro.",
            "Me diga o escopo atual da minha conta neste canal, incluindo acesso academico e financeiro.",
            "Quero confirmar meu escopo no Telegram: estou autenticado e consigo ver o que de academico e financeiro?",
        ],
    },
    {
        "category": "protected_admin_finance_combo",
        "slice": "protected",
        "expected_keywords": ["Financeiro", "document"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_admin_finance_combo",
        "telegram_chat_id": 1649845499,
        "note": "combined admin and finance overview",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Minha documentacao ou cadastro esta bloqueando atendimento financeiro? Quero um panorama combinado de documentacao e financeiro.",
            "Junte documentacao administrativa e financeiro das contas vinculadas e diga se ha bloqueio de atendimento.",
            "Quero um quadro unico de documentacao e financeiro para saber se alguma pendencia esta bloqueando atendimento.",
            "Tem algo na minha documentacao ou no cadastro que esteja travando o financeiro? Me de a visao combinada.",
            "Cruze meu status documental com o financeiro e diga se existe bloqueio ou pendencia relevante.",
            "Resuma junto documentacao administrativa e financeiro das contas vinculadas para eu saber se ha impedimento de atendimento.",
        ],
    },
    {
        "category": "public_health_emergency_bundle",
        "slice": "public",
        "expected_keywords": ["medicacao", "emerg"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_health_emergency_bundle",
        "telegram_chat_id": 777229,
        "note": "public health, medication and emergencies bundle",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Como a escola conecta medicacao, saude e procedimentos de emergencia nos documentos publicos?",
            "No material publico, como ficam juntas medicacao, cuidado em saude e resposta a emergencias?",
            "Quero uma sintese publica de como medicacao, protocolo de saude e emergencia se amarram na escola.",
            "Pelos documentos publicos, como a escola organiza medicacao, acompanhamento de saude e emergencias?",
            "Como o protocolo publico da escola articula medicacao, ocorrencias de saude e situacoes de emergencia?",
            "Na base publica, como aparecem conectados medicacao escolar, cuidados de saude e procedimentos de emergencia?",
        ],
    },
    {
        "category": "public_integral_study_support",
        "slice": "public",
        "expected_keywords": ["integral", "estudo orientado"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_integral_study_support",
        "telegram_chat_id": 777230,
        "note": "public integral and study support bridge",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Como periodo integral e estudo orientado se conectam no apoio ao estudante segundo a base publica?",
            "Na documentacao publica, como a escola articula periodo integral, estudo orientado e apoio ao aluno?",
            "Quero entender como o programa integral conversa com estudo orientado e apoio escolar no material publico.",
            "Pelos documentos publicos, de que forma periodo integral e estudo orientado se reforcam no suporte ao estudante?",
            "Como a escola apresenta publicamente a relacao entre periodo integral, estudo orientado e acompanhamento do aluno?",
            "Na base publica, como aparecem juntos periodo integral, estudo orientado e apoio a rotina de estudos?",
        ],
    },
    {
        "category": "public_transport_uniform_bundle",
        "slice": "public",
        "expected_keywords": ["transporte", "uniforme"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_transport_uniform_bundle",
        "telegram_chat_id": 777231,
        "note": "public transport, food and uniform bundle",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Como transporte, alimentacao e uniforme aparecem juntos nas orientacoes publicas da escola?",
            "No material publico, como a escola organiza transporte, uniforme e refeicoes para as familias?",
            "Quero uma visao publica de transporte, alimentacao e uniforme para entender a rotina da familia.",
            "Pelos documentos publicos, como ficam amarrados transporte escolar, uniforme e alimentacao?",
            "Como a base publica explica, de forma conjunta, transporte, uniforme e alimentacao no dia a dia escolar?",
            "Na documentacao publica, como a escola apresenta transporte, uniforme e refeicoes como parte da rotina?",
        ],
    },
    {
        "category": "public_inclusion_accessibility",
        "slice": "public",
        "expected_keywords": ["inclus", "acess"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_inclusion_accessibility",
        "telegram_chat_id": 777232,
        "note": "public inclusion and accessibility policy",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Como inclusao, acessibilidade e seguranca aparecem articuladas nos documentos publicos da escola?",
            "Quero um panorama publico de inclusao, acessibilidade e seguranca institucional.",
            "Na base publica, como a escola conecta acessibilidade, inclusao e protecao do estudante?",
            "Pelos documentos publicos, como ficam juntas as politicas de inclusao, acessibilidade e seguranca?",
            "Como a escola apresenta publicamente suas orientacoes de inclusao, acessibilidade e seguranca?",
            "No material publico, como se articulam inclusao, acessibilidade e cuidado com a seguranca escolar?",
        ],
    },
    {
        "category": "public_outings_authorizations",
        "slice": "public",
        "expected_keywords": ["autoriz", "saida"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_outings_authorizations",
        "telegram_chat_id": 777233,
        "note": "public outings and authorizations",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Como saidas pedagogicas, eventos e autorizacoes aparecem conectados na base publica?",
            "No material publico, como a escola organiza saidas pedagogicas, eventos e autorizacoes das familias?",
            "Quero entender como a escola conecta eventos externos, saidas pedagogicas e autorizacoes no material publico.",
            "Pelos documentos publicos, como ficam juntos eventos, saidas pedagogicas e autorizacoes?",
            "Como a escola descreve publicamente a relacao entre saidas pedagogicas, participacao em eventos e autorizacoes?",
            "Na base publica, como se articulam eventos escolares, saidas pedagogicas e autorizacoes das familias?",
        ],
    },
    {
        "category": "public_governance_protocol",
        "slice": "public",
        "expected_keywords": ["direcao", "protocolo"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_governance_protocol",
        "telegram_chat_id": 777234,
        "note": "public governance and formal protocol routing",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Quando uma questao precisa sair da rotina, como a escola liga direcao, coordenacao e protocolo formal no material publico?",
            "Na governanca publica da escola, como demandas formais chegam a direcao e viram protocolo?",
            "Quero entender como coordenacao, direcao e protocolo se conectam quando o assunto deixa de ser rotineiro.",
            "Pelos documentos publicos, como uma familia deve escalar um tema da rotina para direcao e protocolo formal?",
            "Como a escola descreve publicamente a passagem entre coordenacao, direcao e protocolo institucional?",
            "Na base publica, como aparecem conectados direcao, atendimento formal e numero de protocolo?",
        ],
    },
    {
        "category": "public_known_unknown_total_teachers",
        "slice": "public",
        "expected_keywords": ["nao informam", "professores"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_known_unknown_total_teachers",
        "telegram_chat_id": 777235,
        "note": "public known unknown total teachers",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Quantos professores a escola tem hoje? Se isso nao estiver publicado, deixe claro.",
            "A escola informa publicamente a quantidade de professores? Se nao, me diga isso de forma direta.",
            "Nos canais publicos, aparece o numero total de professores da escola?",
            "Quero saber se a escola publica a quantidade total de professores ou se esse dado nao esta disponivel.",
            "Existe numero publico de professores na escola ou esse dado nao e informado oficialmente?",
            "A base publica mostra quantos professores a escola tem? Se nao mostrar, diga isso sem enrolar.",
        ],
    },
    {
        "category": "public_known_unknown_library_books",
        "slice": "public",
        "expected_keywords": ["nao informam", "livros"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_known_unknown_library_books",
        "telegram_chat_id": 777236,
        "note": "public known unknown library books",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "Quantos livros a biblioteca tem hoje? Se esse dado nao for publico, diga isso claramente.",
            "A escola publica a quantidade total de livros do acervo da biblioteca?",
            "Nos canais publicos, aparece o numero de livros da biblioteca ou isso nao esta informado?",
            "Quero saber se o acervo total de livros e publicado oficialmente pela escola.",
            "Existe numero publico da quantidade de livros da biblioteca?",
            "A base publica informa quantos livros ha no acervo da biblioteca ou nao?",
        ],
    },
    {
        "category": "public_known_unknown_minimum_age",
        "slice": "public",
        "expected_keywords": ["idade minima", "admissions"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_known_unknown_minimum_age",
        "telegram_chat_id": 777237,
        "note": "public known unknown minimum age",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "A escola publica uma idade minima exata para ingresso? Se nao, para onde devo ir?",
            "Existe idade minima publicada para matricular ou o canal correto e admissions?",
            "Quero saber se a escola informa idade minima exata para ingresso no material publico.",
            "Nos canais publicos, aparece uma idade minima precisa para matricula?",
            "A base publica define idade minima exata para estudar na escola ou orienta procurar admissions?",
            "Se eu quiser confirmar idade minima para ingresso, isso aparece publicamente ou depende de admissions?",
        ],
    },
    {
        "category": "public_known_unknown_cafeteria_menu",
        "slice": "public",
        "expected_keywords": ["cantina", "cardapio"],
        "forbidden_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "thread_id": "retrieval_public_known_unknown_cafeteria_menu",
        "telegram_chat_id": 777238,
        "note": "public known unknown cafeteria menu",
        "user": {"role": "anonymous", "authenticated": False, "linked_student_ids": [], "scopes": []},
        "prompts": [
            "A escola publica o cardapio detalhado da cantina? Se nao, me diga isso claramente.",
            "Existe cardapio publico da cantina ou esse detalhe nao fica publicado?",
            "Nos canais publicos, o cardapio da cantina aparece detalhado ou nao?",
            "Quero saber se a escola publica o cardapio da cantina ou se isso fica fora dos canais publicos.",
            "Ha cardapio publico da cantina na escola ou so a confirmacao de que ela existe?",
            "A base publica mostra o cardapio da cantina em detalhe ou nao chega a esse nivel?",
        ],
    },
    {
        "category": "protected_structured_attendance_family",
        "slice": "protected",
        "expected_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_attendance_panorama",
        "telegram_chat_id": 1649845499,
        "note": "protected structured attendance family summary",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Quero um panorama de frequencia dos meus filhos e quem esta mais vulneravel por faltas.",
            "Resuma a frequencia dos meus dois filhos e diga quem preocupa mais por ausencias.",
            "Entre meus filhos, quem esta mais exposto olhando faltas e frequencia? Me de um panorama.",
            "Faca um resumo de frequencia dos meus dois filhos e destaque quem inspira mais atencao por faltas.",
            "Quero comparar a situacao de frequencia dos meus filhos e saber quem esta mais vulneravel por ausencias.",
            "Me de um panorama de faltas e frequencia dos meus filhos, apontando quem exige maior atencao agora.",
        ],
    },
    {
        "category": "protected_structured_attendance_followup",
        "slice": "protected",
        "expected_keywords": ["Lucas Oliveira"],
        "forbidden_keywords": ["Ana Oliveira"],
        "thread_id": "retrieval_protected_attendance_panorama",
        "telegram_chat_id": 1649845499,
        "note": "protected attendance follow-up context retention",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Agora foque so no Lucas e diga o que mais preocupa na frequencia dele.",
            "Mantendo o contexto anterior, quero apenas o Lucas e os pontos de maior risco por faltas.",
            "Agora olhe so para o Lucas e explique onde a frequencia dele pede mais atencao.",
            "Seguindo o panorama, filtre apenas o Lucas e diga o que mais chama atencao nas faltas dele.",
            "Continuando a analise, isole o Lucas e mostre por que a frequencia dele preocupa mais ou menos.",
            "Sem repetir o quadro inteiro, recorte so o Lucas e diga o principal alerta de frequencia.",
        ],
    },
    {
        "category": "protected_structured_upcoming_assessments",
        "slice": "protected",
        "expected_keywords": ["Lucas Oliveira", "Ana Oliveira", "avali"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_upcoming_assessments",
        "telegram_chat_id": 1649845499,
        "note": "protected upcoming assessments family summary",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Quero ver as proximas avaliacoes dos meus filhos em um resumo unico.",
            "Resuma as proximas provas e avaliacoes previstas para Lucas e Ana.",
            "Me de uma visao rapida das proximas avaliacoes dos meus dois filhos.",
            "Quero um quadro unico com as proximas avaliacoes dos meus filhos.",
            "Mostre em resumo as proximas avaliacoes dos meus filhos para eu me organizar.",
            "Traga um panorama das proximas provas e entregas previstas para meus dois filhos.",
        ],
    },
    {
        "category": "protected_structured_upcoming_assessments_followup",
        "slice": "protected",
        "expected_keywords": ["Ana Oliveira"],
        "forbidden_keywords": ["Lucas Oliveira"],
        "thread_id": "retrieval_protected_upcoming_assessments",
        "telegram_chat_id": 1649845499,
        "note": "protected upcoming assessments follow-up",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Agora foque so na Ana e mostre as proximas avaliacoes dela.",
            "Mantendo o contexto, quero apenas a Ana com as proximas provas e entregas.",
            "Agora filtre so a Ana e diga as proximas avaliacoes dela.",
            "Continuando a consulta, isole a Ana e me mostre apenas as avaliacoes dela.",
            "Sem repetir o quadro inteiro, recorte so a Ana e traga as proximas avaliacoes.",
            "Agora deixe so a Ana no contexto e mostre as provas e entregas que vem pela frente.",
        ],
    },
    {
        "category": "protected_identity_linked_students",
        "slice": "protected",
        "expected_keywords": ["Lucas Oliveira", "Ana Oliveira"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_identity_linked_students",
        "telegram_chat_id": 1649845499,
        "note": "protected identity and linked students overview",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Confirme quem esta vinculado a esta conta e quais alunos eu consigo acompanhar aqui.",
            "Quero checar quais alunos estao ligados a esta conta autenticada.",
            "Quem sao exatamente os alunos vinculados ao meu acesso neste canal?",
            "Me confirme os alunos associados a esta conta para eu saber quem consigo acompanhar aqui.",
            "Quero validar os alunos vinculados ao meu acesso no Telegram.",
            "Diga claramente quais alunos estao conectados a esta conta autenticada.",
        ],
    },
    {
        "category": "protected_administrative_self_status",
        "slice": "protected",
        "expected_keywords": ["cadastro", "pend"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_administrative_self_status",
        "telegram_chat_id": 1649845499,
        "note": "protected own administrative status",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Meu proprio cadastro de responsavel tem alguma pendencia administrativa hoje?",
            "Quero saber se ha alguma pendencia no meu cadastro como responsavel.",
            "Me diga o status administrativo do meu cadastro de responsavel, incluindo pendencias.",
            "Hoje existe alguma pendencia administrativa no meu cadastro pessoal aqui na escola?",
            "Quero um resumo do meu status cadastral de responsavel e das pendencias que ainda restam.",
            "No meu proprio cadastro, ha algo pendente do ponto de vista administrativo?",
        ],
    },
    {
        "category": "restricted_doc_positive_teacher_feedback",
        "slice": "restricted",
        "expected_keywords": ["professor", "pedagog"],
        "forbidden_keywords": ["nao posso compartilhar"],
        "thread_id": "retrieval_restricted_teacher_feedback",
        "telegram_chat_id": 1649845499,
        "note": "restricted positive teacher manual on pedagogical feedback",
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
            "No manual interno do professor, o que aparece sobre comunicacao pedagogica e devolutiva ao estudante?",
            "Segundo o manual interno do professor, como a escola trata comunicacao pedagogica e feedback ao aluno?",
            "Quero o trecho interno do manual do professor sobre devolutiva pedagogica e comunicacao com o estudante.",
            "No material interno do professor, como ficam comunicacao pedagogica e devolutiva de aprendizagem?",
            "O manual interno do professor fala o que sobre feedback pedagogico ao estudante e comunicacao docente?",
            "Pelo manual interno do professor, como a escola orienta a devolutiva pedagogica ao aluno?",
        ],
    },
    {
        "category": "restricted_doc_positive_scope_protocol_variant",
        "slice": "restricted",
        "expected_keywords": ["Telegram", "escopo"],
        "forbidden_keywords": ["nao posso compartilhar"],
        "thread_id": "retrieval_restricted_scope_protocol_variant",
        "telegram_chat_id": 1649845499,
        "note": "restricted positive protocol variant for partial scope",
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
            "No protocolo interno de escopo parcial, como o Telegram deve se comportar diante de pedidos fora do escopo?",
            "Quero o trecho interno sobre limites do Telegram quando o responsavel tem escopo parcial.",
            "Segundo o protocolo interno de escopo parcial, qual e a regra do Telegram para pedidos acima do escopo autorizado?",
            "No material interno de escopo parcial, como o Telegram deve reagir a consultas fora do escopo?",
            "Pelo protocolo interno, que limite de escopo o Telegram precisa respeitar para responsavel com acesso parcial?",
            "No protocolo interno de escopo parcial, como ficam os limites de atendimento do Telegram para pedidos fora do escopo?",
        ],
    },
    {
        "category": "restricted_doc_negative_exchange_program",
        "slice": "restricted",
        "expected_keywords": ["nao encontrei", "internacional"],
        "forbidden_keywords": ["nao posso compartilhar"],
        "thread_id": "retrieval_restricted_exchange_no_match",
        "telegram_chat_id": 1649845499,
        "note": "restricted no-match exchange program",
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
            "Existe algum procedimento interno sobre intercambio internacional com hospedagem para o ensino medio?",
            "Ha documento interno sobre intercambio internacional com hospedagem envolvendo turmas do ensino medio?",
            "Nos documentos internos, existe orientacao sobre programa de intercambio internacional com hospedagem?",
            "A escola tem algum protocolo interno para intercambio internacional com hospedagem no ensino medio?",
            "Quero saber se ha material interno sobre intercambio internacional com hospedagem para alunos do ensino medio.",
            "Existe orientacao interna para intercambio internacional com hospedagem de estudantes do ensino medio?",
        ],
    },
    {
        "category": "protected_structured_grade_components",
        "slice": "protected",
        "expected_keywords": ["Ana Oliveira", "media"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_grade_components",
        "telegram_chat_id": 1649845499,
        "note": "protected sql-backed grade/component detail",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Quero as menores medias atuais da Ana e em quais componentes ela esta mais pressionada agora.",
            "Mostre as materias da Ana com menor media neste momento e onde o risco academico dela aparece mais forte.",
            "Na Ana, quais componentes estao puxando a media para baixo hoje? Quero os pontos de maior atencao.",
            "Traga as disciplinas ou componentes em que a Ana aparece com as menores medias agora.",
            "Quais sao hoje as menores medias da Ana e em que componentes isso aparece com mais clareza?",
            "Recorte a Ana e mostre onde estao as medias mais baixas dela neste momento.",
        ],
    },
    {
        "category": "protected_structured_finance_detail",
        "slice": "protected",
        "expected_keywords": ["venc", "Financeiro"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_finance_detail",
        "telegram_chat_id": 1649845499,
        "note": "protected sql-backed finance detail",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Quais cobrancas da familia estao vencidas, pagas parcialmente ou vencendo em seguida? Quero um retrato financeiro objetivo.",
            "Mostre o financeiro da familia separando o que venceu, o que foi pago em parte e o que vence logo.",
            "Quero ver quais titulos da familia estao atrasados, quais ficaram parciais e quais sao os proximos vencimentos.",
            "No financeiro da familia, separe para mim o que esta vencido, o que esta parcialmente quitado e o que vem a seguir.",
            "Traga um resumo financeiro com cobrancas vencidas, parciais e proximos vencimentos da familia.",
            "Hoje, quais cobrancas da familia estao em atraso, quais tiveram pagamento parcial e quais vencem em seguida?",
        ],
    },
    {
        "category": "protected_structured_attendance_detail",
        "slice": "protected",
        "expected_keywords": ["Lucas Oliveira", "frequencia"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_protected_attendance_detail",
        "telegram_chat_id": 1649845499,
        "note": "protected sql-backed attendance detail",
        "user": {
            "role": "guardian",
            "authenticated": True,
            "linked_student_ids": ["stu-lucas", "stu-ana"],
            "scopes": ["students:read", "administrative:read", "financial:read", "academic:read"],
        },
        "prompts": [
            "Quero um retrato das faltas do Lucas com foco em frequencia, componentes mais afetados e principal alerta atual.",
            "Mostre a situacao de frequencia do Lucas e onde as faltas dele mais pesam hoje.",
            "No Lucas, quais faltas ou ausencias mais chamam atencao agora e como isso bate na frequencia dele?",
            "Recorte so o Lucas e diga onde a frequencia dele esta mais sensivel por faltas recentes.",
            "Quero ver o ponto mais critico da frequencia do Lucas e em quais componentes as ausencias pesam mais.",
            "Hoje, qual e o principal alerta de frequencia do Lucas olhando as faltas registradas?",
        ],
    },
    {
        "category": "restricted_doc_denied_playbook",
        "slice": "restricted",
        "expected_keywords": ["nao posso compartilhar", "intern"],
        "forbidden_keywords": [],
        "thread_id": "retrieval_restricted_denied_playbook",
        "telegram_chat_id": 777239,
        "note": "restricted deny playbook without permission",
        "user": {
            "role": "anonymous",
            "authenticated": False,
            "linked_student_ids": [],
            "scopes": [],
        },
        "prompts": [
            "Quero ver o playbook interno de negociacao financeira da escola.",
            "Pode abrir para mim o playbook interno de negociacao financeira?",
            "Mostre aqui no chat o playbook interno de negociacao financeira.",
            "Sou responsavel e quero acessar o playbook interno de negociacao financeira pelo bot.",
            "Quero que voce me mostre o playbook interno de negociacao financeira agora.",
            "Preciso do playbook interno de negociacao financeira aqui no Telegram.",
        ],
    },
]


PROTECTED_SQL_CATEGORIES = {
    "protected_structured_academic",
    "protected_structured_followup",
    "protected_structured_finance",
    "protected_structured_finance_detail",
    "protected_structured_grade_components",
    "protected_structured_attendance_family",
    "protected_structured_attendance_followup",
    "protected_structured_attendance_detail",
    "protected_structured_upcoming_assessments",
    "protected_structured_upcoming_assessments_followup",
    "protected_admin_finance_combo",
}

PROTECTED_OTHER_CATEGORIES = {
    "protected_structured_admin",
    "protected_access_scope",
    "protected_identity_linked_students",
    "protected_administrative_self_status",
}

PROTECTED_SQL_DOMAIN_CATEGORIES = {
    "academic": {
        "protected_structured_academic",
        "protected_structured_followup",
        "protected_structured_grade_components",
    },
    "finance": {
        "protected_structured_finance",
        "protected_structured_finance_detail",
        "protected_admin_finance_combo",
    },
    "attendance": {
        "protected_structured_attendance_family",
        "protected_structured_attendance_followup",
        "protected_structured_attendance_detail",
        "protected_structured_upcoming_assessments",
        "protected_structured_upcoming_assessments_followup",
    },
}


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


def _selection_bucket(spec: dict[str, Any]) -> str:
    slice_name = str(spec.get("slice") or "public")
    category = str(spec.get("category") or "")
    if slice_name == "public":
        return "public"
    if slice_name == "restricted":
        return "restricted"
    if category in PROTECTED_SQL_CATEGORIES:
        return "protected_sql"
    if category in PROTECTED_OTHER_CATEGORIES:
        return "protected_other"
    return "protected_sql"


def _protected_sql_domain(spec: dict[str, Any]) -> str | None:
    category = str(spec.get("category") or "")
    for domain, categories in PROTECTED_SQL_DOMAIN_CATEGORIES.items():
        if category in categories:
            return domain
    return None


def _build_selection_units(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    index = 0
    while index < len(specs):
        start_index = index
        current = specs[index]
        thread_id = str(current.get("thread_id") or "")
        grouped = [current]
        index += 1
        while index < len(specs) and thread_id and str(specs[index].get("thread_id") or "") == thread_id:
            grouped.append(specs[index])
            index += 1
        units.append(
            {
                "thread_id": thread_id or f"unit-{start_index}",
                "bucket": _selection_bucket(current),
                "protected_sql_domain": _protected_sql_domain(current),
                "specs": grouped,
                "start_index": start_index,
                "size": len(grouped),
            }
        )
    return units


def _focus_filtered_specs(specs: list[dict[str, Any]], *, focus: str) -> list[dict[str, Any]]:
    if focus == FOCUS_ALL:
        return list(specs)
    if focus == FOCUS_PROTECTED_SQL:
        return [spec for spec in specs if _selection_bucket(spec) == "protected_sql"]
    raise ValueError(f"unsupported_focus:{focus}")


def _minimum_bucket_cases(count: int) -> dict[str, int]:
    public_min = 1 if count <= 3 else 2
    if count == 1:
        protected_sql_min = 0
    elif count <= 3:
        protected_sql_min = 1
    elif count == 4:
        protected_sql_min = 2
    elif count <= 8:
        protected_sql_min = 3
    elif count <= 14:
        protected_sql_min = 4
    else:
        protected_sql_min = 5
    minimums = {
        "public": public_min,
        "protected_sql": protected_sql_min,
        "restricted": 1 if count >= 12 else 0,
        "protected_other": 1 if count >= 16 else 0,
    }
    return minimums


def _minimum_sql_domains(count: int) -> list[str]:
    if count <= 1:
        return []
    if count <= 3:
        return ["academic"]
    if count <= 5:
        return ["academic", "finance"]
    return ["academic", "finance", "attendance"]


def _pick_unit(
    units: list[dict[str, Any]],
    *,
    remaining: int,
    max_size: int | None,
    rng: random.Random,
    prefer_follow_up: bool,
) -> dict[str, Any] | None:
    if remaining <= 0:
        return None
    size_cap = remaining if max_size is None else min(remaining, max_size)
    fitting = [unit for unit in units if int(unit["size"]) <= size_cap]
    if max_size is not None:
        pool = fitting
    else:
        pool = fitting or units
    if not pool:
        return None
    if prefer_follow_up:
        paired = [unit for unit in pool if int(unit["size"]) > 1]
        if paired:
            pool = paired
    else:
        singletons = [unit for unit in pool if int(unit["size"]) == 1]
        if singletons:
            pool = singletons
    return rng.choice(pool)


def _select_units_for_count(specs: list[dict[str, Any]], *, count: int, rng: random.Random) -> list[dict[str, Any]]:
    units = _build_selection_units(specs)
    if count > sum(int(unit["size"]) for unit in units):
        raise ValueError(
            f"Requested {count} cases, but the grouped selection units only cover "
            f"{sum(int(unit['size']) for unit in units)} cases."
        )

    by_bucket: dict[str, list[dict[str, Any]]] = {bucket: [] for bucket in ("public", "protected_sql", "restricted", "protected_other")}
    for unit in units:
        by_bucket[str(unit["bucket"])].append(unit)

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    selected_case_count = 0
    bucket_case_count = {bucket: 0 for bucket in by_bucket}
    selected_sql_domains: set[str] = set()

    def add_unit(unit: dict[str, Any]) -> None:
        nonlocal selected_case_count
        unit_id = str(unit["thread_id"])
        if unit_id in selected_ids:
            return
        selected.append(unit)
        selected_ids.add(unit_id)
        bucket_case_count[str(unit["bucket"])] += int(unit["size"])
        selected_case_count += int(unit["size"])
        sql_domain = unit.get("protected_sql_domain")
        if isinstance(sql_domain, str) and sql_domain:
            selected_sql_domains.add(sql_domain)

    sql_domain_targets = _minimum_sql_domains(count)
    for domain in sql_domain_targets:
        if domain in selected_sql_domains or selected_case_count >= count:
            continue
        remaining = count - selected_case_count
        minimums = _minimum_bucket_cases(count)
        remaining_public = max(0, int(minimums.get("public", 0)) - int(bucket_case_count["public"]))
        remaining_restricted = max(0, int(minimums.get("restricted", 0)) - int(bucket_case_count["restricted"]))
        remaining_other = max(0, int(minimums.get("protected_other", 0)) - int(bucket_case_count["protected_other"]))
        remaining_domains = sum(1 for item in sql_domain_targets if item not in selected_sql_domains and item != domain)
        unit = _pick_unit(
            [
                candidate
                for candidate in by_bucket["protected_sql"]
                if str(candidate["thread_id"]) not in selected_ids and candidate.get("protected_sql_domain") == domain
            ],
            remaining=remaining,
            max_size=max(1, remaining - (remaining_public + remaining_restricted + remaining_other + remaining_domains)),
            rng=rng,
            prefer_follow_up=True,
        )
        if unit is not None:
            add_unit(unit)

    minimums = _minimum_bucket_cases(count)
    for bucket in ("protected_sql", "public", "restricted", "protected_other"):
        while bucket_case_count[bucket] < minimums.get(bucket, 0) and selected_case_count < count:
            remaining = count - selected_case_count
            remaining_required_for_others = sum(
                max(0, int(minimums.get(other_bucket, 0)) - int(bucket_case_count[other_bucket]))
                for other_bucket in minimums
                if other_bucket != bucket
            )
            unit = _pick_unit(
                [candidate for candidate in by_bucket[bucket] if str(candidate["thread_id"]) not in selected_ids],
                remaining=remaining,
                max_size=max(1, remaining - remaining_required_for_others),
                rng=rng,
                prefer_follow_up=(bucket == "protected_sql"),
            )
            if unit is None:
                break
            add_unit(unit)

    fill_order = (
        ("public", False),
        ("protected_sql", True),
        ("restricted", False),
        ("protected_other", False),
    )
    while selected_case_count < count:
        remaining = count - selected_case_count
        picked: dict[str, Any] | None = None
        for bucket, prefer_follow_up in fill_order:
            picked = _pick_unit(
                [candidate for candidate in by_bucket[bucket] if str(candidate["thread_id"]) not in selected_ids],
                remaining=remaining,
                max_size=None,
                rng=rng,
                prefer_follow_up=prefer_follow_up,
            )
            if picked is not None:
                break
        if picked is None:
            raise ValueError("Unable to complete dataset selection with the available question units.")
        add_unit(picked)

    selected.sort(key=lambda unit: int(unit["start_index"]))
    return selected


def build_cases(
    seed: int,
    existing_prompts: set[str] | None = None,
    *,
    count: int = 20,
    focus: str = FOCUS_ALL,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    history = {prompt.strip() for prompt in (existing_prompts or set()) if prompt.strip()}
    candidate_specs = _focus_filtered_specs(QUESTION_SPECS, focus=focus)
    if count < 1:
        raise ValueError("count_must_be_positive")
    total_available_cases = len(candidate_specs)
    if count > total_available_cases:
        raise ValueError(
            f"Requested {count} cases, but only {total_available_cases} question specs are available. "
            "Add more specs before generating a larger dataset."
        )
    cases: list[dict[str, Any]] = []
    if focus == FOCUS_ALL:
        selected_units = _select_units_for_count(candidate_specs, count=count, rng=rng)
    else:
        selected_units = _build_selection_units(candidate_specs)
        selected_units.sort(key=lambda unit: int(unit["start_index"]))
        shuffled_units = list(selected_units)
        rng.shuffle(shuffled_units)
        chosen_units: list[dict[str, Any]] = []
        chosen_count = 0
        for unit in shuffled_units:
            if chosen_count + int(unit["size"]) > count:
                continue
            chosen_units.append(unit)
            chosen_count += int(unit["size"])
            if chosen_count == count:
                break
        if chosen_count != count:
            raise ValueError(
                f"Unable to satisfy count={count} with focus='{focus}' while preserving grouped thread units."
            )
        selected_units = sorted(chosen_units, key=lambda unit: int(unit["start_index"]))
    selected_specs = [spec for unit in selected_units for spec in unit["specs"]]
    if len(selected_specs) != count:
        raise ValueError(
            f"Selection logic produced {len(selected_specs)} cases for requested count={count}. "
            "Adjust bucket minimums or grouped units before generating this dataset."
        )
    for index, spec in enumerate(selected_specs, start=1):
        available_prompts = _fresh_prompt_candidates(spec, history)
        if not available_prompts:
            raise ValueError(
                f"No fresh prompt variants left for category '{spec['category']}'. "
                "Add new prompt phrasings or expand the augmentation templates before generating another retrieval probe dataset."
            )
        prompt = rng.choice(available_prompts)
        item = {key: value for key, value in spec.items() if key != "prompts"}
        item["id"] = f"Q{200 + index}"
        item["prompt"] = prompt
        cases.append(item)
        history.add(prompt)
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a fresh retrieval probe dataset for EduAssist.")
    parser.add_argument("--seed", type=int, default=20260402)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--focus",
        choices=(FOCUS_ALL, FOCUS_PROTECTED_SQL),
        default=FOCUS_ALL,
        help="Optional focus profile for selecting a narrower slice of question specs.",
    )
    parser.add_argument(
        "--datasets-dir",
        type=Path,
        default=DATASETS_DIR,
        help="Directory whose existing JSON datasets are scanned to forbid exact prompt overlap.",
    )
    args = parser.parse_args()

    existing_prompts = _collect_existing_prompts(args.datasets_dir)
    dataset = build_cases(
        seed=args.seed,
        existing_prompts=existing_prompts,
        count=int(args.count),
        focus=str(args.focus or FOCUS_ALL),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"generated {len(dataset)} cases -> {args.output} "
        f"(history_blocked={len(existing_prompts)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
