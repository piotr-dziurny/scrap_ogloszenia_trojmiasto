FROM python:3.12.8-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /frontend

# copy requirements first to cache dependencies
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . . 

RUN useradd appuser && \
    chown -R appuser:appuser /frontend

USER appuser

# idk matplotlib needs this:
ENV MPLCONFIGDIR=/tmp/matplotlib

CMD ["sh", "-c", "python3 main.py"]
