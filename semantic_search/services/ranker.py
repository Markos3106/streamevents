# -*- coding: utf-8 -*-
"""
Servei de ranking per a cerca semàntica.

Aquest mòdul proporciona funcions per ordenar resultats segons
similitud cosinus entre vectors d'embedding.
"""
import numpy as np
from typing import TypeVar, List, Tuple, Optional

# Tipus genèric per als objectes a ordenar
T = TypeVar('T')


def cosine_top_k(
    query_vec: List[float],
    items: List[Tuple[T, Optional[List[float]]]],
    k: int = 20
) -> List[Tuple[T, float]]:
    """
    Ordena items per similitud cosinus amb el vector de consulta.
    
    Com que els vectors estan normalitzats (norma 1), el producte escalar
    és equivalent a la similitud cosinus.
    
    Args:
        query_vec: Vector d'embedding de la consulta.
        items: Llista de tuples (objecte, embedding) a ordenar.
        k: Nombre màxim de resultats a retornar.
        
    Returns:
        Llista de tuples (objecte, score) ordenada per score descendent.
        El score és la similitud cosinus (entre -1 i 1, típicament 0 a 1).
    """
    if not query_vec:
        return []
    
    q = np.array(query_vec, dtype=np.float32)
    
    # Verificar que el vector de consulta no és zero
    if np.linalg.norm(q) == 0:
        return []
    
    scored: List[Tuple[T, float]] = []
    
    for obj, emb in items:
        # Saltar items sense embedding vàlid
        if not emb:
            continue
            
        v = np.array(emb, dtype=np.float32)
        
        # Verificar dimensions i que no sigui vector zero
        if v.shape != q.shape or np.linalg.norm(v) == 0:
            continue
            
        # Dot product de vectors normalitzats = cosine similarity
        score = float(np.dot(q, v))
        scored.append((obj, score))
    
    # Ordenar per score descendent i retornar top-k
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
