from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _public_doc_path(filename: str) -> Path:
    return _repo_root() / "data" / "corpus" / "public" / filename


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        _, _, remainder = text.partition("\n---\n")
        return remainder
    return text


def _normalize_space(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "").strip())
    return cleaned.strip()


@lru_cache(maxsize=64)
def _load_public_doc(filename: str) -> str:
    path = _public_doc_path(filename)
    if not path.exists():
        return ""
    return _strip_frontmatter(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=64)
def _load_sections(filename: str) -> dict[str, str]:
    text = _load_public_doc(filename)
    if not text:
        return {}
    sections: dict[str, str] = {}
    current = "_intro"
    buffer: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            if buffer:
                sections[current] = _normalize_space("\n".join(buffer))
            current = _normalize_space(line.removeprefix("## ")).lower()
            buffer = []
            continue
        if line.startswith("# "):
            continue
        buffer.append(line)
    if buffer:
        sections[current] = _normalize_space("\n".join(buffer))
    return sections


def _section(filename: str, heading: str) -> str:
    return _load_sections(filename).get(_normalize_space(heading).lower(), "")


def _safe_sentence(text: str) -> str:
    normalized = _normalize_space(text)
    if not normalized:
        return ""
    if normalized.endswith("."):
        return normalized
    return f"{normalized}."


def _first_line(text: str) -> str:
    normalized = _normalize_space(text)
    if not normalized:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", normalized, maxsplit=1)
    return _safe_sentence(parts[0])


def _render_decimal(value: Any, fallback: str) -> str:
    rendered = str(value or "").strip()
    if not rendered:
        return fallback
    return rendered.replace(".", ",")


def _school_name(profile: dict[str, Any] | None) -> str:
    rendered = str((profile or {}).get("school_name") or "Colegio Horizonte").strip()
    return rendered or "Colegio Horizonte"


def _timeline_entry_from_profile(profile: dict[str, Any] | None, topic_fragment: str) -> dict[str, Any] | None:
    entries = (profile or {}).get("public_timeline") if isinstance(profile, dict) else None
    if not isinstance(entries, list):
        return None
    for item in entries:
        if not isinstance(item, dict):
            continue
        if topic_fragment in str(item.get("topic_key", "") or ""):
            return item
    return None


def _timeline_summary(entry: dict[str, Any] | None) -> str:
    if not isinstance(entry, dict):
        return ""
    return _normalize_space(
        " ".join(
            part
            for part in (
                entry.get("summary"),
                entry.get("notes"),
            )
            if str(part or "").strip()
        )
    )


def compose_public_academic_policy_overview(profile: dict[str, Any] | None) -> str | None:
    policy = (profile or {}).get("academic_policy") if isinstance(profile, dict) else None
    evaluation = _section("politica-avaliacao-recuperacao-e-promocao.md", "Avaliacao continua")
    feedback = _section("politica-avaliacao-recuperacao-e-promocao.md", "Registro e devolutiva")
    recovery = _section("politica-avaliacao-recuperacao-e-promocao.md", "Recuperacao")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    promotion = _section("politica-avaliacao-recuperacao-e-promocao.md", "Promocao e decisao final")
    if not any((evaluation, feedback, recovery, second_call, promotion)):
        return None
    passing = policy.get("passing_policy") if isinstance(policy, dict) else {}
    attendance = policy.get("attendance_policy") if isinstance(policy, dict) else {}
    average = _render_decimal(getattr(passing, "get", lambda *_: None)("passing_average"), "7,0")
    minimum_attendance = _render_decimal(getattr(attendance, "get", lambda *_: None)("minimum_attendance_percent"), "75,0")
    return " ".join(
        part
        for part in (
            "Na pratica, convivencia, frequencia, recuperacao e promocao precisam ser lidas como um mesmo fluxo academico.",
            _first_line(evaluation),
            _first_line(feedback),
            _first_line(recovery),
            _first_line(second_call),
            f"Na referencia publica atual, a escola trabalha com media {average}/10 e frequencia minima de {minimum_attendance}% por componente.",
            _first_line(promotion),
            "Primeiro a familia acompanha criterio, devolutiva e frequencia; depois usa segunda chamada e recuperacao quando houver impacto academico; e, por fim, observa a decisao final de promocao pelo canal oficial.",
        )
        if part
    ).strip()


def compose_public_policy_compare(profile: dict[str, Any] | None) -> str | None:
    manual_conduct = _section("manual-regulamentos-gerais.md", "Convivencia e respeito")
    manual_attendance = _section("manual-regulamentos-gerais.md", "Pontualidade e frequencia")
    evaluation = _section("politica-avaliacao-recuperacao-e-promocao.md", "Avaliacao continua")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    recovery = _section("politica-avaliacao-recuperacao-e-promocao.md", "Recuperacao")
    promotion = _section("politica-avaliacao-recuperacao-e-promocao.md", "Promocao e decisao final")
    policy = (profile or {}).get("academic_policy") if isinstance(profile, dict) else None
    attendance = policy.get("attendance_policy") if isinstance(policy, dict) else {}
    passing = policy.get("passing_policy") if isinstance(policy, dict) else {}
    minimum_attendance = _render_decimal(getattr(attendance, "get", lambda *_: None)("minimum_attendance_percent"), "75,0")
    average = _render_decimal(getattr(passing, "get", lambda *_: None)("passing_average"), "7,0")
    if not any((manual_conduct, manual_attendance, evaluation, second_call, recovery, promotion)):
        return None
    return " ".join(
        part
        for part in (
            "Os dois documentos se complementam, mas cumprem papeis diferentes.",
            "O manual de regulamentos gerais organiza convivencia, rotina institucional, pontualidade e frequencia da vida escolar.",
            _first_line(manual_conduct),
            _first_line(manual_attendance),
            f"Nesse plano geral, a frequencia minima publicada e de {minimum_attendance}% por componente.",
            "Ja a politica de avaliacao explica como a escola mede aprendizagem, trata segunda chamada, recuperacao e promocao.",
            _first_line(evaluation),
            _first_line(second_call),
            _first_line(recovery),
            f"Nesse plano academico, a referencia publica de media e {average}/10.",
            _first_line(promotion),
            "Na pratica, primeiro a familia usa o manual para entender combinados, frequencia e rotina; depois consulta a politica de avaliacao para segunda chamada, recuperacao e promocao; e, se restar duvida operacional, o proximo passo e confirmar isso pelo canal oficial da secretaria ou da coordenacao.",
        )
        if part
    ).strip()


