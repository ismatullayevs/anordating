FROM python:3.11-slim as base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

FROM base as development
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN pip install --no-cache-dir pytest pytest-asyncio pytest-cov ipython

FROM base as production
ENV PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir gunicorn
