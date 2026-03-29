"""
Search View — renders the main literature search engine interface.

Activated when st.session_state.view_mode == "search" (the default).

Responsibilities:
  - Search form (query input, source selection, year/language filters)
  - Async fetch orchestration with smart cross-lingual routing
  - @st.cache_data result caching (TTL 30 min)
  - Post-search sidebar filters (source, author, access type)
  - AI re-ranking (optional, Top-15)
  - Paginated article card listing
  - Export buttons (CSV / Excel / BibTeX)

Session state keys consumed / produced:
    view_mode           (str)   — set to "global_chat" or "research" when AI buttons pressed
    search_triggered    (bool)  — True after form submit
    last_query          (str)   — cached query string
    all_results_cache   (list)  — fetched article dicts
    api_errors_cache    (list)  — per-source error dicts
    page_number         (int)   — current page (1-indexed)
    scroll_to_top       (bool)  — flag to trigger JS scroll
    search_query_input  (str)   — Streamlit widget key
    search_type_input   (str)   — Streamlit widget key
"""
import asyncio
import base64
import html
import io
import json
import re

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from components.ui_components import render_article_card, render_metrics, track_ga_event
from utils.ai_manager import rank_results_with_ai, score_heuristic, translate_query
from utils.export import generate_bibtex
from utils.fetcher import fetch_all_sources
from utils.ui_helpers import generate_scihub_link, tr_lower

# ---------------------------------------------------------------------------
# Module-level cached fetcher — defined here (not inside render) so that
# @st.cache_data survives across reruns without being recreated.
# ---------------------------------------------------------------------------

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_data_cached(
    search_type_str: str,
    sources_list: list,
    q: str,
    filters_dict: dict,
) -> dict:
    """Fetches results from all selected sources with smart translation routing."""

    async def run_fetch() -> dict:
        nonlocal q
        filters_dict["search_type"] = search_type_str
        selected_langs = filters_dict.get("language", [])

        # Smart Routing & Auto-Translation
        is_turkish = "Türkçe" in q or any(
            c in q.lower() for c in ["ş", "ç", "ğ", "ü", "ö", "ı"]
        )
        if (
            "Türkçe" not in selected_langs
            and "İngilizce" in selected_langs
            and is_turkish
        ):
            q = await translate_query(q, target_lang="en")

        # Cross-Lingual Fallback (both languages selected)
        if len(selected_langs) == 2:
            target = "en" if is_turkish else "tr"
            translated_q = await translate_query(q, target_lang=target)

            if translated_q and translated_q.lower() != q.lower():
                task1 = fetch_all_sources(sources_list, q, filters_dict)
                task2 = fetch_all_sources(sources_list, translated_q, filters_dict)
                res1, res2 = await asyncio.gather(task1, task2)

                combined_results = res1.get("results", []) + res2.get("results", [])
                combined_errors = res1.get("errors", []) + res2.get("errors", [])

                # Deduplicate by DOI
                seen_dois: set = set()
                unique_results = []
                for item in combined_results:
                    doi = item.get("DOI", "-")
                    if doi != "-" and doi in seen_dois:
                        continue
                    seen_dois.add(doi)
                    unique_results.append(item)

                return {"results": unique_results, "errors": combined_errors}

        return await fetch_all_sources(sources_list, q, filters_dict)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_fetch())
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------

