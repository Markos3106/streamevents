# -*- coding: utf-8 -*-
"""
Parser de consultes per extreure filtres simples.

Mòdul opcional per extreure filtres com dates o ciutats
de les consultes de cerca semàntica.
"""
import re
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


def parse_query(query: str) -> Dict[str, Any]:
    """
    Analitza una consulta i extreu filtres simples.
    
    Args:
        query: Consulta de l'usuari.
        
    Returns:
        Diccionari amb:
            - 'clean_query': consulta sense els filtres extrets
            - 'filters': diccionari de filtres trobats
    """
    filters: Dict[str, Any] = {}
    clean_query = query
    
    # Detectar patrons temporals comuns en català/castellà
    temporal_patterns = {
        r'\bavui\b': 'today',
        r'\bdemà\b': 'tomorrow', 
        r'\bhoy\b': 'today',
        r'\bmañana\b': 'tomorrow',
        r'\baquesta setmana\b': 'this_week',
        r'\beste cap de setmana\b': 'weekend',
        r'\bel fin de semana\b': 'weekend',
        r'\bpropers dies\b': 'next_days',
    }
    
    for pattern, time_filter in temporal_patterns.items():
        if re.search(pattern, query, re.IGNORECASE):
            filters['time_filter'] = time_filter
            clean_query = re.sub(pattern, '', clean_query, flags=re.IGNORECASE)
            break
    
    # Netejar espais múltiples
    clean_query = re.sub(r'\s+', ' ', clean_query).strip()
    
    return {
        'clean_query': clean_query,
        'filters': filters
    }


def get_date_range(time_filter: Optional[str]) -> Optional[tuple]:
    """
    Converteix un filtre temporal en un rang de dates.
    
    Args:
        time_filter: Identificador del filtre temporal.
        
    Returns:
        Tupla (start_date, end_date) o None si no hi ha filtre.
    """
    if not time_filter:
        return None
        
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    ranges = {
        'today': (today, today + timedelta(days=1)),
        'tomorrow': (today + timedelta(days=1), today + timedelta(days=2)),
        'this_week': (today, today + timedelta(days=7)),
        'weekend': _get_weekend_range(today),
        'next_days': (today, today + timedelta(days=3)),
    }
    
    return ranges.get(time_filter)


def _get_weekend_range(today: datetime) -> tuple:
    """Calcula el rang del proper cap de setmana."""
    # Trobar el proper dissabte
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0 and today.weekday() != 5:
        days_until_saturday = 7
    saturday = today + timedelta(days=days_until_saturday)
    sunday_end = saturday + timedelta(days=2)
    return (saturday, sunday_end)
