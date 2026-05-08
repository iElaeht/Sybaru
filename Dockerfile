# Usamos una imagen ligera de Python
FROM python:3.13-slim

# Instalamos FFmpeg y herramientas básicas del sistema
# Eliminamos la limpieza de caché al final para reducir el tamaño
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos primero los requerimientos para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código del bot
COPY . .

# Exponemos el puerto que usará FastAPI (Render lo mapeará automáticamente)
EXPOSE 10000

# Comando para arrancar el bot usando el main.py modificado
CMD ["python", "main.py"]