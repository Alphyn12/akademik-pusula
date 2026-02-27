import streamlit as st
import pandas as pd
from utils.citation import format_apa_7

def render_metrics(df: pd.DataFrame, sci_hub_base: str):
    """Renders the top key metric cards."""
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(f"<div class='metric-card'><h3>{len(df)}</h3><p>Makale Bulundu</p></div>", unsafe_allow_html=True)
    with col_m2:
        locked_count = df[df['Erişim Durumu'].str.contains('Kilitli', na=False)].shape[0] if not df.empty else 0
        st.markdown(f"<div class='metric-card'><h3>{locked_count}</h3><p>Erişime Kapalı</p></div>", unsafe_allow_html=True)
    with col_m3:
        scihub_count = df['Sci-Hub Linki'].notna().sum() if not df.empty and 'Sci-Hub Linki' in df.columns else 0
        st.markdown(f"<div class='metric-card'><h3 class='highlight-val'>{scihub_count}</h3><p>Sci-Hub Bypass Links</p></div>", unsafe_allow_html=True)
    
def render_article_card(row: pd.Series, index: int, is_focus_mode: bool = False):
    """Renders a single article card with citation and responsive components."""
    borderColor = "#00D2FF" if pd.notna(row.get("Sci-Hub Linki")) else "#555"
    
    apa_ref_text = format_apa_7(
        str(row.get('Yazarlar', '')), 
        str(row.get('Yıl', '')), 
        str(row.get('Başlık', '')), 
        str(row.get('Kaynak', '')), 
        str(row.get('DOI', '-'))
    )
    
    import urllib.parse
    clean_doi = ""
    if pd.notna(row.get('DOI')) and row.get('DOI') != "-":
        clean_doi = str(row['DOI']).replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
    query_str = clean_doi if clean_doi else urllib.parse.quote_plus(str(row.get('Başlık', '')))
    sci_hub_href = row.get('Sci-Hub Linki') if pd.notna(row.get('Sci-Hub Linki')) else "https://sci-hub.se"
    annas_archive_link = f"https://annas-archive.li/search?q={query_str}"
    libgen_link = f"https://libgen.li/index.php?req={query_str}"
    
    # Original Link Setup
    orig_link_html = f'<a href="{row.get("Link")}" target="_blank" class="action-badge badge-original">🌐 ORİJİNAL LİNK</a>' if row.get('Link') and row.get('Link') != '-' else '<span class="action-badge badge-none">🌐 LİNK YOK</span>'
    
    # Generate abstract with fallbacks
    abstract_text = str(row.get('Özet', ''))
    abstract_display = f"{abstract_text[:450]}..." if len(abstract_text) > 450 else abstract_text
    
    # New Responsive HTML using CSS classes defined in style.css
    html_content = f"""
<div class="brutalist-card" style="border: 4px solid {borderColor};">
    <div class="brutalist-card-header">
        <h2 class="brutalist-card-title">{row['Başlık']}</h2>
        <div class="doi-badge">📝 DOI: {row.get('DOI', '-')}</div>
    </div>
    
    <div class="brutalist-card-meta">
        <span>📍 Kaynak: {row['Kaynak']}</span>
        <span class="separator">|</span>
        <span>📅 Yıl: {row['Yıl']}</span>
        <span class="separator">|</span>
        <span>🔒 Erişim: {row['Erişim Durumu']}</span>
    </div>
    
    <p class="brutalist-card-summary">
        <b>Özet:</b> {abstract_display}
    </p>
    
    <div class="action-badges-container">
        {orig_link_html}
        <a href="{sci_hub_href}" target="_blank" class="action-badge badge-scihub">🔓 SCI-HUB</a>
        <a href="{annas_archive_link}" target="_blank" class="action-badge badge-annas">📚 ANNA'S ARCHIVE</a>
        <a href="{libgen_link}" target="_blank" class="action-badge badge-libgen">🏴‍☠️ LIBGEN</a>
    </div>
    
    <div style="background-color:#1a1c23; border:2px solid #555; padding:15px; margin-bottom:10px; border-left:4px solid #CCFF00;">
        <p style="color:#FFF; font-family:'Bebas Neue',sans-serif; font-size:1.3rem; letter-spacing:1px; margin:0 0 5px 0;">📌 APA REFERANS FORMATI:</p>
        <p style="color:#FFF; font-family:'Space Mono',monospace; font-size:0.95rem; margin:0; overflow-wrap: break-word;">{apa_ref_text}</p>
    </div>
</div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Only keep the large interactive Focus button as a Streamlit block 
    if not is_focus_mode:
        if st.button("👁️ MAKALEYE ODAKLAN & AI İLE TARTIŞ", key=f"focus_btn_{index}", use_container_width=True):
            st.session_state.view_mode = 'focus'
            st.session_state.selected_paper = row
            st.session_state.chat_history = []
            st.rerun()
            
    # Native Streamlit code block for easy copy-pasting of citation right below
    st.code(apa_ref_text, language="text")
