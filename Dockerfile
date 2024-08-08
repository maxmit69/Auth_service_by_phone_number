# Используем официальную образ Python 3.12
FROM python:3.12-slim

# Устанавливаем переменные окружения и версию Poetry
ENV POETRY_VERSION=1.4.0
ENV PYTHONUNBUFFERED=1

# Устанавливаем необходимые пакеты
RUN apt update && apt install -y curl

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

# Устанавливаем рабочий каталог
WORKDIR /app

# Копируем poetry.lock и poetry.toml в рабочий каталог
COPY pyproject.toml poetry.lock* /app/

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false && poetry install --no-root

# Копируем код
COPY . .
