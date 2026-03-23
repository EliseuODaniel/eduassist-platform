ARG PYTHON_BASE_IMAGE=ghcr.io/astral-sh/uv:python3.12-bookworm-slim
FROM ${PYTHON_BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /workspace/apps/telegram-gateway

COPY packages/observability/python /workspace/packages/observability/python
COPY apps/telegram-gateway/pyproject.toml ./
COPY apps/telegram-gateway/uv.lock ./
COPY apps/telegram-gateway/src ./src

RUN uv sync --locked --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "telegram_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
