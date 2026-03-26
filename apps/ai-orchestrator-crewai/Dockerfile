ARG PYTHON_BASE_IMAGE=ghcr.io/astral-sh/uv:python3.12-bookworm-slim
FROM ${PYTHON_BASE_IMAGE}

WORKDIR /workspace/apps/ai-orchestrator-crewai

COPY apps/ai-orchestrator-crewai/pyproject.toml ./
COPY apps/ai-orchestrator-crewai/src ./src

RUN uv sync --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "ai_orchestrator_crewai.main:app", "--host", "0.0.0.0", "--port", "8000"]
