FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --no-create-home app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Образ для тестов: dev-зависимости и tests/ есть только здесь.
FROM base AS test
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini pytest.ini ./
COPY tests ./tests
USER app
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]

# Рабочий образ (последний этап, собирается по умолчанию).
FROM base AS runtime
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
USER app
EXPOSE 8000
# uvicorn читает эти переменные сам. Доверяем X-Forwarded-* только потому,
# что порт 8000 не опубликован и доступен лишь nginx во внутренней сети.
ENV WEB_CONCURRENCY=2 \
    FORWARDED_ALLOW_IPS=*
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
# Миграции здесь НЕ запускаются: это отдельный сервис migrate в compose.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
