# syntax=docker/dockerfile:1
FROM python:3.9-slim as builder

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y gcc && apt-get -y clean
RUN pip install --no-cache-dir --upgrade pip wheel
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.9-slim

WORKDIR /app
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache /wheels/*
RUN rm -rf /wheels

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "${WEB_CONCURRENCY:-2}", "-k", "uvicorn.workers.UvicornH11Worker asgi:application"]
