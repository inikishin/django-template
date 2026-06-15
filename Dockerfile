FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run as a non-root user; it owns /app so migrate/collectstatic and the sqlite file can write.
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/src

ENTRYPOINT ["/entrypoint.sh"]
# Shell form so ${PORT} is expanded at runtime (defaults to 8000).
CMD gunicorn app.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
