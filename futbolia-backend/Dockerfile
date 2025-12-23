# syntax=docker/dockerfile:1

# ===========================================
# FutbolIA Backend - Dockerfile OPTIMIZADO
# Build time reducido con uv package manager
# ===========================================

# ---------------------------------------------
# Stage 1: Builder (instala dependencias)
# ---------------------------------------------
FROM python:3.13-slim AS builder

WORKDIR /app

# Instalar uv (gestor de paquetes ultra-rápido)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Build dependencies (solo las necesarias)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY pyproject.toml uv.lock* ./

# Instalar dependencias con caché
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/root/.cache/pip \
    uv venv .venv && \
    uv sync --frozen --no-dev --no-install-project || \
    uv sync --no-dev --no-install-project

# Verificar instalación
RUN .venv/bin/python -c "import uvicorn; print('uvicorn ok')"
RUN .venv/bin/python -c "import fastapi; print('fastapi ok')"

# ---------------------------------------------
# Stage 2: Production (imagen final mínima)
# ---------------------------------------------
FROM python:3.13-slim AS production

# Metadata
LABEL maintainer="FutbolIA Team"
LABEL description="FutbolIA Backend - API de predicciones de fútbol con IA Dixie"
LABEL version="1.0.0"

# Crear usuario NO-root ANTES de copiar archivos
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# Runtime dependencies mínimas
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Crear directorios con permisos correctos ANTES de copiar
RUN mkdir -p /app/data/chromadb /app/logs && \
    chown -R appuser:appuser /app

# Copiar .venv directamente (sin chown recursivo)
COPY --from=builder /app/.venv /app/.venv

# Copiar código de la aplicación con permisos correctos
COPY --chown=appuser:appuser . ./

# Variables de entorno
ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=production \
    CHROMADB_PATH=/app/data/chromadb \
    LOG_LEVEL=INFO

# Cambiar a usuario no-root
USER appuser

# Puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Comando de inicio (CORREGIDO: src.main:app)
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
