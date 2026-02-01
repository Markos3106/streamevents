# Serveis per a cerca semàntica
from .embeddings import embed_text, get_model, model_name
from .ranker import cosine_top_k

__all__ = ['embed_text', 'get_model', 'model_name', 'cosine_top_k']
