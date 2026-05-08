FROM python:3.11-slim

# Instalamos ffmpeg + dependencias para psycopg2 (base de datos)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    ca-certificates \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["python", "main.py"]