def compose_public_access_scope_compare(profile: dict[str, Any] | None) -> str | None:
    school_name = _school_name(profile)
    return " ".join(
        part
        for part in (
            "Quando a pergunta compara a orientacao publica com a interna sobre acessos diferentes entre responsaveis, a mudanca principal aparece em linguagem e em acao.",
            f"Na linguagem publica do {school_name}, a escola orienta a familia por canais oficiais e evita detalhar permissao interna por perfil.",
            "Ja na orientacao interna, a linguagem fica operacional: a equipe verifica vinculo, escopo autorizado, restricao por responsavel e registro antes de seguir.",
            "Na pratica, a camada publica explica o caminho e pede confirmacao oficial; a camada interna decide quem pode acessar o que e qual setor valida excecoes ou ajustes.",
        )
        if part
    ).strip()


def compose_public_conduct_frequency_punctuality(profile: dict[str, Any] | None) -> str | None:
    manual_punctuality = _section("manual-regulamentos-gerais.md", "Pontualidade e frequencia")
    manual_conduct = _section("manual-regulamentos-gerais.md", "Convivencia e respeito")
    manual_justifications = _section("manual-regulamentos-gerais.md", "Avaliacoes e justificativas")
    policy = (profile or {}).get("academic_policy") if isinstance(profile, dict) else None
    attendance = policy.get("attendance_policy") if isinstance(policy, dict) else {}
    minimum_attendance = _render_decimal(getattr(attendance, "get", lambda *_: None)("minimum_attendance_percent"), "75,0")
    chronic = str(getattr(attendance, "get", lambda *_: None)("chronic_absence_guidance") or "").strip()
    if not any((manual_punctuality, manual_conduct, manual_justifications, chronic)):
        return None
    return " ".join(
        part
        for part in (
            "Pontualidade, frequencia e convivencia aparecem juntas nos documentos publicos da escola.",
            _first_line(manual_punctuality),
            _first_line(manual_conduct),
            _first_line(manual_justifications),
            f"A politica publica de frequencia reforca presenca minima de {minimum_attendance}% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao.",
            _first_line(chronic),
            "Na pratica, o proximo passo e justificar faltas no prazo, alinhar pontualidade e acionar a coordenacao assim que a frequencia comecar a comprometer a rotina academica.",
        )
        if part
    ).strip()


def compose_public_conduct_policy_contextual_answer(
    message: str,
    *,
    profile: dict[str, Any] | None = None,
) -> str | None:
    normalized = _normalize_space(message).lower()
    if not normalized:
        return None
    conduct_answer = compose_public_conduct_frequency_punctuality(profile)
    if not conduct_answer:
        return None
    if (
        any(term in normalized for term in ("convivencia", "convivência", "comportamento"))
        and any(term in normalized for term in ("frequencia", "frequência", "faltas", "pontualidade", "atrasos"))
    ):
        return conduct_answer
    school_name = _school_name(profile)
    concise_conduct = (
        "Na leitura publica atual, bom comportamento significa respeito mutuo, linguagem adequada, cuidado com pessoas, rotina e patrimonio; "
        "ja agressao, intimidacao, discriminacao, bullying, assedio ou uso indevido de imagem entram como ocorrencias que a escola trata com coordenacao e, se necessario, encaminhamento humano."
    )
    concise_protocol = (
        f"No {school_name}, o encaminhamento institucional passa por coordenacao, registro formal pelos canais oficiais e, em ocorrencias graves, escalonamento para a direcao."
    )
    substance_terms = (
        "maconha",
        "droga",
        "drogas",
        "entorpecente",
        "entorpecentes",
        "fumar",
        "fumo",
        "cigarro",
        "vape",
        "vapear",
        "alcool",
        "álcool",
        "bebida alcoolica",
        "bebida alcoólica",
    )
    conduct_terms = (
        "bullying",
        "assedio",
        "assédio",
        "agressao",
        "agressão",
        "intimidacao",
        "intimidação",
        "discriminacao",
        "discriminação",
        "bom comportamento",
        "mal comportamento",
        "comportamento",
        "convivencia",
        "convivência",
        "uso indevido de imagem",
        "expulsao",
        "expulsão",
        "exclusao",
        "exclusão",
        "desligamento",
        "desligar",
        "bomba",
        "explosivo",
        "explosivos",
        "seguranca",
        "segurança",
        *substance_terms,
    )
    if not any(term in normalized for term in conduct_terms):
        return None
    if any(term in normalized for term in ("expulsao", "expulsão", "exclusao", "exclusão", "desligamento")):
        return " ".join(
            part
            for part in (
                "Na base publica atual, a escola nao publica uma tabela fechada de hipoteses de expulsao, exclusao ou desligamento.",
                concise_conduct,
                concise_protocol,
            )
            if part
        ).strip()
    if any(term in normalized for term in ("bomba", "explosivo", "explosivos", "seguranca", "segurança")):
        return " ".join(
            part
            for part in (
                "Pelo material publico, condutas que colocam pessoas, patrimonio ou seguranca em risco nao sao tratadas como comportamento permitido.",
                concise_conduct,
                concise_protocol,
            )
            if part
        ).strip()
    if any(term in normalized for term in substance_terms):
        return " ".join(
            part
            for part in (
                "Na base publica atual, eu nao encontrei uma tabela fechada por substancia, mas uso, porte ou consumo de maconha, cigarro, vape, alcool ou outras substancias nao aparece como comportamento permitido no ambiente escolar.",
                concise_conduct,
                concise_protocol,
                "Se a familia precisar da regra formal exata para um caso concreto, o caminho seguro e confirmar com a coordenacao pelos canais oficiais.",
            )
            if part
        ).strip()
    if any(term in normalized for term in ("bom comportamento", "mal comportamento", "comportamento")):
        return " ".join(
            part
            for part in (
                concise_conduct,
                "Na pratica, se a familia precisar tratar um episodio concreto, o primeiro passo e acionar a coordenacao pelo canal oficial.",
            )
            if part
        ).strip()
    if any(term in normalized for term in ("procedimento", "protocolo", "permitido", "permitida", "pensa", "define", "o que acontece")):
        return " ".join(
            part
            for part in (
                concise_conduct,
                concise_protocol,
            )
            if part
        ).strip()
    return concise_conduct


