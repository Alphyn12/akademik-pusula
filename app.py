import os
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

# --- Page Config ---
st.set_page_config(page_title="Akademik Pusula 🧭", layout="wide", initial_sidebar_state="collapsed")

# --- PWA SETUP ---
import streamlit.components.v1 as components
components.html(
    """
    <script>
      // Register Service Worker in the parent window
      if ('serviceWorker' in window.parent.navigator) {
        window.parent.navigator.serviceWorker.register('/app/static/sw.js').then(function(registration) {
          console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }).catch(function(err) {
          console.log('ServiceWorker registration failed: ', err);
        });
      }

      // Inject manifest and apple touch icons
      const head = window.parent.document.head;
      if (!head.querySelector('link[rel="manifest"]')) {
          const manifest = document.createElement('link');
          manifest.rel = 'manifest';
          manifest.href = '/app/static/manifest.json';
          head.appendChild(manifest);
          
          const appleMeta = document.createElement('meta');
          appleMeta.name = 'apple-mobile-web-app-capable';
          appleMeta.content = 'yes';
          head.appendChild(appleMeta);
          
          const appleTitle = document.createElement('meta');
          appleTitle.name = 'apple-mobile-web-app-title';
          appleTitle.content = 'Pusula';
          head.appendChild(appleTitle);
          
          const appleIcon = document.createElement('link');
          appleIcon.rel = 'apple-touch-icon';
          appleIcon.href = '/app/static/apple-touch-icon.png';
          head.appendChild(appleIcon);
      }
    </script>
    """,
    height=0
)

# --- BOLD AESTHETIC CSS ---
# Theme: "Dark Neobrutalism"
# Aggressive dark mode, pitch black background, neon lime/light blue thick unblurred drop shadows.
# Typography: Anton for headers, Space Mono for raw data, Bebas Neue for raw buttons.
def load_css(file_path):
    import os
    import streamlit as st
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css(os.path.join(os.path.dirname(__file__), 'assets', 'style.css'))



# --- Backend Fetcher Functions ---



# --- Search Engine Layout ---


# Central Logo - Brutalist
st.markdown("""
<div class="logo-container">
    <h1 class="logo-text"><span class="shift-left">AKADEMİK</span><br>PUSULA</h1>
    <div class="logo-subtext">AKADEMİK LİTERATÜR. SANSÜRSÜZ VE LİMİTSİZ.</div>
</div>
""", unsafe_allow_html=True)

# Application State Router
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "search"

