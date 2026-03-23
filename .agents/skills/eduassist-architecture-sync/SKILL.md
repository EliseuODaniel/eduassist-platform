---
name: eduassist-architecture-sync
description: Use when changing the product plan, architecture, security model, data model, AI strategy, Codex workflow, or any cross-cutting decision in eduassist-platform. Keep the planning documents aligned and consult the OpenAI developer docs MCP whenever the task touches OpenAI, Codex, MCP, AGENTS.md, skills, or subagents.
---

# EduAssist Architecture Sync

## Purpose

Keep the platform planning artifacts synchronized whenever a cross-cutting architectural decision changes.

## Use this skill when

- the PRD changes;
- the architecture changes;
- the security or access model changes;
- the data model changes;
- the AI provider, orchestration model, or retrieval strategy changes;
- the team changes how Codex, MCP, AGENTS.md, skills, or custom agents are used in the repository.

## Required document sync

Review and update, when relevant:

- `README.md`
- `docs/prd/product-requirements.md`
- `docs/architecture/system-architecture.md`
- `docs/architecture/service-catalog.md`
- `docs/security/security-architecture.md`
- `docs/security/access-control-matrix.md`
- `docs/data/data-model.md`
- `docs/operations/local-development.md`
- `docs/operations/codex-workflow.md`
- `docs/research/ai-technology-review.md`
- `docs/roadmap/implementation-roadmap.md`
- `docs/article/refactor-outline.md`

## Workflow

1. Identify which architectural decision changed.
2. Determine which docs are now stale.
3. Update the source-of-truth documents in the same task.
4. If the change touches OpenAI or Codex usage, consult the OpenAI developer docs MCP first.
5. Keep runtime design and developer-workflow design clearly separated.
6. Preserve provider abstraction even when adding OpenAI-specific guidance.

## Guardrails

- Do not let development tooling choices leak into runtime architecture unintentionally.
- Do not let AI convenience features weaken authorization or auditability.
- Do not leave the README or roadmap stale after architecture changes.

