# 🧭 AKADEMİK PUSULA

<div align="center">

**Yapay Zeka Destekli Asenkron Akademik Literatür Arama & Sentez Motoru**

[![Status](https://img.shields.io/badge/Durum-Canlı-CCFF00?style=for-the-badge&logo=railway&logoColor=black)](https://akademikpusula.up.railway.app/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![AI Council](https://img.shields.io/badge/AI_Kurul-3_Model-00D2FF?style=for-the-badge&logo=openai&logoColor=white)](https://groq.com)
[![License](https://img.shields.io/badge/Lisans-MIT-white?style=for-the-badge)](LICENSE)

<br>

> *"Anahtar kelime değil, araştırma sorusu sor. Makale ara değil, bilgi sentezle."*

<br>

[![UYGULAMAYI DENEYİN](https://img.shields.io/badge/UYGULAMAYI_ŞİMDİ_DENEYİN_→-CCFF00?style=for-the-badge&logo=streamlit&logoColor=black)](https://akademikpusula.up.railway.app/)

</div>

---

## 📋 İçindekiler

- [Nedir?](#-nedir)
- [Özellikler](#-özellikler)
- [Mimari](#-mimari)
- [Veri Kaynakları](#-veri-kaynakları)
- [AI Sistemi](#-ai-sistemi)
- [Kurulum](#-kurulum)
- [Ortam Değişkenleri](#-ortam-değişkenleri)
- [Tasarım Felsefesi](#-tasarım-felsefesi)
- [Güvenlik](#-güvenlik)

---

## 🔍 Nedir?

**Akademik Pusula**, 10'dan fazla ulusal ve uluslararası akademik veri tabanını **eş zamanlı ve asenkron** olarak sorgulayan, bulunan yüzlerce makaleyi yapay zeka ile sıralayan ve kullanıcının araştırma sorusuna Perplexity benzeri **atıflı Türkçe rapor** sentezleyen bir web uygulamasıdır.

Geleneksel akademik arama motorlarının aksine:

| Geleneksel Arama | Akademik Pusula |
|---|---|
| Tek veritabanı, tek dil | 10+ veritabanı, çift dil, eş zamanlı |
| Anahtar kelime eşleştirmesi | Semantik sıralama + AI re-ranking |
| Ham sonuç listesi | 3-model AI kurul analizi |
| Manuel kaynak okuma | Tam metin otomatik çekim (6 kaynak zinciri) |
| Statik atıf kopyalama | APA 7 otomasyonu |

---

## 🚀 Özellikler

### ⚡ Paralel Asenkron Tarama
`asyncio` + `httpx`/`aiohttp` ile tüm veritabanları aynı anda sorgulanır. İlk sonuçlar saniyeler içinde gelir. En yavaş kaynak diğerlerini bekletmez.

### 🔬 Araştırma Zekası Modu
Perplexity tarzı semantik araştırma modu:
1. Kullanıcının Türkçe/İngilizce sorusu alınır
2. `llama-3.1-8b-instant` ile 3 farklı İngilizce akademik sorguya genişletilir
3. OpenAlex + Crossref'ten 60'a kadar makale paralel çekilir
4. Alaka ve kalite filtresi + heuristik sıralama uygulanır
5. 3-model AI kurul, inline `[N]` atıflı akıcı Türkçe rapor üretir
6. Yalnızca raporda gerçekten atıf yapılan kaynaklar gösterilir

### 🧠 AI Genel Kurul (Consensus Engine)
Üç farklı uzman model hiyerarşik olarak çalışır:

```
Araştırmacı (Qwen3-32B)    →  Verileri ve metodolojik detayları çıkarır
Eleştirmen (Llama-4-Scout)  →  Metodolojik zayıflıkları ve boşlukları tespit eder
Kurul Başkanı (Llama-3.3-70B) →  Nihai sentezi ve yanıtı üretir
```

### 📊 İki Aşamalı Akıllı Sıralama
- **Aşama 1 — Heuristik (sıfır API):** Tüm N sonuç puanlanır
  - Güncellik (≤2 yıl → 30 puan, ≤5 yıl → 20, ≤10 yıl → 10)
  - Başlık kelime örtüşmesi (+8/kelime, maks 40)
  - Özet kalitesi (>200 karakter → 15, >50 → 8)
  - Açık erişim bonusu (+10)
  - Atıf sayısı (≥500 → +25, ≥100 → +20, ≥20 → +12, ≥5 → +6)
- **Aşama 2 — AI re-ranking:** İlk 25 sonuç semantik olarak yeniden sıralanır

### 📄 Akıllı Tam Metin Çekim Zinciri (6 Adım)
Kilitli yayıncı duvarlarını aşmak için otomatik açık erişim yolu bulur:
```
1. arXiv HTML viewer  → bot koruması yok, her zaman çalışır
2. Unpaywall API      → DOI ile yasal OA PDF bulur
3. Semantic Scholar   → OA PDF veya zenginleştirilmiş özet
4. OpenAlex           → best_oa_location PDF veya özet yeniden inşası
5. CORE repository    → fullText alanı olan büyük OA arşivi
6. Jina r.jina.ai     → son çare (publisher engellerine takılabilir)
```

### 🌐 Çapraz Dil Arama
- Türkçe sorgu → otomatik İngilizceye çeviri → her iki dilde paralel arama
- Zaten doğru dildeki sorgular API çağrısı yapmadan geçer (karakter tabanlı tespit)

### 📤 Dışa Aktarım
- **BibTeX:** Seçili makaleler için tek tıkla `.bib` dosyası
- **APA 7:** Her makale için otomatik atıf formatı
- **Excel:** Tüm sonuçları `.xlsx` olarak indir
- **Sci-Hub / Anna's Archive:** Kilitli makaleler için otomatik yönlendirme

---

## 🏗️ Mimari

```
akademik-pusula/
│
├── app.py                          # Giriş noktası, GA4 enjeksiyonu, sayfa yönlendirmesi
│
├── views/
│   ├── search_view.py              # Ana arama ekranı ve sonuç listesi
│   ├── focus_view.py               # Makale odak modu + AI kurul sohbeti
│   ├── research_intelligence_view.py  # Araştırma Zekası (Perplexity modu)
│   └── global_chat_view.py         # Bağımsız AI danışman sohbeti
│
├── api_services/
│   ├── openalex.py                 # OpenAlex (250M+ çalışma)
│   ├── arxiv.py                    # arXiv (açık erişim)
│   ├── elsevier.py                 # ScienceDirect / Scopus
│   ├── springer.py                 # Springer Nature
│   ├── ieee.py                     # IEEE Xplore
│   ├── asme.py                     # ASME Digital Collection
│   ├── tr_dizin.py                 # TR Dizin (Türkiye)
│   └── yok_tez.py                  # YÖK Ulusal Tez Merkezi
│
├── utils/
│   ├── ai_manager.py               # Groq API, AI modelleri, tam metin zinciri
│   ├── fetcher.py                  # Paralel kaynak birleştirici
│   ├── export.py                   # BibTeX & Excel dışa aktarım
│   └── citation.py                 # APA 7 formatı
│
└── components/
    └── ui_components.py            # Makale kartları, metrikler, GA4 event'leri
```

### Veri Akışı

```
Kullanıcı Sorusu
      │
      ▼
[Dil Tespiti] ──► [Çeviri (gerekirse)] ──► [Sorgu Genişletme]
                                                    │
                    ┌───────────────────────────────┤
                    ▼                               ▼
              [API Servisleri]              [OpenAlex + Crossref]
              (paralel asyncio)             (Araştırma Zekası)
                    │                               │
                    ▼                               ▼
              [Ham Sonuçlar]               [Dedup + Filtre]
                    │                               │
                    ▼                               ▼
         [Heuristik Sıralama]          [3-Model AI Sentez]
                    │                               │
                    ▼                               ▼
         [AI Re-ranking (top 25)]      [Atıflı Türkçe Rapor]
                    │
                    ▼
             [Kullanıcı Arayüzü]
```

---

## 📚 Veri Kaynakları

| Kaynak | Kapsam | Erişim | Yıl Filtresi |
|--------|--------|--------|--------------|
| **OpenAlex** | 250M+ çalışma, global | Ücretsiz | API düzeyinde |
| **Crossref** | 150M+ DOI kaydı | Ücretsiz | API düzeyinde |
| **arXiv** | Ön baskılar (fizik, CS, mat.) | Ücretsiz | API düzeyinde |
| **Elsevier / Scopus** | ScienceDirect, 18M+ makale | API anahtarı | Sorgu düzeyinde |
| **Springer Nature** | 12M+ makale | API anahtarı | API düzeyinde |
| **IEEE Xplore** | Mühendislik & teknoloji | API anahtarı | API düzeyinde |
| **ASME** | Makine mühendisliği | Crossref üzerinden | API düzeyinde |
| **DergiPark** | Türk akademik dergiler | MCP / Ücretsiz | İstemci tarafı |
| **TR Dizin** | Türkiye atıf dizini | Crossref üzerinden | API düzeyinde |
| **YÖK Tez** | Türk lisansüstü tezler | MCP / Ücretsiz | İstemci tarafı |

---

## 🤖 AI Sistemi

### Kullanılan Modeller (Groq API)

| Model | Görev | Bağlam |
|-------|-------|--------|
| `llama-3.3-70b-versatile` | Kurul Başkanı, nihai sentez | 128K token |
| `qwen/qwen3-32b` | Araştırmacı, veri çıkarımı | 32K token |
| `meta-llama/llama-4-scout-17b-16e-instruct` | Eleştirmen, metodoloji analizi | 128K token |
| `llama-3.1-8b-instant` | Sorgu çevirisi, genişletme, re-ranking | 8K token |

### Prompt Güvenliği
Tüm kullanıcı girdileri `[USER_INPUT_START]` / `[USER_INPUT_END]` etiketleri ile izole edilir. Sistem promptlarını değiştirmeye yönelik prompt injection girişimleri her modelin sistem mesajında açıkça engellenir.

---

## 🛠️ Kurulum

### Gereksinimler
- Python 3.11+
- Groq API anahtarı (zorunlu)
- Elsevier / Springer / IEEE anahtarları (isteğe bağlı, ilgili kaynaklar için)

### Yerel Kurulum

```bash
# Repoyu klonla
git clone https://github.com/Alphyn12/akademik-pusula.git
cd akademik-pusula

# Bağımlılıkları yükle
pip install -r requirements.txt

# Streamlit secrets dosyasını oluştur
mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'EOF'
GROQ_API_KEY = "gsk_..."
ELSEVIER_API_KEY = "..."
SPRINGER_API_KEY = "..."
IEEE_API_KEY = "..."
UNPAYWALL_EMAIL = "your@email.com"
EOF

# Uygulamayı başlat
streamlit run app.py
```

### Docker ile Kurulum

```bash
# Image oluştur ve çalıştır
docker-compose up --build

# Uygulama http://localhost:8501 adresinde erişilebilir olur
```

---

## 🔑 Ortam Değişkenleri

| Değişken | Zorunlu | Açıklama |
|----------|---------|----------|
| `GROQ_API_KEY` | ✅ Evet | Tüm AI işlemleri için |
| `ELSEVIER_API_KEY` | Hayır | ScienceDirect / Scopus erişimi |
| `SPRINGER_API_KEY` | Hayır | Springer Nature erişimi |
| `IEEE_API_KEY` | Hayır | IEEE Xplore erişimi |
| `UNPAYWALL_EMAIL` | Hayır | Unpaywall politikası gereği (herhangi e-posta) |
| `OPENALEX_EMAIL` | Hayır | OpenAlex polite pool erişimi için |

> Değişkenler Railway / Streamlit Cloud ortamlarında environment variable olarak veya `.streamlit/secrets.toml` üzerinden tanımlanabilir. Uygulama her ikisini de destekler ve önce `st.secrets`, sonra `os.environ` yolunu dener.

---

## 🎨 Tasarım Felsefesi

Uygulama **Dark Neo-Brutalism** akımını benimser:

- **Tipografi:** `Anton` (başlıklar) + `Space Mono` (içerik) kombinasyonu
- **Renk Paleti:**
  - `#CCFF00` — Neon Lime (vurgu, başlıklar)
  - `#00D2FF` — Elektrik Cyan (interaktif öğeler, gölgeler)
  - `#FF6B6B` — Kırmızı (uyarı, eleştiri bölümleri)
  - `#050505` — Siyah (arka plan)
- **Stil:** Keskin köşeler, hard box-shadow (`5px 5px 0px #00D2FF`), `3px solid` sınırlar
- **İlke:** Her UI öğesi anlık okunabilir ve hiyerarşik olmalı

---

## 🔐 Güvenlik

| Tehdit | Uygulanan Önlem |
|--------|-----------------|
| **Prompt Injection** | Kullanıcı girdisi her model çağrısında `[USER_INPUT_START/END]` ile izole edilir |
| **XSS** | `html.escape()` ile tüm kullanıcı içerikleri HTML render öncesi sanitize edilir |
| **SSRF** | `fetch_full_text_jina` içinde iç ağ adreslerine (localhost, 10.x, 192.168.x) istek engeli |
| **API Key Sızıntısı** | Tüm anahtarlar `st.secrets` / `os.environ` üzerinden okunur, kod içinde sabit değer yok |
| **Bot Koruması Bypass** | HTTP 401/403/503 ve Cloudflare sayfaları tespit edilerek kullanıcıya bildirilir |

---

## 📈 Performans

- **Paralel Sorgulama:** 10 kaynak eş zamanlı — tipik toplam tarama süresi **8–15 saniye**
- **AI Kurul Analizi:** Özet üzerinden **10–20 saniye**, tam metin üzerinden **20–40 saniye**
- **Araştırma Zekası:** Sorgu genişletme + 6 paralel fetch + 3-model sentez — **30–60 saniye**
- **Heuristik Sıralama:** 200+ sonuç, **< 50ms** (sıfır API çağrısı)

---

## 🧩 Teknoloji Yığını

```
Frontend   →  Streamlit 1.31+ (Neo-Brutalist custom CSS)
AI         →  Groq API (llama-3.3-70b, qwen3-32b, llama-4-scout, llama-3.1-8b)
HTTP       →  httpx (async) + aiohttp (scraper servisleri)
HTML Parse →  BeautifulSoup4 + lxml
Analytics  →  Google Analytics 4 (root injection yöntemi)
Deploy     →  Railway (Docker container)
PWA        →  Service Worker + Web Manifest
```

---

<div align="center">

**Akademik Pusula** — Bilgiye erişimdeki teknik engelleri kaldırmak için geliştirilmiştir.

[![Railway](https://img.shields.io/badge/Deployed_on-Railway-7B2FBE?style=for-the-badge&logo=railway)](https://railway.app)
[![Made with Streamlit](https://img.shields.io/badge/Made_with-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

</div>
