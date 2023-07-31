FROM python:3.11.4-slim
WORKDIR /projeto

# variáveis para desenvolvimento
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH /projeto

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false

# Instala apenas as dependências.
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

COPY . .