def render_search_view() -> None:
    """Renders the full search form, results list, sidebar filters, and export panel."""

    col_empty1, col_center, col_empty2 = st.columns([1, 6, 1])

    with col_center:
        def trigger_search() -> None:
            st.cache_data.clear()  # prevent stuck timeout errors from stale cache
            st.session_state.search_triggered = True
            st.session_state.last_query = st.session_state.search_query_input
            st.session_state.all_results_cache = []
            st.session_state.page_number = 1

        with st.container():
            st.markdown(
                "<div style='text-align: center; margin-bottom: 20px;'>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with st.form(key="search_form", clear_on_submit=False):
            st.text_input(
                "Arama Terimi",
                placeholder="Mühendislik literatüründe arayın...",
                label_visibility="collapsed",
                key="search_query_input",
            )

            with st.expander("⚙️ Tarama Seçenekleri ve Sci-Hub Ayarları", expanded=True):
                ecol1, ecol2 = st.columns(2)
                with ecol1:
                    search_type = st.selectbox(
                        "Arama Tipi",
                        ["Kavram/Kelime Arama", "DOI Numarası", "Yazar Adı"],
                        key="search_type_input",
                    )
                    db_options = [
                        "OpenAlex (Global)", "Crossref", "arXiv", "DergiPark",
                        "YÖK Tez / TR Üniversiteleri", "TR Kaynaklı / TR Dizin",
                        "IEEE Xplore", "Elsevier (ScienceDirect)", "Springer", "ASME",
                    ]
                    default_dbs = [
                        "OpenAlex (Global)", "Crossref", "arXiv", "DergiPark",
                        "YÖK Tez / TR Üniversiteleri", "TR Kaynaklı / TR Dizin", "ASME",
                    ]
                    sources = st.multiselect("Veritabanları", db_options, default=default_dbs)
                    year_range = st.slider(
                        "Yayın Yılı", min_value=1990, max_value=2026, value=(1990, 2026)
                    )
                    start_year, end_year = year_range

                with ecol2:
                    sci_hub_base = st.text_input("Sci-Hub Domain URL", value="https://sci-hub.ist")
                    language = st.multiselect(
                        "Sorgu Dili", ["İngilizce", "Türkçe"], default=["Türkçe", "İngilizce"]
                    )
                    show_only_locked = st.toggle(
                        "Sadece Kilitli/Sci-Hub'lık Olanları Göster", value=False
                    )
                    exact_match_only = st.toggle(
                        "Tam Eşleşme (Sadece başlık/özette bu kelimeyi içerenler)",
                        value=False,
                    )

            st.markdown("<span class='start-btn-anchor'></span>", unsafe_allow_html=True)
            col_start1, col_start2, col_start3 = st.columns([1, 1, 1])
            with col_start2:
                st.form_submit_button(
                    "Taramayı Başlat",
                    use_container_width=True,
                    on_click=trigger_search,
                )

    # -----------------------------------------------------------------------
    # Execution block (runs after form submit)
    # -----------------------------------------------------------------------
    if not st.session_state.get("search_triggered", False):
        return

    query_to_run: str = st.session_state.get("last_query", "")

    if not query_to_run.strip():
        st.error("Lütfen arama yapmak için bir terim girin.", icon="⚠️")
        return

    if not sources:
        st.error("Lütfen en az bir veritabanı seçin.", icon="⚠️")
        return

    track_ga_event(
        "search",
        {
            "search_term": query_to_run,
            "search_type": st.session_state.get("search_type_input", "Kavram/Kelime Arama"),
            "sources": ", ".join(sources),
        },
    )

    # --- Fetch (with loading UI) ---
    if not st.session_state.get("all_results_cache"):
        st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)

        loading_container = st.empty()
        with loading_container.container():
            st.markdown("<div id='search-execution-anchor'></div>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="border: 4px solid #CCFF00; background-color: #111;
                            padding: 40px; text-align: center;
                            box-shadow: 8px 8px 0px #00D2FF;
                            margin: 40px auto; max-width: 800px;">
                    <h3 style="font-family: 'Anton', sans-serif; color: #CCFF00;
                               font-size: 2.2rem; letter-spacing: 2px;
                               margin-top:0; margin-bottom:0; text-transform: uppercase;">
                        🧭 AKADEMİK PUSULA ⚡ LİTERATÜR TARIYOR... LÜTFEN BEKLEYİN.
                    </h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            components.html(
                """
                <script>
                    setTimeout(function() {
                        window.parent.document
                            .getElementById('search-execution-anchor')
                            .scrollIntoView({behavior: 'smooth', block: 'center'});
                    }, 100);
                </script>
                """,
                height=0,
            )

        filters = {
            "start_year": start_year,
            "end_year": end_year,
            "language": language,
        }

        fetch_output = fetch_data_cached(
            st.session_state.get("search_type_input", "Kavram/Kelime Arama"),
            sources,
            query_to_run,
            filters,
        )

        loading_container.empty()
        st.session_state.all_results_cache = fetch_output.get("results", [])
        st.session_state.api_errors_cache = fetch_output.get("errors", [])

    all_results: list = st.session_state.get("all_results_cache", [])
    api_errors: list = st.session_state.get("api_errors_cache", [])

    # --- Per-source error banner ---
    if api_errors:
        error_html_str = (
            "<div style='background-color: #331111; border-left: 5px solid #ff4444; "
            "padding: 15px; margin-bottom: 20px; font-family: \"Space Mono\", monospace;'>"
            "<h4 style='color: #ff4444; margin-top: 0;'>⚠️ Bazı Kaynaklarda Tarama Sorunu:</h4>"
            "<ul style='color: #ffaaaa; margin-bottom: 0;'>"
        )
        for err in api_errors:
            safe_source = html.escape(str(err.get("source", "")))
            safe_message = html.escape(str(err.get("message", "")))
            error_html_str += f"<li><b>{safe_source}:</b> {safe_message}</li>"
        error_html_str += "</ul></div>"
        st.markdown(error_html_str, unsafe_allow_html=True)

    # --- Exact match client-side filter ---
    if all_results and exact_match_only:
        q_lower = tr_lower(query_to_run)
        all_results = [
            item
            for item in all_results
            if q_lower in tr_lower(str(item.get("Başlık", "")))
            or q_lower in tr_lower(str(item.get("Özet", "")))
            or q_lower in tr_lower(str(item.get("Yazarlar", "")))
        ]

    if not all_results:
        st.info("Bu arama kriterine uygun, sınırlandırılmış alanda bir sonuç bulunamadı.")
        return

    df = pd.DataFrame(all_results)

    # -----------------------------------------------------------------------
    # Sidebar filters (post-search)
    # -----------------------------------------------------------------------
    with st.sidebar:
        st.markdown(
            "<h2 style='font-family:\"Anton\"; color:#00D2FF; letter-spacing:1px;'>"
            "⚙️ SONUÇ FİLTRELERİ</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color:#AAA; font-size:0.9rem;'>Bulunan sonuçları daraltın.</p>",
            unsafe_allow_html=True,
        )

        # 1. Source filter
        available_sources = sorted(df["Kaynak"].unique().tolist())
        selected_sources = st.multiselect(
            "Veritabanına Göre Filtrele", available_sources, default=available_sources
        )
        if selected_sources:
            df = df[df["Kaynak"].isin(selected_sources)]

        # 2. Author filter (top 100 for performance)
        authors_set: set = set()
        for authors_str in df["Yazarlar"].dropna().tolist():
            if authors_str and authors_str != "Bilinmiyor":
                for a in authors_str.split(","):
                    clean_a = a.strip()
                    if clean_a:
                        authors_set.add(clean_a)
        available_authors = sorted(authors_set)[:100]
        selected_authors = st.multiselect("Yazara Göre Filtrele", available_authors, default=[])
        if selected_authors:
            mask = df["Yazarlar"].apply(
                lambda x: any(sa.lower() in str(x).lower() for sa in selected_authors)
            )
            df = df[mask]

        # 3. Access type filter
        available_access = sorted(df["Erişim Durumu"].astype(str).unique().tolist())
        selected_access = st.multiselect(
            "Erişim Durumu", available_access, default=available_access
        )
        if selected_access:
            df = df[df["Erişim Durumu"].isin(selected_access)]

        st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
        st.markdown(
            "<h3 style='font-family:\"Anton\"; color:#CCFF00; letter-spacing:1px;'>"
            "🧠 AI AKILLI SIRALAMA</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color:#AAA; font-size:0.8rem;'>Önce <b>tüm sonuçlar</b> hızlı "
            "buluşsal sıralamaya (yenilik + başlık eşleşmesi + özet kalitesi) tabi tutulur. "
            "Ardından listenin başındaki <b>Top 25 makale</b>, yapay zeka tarafından "
            "semantik alaka puanına göre yeniden sıralanır.</p>",
            unsafe_allow_html=True,
        )
        use_smart_rerank = st.toggle("🤖 Süper Akıllı Sıralama (Re-ranking)", value=False)

    # -----------------------------------------------------------------------
    # AI Re-ranking — Two-stage: heuristic pre-sort (all) + AI top-25
    # -----------------------------------------------------------------------
    if use_smart_rerank and not df.empty:
        import datetime as _dt

        # Stage 1: Heuristic pre-sort across ALL results (synchronous, zero API cost)
        all_records = df.to_dict("records")
        sorted_records = score_heuristic(query_to_run, all_records, _dt.date.today().year)
        df = pd.DataFrame(sorted_records)

        # Stage 2: AI re-ranks top 25 from the heuristic-sorted list
        top_25_df = df.head(25).reset_index(drop=True).copy()
        items_to_rank = [
            {
                "id": str(i),
                "title": str(row.get("Başlık", "")),
                "abstract": str(row.get("Özet", ""))[:400],
            }
            for i, row in enumerate(top_25_df.to_dict("records"))
        ]
        items_json = json.dumps(items_to_rank, ensure_ascii=False)

        with st.spinner(f"🧠 {len(all_records)} makale ön sıralandı. En iyi 25 tanesi yapay zeka ile analiz ediliyor..."):
            try:
                ai_ranking_response = asyncio.run(rank_results_with_ai(query_to_run, items_json))
                try:
                    ranking_data = json.loads(ai_ranking_response)
                    score_map = {
                        item["id"]: item["score"]
                        for item in ranking_data.get("results", [])
                    }
                    top_25_df["AI_Score"] = (
                        top_25_df.index.astype(str).map(score_map).fillna(0).astype(int)
                    )
                    top_25_df = top_25_df.sort_values(by="AI_Score", ascending=False)
                    df = pd.concat([top_25_df, df.iloc[25:]], ignore_index=True)
                    st.success(
                        f"✅ Akıllı Sıralama Tamamlandı! {len(all_records)} makalenin tamamı sıralandı "
                        f"(Top 25 AI-puanlı, geri kalanlar buluşsal sırayla).",
                        icon="🎯",
                    )
                except json.JSONDecodeError:
                    st.error("AI Puanlama servisinde bir hata oluştu. Buluşsal sıralama kullanılıyor.")
            except Exception as e:
                st.error(f"Sıralama motoru hatası: {str(e)}")

    # -----------------------------------------------------------------------
    # Sci-Hub column + locked filter
    # -----------------------------------------------------------------------
    df["Sci-Hub Linki"] = df.apply(
        lambda row: generate_scihub_link(row, sci_hub_base), axis=1
    )

    if show_only_locked:
        df = df[df["Sci-Hub Linki"].notna()]

    if df.empty:
        st.warning("Seçilmiş olan filtrelere uyan bir sonuç kalmadı. Lütfen sol menüden filtreleri gevşetin.")
        return

    # -----------------------------------------------------------------------
    # Metrics + sorting
    # -----------------------------------------------------------------------
    render_metrics(df, sci_hub_base)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )

    sort_option = st.selectbox(
        "📅 Sonuçları Sırala",
        ["Varsayılan", "Yıla Göre (En Yeni En Üstte)", "Yıla Göre (En Eski En Üstte)"],
        label_visibility="collapsed",
    )

    if sort_option == "Yıla Göre (En Yeni En Üstte)":
        df["Yıl_Sırala"] = pd.to_numeric(df["Yıl"], errors="coerce").fillna(0)
        df = df.sort_values(by="Yıl_Sırala", ascending=False).drop(columns=["Yıl_Sırala"])
    elif sort_option == "Yıla Göre (En Eski En Üstte)":
        df["Yıl_Sırala"] = pd.to_numeric(df["Yıl"], errors="coerce").fillna(9999)
        df = df.sort_values(by="Yıl_Sırala", ascending=True).drop(columns=["Yıl_Sırala"])

    st.markdown("<br>", unsafe_allow_html=True)
    _btn_col1, _btn_col2 = st.columns(2)
    with _btn_col1:
        if st.button("🏛️ BAĞIMSIZ AI DANIŞMANI (GENEL KURUL)", type="primary", use_container_width=True):
            st.session_state.view_mode = "global_chat"
            if "chat_history_global" in st.session_state:
                del st.session_state.chat_history_global
            st.rerun()
    with _btn_col2:
        if st.button("🔬 ARAŞTIRMA ZEKASI (SORU SOR)", type="secondary", use_container_width=True):
            st.session_state.view_mode = "research"
            st.session_state.ri_question = st.session_state.get("last_query", "")
            for key in ("ri_report", "ri_sources", "ri_triggered"):
                st.session_state.pop(key, None)
            st.rerun()

    st.markdown(
        "<div id='results-top'></div>"
        "<div style='height: 20px;'></div>"
        "<hr style='border-color: #333;'>"
        "<div style='height: 20px;'></div>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Pagination
    # -----------------------------------------------------------------------
    items_per_page = 10
    total_items = len(df)
    total_pages = max(1, (total_items - 1) // items_per_page + 1)

    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    st.session_state.page_number = max(1, min(st.session_state.page_number, total_pages))

    start_idx = (st.session_state.page_number - 1) * items_per_page
    page_df = df.iloc[start_idx : start_idx + items_per_page]

    if st.session_state.get("scroll_to_top", False):
        components.html(
            "<script>window.parent.document.getElementById('results-top')"
            ".scrollIntoView({behavior: 'smooth', block: 'start'});</script>",
            height=0,
        )
        st.session_state.scroll_to_top = False

    for idx, (_, row) in enumerate(page_df.iterrows()):
        with st.container():
            render_article_card(row, index=idx)

    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    pc1, pc2, pc3 = st.columns([1, 2, 1])
    with pc1:
        st.markdown("<span class='prev-btn-anchor'></span>", unsafe_allow_html=True)
        if st.button(
            "⬅️ Önceki Sayfa",
            disabled=(st.session_state.page_number <= 1),
            use_container_width=True,
        ):
            st.session_state.page_number -= 1
            st.session_state.scroll_to_top = True
            st.rerun()
    with pc2:
        st.markdown(
            f"<div style='text-align:center; color:#CCFF00; font-family:\"Space Mono\"; "
            f"font-size:1.5rem; margin-top:10px;'>"
            f"<b>Sayfa {st.session_state.page_number} / {total_pages}</b></div>",
            unsafe_allow_html=True,
        )
    with pc3:
        st.markdown("<span class='next-btn-anchor'></span>", unsafe_allow_html=True)
        if st.button(
            "Sonraki Sayfa ➡️",
            disabled=(st.session_state.page_number >= total_pages),
            use_container_width=True,
        ):
            st.session_state.page_number += 1
            st.session_state.scroll_to_top = True
            st.rerun()

    st.markdown(
        "<div style='height: 40px;'></div><hr style='border-color: #333;'>"
        "<div style='height: 40px;'></div>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Export buttons (CSV / Excel / BibTeX)
    # -----------------------------------------------------------------------
    csv_data = df.to_csv(index=False).encode("utf-8")
    b64_csv = base64.b64encode(csv_data).decode("utf-8")

    output_buf = io.BytesIO()
    with pd.ExcelWriter(output_buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sonuçlar")
    b64_excel = base64.b64encode(output_buf.getvalue()).decode("utf-8")

    bibtex_data = generate_bibtex(df)
    b64_bibtex = base64.b64encode(bibtex_data.encode("utf-8")).decode("utf-8")

    btn_style_cyan = (
        "text-decoration:none; background-color:#050505; color:#FFF; "
        "font-family:'Bebas Neue',sans-serif; letter-spacing:2px; font-size:1.5rem; "
        "padding:10px 25px; border:2px solid #00D2FF; box-shadow:4px 4px 0px #00D2FF; "
        "transition:all 0.2s; white-space:nowrap; display:inline-block;"
    )
    btn_style_lime = (
        "text-decoration:none; background-color:#CCFF00; color:#050505; "
        "font-family:'Bebas Neue',sans-serif; letter-spacing:2px; font-size:1.5rem; "
        "font-weight:bold; padding:10px 25px; border:2px solid #050505; "
        "box-shadow:4px 4px 0px #050505; transition:all 0.2s; "
        "white-space:nowrap; display:inline-block;"
    )

    export_feedback_html = re.sub(
        r"^[ \t]+",
        "",
        f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 30px; margin-bottom: 30px; align-items: stretch;">
            <div style="border: 4px solid #CCFF00; background-color: #111; padding: 30px;
                        border-radius: 0; box-shadow: 8px 8px 0px #00D2FF;
                        display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <h3 style="font-family: 'Anton', sans-serif; font-size: 2.5rem;
                               color: #F0F0F0; margin-top: 0; margin-bottom: 15px;
                               letter-spacing: 2px; text-shadow: 4px 4px 0px #00D2FF;
                               text-transform: uppercase;">💾 SONUÇLARI DIŞA AKTAR</h3>
                    <p style="color: #AAA; font-family: 'Space Mono', monospace;
                              font-size: 1.1rem; margin-bottom: 25px; line-height: 1.6;">
                        Taraması tamamlanan makaleleri Excel, CSV veya BibTeX formatlarında
                        cihazınıza indirerek literatür taramanızı kolayca arşivleyebilirsiniz.
                    </p>
                </div>
                <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: center;">
                    <a href="data:text/csv;base64,{b64_csv}"
                       download="akademik_pusula_sonuclar.csv"
                       style="{btn_style_cyan}">📥 CSV İNDİR</a>
                    <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}"
                       download="akademik_pusula_sonuclar.xlsx"
                       style="{btn_style_lime}">📊 EXCEL İNDİR</a>
                    <a href="data:text/plain;base64,{b64_bibtex}"
                       download="akademik_pusula_sonuclar.bib"
                       style="{btn_style_cyan}">📝 BİBTEX İNDİR</a>
                </div>
            </div>
            <div style="border: 4px solid #CCFF00; background-color: #111; padding: 30px;
                        border-radius: 0; box-shadow: 8px 8px 0px #00D2FF;
                        display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <h3 style="font-family: 'Anton', sans-serif; font-size: 2.5rem;
                               color: #F0F0F0; margin-top: 0; margin-bottom: 15px;
                               letter-spacing: 2px; text-shadow: 4px 4px 0px #00D2FF;
                               text-transform: uppercase;">🐛 HATA BİLDİR / GERİ BİLDİRİM</h3>
                    <p style="color: #AAA; font-family: 'Space Mono', monospace;
                              font-size: 1.1rem; margin-bottom: 25px; line-height: 1.6;">
                        Eşleşmeyen, yanlış eşleşen bir sonuç fark ettiyseniz veya sistemle
                        ilgili bir öneriniz varsa e-posta üzerinden bize iletebilirsiniz.
                    </p>
                </div>
                <div>
                    <a href="mailto:bariskirli@trakya.edu.tr?subject=Akademik%20Pusula%20Geri%20Bildirim"
                       style="{btn_style_cyan}">📧 E-POSTA GÖNDER</a>
                </div>
            </div>
        </div>
        """,
        flags=re.MULTILINE,
    )
    st.markdown(export_feedback_html, unsafe_allow_html=True)
