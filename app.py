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
    from utils.ai_manager import chat_with_paper_consensus
    import asyncio
    
    paper = st.session_state.get("selected_paper", {})
    
    # "Geri Dön" button at the very top of focus mode
    if st.button("🔙 Geri Dön (Arama Sonuçları)", key="back_btn"):
        st.session_state.view_mode = "search"
        st.rerun()
        
    from components.ui_components import render_article_card
    render_article_card(paper, index=0, is_focus_mode=True)
        
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    
    # Consensus Engine Briefing & Chat Container
    st.markdown("<h3 style='font-family:\"Anton\", sans-serif; color:#00D2FF; letter-spacing:2px;'>🏛️ AI GENEL KURUL BRİFİNGİ VE SOHBET</h3>", unsafe_allow_html=True)
    
    # Initialize Chat History if empty
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    # Auto-Briefing (First interaction is an empty query synthesized to a summary request)
    if not st.session_state.chat_history:
        with st.spinner("Genel Kurul toplanıyor ve makale sentezleniyor..."):
            initial_prompt = "Lütfen makalenin ana amacını, kullanılan yöntemleri, kilit teknik verileri (parametre, cihaz, istatistik) ve olası sınırlandırmaları içeren kısa bir genel kurul brifingi ver."
            response = asyncio.run(chat_with_paper_consensus(
                paper_title=str(paper.get('Başlık', '')),
                paper_abstract=str(paper.get('Özet', '')),
                user_question=initial_prompt
            ))
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
    # Display Chat History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Chat Input for interactive querying
    if prompt := st.chat_input("Bu makale hakkında spesifik bir soru sorun... (Örn: Hangi soğutma sıvısı kullanılmış?)"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Genel Kurul makineden veri çekip tartışıyor..."):
                answer = asyncio.run(chat_with_paper_consensus(
                    paper_title=str(paper.get('Başlık', '')),
                    paper_abstract=str(paper.get('Özet', '')),
                    user_question=prompt
                ))
                st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

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
                    db_options = ["OpenAlex (Global)", "Crossref", "arXiv", "DergiPark", "YÖK Tez / TR Üniversiteleri", "TR Kaynaklı / TR Dizin", "IEEE Xplore", "Elsevier (ScienceDirect)", "Springer", "ASME"]
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
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(fetch_all_sources(sources_list, q, filters_dict))
                    finally:
                        # Do not shutdown default executor to prevent zombie threads from hanging Streamlit
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
                error_html = "<div style='background-color: #331111; border-left: 5px solid #ff4444; padding: 15px; margin-bottom: 20px; font-family: \"Space Mono\", monospace;'>"
                error_html += "<h4 style='color: #ff4444; margin-top: 0;'>⚠️ Bazı Kaynaklarda Tarama Sorunu:</h4><ul style='color: #ffaaaa; margin-bottom: 0;'>"
                for err in api_errors:
                    error_html += f"<li><b>{err['source']}:</b> {err['message']}</li>"
                error_html += "</ul></div>"
                st.markdown(error_html, unsafe_allow_html=True)

            if all_results:
                df = pd.DataFrame(all_results)
                
                def generate_scihub_link(row):
                    if pd.notna(row.get("DOI")) and row.get("DOI") != "-":
                        clean_doi = str(row["DOI"]).replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
                        return f"{sci_hub_base.rstrip('/')}/{clean_doi}"
                    return None

                df["Sci-Hub Linki"] = df.apply(generate_scihub_link, axis=1)
                
                if show_only_locked:
                    df = df[df["Sci-Hub Linki"].notna()]
                
                from components.ui_components import render_metrics, render_article_card
                from utils.export import generate_bibtex
                
                # Key Visual Metrics - Brutalist
                render_metrics(df, sci_hub_base)
                    
                st.markdown("<div id='results-top'></div><div style='height: 40px;'></div><hr style='border-color: #333;'><div style='height: 40px;'></div>", unsafe_allow_html=True)

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
if st.session_state.view_mode != "focus":
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
