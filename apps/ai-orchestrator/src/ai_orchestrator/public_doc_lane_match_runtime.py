from __future__ import annotations

# ruff: noqa: F401,F403,F405

LOCAL_EXTRACTED_NAMES = {'match_public_canonical_lane'}

from . import public_doc_knowledge as _native
from .public_act_rules_runtime import _is_leadership_specific_query


def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value


def match_public_canonical_lane(message: str) -> str | None:
    _refresh_native_namespace()
    normalized = _normalize_space(message).lower()
    if not normalized:
        return None
    # Leadership-specific public contact queries should stay on the structured
    # profile directory path instead of being swallowed by bundle heuristics.
    if _is_leadership_specific_query(message):
        return None
    if (
        any(term in normalized for term in ("compare", "comparar", "comparacao", "comparação"))
        and any(term in normalized for term in ("publica", "pública", "interna"))
        and any(term in normalized for term in ("acessos", "acesso", "responsaveis", "responsáveis"))
    ):
        return "public_bundle.access_scope_compare"
    if (
        any(term in normalized for term in ("compare", "comparar", "comparacao", "comparação"))
        and any(term in normalized for term in ("manual de regulamentos", "manual geral", "regulamentos gerais"))
        and any(term in normalized for term in ("politica de avaliacao", "política de avaliação", "avaliacao e promocao", "avaliação e promoção"))
    ):
        return "public_bundle.policy_compare"
    if (
        any(term in normalized for term in ("inclus", "acessib"))
        and any(
            term in normalized
            for term in ("acolh", "prote", "seguran", "compromisso institucional", "necessidades especificas", "necessidades específicas")
        )
    ):
        return "public_bundle.inclusion_accessibility"
    if (
        any(
            term in normalized
            for term in (
                "necessidades especificas",
                "necessidades específicas",
                "mediacao de rotina",
                "mediação de rotina",
                "rede de apoio",
                "equilibrio entre apoio",
                "equilíbrio entre apoio",
            )
        )
        and any(term in normalized for term in ("seguran", "acolh", "prote", "acessib", "inclus"))
    ):
        return "public_bundle.inclusion_accessibility"
    if (
        any(term in normalized for term in ("periodo integral", "período integral", "integral"))
        and any(term in normalized for term in ("estudo orientado", "apoio ao estudo", "suporte ao aluno", "alem da sala", "além da sala"))
    ):
        return "public_bundle.integral_study_support"
    if (
        any(term in normalized for term in ("turno estendido", "contraturno", "jornada estendida", "tempo estendido"))
        and any(term in normalized for term in ("estudo guiado", "estudo orientado", "apoio ao estudo", "apoio fora da sala", "desenho"))
    ):
        return "public_bundle.integral_study_support"
    if (
        sum(
            1
            for term in ("turno estendido", "contraturno", "oficinas", "refeicao", "refeição", "permanencia", "permanência", "estudo acompanhado")
            if term in normalized
        )
        >= 3
        and any(term in normalized for term in ("rotina", "arquitetura", "jornada", "ecossistema", "permanencia no contraturno", "permanência no contraturno"))
    ):
        return "public_bundle.integral_study_support"
    if (
        any(term in normalized for term in ("medicacao", "medicação", "saude", "saúde"))
        and any(term in normalized for term in ("emerg", "mal-estar", "mal estar", "monitoramento"))
        and not (
            any(term in normalized for term in ("atestado", "atestados", "justificativa", "justificativas"))
            and any(term in normalized for term in ("segunda chamada", "segunda", "chamada"))
            and any(term in normalized for term in ("recuperacao", "recuperação", "avaliacao", "avaliação", "perde uma avaliacao", "perde uma avaliação"))
        )
    ):
        return "public_bundle.health_emergency_bundle"
    if (
        any(term in normalized for term in ("saude", "saúde", "atestado", "reorganiz", "reorganização"))
        and any(term in normalized for term in ("avali", "devolut", "recuper", "rotina escolar", "recompos"))
        and not (
            any(term in normalized for term in ("segunda chamada", "segunda", "chamada"))
            and any(term in normalized for term in ("recuperacao", "recuperação", "avaliacao", "avaliação", "perde uma avaliacao", "perde uma avaliação"))
        )
    ):
        return "public_bundle.health_emergency_bundle"
    if (
        any(term in normalized for term in ("saida", "saída", "eventos externos", "saidas pedagogicas", "saídas pedagógicas"))
        and any(term in normalized for term in ("autoriz", "familias", "famílias", "previa", "prévia"))
    ):
        return "public_bundle.outings_authorizations"
    if (
        any(term in normalized for term in ("atividade externa", "atividades externas", "risco", "anuencia", "anuência", "retorno"))
        and any(term in normalized for term in ("autoriz", "saude", "saúde", "impedimento", "familia", "família"))
    ):
        return "public_bundle.outings_authorizations"
    if (
        any(term in normalized for term in ("transporte", "uniforme"))
        and any(term in normalized for term in ("alimentacao", "alimentação", "cantina", "almoco", "almoço", "refeicoes", "refeições", "rotina fora da sala", "rotina"))
    ):
        return "public_bundle.transport_uniform_bundle"
    if (
        any(term in normalized for term in ("deslocamento", "refeicao", "refeição", "refeicoes", "refeições", "identificacao", "identificação", "itens institucionais"))
        and any(
            term in normalized
            for term in ("rotina", "entrada", "saida", "saída", "uniforme", "transporte", "cotidiano fora da aula", "experiencia operacional", "experiência operacional", "uso diario", "uso diário")
        )
    ):
        return "public_bundle.transport_uniform_bundle"
    if (
        any(term in normalized for term in ("direcao", "direção"))
        and any(term in normalized for term in ("coordenacao", "coordenação", "cotidiano", "assunto foge", "assunto sair do cotidiano"))
        and any(term in normalized for term in ("protocolo", "formal"))
    ):
        return "public_bundle.governance_protocol"
    if (
        any(term in normalized for term in ("lideranca maior", "liderança maior", "escalonamento", "escala de autoridade", "autoridade institucional"))
        and any(term in normalized for term in ("impasse", "rotina normal", "encaminhamento", "coordenacao", "coordenação", "direcao", "direção"))
    ):
        return "public_bundle.governance_protocol"
    if (
        any(term in normalized for term in ("governanca", "governança"))
        and any(term in normalized for term in ("demanda formal", "demandas formais", "demanda", "demandas"))
        and any(term in normalized for term in ("direcao", "direção"))
        and any(term in normalized for term in ("protocolo", "viram protocolo", "vira protocolo"))
    ):
        return "public_bundle.governance_protocol"
    if (
        sum(
            1
            for term in ("secretaria", "coordenacao", "coordenação", "direcao", "direção", "canais oficiais", "trilha institucional", "tema caminha", "escalonamento")
            if term in normalized
        )
        >= 3
    ):
        return "public_bundle.governance_protocol"
    if (
        any(term in normalized for term in ("professor", "professora", "docente"))
        and any(term in normalized for term in ("contato", "telefone", "canal", "como falar", "como falo"))
    ):
        return "public_bundle.teacher_directory_boundary"
    if (
        any(term in normalized for term in ("antes da confirmacao da vaga", "antes da confirmação da vaga", "depois do inicio das aulas", "depois do início das aulas"))
        or (
            any(term in normalized for term in ("sequencia", "sequência", "ordem", "linha do tempo", "passo a passo", "marcos entre", "qual vem primeiro", "o que vem primeiro", "vem primeiro"))
            and any(term in normalized for term in ("vaga", "matricula", "matrícula"))
            and any(term in normalized for term in ("inicio das aulas", "início das aulas", "ano letivo", "aulas"))
            and any(term in normalized for term in ("responsaveis", "responsáveis", "reuniao", "reunião", "familia", "família"))
        )
    ):
        return "public_bundle.timeline_lifecycle"
    if (
        any(
            term in normalized
            for term in (
                "responsaveis",
                "responsáveis",
                "responsavel",
                "responsável",
                "familia",
                "família",
                "comunicacao com responsaveis",
                "comunicação com responsáveis",
            )
        )
        and any(
            term in normalized
            for term in (
                "avaliacoes",
                "avaliações",
                "avaliacao",
                "avaliação",
                "agenda avaliativa",
                "agenda de avaliacoes",
                "agenda de avaliações",
            )
        )
        and any(
            term in normalized
            for term in (
                "estudo orientado",
                "canais digitais",
                "portal",
                "telegram",
                "digitais",
                "meios digitais",
                "meios oficiais",
                "canais oficiais",
                "comunicacao digital",
                "comunicação digital",
            )
        )
    ):
        return "public_bundle.transversal_year"
    if (
        any(term in normalized for term in ("calendario publico", "calendário público", "calendario", "calendário", "agenda", "eventos"))
        and any(term in normalized for term in ("familias", "famílias", "responsaveis", "responsáveis"))
        and any(
            term in normalized
            for term in (
                "desta semana",
                "esta semana",
                "importantes",
                "mais importantes",
                "mais relevantes",
                "prioritarios",
                "prioritários",
                "visiveis",
                "visíveis",
                "marcos",
                "falam mais diretamente",
                "mais diretamente",
                "principais",
                "publicos",
                "públicos",
            )
        )
    ):
        return "public_bundle.calendar_week"
    if (
        any(
            term in normalized
            for term in (
                "atestado",
                "atestados",
                "justificativa",
                "justificativas",
                "comprovacao",
                "comprovação",
                "saude",
                "saúde",
                "medicacao",
                "medicação",
                "motivo de saude",
                "motivo de saúde",
            )
        )
        and any(
            term in normalized
            for term in (
                "segunda chamada",
                "perde uma prova",
                "perder uma prova",
                "perdi uma prova",
                "faltar",
                "faltei",
            )
        )
        and any(
            term in normalized
            for term in (
                "o que devo fazer",
                "onde a escola explica",
                "como a escola explica",
                "como proceder",
                "como devo proceder",
                "avaliacao",
                "avaliação",
                "prova",
                "provas",
                "recuperacao",
                "recuperação",
            )
        )
    ):
        return "public_bundle.health_second_call"
    if (
        ("tres fases" in normalized and all(term in normalized for term in ("admiss", "rotina", "fechamento")))
        or (
            all(term in normalized for term in ("admiss", "rotina academica", "fechamento"))
            and any(term in normalized for term in ("distribui", "distribui entre", "olhando so a base publica", "olhando apenas a base publica"))
        )
        or (
            all(term in normalized for term in ("admiss", "rotina academica", "fechamento"))
            and any(term in normalized for term in ("jornada completa", "ano escolar", "documentacao publica", "documentação pública", "segundo a documentacao publica", "se eu dividir o ano", "dividir o ano"))
        )
    ):
        return "public_bundle.year_three_phases"
    if (
        any(term in normalized for term in ("politica de avaliacao", "política de avaliação", "recuperacao", "recuperação", "promocao", "promoção"))
        and any(term in normalized for term in ("escola", "manual", "criterios", "critérios", "media", "média", "frequencia", "frequência"))
    ):
        return "public_bundle.academic_policy_overview"
    if (
        any(term in normalized for term in ("documentos publicos", "documentos públicos", "base publica", "base pública", "material publico", "material público"))
        and any(term in normalized for term in ("convivencia", "convivência", "frequencia", "frequência"))
        and any(term in normalized for term in ("recuperacao", "recuperação", "segunda chamada", "avaliacao", "avaliação"))
    ):
        return "public_bundle.academic_policy_overview"
    if _looks_like_public_conduct_policy_query(normalized):
        return "public_bundle.conduct_frequency_punctuality"

    family_entry_terms = (
        "familia nova",
        "família nova",
        "familia entrando agora",
        "família entrando agora",
        "familia entrando este ano",
        "família entrando este ano",
        "familia chegando agora",
        "família chegando agora",
        "primeira vez",
        "vai entrar este ano",
        "vai entrar pela primeira vez",
        "entrando agora",
        "chegando agora",
        "casa que esta entrando",
        "casa que está entrando",
        "casa entrando",
        "casa entrando agora",
        "primeiro filho",
        "primeiro bimestre",
        "inicio do ano",
        "início do ano",
        "comeco das aulas",
        "começo das aulas",
    )
    if (
        any(term in normalized for term in family_entry_terms)
        and any(
            term in normalized
            for term in (
                "calendario",
                "calendário",
                "inicio do ano",
                "início do ano",
                "inicio das aulas",
                "início das aulas",
                "comeco do ano",
                "começo do ano",
                "primeiro bimestre",
            )
        )
        and (
            (
                any(term in normalized for term in ("avaliacao", "avaliações", "avaliacoes"))
                and "matricula" in normalized
            )
            or (
                any(
                    term in normalized
                    for term in ("portal", "secretaria", "documentos", "documentacao", "documentação", "credenciais")
                )
                and any(
                    term in normalized
                    for term in ("matricula", "matrícula", "inicio das aulas", "início das aulas", "comeco das aulas", "começo das aulas")
                )
            )
        )
    ):
        return "public_bundle.family_new_calendar_assessment_enrollment"
    if (
        any(term in normalized for term in ("entrada", "encontros com responsaveis", "encontros com responsáveis", "devolutivas", "recomposicao academica", "recomposição acadêmica"))
        and any(term in normalized for term in ("familia", "família", "tempo", "arquitetura do tempo", "ano"))
        and any(term in normalized for term in ("avali", "reunioes", "reuniões", "rotina", "responsaveis", "responsáveis"))
    ):
        return "public_bundle.family_new_calendar_assessment_enrollment"
    has_visibility_channel = any(
        term in normalized
        for term in ("canais digitais", "canais da escola", "portal", "calendario", "calendário", "canais oficiais")
    )
    has_public_visibility = any(
        term in normalized
        for term in ("publico", "público", "publica", "pública", "conteudo publico", "conteúdo público", "aberto", "aberta")
    )
    has_auth_visibility = any(
        term in normalized
        for term in (
            "autenticacao",
            "autenticação",
            "autenticado",
            "autenticada",
            "login",
            "senha",
            "depende de autenticacao",
            "depende de autenticação",
            "so aparece depois",
            "só aparece depois",
        )
    )
    if (
        has_visibility_channel
        and (
            (has_public_visibility and has_auth_visibility)
            or any(
                term in normalized
                for term in ("fronteira", "limite", "o que fica publico", "o que e publico", "onde termina", "onde comeca", "onde começa")
            )
        )
    ):
        return "public_bundle.visibility_boundary"
    family_terms = (
        "familia",
        "família",
        "responsaveis",
        "responsáveis",
        "acompanhamento da familia",
        "acompanhamento da família",
        "acompanhe",
    )
    permanence_terms = (
        "permanencia",
        "permanência",
        "permanencia escolar",
        "permanência escolar",
        "vida escolar",
        "apoio",
        "orientacao",
        "orientação",
    )
    finance_terms = (
        "financeiro",
        "pagamentos",
        "boleto",
        "boletos",
        "fatura",
        "faturas",
        "vencimento",
        "vencimentos",
        "atraso",
        "atrasos",
        "desconto",
        "descontos",
        "mensalidade",
        "taxa",
    )
    if (
        any(term in normalized for term in family_terms)
        and any(term in normalized for term in permanence_terms)
        and not any(term in normalized for term in finance_terms)
    ):
        return "public_bundle.permanence_family_support"
    if (
        any(term in normalized for term in ("bolsas", "bolsa", "descontos", "desconto"))
        and any(term in normalized for term in ("rematricula", "rematrícula", "transferencia", "transferência", "cancelamento", "matricula", "matrícula"))
    ):
        return "public_bundle.bolsas_and_processes"
    if (
        any(term in normalized for term in ("rematricula", "rematrícula"))
        and any(term in normalized for term in ("transferencia", "transferência"))
        and "cancelamento" in normalized
    ):
        return "public_bundle.process_compare"
    if (
        any(
            term in normalized
            for term in (
                "atestado",
                "atestados",
                "justificativa",
                "justificativas",
                "comprovacao",
                "comprovação",
                "saude",
                "saúde",
                "medicacao",
                "medicação",
            )
        )
        and any(term in normalized for term in ("segunda chamada", "segunda", "chamada"))
        and any(
            term in normalized
            for term in (
                "recuperacao",
                "recuperação",
                "avaliacao",
                "avaliação",
                "prova",
                "provas",
                "perde uma avaliacao",
                "perde uma avaliação",
                "perde uma prova",
                "perder uma prova",
            )
        )
    ):
        return "public_bundle.health_second_call"
    if (
        any(term in normalized for term in ("autorizacao", "autorização", "saidas", "saídas"))
        and any(term in normalized for term in ("saude", "saúde", "medicacao", "medicação"))
    ):
        return "public_bundle.health_authorizations_bridge"
    if (
        any(
            term in normalized
            for term in (
                "primeiro mes",
                "primeiro mês",
                "comeco do ano",
                "começo do ano",
                "primeiras semanas",
                "arranque do ano",
                "arranque do ano letivo",
                "inicio do ano letivo",
                "início do ano letivo",
            )
        )
        and any(
            term in normalized
            for term in (
                "prazo",
                "prazos",
                "credenciais",
                "documentos",
                "papelada",
                "deslizes",
                "descuidos",
                "erros",
                "problema",
                "problemas",
                "comprometem",
                "baguncam",
                "bagunçam",
                "explodem",
                "explodir",
            )
        )
        and any(term in normalized for term in ("credenciais", "documentos", "documentacao", "documentação", "rotina", "papelada"))
    ):
        return "public_bundle.first_month_risks"
    if (
        any(term in normalized for term in ("secretaria", "portal", "credenciais", "login", "senha"))
        and any(term in normalized for term in ("documentos", "documentacao", "documentação", "envio"))
    ):
        return "public_bundle.secretaria_portal_credentials"
    if (
        any(term in normalized for term in ("disciplina", "disciplinar", "regulamentos", "regulamento", "convivencia", "convivência"))
        and any(term in normalized for term in ("frequencia", "frequência", "faltas", "falta", "ausencias", "ausências"))
        and any(term in normalized for term in ("recuperacao", "recuperação"))
    ):
        return "public_bundle.conduct_frequency_recovery"
    if (
        any(term in normalized for term in ("biblioteca", "laboratorios", "laboratórios", "laboratorio", "laboratório"))
        and any(term in normalized for term in ("estudo", "apoio", "ensino medio", "ensino médio"))
    ):
        return "public_bundle.facilities_study_support"
    return None
