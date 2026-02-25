import asyncio
import httpx

GROQ_API_KEY = "gsk_HIDDEN"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def test():
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [
            {"role": "system", "content": "hello"},
            {"role": "user", "content": "hi"}
        ],
        "temperature": 0.2,
        "max_tokens": 1500
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GROQ_API_URL, 
            headers=headers, 
            json=payload, 
            timeout=10.0
        )
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)

asyncio.run(test())
