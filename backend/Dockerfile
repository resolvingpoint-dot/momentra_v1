# Momentra API — production image for Dokploy / Docker Compose.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Runtime deps for psycopg2-binary / health probes (optional curl).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app
COPY scripts/docker-entrypoint.sh scripts/docker-worker-entrypoint.sh ./scripts/

RUN chmod +x scripts/docker-entrypoint.sh scripts/docker-worker-entrypoint.sh \
    && mkdir -p .local-uploads

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT:-${API_PORT:-8000}}/health" || exit 1

ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
CMD ["api"]
