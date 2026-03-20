FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

RUN pip install --upgrade pip setuptools wheel

COPY apps/api/pyproject.toml /workspace/apps/api/pyproject.toml
COPY apps/api /workspace/apps/api
COPY packages /workspace/packages
COPY ml /workspace/ml

WORKDIR /workspace/apps/api
RUN pip install -e .[dev]

ENV PYTHONPATH=/workspace/apps/api

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