def _looks_like_public_conduct_policy_query(normalized: str) -> bool:
    conduct_terms = (
        "convivencia",
        "convivência",
        "frequencia",
        "frequência",
        "pontualidade",
        "bullying",
        "assedio",
        "assédio",
        "agressao",
        "agressão",
        "intimidacao",
        "intimidação",
        "discriminacao",
        "discriminação",
        "bom comportamento",
        "mal comportamento",
        "comportamento",
        "expulsao",
        "expulsão",
        "exclusao",
        "exclusão",
        "desligamento",
        "desligar",
        "bomba",
        "explosivo",
        "explosivos",
        "seguranca",
        "segurança",
        "ocorrencia disciplinar",
        "ocorrência disciplinar",
        "maconha",
        "droga",
        "drogas",
        "entorpecente",
        "entorpecentes",
        "fumar",
        "fumo",
        "cigarro",
        "vape",
        "vapear",
        "alcool",
        "álcool",
    )
    if not any(term in normalized for term in conduct_terms):
        return False
    action_terms = (
        "regra",
        "regras",
        "manual",
        "regulamento",
        "politica",
        "política",
        "escola",
        "procedimento",
        "protocolo",
        "permitido",
        "permitida",
        "o que acontece",
        "o que gera",
        "qual e",
        "qual é",
        "como a escola",
        "como funciona",
        "quando",
        "pode levar",
        "posso",
        "pode",
        "usar",
        "levar",
        "consumir",
        "porte",
        "fumar",
    )
    return any(term in normalized for term in action_terms)


def compose_public_teacher_directory_boundary(profile: dict[str, Any] | None) -> str | None:
    school_name = _school_name(profile)
    return (
        f"O {school_name} nao divulga nome nem contato direto de professor individual por disciplina. "
        "Quando a familia precisa tratar esse tipo de assunto, o caminho publico correto e a coordenacao pedagogica, que faz a ponte institucional. "
        "Na pratica, o proximo passo e registrar a demanda pelo canal oficial da secretaria ou da coordenacao, para que a escola devolva pelo fluxo institucional."
    )


def compose_public_bolsas_and_processes(profile: dict[str, Any] | None) -> str | None:
    edital = {
        "abrangencia": _section("edital-bolsas-e-descontos-2026.md", "Abrangencia"),
        "inscricao": _section("edital-bolsas-e-descontos-2026.md", "Inscricao"),
        "analise": _section("edital-bolsas-e-descontos-2026.md", "Analise"),
        "manutencao": _section("edital-bolsas-e-descontos-2026.md", "Manutencao"),
    }
    rematricula = {
        "rematricula": _section("rematricula-transferencia-e-cancelamento-2026.md", "Rematricula interna"),
        "transfer_in": _section("rematricula-transferencia-e-cancelamento-2026.md", "Transferencia de entrada"),
        "transfer_out": _section("rematricula-transferencia-e-cancelamento-2026.md", "Transferencia de saida"),
        "cancelamento": _section("rematricula-transferencia-e-cancelamento-2026.md", "Cancelamento contratual"),
        "prazos": _section("rematricula-transferencia-e-cancelamento-2026.md", "Prazos de emissao"),
    }
    if not any((*edital.values(), *rematricula.values())):
        return None
    return " ".join(
        part
        for part in (
            "Bolsas e descontos entram como frente comercial e de concessao; rematricula, transferencia e cancelamento entram como trilhas administrativas diferentes.",
            f"Bolsas e descontos: {_first_line(edital['abrangencia'])}",
            f"Inscricao e analise: {_first_line(edital['inscricao'])}",
            _first_line(edital["analise"]),
            f"Manutencao do beneficio: {_first_line(edital['manutencao'])}",
            f"Rematricula: {_first_line(rematricula['rematricula'])}",
            f"Transferencia de entrada: {_first_line(rematricula['transfer_in'])}",
            f"Transferencia de saida: {_first_line(rematricula['transfer_out'])}",
            f"Cancelamento: {_first_line(rematricula['cancelamento'])}",
            f"Prazos e documentos: {_first_line(rematricula['prazos'])}",
        )
        if part
    ).strip()


def compose_public_health_second_call() -> str | None:
    attested = _section("protocolo-saude-medicacao-e-emergencias.md", "Atestados e justificativas")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    recovery = _section("politica-avaliacao-recuperacao-e-promocao.md", "Recuperacao")
    if not attested and not second_call and not recovery:
        return None
    return " ".join(
        part
        for part in (
            "Na documentacao publica da escola, a sequencia e direta.",
            "Primeiro passo: registrar atestado ou justificativa formal da ausencia.",
            _first_line(attested),
            "Segundo passo: com esse registro em maos, a familia solicita segunda chamada.",
            _first_line(second_call),
            "Se ainda assim o desempenho ficar abaixo da referencia, o proximo passo passa a ser a recuperacao prevista na politica academica.",
            _first_line(recovery),
        )
        if part
    ).strip()


