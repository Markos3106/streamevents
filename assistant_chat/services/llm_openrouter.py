import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openrouter/free" 

def generate(prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if not api_key:
        fallback = {
            "answer": "Falta configurar la clau d'OpenRouter (OPENROUTER_API_KEY) a l'arxiu .env o l'entorn.",
            "recommended_ids": [],
            "follow_up": ""
        }
        return json.dumps(fallback)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "StreamEvents",
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "top_p": 0.9,
    }
    
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if content.startswith("```"):
            lines = content.split('\n')
            if len(lines) > 2:
                content = '\n'.join(lines[1:-1]).strip()
        
        return content
    except Exception as e:
        print(f"Error calling OpenRouter: {e}")
        try:
             print(r.text)
        except:
             pass
        
        fallback = {
            "answer": "S'ha produït un error de connexió amb l'API d'OpenRouter. Revisa que tot estigui bé.",
            "recommended_ids": [],
            "follow_up": ""
        }
        return json.dumps(fallback)
