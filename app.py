"""
app.py — Entry Point & Router for Akademik Pusula

Responsibilities (ONLY):
  1. GA4 root injection (must run before any st.* call)
  2. st.set_page_config (must be the first Streamlit command)
  3. PWA setup (service worker + manifest injection)
  4. CSS loading
  5. Session state initialisation
  6. Logo render
  7. View routing  →  focus / global_chat / search
  8. Footer

All UI and business logic lives in views/ and utils/.
"""
import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from utils.logger import logger

# ---------------------------------------------------------------------------
# 1. GA4 Root Injection — runs before any Streamlit command
# ---------------------------------------------------------------------------

def inject_ga_root() -> None:
    """Injects the GA4 tracking script into Streamlit's static index.html.

    This is a one-time write per container lifetime. The check for the GA_ID
    string prevents double-injection on hot-reloads.
    """
    GA_ID = "G-YHN57XNL0S"
    index_path = Path(st.__file__).parent / "static" / "index.html"
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        if GA_ID not in html_content:
            ga_script = f"""
            <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
            <script>
              window.dataLayer = window.dataLayer || [];
              function gtag(){{dataLayer.push(arguments);}}
              gtag('js', new Date());
              gtag('config', '{GA_ID}');
              window.sendGAEvent = function(eventName, params) {{
                  gtag('event', eventName, params);
              }};
            </script>
            """
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_content.replace("<head>", f"<head>\n{ga_script}"))
    except Exception as e:
        logger.error(f"GA4 root injection failed (non-critical): {e}")


inject_ga_root()

# ---------------------------------------------------------------------------
# 2. Page config — MUST be the very first st.* call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Akademik Pusula",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# track_ga_event is imported after set_page_config (Streamlit initialisation order)
from components.ui_components import track_ga_event  # noqa: E402

# ---------------------------------------------------------------------------
# 3. PWA setup (service worker + manifest)
# ---------------------------------------------------------------------------

components.html(
    """
    <script>
      if ('serviceWorker' in window.parent.navigator) {
        window.parent.navigator.serviceWorker
          .register('/app/static/sw.js')
          .then(function(reg) {
            console.log('ServiceWorker registered, scope:', reg.scope);
          })
          .catch(function(err) {
            console.log('ServiceWorker registration failed:', err);
          });
      }

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
    height=0,
)

# ---------------------------------------------------------------------------
# 4. CSS loading
# ---------------------------------------------------------------------------

def load_css(file_path: str) -> None:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css(os.path.join(os.path.dirname(__file__), "assets", "style.css"))
st.markdown(
    "<style>div[data-testid='stDataFrame'] { overflow-x: auto; max-width: 100%; }</style>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 5. Session state initialisation
# ---------------------------------------------------------------------------

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "search"

# ---------------------------------------------------------------------------
# 6. Logo
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="logo-container">
        <h1 class="logo-text"><span class="shift-left">AKADEMİK</span><br>PUSULA</h1>
        <div class="logo-subtext">AKADEMİK LİTERATÜR. SANSÜRSÜZ VE LİMİTSİZ.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 7. View router
# ---------------------------------------------------------------------------

if st.session_state.view_mode == "focus":
    from views.focus_view import render_focus_view
    render_focus_view()

elif st.session_state.view_mode == "global_chat":
    from views.global_chat_view import render_global_chat_view
    render_global_chat_view()

elif st.session_state.view_mode == "research":
    from views.research_intelligence_view import render_research_intelligence_view
    render_research_intelligence_view()

else:
    from views.search_view import render_search_view
    render_search_view()

# ---------------------------------------------------------------------------
# 8. Footer (hidden in focus and global_chat modes)
# ---------------------------------------------------------------------------