def compose_public_permanence_and_family_support(profile: dict[str, Any] | None) -> str | None:
    support = _section("orientacao-apoio-e-vida-escolar.md", "Apoio ao estudante")
    mentoring = _section("orientacao-apoio-e-vida-escolar.md", "Reforco e monitoria")
    family = _section("orientacao-apoio-e-vida-escolar.md", "Comunicacao com responsaveis")
    attendance = _section("politica-avaliacao-recuperacao-e-promocao.md", "Frequencia minima")
    project = str((((profile or {}).get("academic_policy") or {}).get("project_of_life_summary")) or "").strip()
    if not any((support, mentoring, family, attendance, project)):
        return None
    parts = [
        "Quando o assunto e permanencia escolar com acompanhamento da familia, varios documentos publicos repetem os mesmos eixos.",
        "Os temas que mais atravessam a base publica sao acolhimento e orientacao do estudante, monitoria e apoio ao estudo, vida escolar acompanhada com a familia, frequencia como sinal de permanencia e projeto de vida como fio de acompanhamento.",
        f"Acolhimento e orientacao: {_first_line(support)}" if support else "",
        f"Monitoria e apoio: {_first_line(mentoring)}" if mentoring else "",
        f"Comunicacao com a familia: {_first_line(family)}" if family else "",
        f"Frequencia e permanencia: {_first_line(attendance)}" if attendance else "",
        f"Projeto de vida e acompanhamento: {_first_line(project)}" if project else "",
        "Na pratica, a familia usa isso em tres movimentos: primeiro acompanha rotina, frequencia e devolutivas; depois aciona monitoria, apoio ou orientacao quando surgem sinais de risco; por fim, mantem a comunicacao com a escola pelos canais institucionais para nao perder o acompanhamento.",
        "O proximo passo mais util e observar cedo faltas recorrentes, queda de rotina ou dificuldade em componentes e acionar apoio antes que o caso vire recuperacao ou risco de permanencia.",
    ]
    return " ".join(part for part in parts if part).strip()


def compose_public_health_authorizations_bridge() -> str | None:
    medication = _section("protocolo-saude-medicacao-e-emergencias.md", "Medicacao de uso eventual")
    emergencies = _section("protocolo-saude-medicacao-e-emergencias.md", "Emergencias")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    authorization = _section("saidas-pedagogicas-eventos-e-autorizacoes.md", "Autorizacao")
    restrictions = _section("saidas-pedagogicas-eventos-e-autorizacoes.md", "Restricoes")
    if not any((medication, emergencies, second_call, authorization, restrictions)):
        return None
    return " ".join(
        part
        for part in (
            _first_line(medication),
            _first_line(second_call),
            _first_line(authorization),
            _first_line(restrictions),
            _first_line(emergencies),
        )
        if part
    ).strip()


def compose_public_inclusion_accessibility() -> str | None:
    inclusion = _load_public_doc("inclusao-acessibilidade-e-seguranca.md")
    support = _section("inclusao-acessibilidade-e-seguranca.md", "Recursos de apoio")
    convivencia = _section("inclusao-acessibilidade-e-seguranca.md", "Convivencia")
    health_emergencies = _section("inclusao-acessibilidade-e-seguranca.md", "Saude e emergencias")
    if not any((inclusion, support, convivencia, health_emergencies)):
        return None
    support_line = ""
    if support:
        cleaned = _normalize_space(support).lstrip("- ").strip()
        support_line = _safe_sentence(
            f"Nos recursos de apoio, a escola cita {cleaned}"
            if cleaned
            else ""
        )
    return " ".join(
        part
        for part in (
            "A base publica trata inclusao, acessibilidade e protecao do estudante como um mesmo compromisso institucional.",
            _first_line(inclusion),
            support_line,
            _first_line(convivencia),
            _first_line(health_emergencies),
        )
        if part
    ).strip()


def compose_public_integral_study_support() -> str | None:
    structure = _section("programa-periodo-integral-e-estudo-orientado.md", "Estrutura do programa")
    guided_study = _section("programa-periodo-integral-e-estudo-orientado.md", "Estudo orientado")
    afternoon = _section("programa-periodo-integral-e-estudo-orientado.md", "Rotina da tarde")
    activities = _section("programa-periodo-integral-e-estudo-orientado.md", "Atividades complementares")
    limits = _section("programa-periodo-integral-e-estudo-orientado.md", "Limites do acompanhamento")
    if not any((structure, guided_study, afternoon, activities, limits)):
        return None
    return " ".join(
        part
        for part in (
            "Fora da sala regular, o material publico mostra que periodo integral e estudo orientado se completam como camadas de apoio ao estudante.",
            _first_line(structure),
            _first_line(guided_study),
            _first_line(afternoon),
            _first_line(activities),
            _first_line(limits),
            "Na pratica, primeiro a familia define se precisa de permanencia ampliada; depois verifica como estudo orientado, oficinas e apoio escolar entram na rotina do contraturno.",
        )
        if part
    ).strip()


def compose_public_health_emergency_bundle() -> str | None:
    health_info = _section("protocolo-saude-medicacao-e-emergencias.md", "Informacoes de saude no cadastro")
    medication_eventual = _section("protocolo-saude-medicacao-e-emergencias.md", "Medicacao de uso eventual")
    medication_continuous = _section("protocolo-saude-medicacao-e-emergencias.md", "Medicacao de uso continuo")
    malaise = _section("protocolo-saude-medicacao-e-emergencias.md", "Mal-estar durante a rotina escolar")
    emergencies = _section("protocolo-saude-medicacao-e-emergencias.md", "Emergencias")
    digital_limits = _section("protocolo-saude-medicacao-e-emergencias.md", "Limites do canal digital")
    attested = _section("protocolo-saude-medicacao-e-emergencias.md", "Atestados e justificativas")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    recovery = _section("politica-avaliacao-recuperacao-e-promocao.md", "Recuperacao")
    if not any((health_info, medication_eventual, medication_continuous, malaise, emergencies, digital_limits, attested, second_call, recovery)):
        return None
    return " ".join(
        part
        for part in (
            "No material publico, uso de medicacao, justificativa de ausencia, reorganizacao avaliativa e resposta a emergencia aparecem como partes do mesmo protocolo escolar.",
            _first_line(health_info),
            _first_line(attested),
            _first_line(medication_eventual),
            _first_line(medication_continuous),
            _first_line(malaise),
            _first_line(second_call),
            _first_line(recovery),
            _first_line(emergencies),
            _first_line(digital_limits),
        )
        if part
    ).strip()


