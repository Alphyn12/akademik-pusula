<div align="center">
  <h1>🧭 Akademik Pusula</h1>
  <p>
    <b>Yapay Zeka Destekli, Eşzamanlı (Asenkron) Akademik Literatür Arama Motoru</b>
  </p>
  <p>
    <a href="https://akademikpusula.streamlit.app/"><strong>🌐 Canlı Uygulama (Live App)</strong></a>
  </p>
</div>

---

**Akademik Pusula**, 10 farklı ulusal ve uluslararası akademik veritabanında aynı anda tarama yapmanızı, açık erişim durumlarını anında görüntülemenizi ve erişime kapalı yayınlar için Sci-Hub bypass linklerine ulaşmanızı sağlayan yapay zeka destekli, modern bir literatür arama motorudur. 

V3 sürümü ile birlikte "Monolitik" yapıdan "Modüler (Asenkron)" yapıya geçilmiş, arama hızları `asyncio` ve `aiohttp` entegrasyonu sayesinde devasa oranda arttırılmıştır.

---

## 🏆 Neden Avantajlı? (Rakiplerine Göre Farkı)

Piyasadaki standart veritabanlarına (örn. Google Scholar) veya bireysel arama motorlarına kıyasla Akademik Pusula'nın sunduğu temel avantajlar:

* ⏱️ **Hız ve Performans:** Asenkron mimarisi sayesinde her veritabanının kendi hızını beklemez; arama motorları birbirinden habersiz eşzamanlı olarak hedefe varır. Tarama hızı standart yöntemlere göre 3 kat artırılmıştır.
* 🌐 **Tek Noktadan Tüm Literatür:** Aramalarınızı tek tek sitelere (Elsevier, IEEE, DergiPark) girerek değil, aynı anda, paralel olarak yaparsınız.
* 🔓 **Benzersiz Sci-Hub Otomasyonu:** Ücretli makaleler için DOI tespiti yapar ve "Kilitli" olanları anında *Sci-Hub, Anna's Archive ve Libgen* altyapısı kullanarak açılabilir Bypass linklerine dönüştürür.
* 📋 **Otomatik APA (7. Sürüm) Referanslama:** Kaynağı bulduğunuz an, güncel APA formatındaki atıf bir tıkla kopyalanmaya hazırdır.
* 📊 **Excel/CSV Toplu Çıktı:** Onlarca sayfada çıkan akademik yayını tablo şeklinde dışa aktararak masaüstünde kendi literatür arşivinizi anında yaratabilirsiniz.

---

## 🌟 Yenilikler ve Öne Çıkan Özellikler (v3.0)

### 🤖 AI Genel Kurul Brifingi & Odak Modu
Seçtiğiniz herhangi bir makale için **"Makaleye Odaklan & AI İle Tartış"** moduna geçiş yapabilirsiniz.
- **Asenkron Llama 3 Motoru:** Makalenin özetini ve verilerini analiz edip saniyeler içinde sentezler.
- **Otomatik Brifing:** Makaleye tıkladığınız an sistem size makalenin temel amacını, yöntemlerini ve sınırlandırmalarını özetleyen genel bir brifing sunar.
- **İnteraktif Sohbet:** Makalenin metodolojisi, kullanılan materyaller veya istatistiksel verileri gibi spesifik sorularınızı doğrudan yapay zeka motoruna sorabilirsiniz.

### ⚡ Eşzamanlı (Asynchronous) Tarama Motoru
* Tüm veritabanları (OpenAlex, Crossref, arXiv, DergiPark, YÖK Tez vb.) eşzamanlı taranır. 10 veritabanı seçilse dahi en yavaş olanın yanıt süresi kadar beklenir.
* API'ler ve `aiohttp` kullanıldığı için CAPTCHA bloklarına takılmazsınız.

### 🎨 Mimari ve Tasarım
* **Neo-Brutalist Kullanıcı Arayüzü (UI):** Kontrast renkler, belirgin sınırlar ve "dark mode" odaklı agresif tasarım bileşenleri. 
* **Modüler Kod Tabanı:** Veritabanı sorguları `api_services/` klasörü altında ayrı dosyalara çıkarılarak kodun okunabilirliği ve yönetimi artırılmıştır.
* **Harici Asset Yönetimi:** Stiller `assets/` klasörüne taşınmıştır, UI elemanları `components/` klasörü üzerinden yönetilmektedir.

---

## 📚 Desteklenen Kaynaklar

Aşağıdaki platformlar asenkron olarak gerçek zamanlı bir şekilde taranmaktadır:

1.  OpenAlex (Global)
2.  Crossref
3.  arXiv
4.  DergiPark
5.  YÖK Tez / TR Üniversiteleri
6.  TR Kaynaklı / TR Dizin
7.  IEEE Xplore
8.  Elsevier (ScienceDirect/Scopus)
9.  Springer
10. ASME

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Gereksinimleri Yükleyin
Proje dizininde aşağıdaki komutu çalıştırarak gerekli Python kütüphanelerini kurun:

```bash
pip install -r requirements.txt
```

### 2. Ortam Değişkenleri (API Keys)
Projeye ait bir `.streamlit/secrets.toml` dosyası oluşturun ve içeriğindeki anahtarları kendi API Key'leriniz ile tanımlayın. AI Asistanı için bir Groq API Key edinmeniz (Llama 3 kullanımı için) gereklidir.

```toml
GROQ_API_KEY = "gsk_xxxxxx"

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

## 📂 Proje Dizin Yapısı

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
 ┃ ┣ 📜 ai_manager.py
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
Projeye dahil edilen async test altyapısı sayesinde API entegrasyonlarının stabilizasyonunu ve bağlantılarını test edebilirsiniz:

```bash
pytest tests/
```

---

## 👨‍💻 Geliştirici & Tasarım
**Geliştiren:** Barış KIRLI  
**Kurum:** Trakya Üniversitesi - Makine Mühendisliği Bölümü Öğrencisi  
**İletişim & Geri Bildirim:** [bariskirli@trakya.edu.tr](mailto:bariskirli@trakya.edu.tr)
