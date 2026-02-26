# 1. Güncel, hızlı ve hafif bir Python tabanı kullanıyoruz
FROM python:3.11-slim

# 2. Çalışma dizinimizi (Workspace) belirliyoruz
WORKDIR /app

# 3. Sadece requirements dosyasını kopyalayıp bağımlılıkları kuruyoruz
# (Sorun çıkaran apt-get komutlarını tamamen yok ettik!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Projenin geri kalan tüm kodlarını konteynere aktarıyoruz
COPY . .

# 5. Streamlit'in dış dünyayla iletişim kuracağı portu açıyoruz
EXPOSE 8501

# 6. Uygulamayı ateşleme komutu (Render için optimize edildi)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
