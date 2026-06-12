# Stage 1: Builder

FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime

FROM python:3.11-slim AS runtime

# Create non-root user

RUN useradd -m appuser

WORKDIR /app

# Copy dependencies from builder

COPY --from=builder /root/.local /home/appuser/.local

# Copy application code

COPY app/ ./app/

# Environment

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PORT=8000

# Permissions

RUN chown -R appuser:appuser /app

USER appuser

# Healthcheck

HEALTHCHECK NONE

# Start FastAPI

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
