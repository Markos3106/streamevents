# -*- coding: utf-8 -*-
"""
Vistes per a cerca semàntica d'esdeveniments.
"""
import json
from django.shortcuts import render
from django.utils import timezone
from pymongo import MongoClient

from events.models import Event
from .services.embeddings import embed_text, model_name
from .services.ranker import cosine_top_k


def _get_events_from_mongo():
    """
    Obté events directament de MongoDB per evitar problemes amb djongo.
    
    Returns:
        Llista de diccionaris amb dades dels events.
    """
    client = MongoClient('mongodb://localhost:27017')
    db = client['streamevents_db']
    events = list(db['events_event'].find())
    client.close()
    return events


def _event_text(e: dict) -> str:
    """
    Genera el text representatiu d'un event per a cerques.
    """
    parts = [
        (e.get('title') or ''),
        (e.get('description') or ''),
        (e.get('category') or ''),
        (e.get('tags') or ''),
    ]
    return " | ".join([p.strip() for p in parts if p and p.strip()])


class EventProxy:
    """
    Proxy per simular un objecte Event amb dades de MongoDB.
    Permet accedir als atributs com si fos un model Django.
    """
    def __init__(self, data: dict):
        self._data = data
        # Mapejar camps principals
        self.pk = data.get('id') or data.get('_id')
        self.id = self.pk
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.category = data.get('category', '')
        self.tags = data.get('tags', '')
        self.status = data.get('status', 'scheduled')
        self.scheduled_date = data.get('scheduled_date')
        self.embedding = data.get('embedding')
        
    def get_absolute_url(self):
        return f"/events/{self.pk}/"
    
    def get_category_display(self):
        categories = {
            'gaming': 'Gaming',
            'music': 'Música',
            'talk': 'Xerrades',
            'education': 'Educació',
            'sports': 'Esports',
            'entertainment': 'Entreteniment',
            'technology': 'Tecnologia',
            'art': 'Art i Creativitat',
            'other': 'Altres',
        }
        return categories.get(self.category, self.category)
    
    def get_status_display(self):
        statuses = {
            'scheduled': 'Programat',
            'live': 'En Directe',
            'finished': 'Finalitzat',
            'cancelled': 'Cancel·lat',
        }
        return statuses.get(self.status, self.status)


def semantic_search(request):
    """
    Vista de cerca semàntica d'esdeveniments.
    """
    q = (request.GET.get("q") or "").strip()
    # Si el checkbox està marcat, envia future=1. Si no, no envia res.
    only_future = request.GET.get("future") == "1"

    results = []
    search_time = None
    
    # Obtenir events directament de MongoDB
    all_events_raw = _get_events_from_mongo()
    
    if q:
        import time
        start_time = time.time()
        
        # Generar embedding de la consulta
        q_vec = embed_text(q)
        
        # Convertir a proxies i filtrar
        all_events = [EventProxy(e) for e in all_events_raw]
        
        if only_future:
            # Usar datetime.now() sense timezone per compatibilitat amb MongoDB
            from datetime import datetime
            now = datetime.now()
            all_events = [
                e for e in all_events 
                if e.scheduled_date and e.scheduled_date >= now
            ]

        # Carregar candidats amb embeddings per fer ranking
        items = []
        for e in all_events:
            emb_str = e.embedding
            if emb_str and isinstance(emb_str, str) and emb_str.strip():
                try:
                    emb = json.loads(emb_str)
                    if isinstance(emb, list) and len(emb) > 0:
                        items.append((e, emb))
                except json.JSONDecodeError:
                    pass

        # Calcular ranking per similitud semàntica
        ranked = cosine_top_k(q_vec, items, k=20)
        results = ranked
        
        search_time = round((time.time() - start_time) * 1000, 2)  # ms

    # Comptar estadístiques
    events_with_emb_count = len([
        e for e in all_events_raw 
        if e.get('embedding') and str(e.get('embedding', '')).strip()
    ])
    
    context = {
        "query": q,
        "results": results,
        "only_future": only_future,
        "embedding_model": model_name(),
        "search_time": search_time,
        "total_events": len(all_events_raw),
        "events_with_embeddings": events_with_emb_count,
    }
    return render(request, "semantic_search/search.html", context)

