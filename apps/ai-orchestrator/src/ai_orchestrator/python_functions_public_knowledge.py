from __future__ import annotations

import re
from typing import Any

from .public_doc_knowledge import (
    compose_public_canonical_lane_answer as _shared_compose_public_canonical_lane_answer,
    compose_public_conduct_frequency_punctuality,
    match_public_canonical_lane as _shared_match_public_canonical_lane,
)


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip()).strip()


def _school_name(profile: dict[str, Any] | None) -> str:
    rendered = str((profile or {}).get("school_name") or "Colegio Horizonte").strip()
    return rendered or "Colegio Horizonte"


def match_public_canonical_lane(message: str) -> str | None:
    return _shared_match_public_canonical_lane(message)


def compose_public_canonical_lane_answer(
    lane: str,
    *,
    profile: dict[str, Any] | None = None,
) -> str | None:
    return _shared_compose_public_canonical_lane_answer(lane, profile=profile)


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
        "Na leitura publica atual, bom comportamento significa respeito mutuo, linguagem adequada, "
        "cuidado com pessoas, rotina e patrimonio; ja agressao, intimidacao, discriminacao, bullying, "
        "assedio ou uso indevido de imagem entram como ocorrencias que a escola trata com coordenacao "
        "e, se necessario, encaminhamento humano."
    )
    concise_protocol = (
        f"No {school_name}, o encaminhamento institucional passa por coordenacao, registro formal "
        "pelos canais oficiais e, em ocorrencias graves, escalonamento para a direcao."
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
        "bomba",
        "explosivo",
        "explosivos",
        "seguranca",
        "segurança",
        *substance_terms,
    )
    if not any(term in normalized for term in conduct_terms):
        return None
    if any(term in normalized for term in ("expulsao", "expulsão", "exclusao", "exclusão")):
        return " ".join(
            part
            for part in (
                "Na base publica atual, a escola nao publica uma tabela fechada de hipoteses de expulsao ou exclusao.",
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
    if any(term in normalized for term in ("procedimento", "protocolo", "permitido", "pensa", "define", "o que acontece")):
        return " ".join(part for part in (concise_conduct, concise_protocol) if part).strip()
    return concise_conduct
