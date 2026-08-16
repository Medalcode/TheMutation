FROM python:3.11-slim AS builder

WORKDIR /app

# Hatchling necesita el paquete presente para construir; se instala no-editable
# y sin extras de desarrollo
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
		PYTHONPATH=/app

# Create non-root user
RUN useradd --create-home --home-dir /home/appuser --shell /bin/bash appuser || true

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Fix permissions
RUN chown -R appuser:appuser /app /home/appuser

USER appuser

EXPOSE 8000

# python:3.11-slim no incluye curl; el healthcheck usa Python directamente
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
