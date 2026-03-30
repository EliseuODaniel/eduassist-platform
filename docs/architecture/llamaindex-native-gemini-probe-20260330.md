# LlamaIndex Native Gemini Probe

Date: 2026-03-30

Prompt:

`quais sao os diferenciais da proposta pedagogica? e como isso aparece na pratica no dia a dia? e na cultura digital?`

Runtime:

- `feature_flag_primary_orchestration_stack=llamaindex`
- `strict_framework_isolation_enabled=true`
- `.env` loaded through `python-dotenv`
- `llm_provider=google`
- `google_model=gemini-2.5-flash-preview`

Observed result:

- `reason`: `llamaindex_public_citation_query_engine`
- `graph_path`:
  - `classify_request`
  - `security_gate`
  - `route_request`
  - `select_slice`
  - `structured_tool_call`
  - `llamaindex:workflow`
  - `llamaindex:llamaindex_public_citation_query_engine`
  - `llamaindex:tool:public_retrieval`
  - `kernel:llamaindex`
- `selected_tools`:
  - `get_public_school_profile`
  - `llamaindex_selector_router`
  - `public_retrieval`

Interpretation:

- The `llamaindex` path no longer depends only on deterministic routing for this public institutional query.
- With the real `Gemini` provider configured, it exercised the native `CitationQueryEngine` path.
- This confirms that the new `llama-index-llms-google-genai` integration is active and can unlock the native `llamaindex` retrieval and synthesis path in the current environment.
