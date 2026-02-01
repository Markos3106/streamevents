# -*- coding: utf-8 -*-
"""
Servei d'embeddings per a cerca semàntica.

Aquest mòdul proporciona funcionalitats per carregar el model de sentence-transformers
i generar embeddings de text normalitzats.
"""
import threading
from sentence_transformers import SentenceTransformer

# Model multilingüe optimitzat per similitud semàntica
_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Lock per garantir thread-safety en la càrrega del model
_lock = threading.Lock()
_model = None


def get_model() -> SentenceTransformer:
    """
    Obté el model de SentenceTransformer.
    
    Utilitza càrrega lazy amb singleton thread-safe per evitar
    càrregues múltiples del model.
    
    Returns:
        SentenceTransformer: Model carregat i llest per usar.
    """
    global _model
    if _model is None:
        with _lock:
            # Double-check locking pattern
            if _model is None:
                _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_text(text: str) -> list[float]:
    """
    Genera un vector d'embedding normalitzat per al text donat.
    
    Args:
        text: Text a convertir en embedding.
        
    Returns:
        Llista de floats representant el vector d'embedding normalitzat.
        Retorna llista buida si el text és buit o None.
    """
    text = (text or "").strip()
    if not text:
        return []
    
    model = get_model()
    # normalize_embeddings=True fa que els vectors tinguin norma 1,
    # permetent calcular cosine similarity amb dot product
    vec = model.encode([text], normalize_embeddings=True)[0]
    return vec.tolist()


def model_name() -> str:
    """
    Retorna el nom del model d'embeddings utilitzat.
    
    Returns:
        Nom del model de SentenceTransformer.
    """
    return _MODEL_NAME