if st.session_state.view_mode == "focus":
    from utils.ai_manager import chat_with_paper_consensus, fetch_full_text_jina
    import asyncio
    
    paper = st.session_state.get("selected_paper", {})
    
    # Focus Mode View
    # View mode logic continues directly to rendering the targeted article card
        
    from components.ui_components import render_article_card
    render_article_card(paper, index=0, is_focus_mode=True)
        
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    
    # Check if Full Text was requested
    is_deep_analysis = st.session_state.get("force_full_text", False)
    
    if is_deep_analysis and "full_text" not in st.session_state:
        st.markdown("""
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(5,5,5,0.95); z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <h1 style="color: #CCFF00; font-family: 'Anton', sans-serif; font-size: 4rem; text-shadow: 4px 4px 0px #00D2FF; margin-bottom: 20px; text-align: center;">🏛️ AKADEMİK KURUL TOPLANIYOR...</h1>
            <p style="color: #FFF; font-family: 'Space Mono', monospace; font-size: 1.5rem; text-align: center; max-width: 800px;">Lütfen Bekleyin. Jina AI makalenin tam metni çıkarırken biraz zaman alabilir.</p>
            <div class="loader" style="border: 8px solid #333; border-top: 8px solid #CCFF00; border-radius: 50%; width: 80px; height: 80px; animation: spin 1s linear infinite; margin-top: 3rem;"></div>
            <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
        </div>
        """, unsafe_allow_html=True)
        with st.spinner("Jina AI ile makalenin tam metni çekiliyor... (Bu işlem sayfa boyutuna göre 10-30 saniye sürebilir)"):
            url_to_scrape = paper.get('Link') if str(paper.get('Link', '')) != '-' else paper.get('DOI', '-')
            full_text = asyncio.run(fetch_full_text_jina(str(url_to_scrape)))
            st.session_state.full_text = full_text
            st.rerun() # Force rerun to remove overlay and show the chat correctly
            
    # Consensus Engine Briefing & Chat Container
    header_title = "🧠 TAM METİN ÜZERİNDEN AI KURUL ANALİZİ" if is_deep_analysis else "🏛️ AI GENEL KURUL BRİFİNGİ VE SOHBET (ÖZET ÜZERİNDEN)"
    st.markdown(f"<h3 style='font-family:\"Anton\", sans-serif; color:#00D2FF; letter-spacing:2px;'>{header_title}</h3>", unsafe_allow_html=True)
    
    if is_deep_analysis and "full_text" in st.session_state:
        with st.expander("Jina AI Tarafından Çekilen Ham Metni Gör:", expanded=False):
            st.text(st.session_state.full_text[:3000] + "\n\n... (Metin uzun olduğu için kırpıldı) ...")
    
    # Determine the context to send to the AI
    active_abstract_or_text = st.session_state.full_text if is_deep_analysis and "full_text" in st.session_state else str(paper.get('Özet', ''))
    
    # Initialize Chat History if empty
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    # Auto-Briefing (First interaction is an empty query synthesized to a summary request)
    if not st.session_state.chat_history:
        with st.spinner("Genel Kurul toplanıyor ve metin sentezleniyor..."):
            initial_prompt = "Lütfen sağlanan metnin ana amacını, kullanılan yöntemleri, kilit teknik verileri (parametre, cihaz, istatistik) ve olası sınırlandırmaları içeren kısa bir genel kurul brifingi ver."
            response = asyncio.run(chat_with_paper_consensus(
                paper_title=str(paper.get('Başlık', '')),
                paper_abstract=active_abstract_or_text,
                user_question=initial_prompt
            ))
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
    # Display Chat History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Chat Input for interactive querying
    placeholder_text = "Tüm makale metni içinde arayın..." if is_deep_analysis else "Özet üzerinden spesifik bir soru sorun..."
    if prompt := st.chat_input(placeholder_text):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Genel Kurul makineden veri çekip tartışıyor..."):
                answer = asyncio.run(chat_with_paper_consensus(
                    paper_title=str(paper.get('Başlık', '')),
                    paper_abstract=active_abstract_or_text,
                    user_question=prompt
                ))
                st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

elif st.session_state.view_mode == "global_chat":
    # --- GLOBAL CHAT MODE (INDEPENDENT) ---
    import asyncio
    from utils.ai_manager import chat_with_paper_consensus
    
    st.markdown("<h3 style='font-family:\"Anton\", sans-serif; color:#CCFF00; letter-spacing:2px;'>🏛️ BAĞIMSIZ AI DANIŞMANI (GENEL KURUL)</h3>", unsafe_allow_html=True)
    
    if st.button("🔙 GERİ DÖN (ARAMA SONUÇLARI)", key="back_btn_global", use_container_width=True):
        st.session_state.view_mode = "search"
        if "chat_history_global" in st.session_state:
            del st.session_state.chat_history_global
        st.rerun()

    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    
    # Initialize Global Chat History if empty
    if "chat_history_global" not in st.session_state:
        st.session_state.chat_history_global = [
            {"role": "assistant", "content": "Merhaba! Ben Akademik Pusula Genel Kurulu. Mühendislik kütüphaneleri, literatür taraması, veya herhangi bir akademik/teknik konu hakkında bana danışabilirsiniz. Size nasıl yardımcı olabilirim?"}
        ]
            
    # Display Chat History
    for message in st.session_state.chat_history_global:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Chat Input for interactive querying
    if prompt := st.chat_input("Genel Kurula akademik veya teknik bir soru sorun..."):
        st.session_state.chat_history_global.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Genel Kurul toplanıyor ve sorunuzu değerlendiriyor..."):
                # Pass a general context so the agents use their AI fallback/general knowledge mode
                answer = asyncio.run(chat_with_paper_consensus(
                    paper_title="Bağımsız Mühendislik ve Akademik Danışmanlık",
                    paper_abstract="Bu bir bağımsız danışmanlık oturumudur. Özel bir makale sunulmamıştır. Kullanıcının sorusuna tamamen devasa mühendislik kültürünü ve akademik bilgini ('💡 BAĞIMSIZ AI YORUMU' olarak veya genel bilgi olarak) kullanarak yanıt ver.",
                    user_question=prompt
                ))
                st.markdown(answer)
        st.session_state.chat_history_global.append({"role": "assistant", "content": answer})