def compose_public_outings_authorizations() -> str | None:
    purpose = _section("saidas-pedagogicas-eventos-e-autorizacoes.md", "Finalidade")
    authorization = _section("saidas-pedagogicas-eventos-e-autorizacoes.md", "Autorizacao")
    essentials = _section("saidas-pedagogicas-eventos-e-autorizacoes.md", "Informacoes essenciais")
    restrictions = _section("saidas-pedagogicas-eventos-e-autorizacoes.md", "Restricoes")
    internal_events = _section("saidas-pedagogicas-eventos-e-autorizacoes.md", "Eventos internos")
    if not any((purpose, authorization, essentials, restrictions, internal_events)):
        return None
    return " ".join(
        part
        for part in (
            "No material publico, o protocolo de saidas pedagogicas, eventos externos, viagens e autorizacao previa da familia aparece como um mesmo fluxo operacional.",
            _first_line(purpose),
            _first_line(authorization),
            _first_line(essentials),
            _first_line(restrictions),
            _first_line(internal_events),
            "Na pratica, o passo a passo publico e este: a escola comunica a atividade, a familia confere data e regras, envia a autorizacao no prazo e acompanha as orientacoes de uniforme, saida e retorno.",
        )
        if part
    ).strip()


def compose_public_transport_uniform_bundle() -> str | None:
    transport = _load_public_doc("transporte-alimentacao-uniforme.md")
    meal = _section("transporte-alimentacao-uniforme.md", "Cantina e almoco")
    restrictions = _section("transporte-alimentacao-uniforme.md", "Restricoes alimentares")
    uniform_use = _section("transporte-alimentacao-uniforme.md", "Uso")
    uniform_purchase = _section("transporte-alimentacao-uniforme.md", "Compra")
    if not any((transport, meal, restrictions, uniform_use, uniform_purchase)):
        return None
    return " ".join(
        part
        for part in (
            "Na documentacao publica da escola, transporte, uniforme e refeicoes aparecem como tres frentes da rotina diaria: deslocamento ate a escola, uso do uniforme institucional e alimentacao no periodo escolar.",
            _first_line(transport),
            _first_line(meal),
            _first_line(restrictions),
            _first_line(uniform_use),
            _first_line(uniform_purchase),
        )
        if part
    ).strip()


def compose_public_governance_protocol(profile: dict[str, Any] | None) -> str | None:
    leadership = _section("governanca-e-lideranca.md", "Estrutura de lideranca")
    family_relationship = _section("governanca-e-lideranca.md", "Relacionamento com familias")
    channels = _section("governanca-e-lideranca.md", "Canais institucionais")
    meetings = _section("governanca-e-lideranca.md", "Reunioes e acompanhamento")
    secretaria = _section("secretaria-documentacao-e-prazos.md", "Canais para documentos")
    school_name = _school_name(profile)
    if not any((leadership, family_relationship, channels, meetings, secretaria)):
        return None
    return " ".join(
        part
        for part in (
            f"Na base publica do {school_name}, a trilha institucional fica mais clara quando secretaria, coordenacao, direcao e canais oficiais aparecem como etapas complementares de encaminhamento e protocolo.",
            "Na pratica, o protocolo formal costuma seguir esta ordem: secretaria para registrar e orientar, coordenacao para acompanhar o tema pedagogico ou de convivio, e direcao como instancia de escalonamento institucional quando o assunto sai da rotina normal.",
            _first_line(secretaria),
            _first_line(leadership),
            _first_line(family_relationship),
            _first_line(channels),
            _first_line(meetings),
            "Se a familia precisar formalizar um impasse, o proximo passo e abrir o protocolo pelo canal oficial e guardar o registro para o escalonamento ate a direcao.",
        )
        if part
    ).strip()


def compose_public_secretaria_portal_credentials() -> str | None:
    documents = _section("secretaria-documentacao-e-prazos.md", "Canais para documentos")
    timelines = _section("secretaria-documentacao-e-prazos.md", "Prazos tipicos")
    declarations = _section("secretaria-documentacao-e-prazos.md", "Declaracoes e comprovantes")
    credentials = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Credenciais pessoais")
    portal = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Portal e aplicativo")
    linkage = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Vinculo com o Telegram")
    support = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Recuperacao e suporte")
    if not any((documents, timelines, declarations, credentials, portal, linkage, support)):
        return None
    return " ".join(
        part
        for part in (
            "Para documentos, portal e credenciais, a familia precisa olhar tudo como um fluxo unico e em ordem.",
            "Primeiro entram secretaria, envio de documentos e prazos tipicos da matricula ou da declaracao pedida.",
            _first_line(documents),
            _first_line(timelines),
            _first_line(declarations),
            "Depois entram portal, aplicativo e credenciais pessoais para acompanhar a rotina sem depender de atendimento manual.",
            _first_line(credentials),
            _first_line(portal),
            _first_line(linkage),
            "Se houver perda de acesso ou erro de cadastro, o proximo passo e acionar recuperacao e suporte.",
            _first_line(support),
        )
        if part
    ).strip()


