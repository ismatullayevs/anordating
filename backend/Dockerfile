FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM builder AS builder-dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --dev

# Multi-stage build

FROM python:3.13-alpine AS dev
WORKDIR /app
RUN addgroup -g 1000 appuser && \
    adduser -u 1000 -G appuser -s /bin/sh -D appuser
USER appuser
COPY --from=builder-dev --chown=appuser:appuser /app /app
ENV PATH="/app/.venv/bin:$PATH"
RUN pybabel compile -d shared/locales -D messages
CMD ["sh", "-c", "alembic upgrade head && python3 main.py"]


FROM python:3.13-alpine AS prod
WORKDIR /app
RUN addgroup -g 1000 appuser && \
    adduser -u 1000 -G appuser -s /bin/sh -D appuser
USER appuser
COPY --from=builder --chown=appuser:appuser /app /app
ENV PATH="/app/.venv/bin:$PATH"
RUN pybabel compile -d shared/locales -D messages
CMD ["sh", "-c", "alembic upgrade head && python3 main.py"]

