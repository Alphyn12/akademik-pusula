"""
Research Intelligence View — Perplexity-like question-based synthesis mode.

Activated when st.session_state.view_mode == "research".

Session state keys consumed / produced:
    view_mode       (str)   — set to "search" on back-button press
    ri_question     (str)   — research question entered by user (may be pre-filled)
    ri_triggered    (bool)  — True after form submit
    ri_report       (str)   — synthesized markdown research report
    ri_sources      (list)  — source paper dicts used in synthesis
"""
import asyncio
import html
import re

import streamlit as st

from utils.ai_manager import research_intelligence

# ---------------------------------------------------------------------------
# Section color palette — (border/header color, box-shadow color)
# ---------------------------------------------------------------------------
_SECTION_COLORS: dict = {
    "Araştırma Sorusu": ("#CCFF00", "#00D2FF"),
    "Ana Bulgular":     ("#00D2FF", "#CCFF00"),
    "Metodolojik":      ("#CCFF00", "#CCFF00"),
    "Boşluklar":        ("#FF6B6B", "#FF6B6B"),
    "Sentez":           ("#00D2FF", "#00D2FF"),
    "Kaynaklar":        ("#666666", "#333333"),
}
_DEFAULT_COLORS = ("#CCFF00", "#00D2FF")


def _citation_badge(n: int) -> str:
    """Renders a clickable cyan inline citation badge."""
    return (
        f'<a href="#cite-{n}" style="display:inline-block; background:#00D2FF; '
        f'color:#050505; font-family:\'Space Mono\',monospace; font-size:0.7rem; '
        f'font-weight:bold; padding:1px 6px; margin:0 2px; text-decoration:none; '
        f'border:1px solid #0099BB; line-height:1.4;">[{n}]</a>'
    )


def _inline_html(text: str) -> str:
    """Converts plain markdown-ish text with [N] markers to safe inline HTML."""
    # Escape HTML special chars
    safe = html.escape(text)
    # Bold: **text** → <b>text</b>
    safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe)
    # Citation badges: [N] → badge
    safe = re.sub(r'\[(\d+)\]', lambda m: _citation_badge(int(m.group(1))), safe)
    return safe


def _build_report_html(report: str) -> tuple:
    """
    Parses ## sections from the markdown report, converts each to a Neo-Brutalist
    HTML card with Anton headers and Space Mono body text.

    Returns:
        (html_string: str, cited_nums: set[int])
    """
    # Split on ## headings; handle leading content before first ##
    raw_sections = re.split(r'\n?## ', report)
    html_parts: list = []
    cited_nums: set = set()

    for section in raw_sections:
        section = section.strip()
        if not section:
            continue

        lines = section.split('\n', 1)
        header = lines[0].lstrip('#').strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        # Determine accent color
        accent, shadow = _DEFAULT_COLORS
        for key, colors in _SECTION_COLORS.items():
            if key in header:
                accent, shadow = colors
                break

        # Build paragraph HTML — split on blank lines or consecutive newlines
        body_html = ""
        paragraphs = re.split(r'\n{2,}', body)
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            # Remove leading bullet/list chars from each line
            para = re.sub(r'^[\s]*[-•*]\s+', '', para, flags=re.MULTILINE)
            para = para.replace('\n', ' ').strip()
            if not para:
                continue
            body_html += (
                f"<p style='color:#DEDEDE; font-family:\"Space Mono\",monospace; "
                f"font-size:0.82rem; line-height:1.75; margin:0 0 14px 0;'>"
                f"{_inline_html(para)}</p>"
            )

        # Collect cited numbers from this section
        for n in re.findall(r'\[(\d+)\]', body):
            cited_nums.add(int(n))

        html_parts.append(
            f"<div style='border:3px solid {accent}; background:#060606; "
            f"padding:22px 28px; margin-bottom:22px; "
            f"box-shadow:5px 5px 0px {shadow};'>"
            f"<h3 style='font-family:\"Anton\",sans-serif; color:{accent}; "
            f"letter-spacing:2px; font-size:1.15rem; margin:0 0 16px 0; "
            f"text-transform:uppercase;'>{html.escape(header)}</h3>"
            f"{body_html}"
            f"</div>"
        )

    return "".join(html_parts), cited_nums


