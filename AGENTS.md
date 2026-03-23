# AGENTS.md

## Purpose

This repository is the source of truth for planning, architecture, implementation, and operational guidance for `eduassist-platform`.

The project is security-sensitive by design. Treat any work that touches identity, authorization, student data, financial data, or AI tool access as high-risk and architecture-significant.

## Default working rules

- Keep the planning documents synchronized with implementation decisions.
- If a change affects architecture, also review `README.md`, the PRD, architecture, security, data, roadmap, and article-refactor docs.
- Prefer small, explicit contracts over implicit behavior.
- Prefer deterministic services for protected data and use AI only for reasoning, orchestration, retrieval, and response composition.
- Never introduce direct model-to-database access.
- Keep tool surfaces narrow and auditable.

## OpenAI and Codex guidance

Always use the OpenAI developer documentation MCP server if you need to work with the OpenAI API, ChatGPT Apps SDK, Codex, MCP, AGENTS.md, skills, or subagents without me having to explicitly ask.

When OpenAI is the chosen runtime provider for a feature:

- prefer the `Responses API` for tool-using and agentic workflows;
- prefer official OpenAI docs over secondary material;
- record any OpenAI-specific architectural decision in the documentation set;
- keep provider abstraction boundaries intact so the runtime can still be benchmarked against alternatives.

## Project-specific documentation sync

When changing any of these areas, update the paired documents in the same task:

- architecture -> `docs/architecture/*`
- security and access -> `docs/security/*`
- domain/data -> `docs/data/*`
- product scope -> `docs/prd/*`
- implementation sequencing -> `docs/roadmap/*`
- Codex/OpenAI workflow -> `docs/operations/codex-workflow.md`

## Skills

Use the project skill `eduassist-architecture-sync` when the task involves:

- architecture updates
- planning changes
- security model changes
- AI stack changes
- cross-document synchronization

## Custom agents

Project-scoped custom agents are available for focused work:

- `docs_researcher`: read-only research using the OpenAI docs MCP
- `security_reviewer`: read-only review focused on correctness, exposure risk, authorization, and missing safeguards

Use custom agents narrowly. Keep them read-only unless there is a strong reason not to.