def compose_public_first_month_risks(profile: dict[str, Any] | None) -> str | None:
    docs = _section("secretaria-documentacao-e-prazos.md", "Canais para documentos")
    timelines = _section("secretaria-documentacao-e-prazos.md", "Prazos tipicos")
    credentials = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Credenciais pessoais")
    linkage = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Vinculo com o Telegram")
    support = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Recuperacao e suporte")
    punctuality = _section("manual-regulamentos-gerais.md", "Pontualidade e frequencia")
    if not any((docs, timelines, credentials, linkage, support, punctuality)):
        return None
    return " ".join(
        part
        for part in (
            "No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade.",
            "Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas.",
            _first_line(docs),
            _first_line(timelines),
            _first_line(credentials),
            _first_line(linkage),
            _first_line(support),
            _first_line(punctuality),
            "Na pratica, primeiro a familia precisa regularizar documentos e credenciais; depois, manter portal, cadastro e frequencia em dia para nao desorganizar o primeiro mes.",
        )
        if part
    ).strip()


def compose_public_process_compare() -> str | None:
    rematricula = _section("rematricula-transferencia-e-cancelamento-2026.md", "Rematricula interna")
    transfer_in = _section("rematricula-transferencia-e-cancelamento-2026.md", "Transferencia de entrada")
    transfer_out = _section("rematricula-transferencia-e-cancelamento-2026.md", "Transferencia de saida")
    cancelamento = _section("rematricula-transferencia-e-cancelamento-2026.md", "Cancelamento contratual")
    prazos = _section("rematricula-transferencia-e-cancelamento-2026.md", "Prazos de emissao")
    if not any((rematricula, transfer_in, transfer_out, cancelamento, prazos)):
        return None
    return " ".join(
        part
        for part in (
            "Na pratica, rematricula, transferencia e cancelamento sao processos diferentes e cada um pede documentos, prazos e protocolo proprio.",
            f"Rematricula: {_first_line(rematricula)}",
            f"Transferencia de entrada: {_first_line(transfer_in)}",
            f"Transferencia de saida: {_first_line(transfer_out)}",
            f"Cancelamento: {_first_line(cancelamento)}",
            f"Prazos e documentos: {_first_line(prazos)}",
        )
        if part
    ).strip()


def compose_public_conduct_frequency_recovery_bridge(profile: dict[str, Any] | None) -> str | None:
    conduct = _section("manual-regulamentos-gerais.md", "Convivencia e respeito")
    punctuality = _section("manual-regulamentos-gerais.md", "Pontualidade e frequencia")
    justifications = _section("manual-regulamentos-gerais.md", "Avaliacoes e justificativas")
    recovery = _section("politica-avaliacao-recuperacao-e-promocao.md", "Recuperacao")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    support = _section("orientacao-apoio-e-vida-escolar.md", "Apoio ao estudante")
    if not any((conduct, punctuality, justifications, recovery, second_call, support)):
        return None
    return " ".join(
        part
        for part in (
            "Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar.",
            _first_line(conduct),
            _first_line(punctuality),
            _first_line(justifications),
            _first_line(second_call),
            _first_line(recovery),
            _first_line(support),
            "Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.",
            "Em termos operacionais, primeiro a familia regulariza a justificativa da ausencia, depois confere a segunda chamada e, por fim, acompanha a recuperacao prevista para o aluno.",
        )
        if part
    ).strip()


def compose_public_transversal_year_bundle() -> str | None:
    communication = _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Comunicacao com as familias")
    support = _section("orientacao-apoio-e-vida-escolar.md", "Comunicacao com responsaveis")
    study = _section("programa-periodo-integral-e-estudo-orientado.md", "Estudo orientado")
    activities = _section("programa-periodo-integral-e-estudo-orientado.md", "Atividades complementares")
    digital = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Vinculo com o Telegram")
    limits = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Limites do canal digital")
    if not any((communication, support, study, activities, digital, limits)):
        return None
    return " ".join(
        part
        for part in (
            "Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente.",
            _first_line(communication),
            _first_line(support),
            _first_line(study),
            _first_line(activities),
            _first_line(digital),
            _first_line(limits),
            "Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.",
        )
        if part
    ).strip()


def compose_public_facilities_and_study_support() -> str | None:
    library = _section("servicos-e-espacos-escolares.md", "Nome oficial e atendimento")
    library_services = _section("servicos-e-espacos-escolares.md", "Servicos disponiveis")
    science_lab = _section("servicos-e-espacos-escolares.md", "Laboratorio de ciencias")
    maker_lab = _section("servicos-e-espacos-escolares.md", "Laboratorio de informatica e sala maker")
    study = _section("programa-periodo-integral-e-estudo-orientado.md", "Estudo orientado")
    activities = _section("programa-periodo-integral-e-estudo-orientado.md", "Atividades complementares")
    if not any((library, library_services, science_lab, maker_lab, study, activities)):
        return None
    return " ".join(
        part
        for part in (
            "Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo.",
            _first_line(library),
            _first_line(library_services),
            _first_line(science_lab),
            _first_line(maker_lab),
            _first_line(study),
            _first_line(activities),
            "No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.",
            "Na pratica, biblioteca, laboratorios e estudo orientado funcionam como tres apoios complementares: pesquisa e leitura, experimentacao e producao, e organizacao da rotina de estudo.",
            "Se a necessidade principal for pesquisa, leitura ou projeto escrito, a referencia mais direta e a biblioteca. Se o foco for aula pratica, prototipo ou experimento, o caminho mais aderente sao os laboratorios. Se a duvida for organizar tarefas, leitura e habitos de estudo, o estudo orientado entra como apoio mais direto.",
        )
        if part
    ).strip()