def _render_source_grid(sources: list, cited_nums: set) -> None:
    """
    Renders a 2-column grid of source paper cards.
    Only shows sources that were actually cited in the report ([N] appears in text).
    Falls back to top 5 if no citations matched.
    """
    # Filter to cited sources (1-based index)
    cited_sources = [s for i, s in enumerate(sources) if (i + 1) in cited_nums][:10]
    display_sources = cited_sources if cited_sources else sources[:5]

    if not display_sources:
        return

    cols = st.columns(2)
    for i, paper in enumerate(display_sources):
        # Recover 1-based index in the original sources list for anchor link
        try:
            orig_idx = sources.index(paper) + 1
        except ValueError:
            orig_idx = i + 1

        title = paper.get("Başlık") or paper.get("title") or "Bilinmiyor"
        year = paper.get("Yıl") or paper.get("year") or "?"
        authors = paper.get("Yazarlar") or paper.get("authors") or ""
        doi = paper.get("DOI") or paper.get("doi") or "-"
        link = paper.get("Link") or paper.get("link") or ""
        href = (
            link if link and link not in ["-", ""]
            else (f"https://doi.org/{doi}" if doi != "-" else "")
        )

        authors_short = (authors[:55] + "…") if len(authors) > 55 else authors
        title_safe = html.escape(str(title))
        authors_safe = html.escape(str(authors_short))

        link_html = (
            f'<a href="{href}" target="_blank" '
            f'style="color:#00D2FF; font-size:0.72rem; font-family:\'Space Mono\',monospace; '
            f'text-decoration:none;">→ Makaleye Git</a>'
            if href else ""
        )

        card_html = (
            f"<div id='cite-{orig_idx}' style='border-left:3px solid #CCFF00; "
            f"background:#0a0a0a; padding:10px 14px; margin-bottom:10px; "
            f"box-shadow:3px 3px 0 #333;'>"
            f"<span style='color:#CCFF00; font-family:\"Space Mono\",monospace; "
            f"font-size:0.72rem; font-weight:bold;'>[{orig_idx}]</span> "
            f"<b style='color:#F0F0F0; font-size:0.82rem; font-family:\"Space Mono\",monospace;'>"
            f"{title_safe}</b><br>"
            f"<span style='color:#777; font-size:0.72rem; font-family:\"Space Mono\",monospace;'>"
            f"{authors_safe} — {year}</span><br>"
            f"{link_html}"
            f"</div>"
        )

        with cols[i % 2]:
            st.markdown(card_html, unsafe_allow_html=True)


