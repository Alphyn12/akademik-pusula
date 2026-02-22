<p align="center">
  <img src="Adsız.png" alt="Akademik Pusula Logo" width="300" />
</p>

# Akademik Pusula 🧭 v3.0

Akademik Pusula, 10 farklı akademik veritabanında aynı anda tarama yapmanızı, açık erişim durumlarını anında görüntülemenizi ve Sci-Hub bypass linklerine ulaşmanızı sağlayan yapay zeka destekli, modern bir arama motorudur. 

V3 sürümü ile birlikte "Monolitik" yapıdan "Modüler (Asenkron)" yapıya geçilmiş, arama hızları `asyncio` ve `aiohttp` entegrasyonu sayesinde büyük oranda arttırılmıştır.

---

## 🔥 Yenilikler (v3.0)

- 🚀 **Asenkron Tarama:** Tüm veritabanları eşzamanlı taranır. 10 veritabanı seçilse dahi en yavaş olanın yanıt süresi kadar beklenir.
- 🧩 **Modüler Mimari:** Veritabanı sorguları `api_services/` klasörü altında ayrı dosyalara çıkarılarak kodun yönetilebilirliği artırılmıştır.
- 💾 **Dışa Aktarma:** Bulunan tüm makaleleri **CSV**, **Excel** ve **BibTeX** formatlarında indirebilme imkanı eklendi.
- 📝 **APA 7 Referanslama:** Tüm kaynaklardan alınan sonuçlar otomatik olarak APA 7 standardına göre formatlanıp, kullanıcıya tek tıkla kopyalayabileceği bir arayüzle sunulur.
- 🎨 **Harici Asset Yönetimi:** Stiller `assets/` klasörüne taşınmıştır, UI elemanları `components/` klasörü üzerinden yönetilmektedir.

---

## 📚 Desteklenen Kaynaklar

> Aşağıdaki platformlar asenkron olarak gerçek zamanlı bir şekilde taranmaktadır.

1. **Google Scholar**
2. **Crossref**
3. **arXiv**
4. **DergiPark**
5. **YÖK Tez / TR Üniversiteleri**
6. **TR Kaynaklı / TR Dizin**
7. **IEEE Xplore**
8. **Elsevier (ScienceDirect/Scopus)**
9. **Springer**
10. **ASME**

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Gereksinimleri Yükleyin
Proje dizininde aşağıdaki komutu çalıştırarak gerekli Python kütüphanelerini kurun:

```bash
pip install -r requirements.txt
```

### 2. Ortam Değişkenleri (API Keys)
Projenin `.streamlit/secrets.toml.example` dosyasının adını `secrets.toml` olarak değiştirin ve içeriğindeki anahtarları (IEEE, Elsevier vb. kullanacaksanız) kendi API key'leriniz ile güncelleyin:

```toml
[ieee]
api_key = "YOUR_API_KEY"

[elsevier]
api_key = "YOUR_API_KEY"

[springer]
api_key = "YOUR_API_KEY"
```

### 3. Uygulamayı Başlatın
```bash
streamlit run app.py
```

---

## 📂 Proje Dizini

```text
📦 Akademik-Pusula
 ┣ 📂 api_services
 ┃ ┣ 📜 arxiv.py
 ┃ ┣ 📜 asme.py
 ┃ ┣ 📜 crossref.py
 ┃ ┣ 📜 dergipark.py
 ┃ ┣ 📜 elsevier.py
 ┃ ┣ 📜 ieee.py
 ┃ ┣ 📜 scholar.py
 ┃ ┣ 📜 springer.py
 ┃ ┣ 📜 tr_dizin.py
 ┃ ┗ 📜 yok_tez.py
 ┣ 📂 assets
 ┃ ┗ 📜 style.css
 ┣ 📂 components
 ┃ ┗ 📜 ui_components.py
 ┣ 📂 tests
 ┃ ┗ 📜 test_api_services.py
 ┣ 📂 utils
 ┃ ┣ 📜 citation.py
 ┃ ┣ 📜 export.py
 ┃ ┣ 📜 fetcher.py
 ┃ ┣ 📜 logger.py
 ┃ ┗ 📜 scraper_base.py
 ┣ 📜 app.py
 ┣ 📜 requirements.txt
 ┗ 📜 README.md
```

---

## 🧪 Test Etme
Projeye dahil edilen async test altyapısı sayesinde API entegrasyonlarının çalışıp çalışmadığını kontrol edebilirsiniz:

```bash
pytest tests/
```
