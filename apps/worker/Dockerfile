ARG PYTHON_BASE_IMAGE=ghcr.io/astral-sh/uv:python3.12-bookworm-slim
FROM ${PYTHON_BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /workspace/apps/worker

COPY apps/worker/pyproject.toml ./
COPY apps/worker/uv.lock ./
COPY apps/worker/src ./src
COPY data/corpus /workspace/data/corpus

RUN uv sync --locked --no-dev

CMD ["uv", "run", "python", "-m", "worker_app.main"]
