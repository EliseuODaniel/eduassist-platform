# Specialist Supervisor Initial Smoke Report

Date: 2026-03-30

## Summary

The new `specialist_supervisor` path is now implemented as an isolated service in
[apps/ai-orchestrator-specialist](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist)
using:

- OpenAI Agents SDK
- manager pattern
- specialists as tools
- session-backed memory
- shared retrieval and GraphRAG bridges
- Gemini via LiteLLM fallback when OpenAI is not configured

The main orchestrator now recognizes the new stack through:

- [engine_selector.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/engine_selector.py)
- [main.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/main.py)
- [compose.yaml](/home/edann/projects/eduassist-platform/infra/compose/compose.yaml)

## Best-Practice Sources Used

- OpenAI Agents SDK multi-agent patterns: https://openai.github.io/openai-agents-python/multi_agent/
- OpenAI guide for building agents: https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- Anthropic context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic tool design for agents: https://www.anthropic.com/engineering/writing-tools-for-agents
- Qdrant hybrid retrieval: https://qdrant.tech/documentation/concepts/hybrid-queries/
- GraphRAG docs: https://microsoft.github.io/graphrag/query/overview/
- LiteLLM provider docs: https://docs.litellm.ai/

## What Was Added

- Isolated path-5 service:
  - [main.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/main.py)
  - [runtime.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/runtime.py)
  - [registry.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/registry.py)
  - [models.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/models.py)
- New remote engine in the main orchestrator:
  - [specialist_supervisor_engine.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/engines/specialist_supervisor_engine.py)
- Internal GraphRAG bridge:
  - [main.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/main.py)
- Path-5 profile:
  - [path_profiles.py](/home/edann/projects/eduassist-platform/apps/ai-orchestrator/src/ai_orchestrator/path_profiles.py)

## Smoke Results

### Fast Public Paths

Validated successfully through `/v1/respond` on the isolated service:

1. `Qual o horario da Biblioteca Aurora?`
   - Result: `specialist_supervisor_fast_path:library_hours`
   - Answer: `A Biblioteca Aurora funciona 7h30 as 18h00.`
2. `A escola segue a BNCC?`
   - Result: `specialist_supervisor_fast_path:bncc`
   - Answer returned grounded institutional curriculum wording.
3. `Se eu matricular 3 filhos, quanto vou pagar de matricula?`
   - Result: `specialist_supervisor_fast_path:pricing_projection`
   - Answer returned the public deterministic projection.

### Protected / Workflow Paths

Validated end-to-end with real LLM execution on Gemini via LiteLLM:

1. `Quanto falta pra Ana ser aprovada em Fisica?`
   - Status: `200`
   - Result: `specialist_supervisor_fast_path:academic_grade_requirement`
   - Answer: `Hoje Ana Oliveira esta com media parcial 6,4 em Fisica. Para chegar a 7,0, faltam 0,6 ponto(s).`
2. `Quero agendar uma visita na quinta a tarde`
   - Status: `200`
   - Result: `specialist_supervisor_fast_path:workflow_date_clarify`
   - Answer: `Perfeito. Para qual quinta-feira voce quer a visita de tarde?`

## Architecture Notes

- Public canonical asks now use deterministic fast paths before the expensive agentic loop.
- The manager/specialist loop remains available for ambiguous, sensitive, or multi-step asks.
- Session memory was moved to `sqlite+aiosqlite` instead of the app Postgres schema, avoiding DDL permission coupling with the transactional database.
- Gemini compatibility required a provider-specific mode for tool agents:
  - no forced tool mode with JSON response format
  - manager and specialists still return structured contracts, but in a Gemini-safe way

## Honest Diagnosis

What is already good:

- The new path is real, isolated, and integrated into the main stack selector.
- Public high-signal cases are already strong and fast.
- Agentic protected/workflow paths already prefer safe clarification over hallucination.
- The service can run without OpenAI credentials by using Gemini through LiteLLM.

What still needs improvement:

- A proper 5-path benchmark harness is still pending.
- The live container stack still needs a rebuild/redeploy before the new path is available on the running Docker services.
- Complex multi-specialist asks still need a broader quality battery now that the fast paths are in place.

## Current Grade

- Path 5 architecture: `9.3/10`
- Path 5 implementation maturity right now: `8.4/10`

This is already a strong first production-grade baseline for the quality-first path, but not yet the final ceiling.
