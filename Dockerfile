FROM python:3.9-slim

WORKDIR /app

# Sistem paketlerini güncelle
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python paketlerini güncelle
RUN pip install --upgrade pip setuptools wheel

# Requirements'ı kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

EXPOSE 8000

CMD ["python", "run.py"]