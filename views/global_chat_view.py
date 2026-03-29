"""
Global Chat View — renders the independent AI advisor mode.

Activated when st.session_state.view_mode == "global_chat".

Session state keys consumed / produced:
    view_mode           (str)   — set to "search" on back-button press
    chat_history_global (list)  — global chat message list
"""
import asyncio

import streamlit as st

from components.ui_components import track_ga_event
from utils.ai_manager import chat_with_paper_consensus

# Fixed context injected for the general-knowledge AI session
_GLOBAL_CHAT_CONTEXT = (
    "Bu bir bağımsız danışmanlık oturumudur. Özel bir makale sunulmamıştır. "
    "Kullanıcının sorusuna tamamen devasa mühendislik kültürünü ve akademik bilgini "
    "('💡 BAĞIMSIZ AI YORUMU' olarak veya genel bilgi olarak) kullanarak yanıt ver."
)

_WELCOME_MESSAGE = (
    "Merhaba! Ben Akademik Pusula Genel Kurulu. Mühendislik kütüphaneleri, "
    "literatür taraması, veya herhangi bir akademik/teknik konu hakkında bana "
    "danışabilirsiniz. Size nasıl yardımcı olabilirim?"
)


def render_global_chat_view() -> None:
    """Renders the standalone AI council advisor chat interface."""
    st.markdown(
        "<h3 style='font-family:\"Anton\", sans-serif; color:#CCFF00; "
        "letter-spacing:2px;'>🏛️ BAĞIMSIZ AI DANIŞMANI (GENEL KURUL)</h3>",
        unsafe_allow_html=True,
    )

    if st.button("🔙 GERİ DÖN (ARAMA SONUÇLARI)", key="back_btn_global", use_container_width=True):
        st.session_state.view_mode = "search"
        if "chat_history_global" in st.session_state:
            del st.session_state.chat_history_global
        st.rerun()

    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)

    # --- Chat history initialisation ---
    if "chat_history_global" not in st.session_state:
        st.session_state.chat_history_global = [
            {"role": "assistant", "content": _WELCOME_MESSAGE}
        ]

    # --- Render chat history ---
    for message in st.session_state.chat_history_global:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Interactive chat input ---
    if prompt := st.chat_input("Genel Kurula akademik veya teknik bir soru sorun..."):
        st.session_state.chat_history_global.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Genel Kurul toplanıyor ve sorunuzu değerlendiriyor..."):
                answer = asyncio.run(
                    chat_with_paper_consensus(
                        paper_title="Bağımsız Mühendislik ve Akademik Danışmanlık",
                        paper_abstract=_GLOBAL_CHAT_CONTEXT,
                        user_question=prompt,
                    )
                )
                st.markdown(answer)

        st.session_state.chat_history_global.append(
            {"role": "assistant", "content": answer}
        )

        track_ga_event(
            "global_ai_interaction",
            {"question": prompt, "context": "global_chat"},
        )
