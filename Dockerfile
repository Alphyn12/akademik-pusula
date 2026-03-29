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

# 5. Güvenlik: Root yetkisiyle çalışmayı önlemek için non-root kullanıcı oluştur
# (Least Privilege prensibi — container escape riskini azaltır)
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# 6. Streamlit'in dış dünyayla iletişim kuracağı portu açıyoruz
EXPOSE 8501

# 7. Uygulamayı ateşleme komutu (Render için optimize edildi)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
