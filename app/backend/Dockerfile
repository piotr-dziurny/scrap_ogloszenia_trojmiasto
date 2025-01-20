FROM python:3.12.8-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /backend

# copy requirements first to cache dependencies
COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY database.py main.py .

RUN useradd appuser && \
    chown -R appuser:appuser /backend

USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
