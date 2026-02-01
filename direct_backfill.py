# -*- coding: utf-8 -*-
"""
Script directe per generar embeddings utilitzant pymongo.
Bypassa djongo per evitar problemes de compatibilitat.

Ús:
    python direct_backfill.py
"""
import json
import os
import sys
from datetime import datetime

# Afegir el projecte al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from pymongo import MongoClient

# Importar el servei d'embeddings
from semantic_search.services.embeddings import embed_text, model_name


def main():
    print(f"🔍 Model d'embeddings: {model_name()}")
    
    # Connectar directament a MongoDB
    client = MongoClient('mongodb://localhost:27017')
    db = client['streamevents_db']
    events_collection = db['events_event']
    
    # Obtenir tots els events
    events = list(events_collection.find())
    print(f"📊 Events totals: {len(events)}")
    
    # Filtrar events sense embedding
    events_to_process = [
        e for e in events 
        if not e.get('embedding') or str(e.get('embedding', '')).strip() == ''
    ]
    print(f"📌 Events sense embedding: {len(events_to_process)}")
    
    processed = 0
    errors = 0
    
    for event in events_to_process:
        # Construir text representatiu
        text_parts = [
            (event.get('title') or '').strip(),
            (event.get('description') or '').strip(),
            (event.get('category') or '').strip(),
            (event.get('tags') or '').strip(),
        ]
        text = ' | '.join([p for p in text_parts if p])
        
        if not text:
            continue
        
        try:
            # Generar embedding
            vec = embed_text(text)
            
            if not vec:
                continue
            
            # Actualitzar directament a MongoDB
            events_collection.update_one(
                {'_id': event['_id']},
                {
                    '$set': {
                        'embedding': json.dumps(vec),
                        'embedding_model': model_name(),
                        'embedding_updated_at': datetime.now()
                    }
                }
            )
            
            processed += 1
            print(f"  ✅ {event.get('title', 'N/A')[:50]}...")
            
        except Exception as ex:
            errors += 1
            print(f"  ❌ Error: {str(ex)}")
    
    print("")
    print("=" * 50)
    print(f"✅ Embeddings generats: {processed}")
    if errors:
        print(f"❌ Errors: {errors}")
    print("=" * 50)
    
    client.close()


if __name__ == '__main__':
    main()
