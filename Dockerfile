FROM python:3

# Уставка рабочего каталога /code
WORKDIR /code

# Копирование файлов проекта
COPY ["pyproject.toml", "poetry.lock", "./"]

# Установка Poetry и зависимостей проекта
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install

# Копирование остальной части кода приложения
COPY . .