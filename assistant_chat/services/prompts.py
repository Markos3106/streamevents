import json

def build_prompt(user_message: str, candidates: list[dict]) -> str:
    context_json = json.dumps(candidates, ensure_ascii=False, indent=2)

    return f"""
Ets un assistent que recomana esdeveniments del lloc StreamEvents.
IMPORTANT:
- NOMÉS pots recomanar esdeveniments que apareguin al CONTEXT.
- No inventis esdeveniments, dates, ni URLs.
- Si no hi ha cap esdeveniment adequat, digues-ho i demana aclariments.

Respon en català i en aquest format JSON EXACTE:

{{
  "answer": "text curt amb recomanació",
  "recommended_ids": [1,2,3],
  "follow_up": "pregunta opcional per afinar (o buit)"
}}

CONTEXT (llista d'esdeveniments disponibles):
{context_json}

Petició de l'usuari: {user_message}
""".strip()