def compose_public_calendar_visibility(profile: dict[str, Any] | None) -> str | None:
    public_events = (profile or {}).get("public_calendar_events") if isinstance(profile, dict) else None
    visible_titles: list[str] = []
    if isinstance(public_events, list):
        for item in public_events:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            if title and title not in visible_titles:
                visible_titles.append(title)
    communication = _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Comunicacao com as familias")
    digital_limits = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Limites do canal digital")
    visible_preview = ", ".join(visible_titles[:3])
    parts = []
    if visible_preview:
        parts.append(
            f"No calendario publico, o que costuma ficar aberto para familias sao marcos gerais como {visible_preview}."
        )
    else:
        parts.append(
            "No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos."
        )
    parts.append(
        "A fronteira pratica aparece assim: orientacoes abertas circulam no calendario publico, no portal institucional aberto e nos canais oficiais; o que so ganha detalhe depois do login, da autenticacao e da conta vinculada no portal sao informacoes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos."
    )
    if communication:
        parts.append(_first_line(communication))
    if digital_limits:
        parts.append(_first_line(digital_limits))
    return " ".join(part for part in parts if part).strip()


def compose_public_calendar_week(profile: dict[str, Any] | None) -> str | None:
    public_events = (profile or {}).get("public_calendar_events") if isinstance(profile, dict) else None
    visible_titles: list[str] = []
    if isinstance(public_events, list):
        for item in public_events:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            if title and title not in visible_titles:
                visible_titles.append(title)
    communication = _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Comunicacao com as familias")
    parts = [
        "No calendario publico da escola, os eventos que mais costumam importar para familias e responsaveis sao marcos coletivos e comunicados institucionais."
    ]
    if visible_titles:
        parts.append(
            f"Entre os eventos publicos mais visiveis para familias e responsaveis estao {', '.join(visible_titles[:4])}."
        )
    if communication:
        parts.append(_first_line(communication))
    parts.append(
        "Quando algum detalhe depende de turma, aluno ou ajuste fino de agenda, a comunicacao segue para responsaveis pelos canais autenticados e oficiais."
    )
    return " ".join(part for part in parts if part).strip()


def compose_public_family_new_calendar_assessment_enrollment() -> str | None:
    school_calendar = {
        "start": _section("calendario-letivo-2026.md", "Inicio das aulas"),
        "entry": _section("calendario-letivo-2026.md", "Matricula e ingresso"),
        "family": _section("calendario-letivo-2026.md", "Reunioes com responsaveis"),
    }
    assessments = {
        "regular": _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Avaliacoes regulares"),
        "recovery": _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Recuperacao paralela"),
        "communication": _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Comunicacao com as familias"),
    }
    enrollment = {
        "steps": _section("manual-matricula-ensino-medio.md", "Etapas do processo"),
        "documents": _section("manual-matricula-ensino-medio.md", "Documentos exigidos"),
        "digital": _section("manual-matricula-ensino-medio.md", "Envio digital de documentos"),
        "service": _section("manual-matricula-ensino-medio.md", "Atendimento durante a matricula"),
    }
    if not any((*school_calendar.values(), *assessments.values(), *enrollment.values())):
        return None
    return " ".join(
        part
        for part in (
            "Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares, e fazem mais sentido quando lidos em ordem.",
            "Primeiro entram matricula, documentacao inicial, envio digital e canais de atendimento.",
            "Depois entram calendario letivo e inicio das aulas, para organizar o comeco do ano.",
            "Na sequencia entram agenda de avaliacoes, devolutivas e recuperacoes, para a familia nao perder os marcos pedagogicos.",
            f"Calendario letivo: {_first_line(school_calendar['start'])}",
            f"Ingresso e marcos do ano: {_first_line(school_calendar['entry'])}",
            f"Relacao com a familia: {_first_line(school_calendar['family'])}",
            f"Agenda de avaliacoes: {_first_line(assessments['regular'])}",
            f"Recuperacao e ajustes: {_first_line(assessments['recovery'])}",
            f"Comunicacao com responsaveis: {_first_line(assessments['communication'])}",
            f"Manual de matricula: {_first_line(enrollment['steps'])}",
            f"Documentos e envio: {_first_line(enrollment['documents'])}",
            _first_line(enrollment["digital"]),
            _first_line(enrollment["service"]),
            "Na pratica, a familia usa o manual para entrar corretamente, o calendario para se orientar antes e logo depois do inicio das aulas, e a agenda para acompanhar provas, comunicados e recuperacoes.",
        )
        if part
    ).strip()


def compose_public_timeline_lifecycle_bundle() -> str | None:
    school_calendar = {
        "entry": _section("calendario-letivo-2026.md", "Matricula e ingresso"),
        "start": _section("calendario-letivo-2026.md", "Inicio das aulas"),
        "family": _section("calendario-letivo-2026.md", "Reunioes com responsaveis"),
    }
    if not any(school_calendar.values()):
        return None
    return " ".join(
        part
        for part in (
            f"1) Matricula e ingresso: {_first_line(school_calendar['entry'])}",
            f"2) Inicio das aulas: {_first_line(school_calendar['start'])}",
            f"3) Reuniao com responsaveis: {_first_line(school_calendar['family'])}",
            "Na pratica, a ordem publica do ciclo e esta: primeiro matricula e ingresso, depois inicio das aulas e, na sequencia, a reuniao inicial com as familias.",
            "Se a familia quiser se organizar sem perder marcos, o melhor uso desse fluxo e confirmar a matricula primeiro, acompanhar o inicio das aulas em seguida e deixar a reuniao com responsaveis como marco de alinhamento inicial.",
        )
        if part
    ).strip()


def compose_public_year_three_phases(profile: dict[str, Any] | None) -> str | None:
    admissions = _timeline_summary(_timeline_entry_from_profile(profile, "admissions_opening")) or _first_line(
        _section("calendario-letivo-2026.md", "Matricula e ingresso")
    )
    school_year = _timeline_summary(_timeline_entry_from_profile(profile, "school_year_start")) or _timeline_summary(
        _timeline_entry_from_profile(profile, "family_meeting")
    ) or _first_line(_section("calendario-letivo-2026.md", "Inicio das aulas"))
    graduation = _timeline_summary(_timeline_entry_from_profile(profile, "graduation")) or _timeline_summary(
        _timeline_entry_from_profile(profile, "school_year_closing")
    ) or _first_line(_section("calendario-letivo-2026.md", "Recesso e encerramento")) or _first_line(
        _section("calendario-letivo-2026.md", "Formatura do ensino fundamental II")
    )
    parts = []
    if admissions:
        parts.append(f"Admissao: {admissions}")
    if school_year:
        parts.append(f"Rotina academica: {school_year}")
    if graduation:
        parts.append(f"Fechamento: {graduation}")
    if parts:
        parts.append(
            "Na pratica, o ano aparece em tres blocos: primeiro admissao para entrada, depois rotina academica para acompanhamento continuo e, por fim, fechamento para encerramento e marcos finais."
        )
    return " ".join(parts).strip() or None