def render_research_intelligence_view() -> None:
    """Renders the Research Intelligence question-based synthesis interface."""

    # --- Header ---
    st.markdown(
        "<h2 style='font-family:\"Anton\",sans-serif; color:#CCFF00; letter-spacing:3px; "
        "font-size:2rem; margin-bottom:4px;'>🔬 ARAŞTIRMA ZEKASI</h2>"
        "<p style='color:#AAA; font-family:\"Space Mono\",monospace; font-size:0.85rem; "
        "margin-bottom:20px;'>Anahtar kelime yerine doğrudan bir <b>araştırma sorusu</b> yaz. "
        "Sistem literatürü tarar, atıflı bir Türkçe rapor sentezler.</p>",
        unsafe_allow_html=True,
    )

    if st.button("🔙 GERİ DÖN", key="back_btn_research", use_container_width=True):
        st.session_state.view_mode = "search"
        for key in ("ri_question", "ri_report", "ri_sources", "ri_triggered"):
            st.session_state.pop(key, None)
        st.rerun()

    st.markdown("<hr style='border-color: #333; margin: 18px 0;'>", unsafe_allow_html=True)

    # --- Neo-Brutalist textarea CSS ---
    st.markdown(
        """
        <style>
        .stTextArea textarea {
            border: 3px solid #CCFF00 !important;
            background-color: #0a0a0a !important;
            color: #F0F0F0 !important;
            font-family: 'Space Mono', monospace !important;
            box-shadow: 4px 4px 0px #00D2FF !important;
            border-radius: 0 !important;
            font-size: 0.88rem !important;
        }
        .stTextArea textarea:focus {
            border-color: #00D2FF !important;
            box-shadow: 4px 4px 0px #CCFF00 !important;
            outline: none !important;
        }
        .stTextArea label {
            font-family: 'Space Mono', monospace !important;
            color: #CCFF00 !important;
            font-size: 0.85rem !important;
            font-weight: bold !important;
            letter-spacing: 1px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- Question input ---
    default_q = st.session_state.get("ri_question", "")
    question = st.text_area(
        "Araştırma sorunuzu buraya yazın",
        value=default_q,
        height=120,
        placeholder=(
            "Örn: Rüzgar türbini kanatlarında yorulma analizi için hangi yöntemler kullanılıyor?\n"
            "Örn: What are the latest deep learning methods for structural health monitoring?"
        ),
        key="ri_question_input",
    )

    if st.button("🔬 ARAŞTIRMAYA BAŞLA", type="primary", use_container_width=True):
        if not question.strip():
            st.error("Lütfen bir araştırma sorusu girin.", icon="⚠️")
        else:
            st.session_state.ri_question = question.strip()
            st.session_state.ri_triggered = True
            st.session_state.pop("ri_report", None)
            st.session_state.pop("ri_sources", None)
            st.rerun()

    # --- Synthesis (runs after submit) ---
    if not st.session_state.get("ri_triggered", False):
        return

    current_question = st.session_state.get("ri_question", "")

    if "ri_report" not in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)
        loading_slot = st.empty()
        loading_slot.markdown(
            """
            <div style="text-align:center; padding:60px 20px;">
              <div style="font-family:'Anton',sans-serif; color:#CCFF00; font-size:2.4rem;
                          text-shadow:4px 4px 0 #00D2FF; margin-bottom:18px;">
                🔬 ARAŞTIRMA ZEKASI ÇALIŞIYOR...
              </div>
              <div style="font-family:'Space Mono',monospace; color:#AAA; font-size:0.88rem;
                          max-width:620px; margin:0 auto 28px; line-height:1.7;">
                Sorgu genişletiliyor &rarr; Literatür taranıyor &rarr; Rapor sentezleniyor<br>
                <span style="color:#555;">(~30–60 saniye sürebilir)</span>
              </div>
              <div style="border:4px solid #CCFF00; border-top-color:#00D2FF; border-radius:50%;
                          width:64px; height:64px; animation:ri_spin 0.9s linear infinite;
                          margin:0 auto;"></div>
              <style>@keyframes ri_spin{to{transform:rotate(360deg)}}</style>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            report, sources = asyncio.run(research_intelligence(current_question))
            st.session_state.ri_report = report
            st.session_state.ri_sources = sources
        except Exception as e:
            loading_slot.empty()
            st.error(f"Araştırma Zekası hatası: {e}", icon="🚨")
            return
        loading_slot.empty()

    report = st.session_state.get("ri_report", "")
    sources = st.session_state.get("ri_sources", [])

    if not report:
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # Build entire report as one HTML string (avoids broken-div Streamlit bug)
    report_html, cited_nums = _build_report_html(report)
    st.markdown(report_html, unsafe_allow_html=True)

    # --- Source grid (only cited papers, max 10) ---
    if sources:
        st.markdown(
            "<h3 style='font-family:\"Anton\",sans-serif; color:#CCFF00; "
            "letter-spacing:2px; font-size:1.1rem; margin-top:10px;'>"
            "📚 KULLANILAN KAYNAKLAR</h3>",
            unsafe_allow_html=True,
        )
        _render_source_grid(sources, cited_nums)
