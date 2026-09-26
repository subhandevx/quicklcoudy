FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home --uid 1000 appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /data/uploads /data/outputs \
    && chown -R appuser:appuser /app /data

USER appuser

ENV PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    REDIS_URL=redis://redis:6379/0

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