else:
    # ------------------ SEARCH MODE ------------------
    # Main Form Wrapper to center contents
    col_empty1, col_center, col_empty2 = st.columns([1, 6, 1])

    with col_center:
        def trigger_search():
            st.session_state.search_triggered = True
            st.session_state.last_query = st.session_state.search_query_input
            st.session_state.all_results_cache = []
            st.session_state.page_number = 1

        with st.form(key="search_form", clear_on_submit=False):
            search_query = st.text_input("Arama Terimi", placeholder="Mühendislik literatüründe arayın...", label_visibility="collapsed", key="search_query_input")
            
            with st.expander("⚙️ Tarama Seçenekleri ve Sci-Hub Ayarları", expanded=True):
                ecol1, ecol2 = st.columns(2)
                with ecol1:
                    db_options = ["OpenAlex (Global)", "Crossref", "arXiv", "DergiPark", "YÖK Tez / TR Üniversiteleri", "TR Kaynaklı / TR Dizin", "Elsevier (ScienceDirect)", "Springer", "ASME"]
                    default_dbs = ["OpenAlex (Global)", "Crossref", "arXiv", "DergiPark", "YÖK Tez / TR Üniversiteleri", "TR Kaynaklı / TR Dizin", "ASME"]
                    sources = st.multiselect("Veritabanları", 
                                             db_options,
                                             default=default_dbs)
                    year_range = st.slider("Yayın Yılı", min_value=1990, max_value=2026, value=(1990, 2026))
                    start_year, end_year = year_range
                with ecol2:
                    sci_hub_base = st.text_input("Sci-Hub Domain URL", value="https://sci-hub.ist")
                    language = st.multiselect("Sorgu Dili", ["İngilizce", "Türkçe"], default=["Türkçe", "İngilizce"])
                    show_only_locked = st.toggle("Sadece Kilitli/Sci-Hub'lık Olanları Göster", value=False)
                    exact_match_only = st.toggle("Tam Eşleşme (Sadece başlık/özette bu kelimeyi içerenler)", value=False)
                    
            st.markdown("<span class='start-btn-anchor'></span>", unsafe_allow_html=True)
            
            col_start1, col_start2, col_start3 = st.columns([1, 1, 1])
            with col_start2:
                search_button = st.form_submit_button("Taramayı Başlat", use_container_width=True, on_click=trigger_search)

    # --- Execution Logic (Below Search) ---
    if st.session_state.get('search_triggered', False):
        query_to_run = st.session_state.get('last_query', "")

        if not query_to_run.strip():
            st.error("Lütfen arama yapmak için bir terim girin.", icon="⚠️")
        elif not sources:
            st.error("Lütfen en az bir veritabanı seçin.", icon="⚠️")
        else:
            # Check cache logic
            if not st.session_state.get('all_results_cache'):
                st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)
                
                # --- Loading UI and Auto-Scroll ---
                import re
                loading_container = st.empty()
                with loading_container.container():
                    st.markdown("<div id='search-execution-anchor'></div>", unsafe_allow_html=True)
                    
                    loading_html = """
    <div style="border: 4px solid #CCFF00; background-color: #111; padding: 40px; text-align: center; box-shadow: 8px 8px 0px #00D2FF; margin: 40px auto; max-width: 800px;">
    <h3 style="font-family: 'Anton', sans-serif; color: #CCFF00; font-size: 2.2rem; letter-spacing: 2px; margin-top:0; margin-bottom:0; text-transform: uppercase;">🧭 AKADEMİK PUSULA AI ⚡ LİTERATÜR TARIYOR... LÜTFEN BEKLEYİN.</h3>
    </div>
                    """
                    st.markdown(loading_html, unsafe_allow_html=True)
                    
                    import streamlit.components.v1 as components
                    components.html(
                        """
                        <script>
                            setTimeout(function() { window.parent.document.getElementById('search-execution-anchor').scrollIntoView({behavior: 'smooth', block: 'center'}); }, 100);
                        </script>
                        """,
                        height=0
                    )
                
                @st.cache_data(ttl=3600, show_spinner=False)
                def fetch_data_cached(sources_list, q, filters_dict):
                    import asyncio
                    from utils.fetcher import fetch_all_sources
                    from utils.ai_manager import translate_query
                    
                    async def run_fetch():
                        selected_langs = filters_dict.get('language', [])
                        
                        # 1) Sadece Türkçe seçiliyse -> Orijinal query Türkçe farz edilir.
                        # 2) Sadece İngilizce seçiliyse -> Orijinal query İngilizce farz edilir.
                        # 3) İki dil birden seçiliyse (Cross-Lingual) -> Query'i diğer dile çevir ve İKİSİNİ BİRDEN asenkron ara!
                        if len(selected_langs) == 2:
                            # Hızlıca query'i hem İngilizce hem Türkçe olacak şekilde hazırla
                            # Basit heuristic: Eğer argümanda ASCII harici karakter (ş, ç, ğ) varsa Türkçedir, yoksa Llama karar versin
                            translated_q = await translate_query(q, target_lang="en" if "Türkçe" in q else "tr") # Hedefi değişimli ayarlayabiliriz ama Llama zaten algılayıp zıttını dönecektir
                            
                            # Güvenli çeviri kontrolü
                            if translated_q and translated_q.lower() != q.lower():
                                # İki ayrı arama task'i oluştur
                                task1 = fetch_all_sources(sources_list, q, filters_dict)
                                task2 = fetch_all_sources(sources_list, translated_q, filters_dict)
                                
                                res1, res2 = await asyncio.gather(task1, task2)
                                
                                # Sonuçları birleştir (Deduplication - DOI bazlı filtreleme)
                                combined_results = res1.get("results", []) + res2.get("results", [])
                                combined_errors = res1.get("errors", []) + res2.get("errors", [])
                                
                                # Tekilleştirme
                                seen_dois = set()
                                unique_results = []
                                for item in combined_results:
                                    doi = item.get("DOI", "-")
                                    if doi != "-" and doi in seen_dois:
                                        continue
                                    seen_dois.add(doi)
                                    unique_results.append(item)
                                    
                                return {"results": unique_results, "errors": combined_errors}
                                
                        # Tek dil seçiliyse veya çeviri başarısızsa standart arama
                        return await fetch_all_sources(sources_list, q, filters_dict)

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(run_fetch())
                    finally:
                        loop.close()
                    
                filters = {
                    'start_year': start_year,
                    'end_year': end_year,
                    'language': language
                }
                
                fetch_output = fetch_data_cached(sources, query_to_run, filters)
                    
                loading_container.empty()
                st.session_state.all_results_cache = fetch_output.get("results", [])
                st.session_state.api_errors_cache = fetch_output.get("errors", [])
                
            all_results = st.session_state.get('all_results_cache', [])
            api_errors = st.session_state.get('api_errors_cache', [])
            
            if api_errors:
                import html
                error_html = "<div style='background-color: #331111; border-left: 5px solid #ff4444; padding: 15px; margin-bottom: 20px; font-family: \"Space Mono\", monospace;'>"
                error_html += "<h4 style='color: #ff4444; margin-top: 0;'>⚠️ Bazı Kaynaklarda Tarama Sorunu:</h4><ul style='color: #ffaaaa; margin-bottom: 0;'>"
                for err in api_errors:
                    safe_source = html.escape(str(err.get('source', '')))
                    safe_message = html.escape(str(err.get('message', '')))
                    error_html += f"<li><b>{safe_source}:</b> {safe_message}</li>"
                error_html += "</ul></div>"
                st.markdown(error_html, unsafe_allow_html=True)

            if all_results:
                if exact_match_only:
                    filtered_res = []
                    q_lower = query_to_run.lower()
                    for item in all_results:
                        title = str(item.get("Başlık", "")).lower()
                        abstract = str(item.get("Özet", "")).lower()
                        if q_lower in title or q_lower in abstract:
                            filtered_res.append(item)
                    all_results = filtered_res

            if all_results:
                df = pd.DataFrame(all_results)
                
                # --- Advanced Data Filtering (Post-Search) ---
                with st.sidebar:
                    st.markdown("<h2 style='font-family:\"Anton\"; color:#00D2FF; letter-spacing:1px;'>⚙️ SONUÇ FİLTRELERİ</h2>", unsafe_allow_html=True)
                    st.markdown("<p style='color:#AAA; font-size:0.9rem;'>Bulunan sonuçları daraltın.</p>", unsafe_allow_html=True)
                    
                    # 1. Kaynak (Veritabanı) Filtresi
                    available_sources = sorted(df['Kaynak'].unique().tolist())
                    selected_sources = st.multiselect("Veritabanına Göre Filtrele", available_sources, default=available_sources)
                    if selected_sources:
                        df = df[df['Kaynak'].isin(selected_sources)]
                        
                    # 2. Yazar Filtresi (Top 50 yazarı gösterelim çok kalabalık olmasın diye)
                    all_authors_raw = df['Yazarlar'].dropna().tolist()
                    authors_set = set()
                    for authors_str in all_authors_raw:
                        if authors_str and authors_str != "Bilinmiyor":
                            # Split by common separators
                            for a in authors_str.split(','):
                                clean_a = a.strip()
                                if clean_a:
                                    authors_set.add(clean_a)
                    available_authors = sorted(list(authors_set))[:100] # Top 100 for perf
                    selected_authors = st.multiselect("Yazara Göre Filtrele", available_authors, default=[])
                    if selected_authors:
                        # Eğer seçili yazarlardan HERHANGİ BİRİ makalenin yazarları içinde geçiyorsa göster
                        mask = df['Yazarlar'].apply(lambda x: any(sa.lower() in str(x).lower() for sa in selected_authors))
                        df = df[mask]
                        
                    # 3. Erişim Durumu Filtresi
                    available_access = sorted(df['Erişim Durumu'].astype(str).unique().tolist())
                    selected_access = st.multiselect("Erişim Durumu", available_access, default=available_access)
                    if selected_access:
                         df = df[df['Erişim Durumu'].isin(selected_access)]
                         
                    # 4. Standart Sıralama (Moved to Main View)
                         
                    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
                    st.markdown("<h3 style='font-family:\"Anton\"; color:#CCFF00; letter-spacing:1px;'>🧠 AI AKILLI SIRALAMA</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='color:#AAA; font-size:0.8rem;'>Kota tasarrufu için sadece liste başındaki <b>Top 15</b> makale, sorunuza ne kadar yanıt verdiğine göre yapay zeka tarafından puanlanıp yeniden sıralanır.</p>", unsafe_allow_html=True)
                    
                    use_smart_rerank = st.toggle("🤖 Süper Akıllı Sıralama (Re-ranking)", value=False)
                    
                if use_smart_rerank and not df.empty:
                    # AI Re-ranking Logic (Top 15 Limit)
                    top_15_df = df.head(15).copy()
                    
                    from utils.ai_manager import rank_results_with_ai
                    import json
                    import asyncio
                    
                    # Prepare JSON payload for the AI
                    items_to_rank = []
                    for idx, row in top_15_df.iterrows():
                        items_to_rank.append({
                            "id": str(idx), # Using dataframe index as temporary ID
                            "title": str(row.get("Başlık", "")),
                            "abstract": str(row.get("Özet", ""))[:500] # Truncate abstract to save more tokens
                        })
                        
                    items_json = json.dumps(items_to_rank, ensure_ascii=False)
                    
                    with st.spinner("🧠 Top 15 makale anlamsal olarak analiz edilip yeniden sıralanıyor..."):
                        try:
                            # Pass original query to the AI to rank against, using standard asyncio.run
                            ai_ranking_response = asyncio.run(rank_results_with_ai(query_to_run, items_json))
                            
                            try:
                                ranking_data = json.loads(ai_ranking_response)
                                results_list = ranking_data.get("results", [])
                                
                                # Create a dictionary mapping id to score
                                score_map = {item["id"]: item["score"] for item in results_list}
                                
                                # Apply scores back to the top 15 dataframe
                                top_15_df["AI_Score"] = top_15_df.index.astype(str).map(score_map).fillna(0).astype(int)
                                
                                # Sort by the new AI Score descending
                                top_15_df = top_15_df.sort_values(by="AI_Score", ascending=False)
                                
                                # Re-attach to the rest of the dataframe (which remains untouched/unsorted below the top 15)
                                remaining_df = df.iloc[15:]
                                df = pd.concat([top_15_df, remaining_df])
                                
                                st.success("Akıllı Sıralama Tamamlandı! En alakalı sonuçlar üstte.", icon="🎯")
                            except json.JSONDecodeError:
                                st.error("AI Puanlama servisinde bir hata oluştu. Varsayılan sıralama kullanılıyor.")
                        except Exception as e:
                            st.error(f"Sıralama motoru hatası: {str(e)}")

                def generate_scihub_link(row):
                    if pd.notna(row.get("DOI")) and row.get("DOI") != "-":
                        clean_doi = str(row["DOI"]).replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
                        return f"{sci_hub_base.rstrip('/')}/{clean_doi}"
                    return None

                df["Sci-Hub Linki"] = df.apply(generate_scihub_link, axis=1)
                
                if show_only_locked:
                    df = df[df["Sci-Hub Linki"].notna()]
                    
                # If dataframe implies empty after filters -> Show warning
                if df.empty:
                    st.warning("Seçilmiş olan filtrelere uyan bir sonuç kalmadı. Lütfen sol menüden filtreleri gevşetin.")
                else:
                    from components.ui_components import render_metrics, render_article_card
                    from utils.export import generate_bibtex
                    
                    # Key Visual Metrics - Brutalist
                    render_metrics(df, sci_hub_base)
                    
                    # --- Main View Sorting Feature ---
                    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                    # --- Main View Sorting Feature ---
                    # Use full width layout (no columns) to match article card width
                    st.markdown("""
                        <style>
                        [data-testid="stMain"] div[data-testid="stSelectbox"] div[data-baseweb="select"] {
                            background-color: #0e1117 !important;
                            border: 4px solid #00D2FF !important;
                            border-radius: 0 !important;
                            box-shadow: 6px 6px 0px #CCFF00 !important;
                            font-family: 'Space Mono', monospace !important;
                            font-size: 1.1rem !important;
                            font-weight: bold !important;
                            color: #F0F0F0 !important;
                            transition: transform 0.1s, box-shadow 0.1s;
                            padding: 5px !important;
                        }
                        [data-testid="stMain"] div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover {
                            transform: translate(-3px, -3px) !important;
                            box-shadow: 9px 9px 0px #CCFF00 !important;
                            border-color: #CCFF00 !important;
                        }
                        [data-testid="stMain"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
                            background-color: transparent !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    sort_option = st.selectbox(
                        "📅 Sonuçları Sırala", 
                        ["Varsayılan", "Yıla Göre (En Yeni En Üstte)", "Yıla Göre (En Eski En Üstte)"], 
                        label_visibility="collapsed"
                    )
                        
                    if sort_option == "Yıla Göre (En Yeni En Üstte)":
                        df['Yıl_Sırala'] = pd.to_numeric(df['Yıl'], errors='coerce').fillna(0)
                        df = df.sort_values(by="Yıl_Sırala", ascending=False).drop(columns=['Yıl_Sırala'])
                    elif sort_option == "Yıla Göre (En Eski En Üstte)":
                        df['Yıl_Sırala'] = pd.to_numeric(df['Yıl'], errors='coerce').fillna(9999)
                        df = df.sort_values(by="Yıl_Sırala", ascending=True).drop(columns=['Yıl_Sırala'])

                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🏛️ BAĞIMSIZ AI DANIŞMANI (GENEL KURUL)", type="primary", use_container_width=True):
                        st.session_state.view_mode = "global_chat"
                        if "chat_history_global" in st.session_state:
                            del st.session_state.chat_history_global
                        st.rerun()
                        
                    st.markdown("<div id='results-top'></div><div style='height: 20px;'></div><hr style='border-color: #333;'><div style='height: 20px;'></div>", unsafe_allow_html=True)

                    # --- PAGINATION & GOOGLE-STYLE LISTING ---
                    items_per_page = 10
                    total_items = len(df)
                    total_pages = max(1, (total_items - 1) // items_per_page + 1)
                    
                    if "page_number" not in st.session_state:
                        st.session_state.page_number = 1
                        
                    if st.session_state.page_number > total_pages:
                        st.session_state.page_number = total_pages
                    if st.session_state.page_number < 1:
                        st.session_state.page_number = 1
                        
                    start_idx = (st.session_state.page_number - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    page_df = df.iloc[start_idx:end_idx]
                    
                    if st.session_state.get('scroll_to_top', False):
                        import streamlit.components.v1 as components
                        components.html(
                            "<script>window.parent.document.getElementById('results-top').scrollIntoView({behavior: 'smooth', block: 'start'});</script>",
                            height=0,
                        )
                        st.session_state.scroll_to_top = False
                    
                    for idx, (_, row) in enumerate(page_df.iterrows()):
                        with st.container():
                            render_article_card(row, index=idx)
                    
                    # Sayfalama Kontrolleri
                    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
                    pc1, pc2, pc3 = st.columns([1, 2, 1])
                    with pc1:
                        st.markdown("<span class='prev-btn-anchor'></span>", unsafe_allow_html=True)
                        if st.button("⬅️ Önceki Sayfa", disabled=(st.session_state.page_number <= 1), use_container_width=True):
                            st.session_state.page_number -= 1
                            st.session_state.scroll_to_top = True
                            st.rerun()
                    with pc2:
                        st.markdown(f"<div style='text-align:center; color:#CCFF00; font-family:\"Space Mono\"; font-size:1.5rem; margin-top:10px;'><b>Sayfa {st.session_state.page_number} / {total_pages}</b></div>", unsafe_allow_html=True)
                    with pc3:
                        st.markdown("<span class='next-btn-anchor'></span>", unsafe_allow_html=True)
                        if st.button("Sonraki Sayfa ➡️", disabled=(st.session_state.page_number >= total_pages), use_container_width=True):
                            st.session_state.page_number += 1
                            st.session_state.scroll_to_top = True
                            st.rerun()

                    st.markdown("<div style='height: 40px;'></div><hr style='border-color: #333;'><div style='height: 40px;'></div>", unsafe_allow_html=True)
                    
                    # Export Buttons (Base64 URIs for pixel-perfect brutalist HTML styling)
                    import base64
                    import io
                    
                    # 1. CSV
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    b64_csv = base64.b64encode(csv_data).decode('utf-8')
                    
                    # 2. Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sonuçlar')
                    b64_excel = base64.b64encode(output.getvalue()).decode('utf-8')
                    
                    # 3. BibTeX
                    bibtex_data = generate_bibtex(df)
                    b64_bibtex = base64.b64encode(bibtex_data.encode('utf-8')).decode('utf-8')
                    
                    btn_style_cyan = "text-decoration:none; background-color:#050505; color:#FFF; font-family:'Bebas Neue',sans-serif; letter-spacing:2px; font-size:1.5rem; padding:10px 25px; border:2px solid #00D2FF; box-shadow:4px 4px 0px #00D2FF; transition:all 0.2s; white-space:nowrap; display:inline-block;"
                    btn_style_lime = "text-decoration:none; background-color:#CCFF00; color:#050505; font-family:'Bebas Neue',sans-serif; letter-spacing:2px; font-size:1.5rem; font-weight:bold; padding:10px 25px; border:2px solid #050505; box-shadow:4px 4px 0px #050505; transition:all 0.2s; white-space:nowrap; display:inline-block;"
                    
                    import re
                    export_feedback_html = re.sub(r'^[ \t]+', '', f"""
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; margin-bottom: 30px; align-items: stretch;">
                        <div style="border: 4px solid #CCFF00; background-color: #111; padding: 30px; border-radius: 0; box-shadow: 8px 8px 0px #00D2FF; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <h3 style="font-family: 'Anton', sans-serif; font-size: 2.5rem; color: #F0F0F0; margin-top: 0; margin-bottom: 15px; letter-spacing: 2px; text-shadow: 4px 4px 0px #00D2FF; text-transform: uppercase;">💾 SONUÇLARI DIŞA AKTAR</h3>
                                <p style="color: #AAA; font-family: 'Space Mono', monospace; font-size: 1.1rem; margin-bottom: 25px; line-height: 1.6;">
                                    Taraması tamamlanan makaleleri Excel, CSV veya BibTeX formatlarında cihazınıza indirerek literatür taramanızı kolayca arşivleyebilirsiniz.
                                </p>
                            </div>
                            <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: center;">
                                <a href="data:text/csv;base64,{b64_csv}" download="akademik_pusula_sonuclar.csv" style="{btn_style_cyan}">📥 CSV İNDİR</a>
                            <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}" download="akademik_pusula_sonuclar.xlsx" style="{btn_style_lime}">📊 EXCEL İNDİR</a>
                            <a href="data:text/plain;base64,{b64_bibtex}" download="akademik_pusula_sonuclar.bib" style="{btn_style_cyan}">📝 BİBTEX İNDİR</a>
                        </div>
                    </div>
                    
                    <div style="border: 4px solid #CCFF00; background-color: #111; padding: 30px; border-radius: 0; box-shadow: 8px 8px 0px #00D2FF; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <h3 style="font-family: 'Anton', sans-serif; font-size: 2.5rem; color: #F0F0F0; margin-top: 0; margin-bottom: 15px; letter-spacing: 2px; text-shadow: 4px 4px 0px #00D2FF; text-transform: uppercase;">🐛 HATA BİLDİR / GERİ BİLDİRİM</h3>
                            <p style="color: #AAA; font-family: 'Space Mono', monospace; font-size: 1.1rem; margin-bottom: 25px; line-height: 1.6;">
                                Eşleşmeyen, yanlış eşleşen bir sonuç fark ettiyseniz veya sistemle ilgili bir öneriniz varsa e-posta üzerinden bize iletebilirsiniz.
                            </p>
                        </div>
                        <div>
                            <a href="mailto:bariskirli@trakya.edu.tr?subject=Akademik%20Pusula%20Geri%20Bildirim" style="{btn_style_cyan}">📧 E-POSTA GÖNDER</a>
                        </div>
                    </div>
                </div>
                """, flags=re.MULTILINE)
                st.markdown(export_feedback_html, unsafe_allow_html=True)

            else:
                st.info("Bu arama kriterine uygun, sınırlandırılmış alanda bir sonuç bulunamadı.")

# ------------------ END OF SEARCH MODE -------------

# --- Footer ---
if st.session_state.view_mode not in ["focus", "global_chat"]:
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="border: 4px solid #CCFF00; background-color: #111; padding: 20px; box-shadow: 8px 8px 0px #00D2FF; text-align: center; margin: 0 auto; max-width: 600px; font-family: 'Space Mono', monospace;">
        <p style="color: #00D2FF; font-size: 1.1rem; margin-bottom: 5px;">
            <span style="color: #CCFF00; font-weight: bold;">Geliştiren:</span> Barış KIRLI
        </p>
        <p style="color: #AAA; font-size: 0.95rem; margin-top: 0;">
            Trakya Üniversitesi Makine Mühendisliği Bölümü Öğrencisi
        </p>
    </div>
    """, unsafe_allow_html=True)
