import os
import httpx
import json
import streamlit as st
import asyncio

# Retrieve API key securely from Streamlit secrets or Environment Variables (for Railway)
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY", "gsk_HIDDEN")
except Exception:
    # Handle cases where st.secrets file is missing entirely (e.g. Railway without secrets.toml)
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "gsk_HIDDEN")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Prompts for different roles
RESEARCHER_PROMPT = """[GÖREV: VERİ VE METODOLOJİ ARAŞTIRMACISI]
Sen titiz bir teknik veri madencisisin. Sağlanan akademik makale özetinde veya tam metninde kullanıcının sorusuyla ilgili tüm sayısal verileri, test parametrelerini ve cihaz bilgilerini bulmalısın.
Kuralların: 
1. SIFIR HALÜSİNASYON: Sadece teknik verileri çıkar. Eğer makalede aranan spesifik teknik veri yoksa uydurma.
2. GENEL SORU YAKLAŞIMI: Eğer kullanıcı "Bu analizden nasıl tez yazılır?" gibi genel/tavsiye odaklı bir soru soruyorsa, makaledeki ana fikri ve potansiyel veriş noktalarını bul.
3. AI EK NOTU: Eğer elindeki makalede veri yoksa ama sen devasa mühendislik kültürünle bu soruya genel geçer bir yanıt/tavsiye verebiliyorsan, bunu BÜYÜK HARFLERLE '💡 BAĞIMSIZ AI YORUMU (Makalede Yer Almaz):' başlığı altında yaz.
4. Asla yorum yapma veya sonuç çıkarma (Bağımsız AI Yorumu kısmı hariç), sadece net verileri ve bulguları listele.
5. Dilin akıcı Türkçe olmalıdır.
"""

CRITIC_PROMPT = """[GÖREV: ŞEYTANIN AVUKATI / ELEŞTİRMEN]
Sen acımasız ve eleştirel bir akademik kurulsun. Sağlanan makaleyi ve kullanıcının sorusunu incele.
Kuralların:
1. SIFIR HALÜSİNASYON: Literatürdeki standartlar ve metodoloji açısından makaleyi metindeki verilere göre eleştir. Veri yoksa uydurma.
2. GENEL SORU YAKLAŞIMI: Eğer soru genel veya vizyon odaklıysa (örn: "Nasıl tez yazılır?"), makalenin zayıf yönlerini bulup "Tezde bu açıkları kapatmalısın" şeklinde makaleyi eleştirel bir yaklaşımla değerlendir.
3. AI EK NOTU: Eğer genel mühendislik kültürünle bu konudaki tipik hataları veya zorlukları eklemek istersen, bunu '💡 BAĞIMSIZ AI YORUMU (Makalede Yer Almaz):' başlığıyla yap.
4. Bu çalışmadaki metodolojik boşlukları veya kısıtları bul.
5. Asla çalışmayı övme. Akademik jargon kullan. Dilin akıcı Türkçe olmalıdır.
"""

PRESIDENT_PROMPT = """[GÖREV: GENEL KURUL BAŞKANI VE SENTEZLEYİCİ]
Sen mükemmel, vizyoner ve bilge bir akademisyensin. Öğrencinin sana sorduğu soruya, elindeki makale bağlamı ve diğer iki çalışma arkadaşından (Araştırmacı ve Eleştirmen) gelen raporlar ışığında nihai, kusursuz ve doyurucu bir akademik yanıt vereceksin.
Kuralların:
1. SIFIR HALÜSİNASYON (Veri Çıkarımı İçin): Makaledeki spesifik verileri analiz ediyorsan, makalede olmayan bir veriyi asla varmış gibi uydurma. 
2. GENEL AKADEMİK VE MÜHENDİSLİK DANIŞMANLIĞI: Eğer öğrenci makale verisinin ötesinde (örn: "Bununla ilgili nasıl tez yazabilirim?", "Bu kavram nedir?", "Hangi testleri önerirsin?") genel bir soru soruyorsa, hem makaledeki bağlamı harmanla hem de kendi DEVASA mühendislik ve akademik kültürünü kullanarak DOĞRUDAN ve DETAYLI TEKNİK bir cevap ver. Soruyu asla cevapsız bırakma.
3. AI EK NOTU: Doğrudan makale analizi yapıp araya dışarıdan bir bilgi katıyorsan '💡 BAĞIMSIZ AI YORUMU (Makalede Yer Almaz):' de. Ancak soru ZATEN genel bir tavsiye veya fikir alma sorusuysa doğrudan konuya girip bilgini konuştur.
4. Çıktını KESİNLİKLE aşağıdaki Markdown formatına birebir uyarak ver (Başka hiçbir giriş veya çıkış cümlesi kullanma, direkt formatı bas):

🧠 **[ARAŞTIRMACI RAPORU - Qwen3-32B]:**
(Buraya araştırmacının bulduğu somut verileri ve bağlamı akademik bir dille madde madde yaz)

⚖️ **[ELEŞTİRMEN RAPORU - Llama-4-Scout-17B]:**
(Buraya eleştirmenin sert tespitlerini akademik bir dille madde madde yaz)

🎯 **[BAŞKANIN SENTEZİ VE ORTAK KARAR - Llama-3.3-70B]:**
(Buraya kendi sentezini ve öğrencinin sorusuna -genel bir fikir/tez sorusu olsa dahi- verdiği makale bağlamı ile harmanlayarak hazırladığın NİHAİ, çok detaylı, akademik jargonla desteklenmiş vizyoner cevabını yaz)
(Eğer gerekliyse, 💡 BAĞIMSIZ AI YORUMU kısmını buranın en sonuna ekle)

5. Dilin akıcı Türkçe olmalıdır.
"""

