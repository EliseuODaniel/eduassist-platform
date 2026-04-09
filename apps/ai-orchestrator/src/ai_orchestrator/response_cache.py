from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from time import monotonic

_PUBLIC_RESPONSE_CACHE: dict[str, dict[str, object]] = {}


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text.lower()).strip()


def _token_set(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]{4,}", _normalize_text(value))
        if token not in {"como", "para", "quando", "onde", "quero", "apenas", "sobre", "entre"}
    }


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left & right)
    union = len(left | right)
    return intersection / union if union else 0.0


@dataclass(frozen=True)
class CachedPublicResponse:
    text: str
    cache_kind: str
    candidate_kind: str
    reason: str
    evidence_fingerprint: str = ""


def _exact_key(
    *,
    canonical_lane: str | None,
    topic: str | None,
    normalized_message: str,
    evidence_fingerprint: str | None = None,
) -> str:
    return "|".join(("public", canonical_lane or "-", topic or "-", evidence_fingerprint or "-", normalized_message))


def get_cached_public_response(
    *,
    message: str,
    canonical_lane: str | None,
    topic: str | None,
    evidence_fingerprint: str | None = None,
    semantic_threshold: float = 0.84,
) -> CachedPublicResponse | None:
    normalized_message = _normalize_text(message)
    now = monotonic()
    exact = _PUBLIC_RESPONSE_CACHE.get(_exact_key(
        canonical_lane=canonical_lane,
        topic=topic,
        evidence_fingerprint=evidence_fingerprint,
        normalized_message=normalized_message,
    ))
    if isinstance(exact, dict) and float(exact.get("expires_at", 0.0) or 0.0) > now:
        text = str(exact.get("text", "") or "").strip()
        if text:
            return CachedPublicResponse(
                text=text,
                cache_kind="exact",
                candidate_kind=str(exact.get("candidate_kind", "") or ""),
                reason=str(exact.get("reason", "") or ""),
                evidence_fingerprint=str(exact.get("evidence_fingerprint", "") or ""),
            )
    message_tokens = _token_set(message)
    for entry in list(_PUBLIC_RESPONSE_CACHE.values()):
        if not isinstance(entry, dict):
            continue
        if float(entry.get("expires_at", 0.0) or 0.0) <= now:
            continue
        if str(entry.get("canonical_lane", "") or "") != str(canonical_lane or ""):
            continue
        if str(entry.get("topic", "") or "") != str(topic or ""):
            continue
        if evidence_fingerprint and str(entry.get("evidence_fingerprint", "") or "") != str(evidence_fingerprint):
            continue
        cached_tokens = set(entry.get("tokens", set()) or set())
        if _jaccard(message_tokens, cached_tokens) < semantic_threshold:
            continue
        text = str(entry.get("text", "") or "").strip()
        if text:
            return CachedPublicResponse(
                text=text,
                cache_kind="semantic",
                candidate_kind=str(entry.get("candidate_kind", "") or ""),
                reason=str(entry.get("reason", "") or ""),
                evidence_fingerprint=str(entry.get("evidence_fingerprint", "") or ""),
            )
    return None


def store_cached_public_response(
    *,
    message: str,
    text: str,
    canonical_lane: str | None,
    topic: str | None,
    evidence_fingerprint: str | None,
    candidate_kind: str,
    reason: str,
    ttl_seconds: float,
) -> None:
    cleaned = str(text or "").strip()
    if not cleaned:
        return
    normalized_message = _normalize_text(message)
    _PUBLIC_RESPONSE_CACHE[_exact_key(
        canonical_lane=canonical_lane,
        topic=topic,
        evidence_fingerprint=evidence_fingerprint,
        normalized_message=normalized_message,
    )] = {
        "text": cleaned,
        "canonical_lane": str(canonical_lane or ""),
        "topic": str(topic or ""),
        "evidence_fingerprint": str(evidence_fingerprint or ""),
        "candidate_kind": candidate_kind,
        "reason": reason,
        "tokens": _token_set(message),
        "expires_at": monotonic() + max(1.0, float(ttl_seconds or 300.0)),
    }
