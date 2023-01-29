FROM python:3.11-slim

ARG LOG_LEVEL=debug

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.3.0 \
    APP_HOME=/app

WORKDIR $APP_HOME

COPY poetry.lock pyproject.toml ${APP_HOME}/

RUN apt-get update -y && \
    apt-get install -y \
    python-dev \
    build-essential && \
    apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install "poetry==${POETRY_VERSION}" --no-cache-dir && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

COPY . ./

CMD ["uvicorn", "src.main:app", "--host=0.0.0.0", "--port=8080", "--no-use-colors", "--log-level=info", "--no-access-log"]
