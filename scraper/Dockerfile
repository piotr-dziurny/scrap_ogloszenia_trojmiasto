FROM python:3.12.8-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /scraper

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd appuser && \
    chown -R appuser:appuser /scraper
   
USER appuser

CMD ["sh", "-c", "python3 scraper_scheduler.py"]
