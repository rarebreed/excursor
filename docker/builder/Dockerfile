FROM python:3.11

ENV PATH="/.local/bin:/root/.local/bin:$PATH" POETRY_CONFIG_DIR="/root/.config" \
    POETRY_CACHE_DIR="/root/.cache/pypoetry" POETRY_DATA_DIR="/root/.local/share/pypoetry"

RUN mkdir /.local /.pip /.cache /mount /app  && \
    chmod -R 667 /.local && \
    chmod -R 667 /.pip && \
    chmod -R 667 /.cache && \
    pip install -U pip && \
    pip install pipx && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    pipx install virtualenv

CMD ["poetry", "-V"]