# Resmi Python imajını temel al
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# İşletim sistemi seviyesindeki bağımlılıkları yükle (isteğe bağlı, gerekirse build-essential vs eklenebilir)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Gereksinimler dosyasını konteynere kopyala
COPY requirements.txt .

# Python paketlerini yükle
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını konteynere kopyala
COPY . .

# Streamlit varsayılan portu expose et
EXPOSE 8501

# Streamlit uygulamasını çalıştır
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
