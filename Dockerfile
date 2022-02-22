FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

CMD alembic upgrade head && uvicorn web:app --port 8000 --host 0.0.0.0
