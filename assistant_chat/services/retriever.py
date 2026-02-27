from django.utils import timezone
from events.models import Event
from semantic_search.services.embeddings import embed_text
from semantic_search.services.ranker import cosine_top_k
from django.db.models import Q

def build_event_text(e: Event) -> str:
    return " | ".join([
        (e.title or "").strip(),
        (e.description or "").strip(),
        (e.category or "").strip(),
        (e.tags or "").strip(),
    ]).strip()

def retrieve_events(query: str, only_future: bool = True, k: int = 8):
    q_vec = embed_text(query)

    qs = Event.objects.all()
    if only_future:
        qs = qs.filter(Q(scheduled_date__gte=timezone.now()) | Q(status='live'))

    items = []
    import json
    for e in qs.only("id", "title", "scheduled_date", "category", "tags", "embedding"):
        emb = getattr(e, "embedding", None)
        if isinstance(emb, str) and emb.strip():
            try:
                emb = json.loads(emb)
            except Exception:
                pass
        if isinstance(emb, list) and len(emb) > 0:
            items.append((e, emb))

    ranked = cosine_top_k(q_vec, items, k=max(k, 20))

    ranked = [(e, s) for (e, s) in ranked if s >= 0.25]

    return ranked[:k]
