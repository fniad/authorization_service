FROM python:3

# Уставка рабочего каталога /code
WORKDIR /code

RUN pip install poetry && \
    poetry config virtualenvs.create false

# Копирование файлов проекта
COPY ["pyproject.toml", "poetry.lock", "./"]

# Установка Poetry и зависимостей проекта
RUN poetry install

# Копирование остальной части кода приложения
COPY . .
