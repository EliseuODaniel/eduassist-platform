from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ShadowRunResult:
    engine_name: str
    executed: bool
    reason: str = ''
    error: str = ''
    metadata: dict[str, Any] | None = None


class ResponseEngine:
    name = 'unknown'
    ready = True

    async def respond(self, *, request: Any, settings: Any) -> Any:
        raise NotImplementedError

    async def shadow_compare(self, *, request: Any, settings: Any) -> ShadowRunResult:
        return ShadowRunResult(
            engine_name=self.name,
            executed=False,
            reason='shadow_not_supported',
        )
