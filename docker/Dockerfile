# syntax=docker/dockerfile:1

# Stage 1: Build dependencies
FROM python:3.11-slim AS build
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
RUN set -eux; apt-get update; apt-get install -y \
    gcc libpq-dev libssl-dev libffi-dev curl; apt-get clean; rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt
COPY app/ ./app
COPY templates/ ./templates

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5; apt-get clean; rm -rf /var/lib/apt/lists/*
RUN groupadd --system appgroup \
 && useradd --system --gid appgroup --no-create-home appuser
COPY --from=build /usr/local/lib/python3.*/site-packages/ /usr/local/lib/python3.*/site-packages/
COPY --from=build /app /app
RUN chown -R appuser:appgroup /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