async def call_groq_model(client: httpx.AsyncClient, model: str, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Helper to make async calls to Groq API"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model, 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": 1500
    }
    try:
        response = await client.post(GROQ_API_URL, headers=headers, json=payload, timeout=40.0)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[HATA - {model}]: {str(e)}"

async def chat_with_paper_consensus(paper_title: str, paper_abstract: str, user_question: str) -> str:
    """Executes the 3-model AI consensus engine asynchronously."""
    
    # Context to share with all agents
    context = f"MAKALE BAŞLIĞI: {paper_title}\nMAKALE METNİ/ÖZETİ: {paper_abstract}\n"
    
    async with httpx.AsyncClient() as client:
        # Step 1: Researcher and Critic run in parallel (approx 1.5 - 2 seconds on Groq)
        researcher_task = asyncio.create_task(call_groq_model(
            client=client, 
            model="qwen/qwen3-32b", 
            system_prompt=RESEARCHER_PROMPT, 
            user_prompt=f"{context}\n\nLütfen yalnızca aşağıdaki KULLANICI SORUSU tagleri içindeki yönergeye yanıt ver:\n<user_question>\n{user_question}\n</user_question>",
            temperature=0.1 # Needs exact data extraction
        ))
        
        critic_task = asyncio.create_task(call_groq_model(
            client=client, 
            model="meta-llama/llama-4-scout-17b-16e-instruct", 
            system_prompt=CRITIC_PROMPT, 
            user_prompt=f"{context}\n\nLütfen yalnızca aşağıdaki KULLANICI SORUSU tagleri içindeki yönergeye yanıt ver:\n<user_question>\n{user_question}\n</user_question>",
            temperature=0.4 # More creative/aggressive
        ))
        
        researcher_report, critic_report = await asyncio.gather(researcher_task, critic_task)
        
        # Step 2: President runs sequentially after the first two, synthesizing the output
        president_context = f"{context}\n\n--- ARAŞTIRMACI RAPORU ---\n{researcher_report}\n\n--- ELEŞTİRMEN RAPORU ---\n{critic_report}\n"
        
        final_answer = await call_groq_model(
            client=client,
            model="llama-3.3-70b-versatile",
            system_prompt=PRESIDENT_PROMPT,
            user_prompt=f"{president_context}\n\nLütfen yalnızca aşağıdaki KULLANICI SORUSU tagleri içindeki yönergeye yanıt ver:\n<user_question>\n{user_question}\n</user_question>",
            temperature=0.2
        )
        
        return final_answer

async def fetch_full_text_jina(url: str) -> str:
    """
    Uses r.jina.ai to scrape the full text of an article link and return it as Markdown.
    If the link is a standard DOI link, Jina will attempt to resolve and read the publisher page.
    Includes HTTP Status Code tracking to prevent Bot Protections (Cloudflare) from breaking AI context.
    """
    import urllib.parse
    import re

    if not url or url == "-":
        return "Geçerli bir orijinal bağlantı bulunamadı."
        
    parsed = urllib.parse.urlparse(url)
    is_doi = bool(re.match(r'^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$', url))
    
    if not is_doi and parsed.scheme not in ["http", "https"]:
        return "Güvenlik İhlali: Sağlanan URL geçerli bir şemaya (http/https) veya DOI formatına sahip değil."
        
    if parsed.hostname:
        hostname = parsed.hostname.lower()
        if hostname in ["localhost", "127.0.0.1", "0.0.0.0"] or hostname.startswith("192.168.") or hostname.startswith("10.") or hostname.endswith(".local"):
            return "Güvenlik İhlali: İç ağ hedeflerine istek yapılamaz."

    jina_url = f"https://r.jina.ai/{url}"
    headers = {}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                jina_url, 
                headers=headers, 
                timeout=45.0,
                follow_redirects=True
            )
            
            # 1) HTTP Durum Kodu Bazlı Bot Koruması Saptama
            if response.status_code in [401, 403, 503]:
                return f"BotKorumasi: Yayıncı (HTTP {response.status_code}) bot koruması uyguladığı için tam metin çekilemedi."
                
            response.raise_for_status()
            text_content = response.text
            
            # 2) Fallback: Eğer HTTP 200 dönüp sayfanın içine Cloudflare sayfası basılmışsa (Jina render etmişse)
            lower_text = text_content.lower()
            if "are you a robot" in lower_text or "just a moment..." in lower_text or "captcha challenge" in lower_text:
                return f"BotKorumasi: Yayıncı bot koruması/Captcha uyguladığı için tam metin çekilemedi."
                
            if len(text_content) < 500:
                return f"BotKorumasi: Makale kilitli veya metin çok kısa. Gelen veri:\n{text_content}"
                
            return text_content
    except Exception as e:
        return f"BotKorumasi: Tam metin çekilirken Jina AI servisinde iletişim hatası oluştu: {str(e)}"

async def translate_query(query: str, target_lang: str = "en") -> str:
    """
    Translates search query to target language (en/tr) to support cross-lingual search.
    Uses llama-3.1-8b-instant for fast, reliable short-text translation.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"Translate the following academic/engineering search query to {'English' if target_lang == 'en' else 'Turkish'}. ONLY return the translated term, nothing else. No quotes, no explanations.\n\nLütfen yalnızca aşağıdaki query tagleri içindeki metni çevir:\n<query>\n{query}\n</query>"
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 50
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GROQ_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            translated_text = data["choices"][0]["message"]["content"].strip().strip('"').strip("'")
            return translated_text
    except Exception as e:
        import logging
        logging.error(f"Translate Query API Error for '{query}': {str(e)}")
        # Fallback to original query if translation fails to not break the search
        return query
