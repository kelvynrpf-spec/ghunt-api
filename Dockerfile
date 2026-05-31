FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clona o GHunt
RUN git clone https://github.com/mxrch/GHunt.git /app/ghunt

# Instala dependências Python
RUN pip install --no-cache-dir flask flask-cors gunicorn requests

WORKDIR /app/ghunt
RUN pip install --no-cache-dir -r requirements.txt

# Copia API server
COPY api_server.py /app/api_server.py

WORKDIR /app

EXPOSE 5000

CMD ["gunicorn", "api_server:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]
