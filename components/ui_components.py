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
    """Renders a single article card with citation and buttons."""
    borderColor = "#CCFF00" if pd.notna(row.get("Sci-Hub Linki")) else "#555"
    boxShadowColor = "#00D2FF" if pd.notna(row.get("Sci-Hub Linki")) else "#333"
    
    apa_ref_text = format_apa_7(
        str(row.get('Yazarlar', '')), 
        str(row.get('Yıl', '')), 
        str(row.get('Başlık', '')), 
        str(row.get('Kaynak', '')), 
        str(row.get('DOI', '-'))
    )
    
    
    # URL ve Buton HTML'leri (Now handled natively via Streamlit below)
    import urllib.parse
    clean_doi = ""
    if pd.notna(row.get('DOI')) and row.get('DOI') != "-":
        clean_doi = str(row['DOI']).replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
    query_str = clean_doi if clean_doi else urllib.parse.quote_plus(str(row.get('Başlık', '')))
    sci_hub_href = row.get('Sci-Hub Linki') if pd.notna(row.get('Sci-Hub Linki')) else "https://sci-hub.se"
    annas_archive_link = f"https://annas-archive.li/search?q={query_str}"
    libgen_link = f"https://libgen.li/index.php?req={query_str}"
    
    # HTML string using brutalist aesthetic
    html_content = f"""<div style="border: 4px solid {borderColor}; background-color: #111; padding: 25px; border-radius: 0; box-shadow: 8px 8px 0px {boxShadowColor}; margin-bottom: 30px;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
<h2 style="margin: 0; padding: 0; font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px; color: #FFF; font-size: 2.2rem; line-height: 1.1;">{row['Başlık']}</h2>
<div style="background-color: #050505; color: #CCFF00; padding: 5px 12px; border: 2px solid #CCFF00; font-family: 'Space Mono', monospace; font-size: 1.05rem; font-weight: bold; white-space: nowrap; height: fit-content; margin-left:15px; box-shadow: 4px 4px 0px #050505;">
📝 DOI: {row.get('DOI', '-')}
</div>
</div>
<p style="color: #00D2FF; font-family: 'Space Mono', monospace; font-weight: bold; font-size: 1.1rem; border-bottom: 2px dashed #444; padding-bottom: 15px; margin-bottom: 15px;">
📍 Kaynak: {row['Kaynak']} &nbsp;&nbsp;|&nbsp;&nbsp; 📅 Yıl: {row['Yıl']} &nbsp;&nbsp;|&nbsp;&nbsp; 🔒 Erişim: {row['Erişim Durumu']}
</p>
<p style="color: #CCC; font-size: 1rem; line-height: 1.6; font-family: 'Space Mono', monospace; margin-bottom: 25px;">
<b>Özet:</b> {str(row.get('Özet', ''))[:450]}{'...' if len(str(row.get('Özet', ''))) > 450 else ''}
</p>
<div style="background-color:#1a1c23; border:2px solid #555; padding:15px; margin-bottom:25px; border-left:4px solid #CCFF00;">
<p style="color:#FFF; font-family:'Bebas Neue',sans-serif; font-size:1.3rem; letter-spacing:1px; margin:0 0 5px 0;">📌 APA REFERANS FORMATI:</p>
<div style="display: flex; justify-content: space-between; align-items: center;">
<p style="color:#FFF; font-family:'Space Mono',monospace; font-size:0.95rem; margin:0; flex-grow: 1;">{apa_ref_text}</p>
</div>
</div>
</div>"""
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Native Streamlit Buttons mapped into columns to utilize exact styling seamlessly
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1.2, 1, 1.8])
    with col1:
        if row.get('Link') and row.get('Link') != '-':
            st.link_button("🌐 ORİJİNAL LİNK", url=row['Link'], use_container_width=True)
        else:
            st.button("🌐 LİNK YOK", disabled=True, key=f"orig_none_{index}", use_container_width=True)
    with col2:
        st.link_button("🔓 SCI-HUB", url=sci_hub_href, use_container_width=True)
    with col3:
        st.link_button("📚 ANNA'S ARCHIVE", url=annas_archive_link, use_container_width=True)
    with col4:
        st.link_button("🏴‍☠️ LIBGEN", url=libgen_link, use_container_width=True)
    with col5:
        if not is_focus_mode:
            if st.button("👁️ MAKALEYE ODAKLAN & AI İLE TARTIŞ", key=f"focus_btn_{index}", use_container_width=True):
                st.session_state.view_mode = 'focus'
                st.session_state.selected_paper = row
                st.session_state.chat_history = []
                st.rerun()
    
    # Native Streamlit code block for easy copy-pasting of citation right below
    st.code(apa_ref_text, language="text")
