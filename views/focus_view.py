"""
Focus View — renders the single-article deep-analysis mode.

Activated when st.session_state.view_mode == "focus".

Session state keys consumed / produced:
    selected_paper      (dict)  — the article row dict set by search_view
    force_full_text     (bool)  — whether the user requested full-text analysis
    full_text           (str)   — Jina-fetched full text (populated here on demand)
    chat_history        (list)  — per-article chat message list
"""
import asyncio

import streamlit as st

from components.ui_components import render_article_card, track_ga_event
from utils.ai_manager import chat_with_paper_consensus, fetch_full_text_smart


def render_focus_view() -> None:
    """Renders the full article focus & AI council chat interface."""
    paper = st.session_state.get("selected_paper", {})

    # --- Article card (focus mode variant) ---
    render_article_card(paper, index=0, is_focus_mode=True)
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)

    # GA4: track article focus event
    track_ga_event("article_focus", {
        "title": paper.get("Başlık", "Bilinmiyor"),
        "source": paper.get("Kaynak", "Bilinmiyor"),
        "deep_analysis": st.session_state.get("force_full_text", False),
    })

    is_deep_analysis: bool = st.session_state.get("force_full_text", False)

    # --- Full-text fetch overlay (runs once, then reruns) ---
    if is_deep_analysis and "full_text" not in st.session_state:
        st.markdown(
            """
            <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                        background-color: rgba(5,5,5,0.95); z-index: 99999;
                        display: flex; flex-direction: column;
                        justify-content: center; align-items: center;">
                <h1 style="color: #CCFF00; font-family: 'Anton', sans-serif; font-size: 4rem;
                            text-shadow: 4px 4px 0px #00D2FF; margin-bottom: 20px;
                            text-align: center;">
                    🏛️ AKADEMİK KURUL TOPLANIYOR...
                </h1>
                <p style="color: #FFF; font-family: 'Space Mono', monospace; font-size: 1.5rem;
                           text-align: center; max-width: 800px;">
                    Lütfen Bekleyin. Tam metin akıllı kaynak sisteminden çekiliyor
                    (arXiv HTML → Unpaywall → Semantic Scholar → CORE → Jina).
                </p>
                <div class="loader"
                     style="border: 8px solid #333; border-top: 8px solid #CCFF00;
                            border-radius: 50%; width: 80px; height: 80px;
                            animation: spin 1s linear infinite; margin-top: 3rem;"></div>
                <style>
                    @keyframes spin {
                        0%   { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.spinner(
            "Tam metin akıllı kaynak sisteminden çekiliyor... "
            "(arXiv / Unpaywall / Semantic Scholar / CORE / Jina — 15-45 saniye sürebilir)"
        ):
            url_to_scrape = (
                paper.get("Link")
                if str(paper.get("Link", "")) != "-"
                else paper.get("DOI", "-")
            )
            doi_val = str(paper.get("DOI", "-"))
            doi_clean = (
                None
                if doi_val in ["-", "", "None"]
                else doi_val.replace("https://doi.org/", "").strip()
            )
            full_text = asyncio.run(
                fetch_full_text_smart(
                    url=str(url_to_scrape),
                    doi=doi_clean,
                    title=str(paper.get("Başlık", "")),
                )
            )
            st.session_state.full_text = full_text
            st.rerun()  # remove overlay and enter chat

    # --- AI Council header ---
    header_title = (
        "🧠 TAM METİN ÜZERİNDEN AI KURUL ANALİZİ"
        if is_deep_analysis
        else "🏛️ AI GENEL KURUL BRİFİNGİ VE SOHBET (ÖZET ÜZERİNDEN)"
    )
    st.markdown(
        f"<h3 style='font-family:\"Anton\", sans-serif; color:#00D2FF; "
        f"letter-spacing:2px;'>{header_title}</h3>",
        unsafe_allow_html=True,
    )

    if is_deep_analysis and "full_text" in st.session_state:
        with st.expander("Jina AI Tarafından Çekilen Ham Metni Gör:", expanded=False):
            st.text(
                st.session_state.full_text[:3000]
                + "\n\n... (Metin uzun olduğu için kırpıldı) ..."
            )

    # Decide which context to feed the AI council
    active_context: str = (
        st.session_state.full_text
        if is_deep_analysis and "full_text" in st.session_state
        else str(paper.get("Özet", ""))
    )

    # --- Chat history initialisation ---
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Auto-briefing: first message triggers a summary synthesis
    if not st.session_state.chat_history:
        with st.spinner("Genel Kurul toplanıyor ve metin sentezleniyor..."):
            initial_prompt = (
                "Lütfen sağlanan metnin ana amacını, kullanılan yöntemleri, "
                "kilit teknik verileri (parametre, cihaz, istatistik) ve olası "
                "sınırlandırmaları içeren kısa bir genel kurul brifingi ver."
            )
            response = asyncio.run(
                chat_with_paper_consensus(
                    paper_title=str(paper.get("Başlık", "")),
                    paper_abstract=active_context,
                    user_question=initial_prompt,
                )
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )

    # --- Render chat history ---
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Interactive chat input ---
    placeholder_text = (
        "Tüm makale metni içinde arayın..."
        if is_deep_analysis
        else "Özet üzerinden spesifik bir soru sorun..."
    )
    if prompt := st.chat_input(placeholder_text):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Genel Kurul makineden veri çekip tartışıyor..."):
                answer = asyncio.run(
                    chat_with_paper_consensus(
                        paper_title=str(paper.get("Başlık", "")),
                        paper_abstract=active_context,
                        user_question=prompt,
                    )
                )
                st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        track_ga_event(
            "ai_interaction",
            {
                "question": prompt,
                "paper_title": paper.get("Başlık", "Bilinmiyor"),
            },
        )