def match_public_canonical_lane(message: str) -> str | None:
    normalized = _normalize_space(message).lower()
    if not normalized:
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
        any(
            term in normalized
            for term in (
                "atividade externa",
                "atividades externas",
                "risco da atividade",
                "risco do evento",
                "risco da saida",
                "risco da saída",
                "anuencia",
                "anuência",
                "retorno",
            )
        )
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
        and any(
            term in normalized
            for term in (
                "contato",
                "telefone",
                "canal",
                "como falar",
                "como falo",
                "falar com",
                "quero falar com",
                "conversar com",
                "falar direto com",
                "falar diretamente com",
            )
        )
    ):
        return "public_bundle.teacher_directory_boundary"
    if (
        any(term in normalized for term in ("antes da confirmacao da vaga", "antes da confirmação da vaga", "depois do inicio das aulas", "depois do início das aulas"))
        or (
            any(term in normalized for term in ("sequencia", "sequência", "ordem", "linha do tempo", "passo a passo", "marcos entre"))
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
        any(term in normalized for term in ("atestado", "atestados", "justificativa", "justificativas", "saude", "saúde", "medicacao", "medicação", "comprovacao", "comprovação", "motivo de saude", "motivo de saúde"))
        and any(term in normalized for term in ("segunda chamada", "perde uma prova", "perder uma prova", "perdi uma prova", "faltar", "faltei"))
        and any(term in normalized for term in ("o que devo fazer", "onde a escola explica", "como a escola explica", "como proceder", "como devo proceder", "recuperacao", "recuperação", "avaliacao", "avaliação", "prova", "provas"))
    ):
        return "public_bundle.health_second_call"
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
        and any(term in normalized for term in ("rematricula", "transferencia", "cancelamento", "matricula"))
    ):
        return "public_bundle.bolsas_and_processes"
    if all(term in normalized for term in ("rematricula", "transferencia", "cancelamento")):
        return "public_bundle.process_compare"
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
        and any(term in normalized for term in ("frequencia", "frequência"))
        and any(term in normalized for term in ("recuperacao", "recuperação"))
    ):
        return "public_bundle.conduct_frequency_recovery"
    if (
        any(term in normalized for term in ("biblioteca", "laboratorios", "laboratórios", "laboratorio", "laboratório"))
        and any(term in normalized for term in ("estudo", "apoio", "ensino medio", "ensino médio"))
    ):
        return "public_bundle.facilities_study_support"
    return None


def compose_public_canonical_lane_answer(
    lane: str,
    *,
    profile: dict[str, Any] | None = None,
) -> str | None:
    if lane == "public_bundle.teacher_directory_boundary":
        return compose_public_teacher_directory_boundary(profile)
    if lane == "public_bundle.inclusion_accessibility":
        return compose_public_inclusion_accessibility()
    if lane == "public_bundle.integral_study_support":
        return compose_public_integral_study_support()
    if lane == "public_bundle.health_emergency_bundle":
        return compose_public_health_emergency_bundle()
    if lane == "public_bundle.outings_authorizations":
        return compose_public_outings_authorizations()
    if lane == "public_bundle.transport_uniform_bundle":
        return compose_public_transport_uniform_bundle()
    if lane == "public_bundle.governance_protocol":
        return compose_public_governance_protocol(profile)
    if lane == "public_bundle.calendar_week":
        return compose_public_calendar_week(profile)
    if lane == "public_bundle.year_three_phases":
        return compose_public_year_three_phases(profile)
    if lane == "public_bundle.academic_policy_overview":
        return compose_public_academic_policy_overview(profile)
    if lane == "public_bundle.access_scope_compare":
        return compose_public_access_scope_compare(profile)
    if lane == "public_bundle.policy_compare":
        return compose_public_policy_compare(profile)
    if lane == "public_bundle.conduct_frequency_punctuality":
        return compose_public_conduct_frequency_punctuality(profile)
    if lane == "public_bundle.family_new_calendar_assessment_enrollment":
        return compose_public_family_new_calendar_assessment_enrollment()
    if lane == "public_bundle.timeline_lifecycle":
        return compose_public_timeline_lifecycle_bundle()
    if lane == "public_bundle.visibility_boundary":
        return compose_public_calendar_visibility(profile)
    if lane == "public_bundle.permanence_family_support":
        return compose_public_permanence_and_family_support(profile)
    if lane == "public_bundle.process_compare":
        return compose_public_process_compare()
    if lane == "public_bundle.health_second_call":
        return compose_public_health_second_call()
    if lane == "public_bundle.health_authorizations_bridge":
        return compose_public_health_authorizations_bridge()
    if lane == "public_bundle.first_month_risks":
        return compose_public_first_month_risks(profile)
    if lane == "public_bundle.conduct_frequency_recovery":
        return compose_public_conduct_frequency_recovery_bridge(profile)
    if lane == "public_bundle.secretaria_portal_credentials":
        return compose_public_secretaria_portal_credentials()
    if lane == "public_bundle.bolsas_and_processes":
        return compose_public_bolsas_and_processes(profile)
    if lane == "public_bundle.transversal_year":
        return compose_public_transversal_year_bundle()
    if lane == "public_bundle.facilities_study_support":
        return compose_public_facilities_and_study_support()
    return None
