import os
import httpx
import json
import streamlit as st

# Retrieve API key securely from Streamlit secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    # Fallback to environment variable or hardcoded if secrets not configured locally
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "gsk_HIDDEN")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# System prompt is given exactly as strictly requested by the prompt engineering instructions
CONSENSUS_SYSTEM_PROMPT = """[SYSTEM: YOU ARE THE "ACADEMIC COMPASS CONSENSUS ENGINE"]
You represent a synchronized assembly of three distinct AI experts working together to analyze an academic paper for a Mechanical Engineering student. Your ultimate goal is to provide unified, highly technical, and strictly accurate answers based ONLY on the provided paper's text/abstract.

[EXPERT PERSONAS IN THE ASSEMBLY]
1. Expert A (The Synthesizer - Llama 4): Focuses on the big picture, core hypotheses, and practical applications in manufacturing.
2. Expert B (The Data Miner - Qwen3): Extremely detail-oriented. Hunts for numerical parameters, material specs (e.g., steel grades, temperatures, hardness values in HRC/HB, tolerances), and testing equipment.
3. Expert C (The Critical Auditor - Llama 3.1): Acts as the devil's advocate. Checks for methodological flaws, statistical significance, and limitations.

[YOUR PROTOCOL FOR ANSWERING USER QUESTIONS]
When the user asks a question about the loaded paper, you must execute the following internal process before answering:
STEP 1 - GATHER: Extract relevant quotes or data from the paper.
STEP 2 - DEBATE: (Internal thought process) Expert A states the main finding. Expert B verifies the exact numbers. Expert C checks if the context supports this claim.
STEP 3 - CONSENSUS: Formulate a single, unified answer that represents the agreement of all three experts. 

[STRICT RULES FOR OUTPUT]
1. LANGUAGE: You must strictly communicate with the user in fluent, academic Turkish.
2. NO HALLUCINATION: If the paper does not contain the answer to the user's question, you must clearly state: "Bu bilgi mevcut makalede yer almamaktadır." Do not use outside knowledge to fill in the gaps unless the user explicitly asks you to guess.
3. STRUCTURE: Present your final answer using the following Neo-Brutalist structure:
   - 🎯 [ORTAK KARAR]: (The direct, synthesized answer to the user's question)
   - ⚙️ [TEKNİK VERİLER]: (Bullet points of exact numbers, formulas, or parameters mentioned)
   - 🛡️ [DENETÇİ NOTU]: (Any limitations, risks, or critical academic context about this specific finding)

"""

async def chat_with_paper_consensus(paper_title: str, paper_abstract: str, user_question: str) -> str:
    """Sends a request to Groq API using the consensus prompt architecture."""
    # Build complete system message including the dynamic input context
    dynamic_context = f"\n[INPUT CONTEXT]\nPAPER TITLE: {paper_title}\nPAPER ABSTRACT/TEXT: {paper_abstract}\n"
    full_system_prompt = CONSENSUS_SYSTEM_PROMPT + dynamic_context
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Create the payload explicitly using the requested Llama 3 wrapper model compatible on Groq
    payload = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_question}
        ],
        "temperature": 0.2, # Low temperature to prevent hallucination and stick strictly to the consensus logic
        "max_tokens": 1500
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GROQ_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"🚨 Üzgünüm, API bağlantısında geçici bir hata oluştu: {str(e)}"
