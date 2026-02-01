# -*- coding: utf-8 -*-
"""
Configuració de l'aplicació SemanticSearch.
"""
from django.apps import AppConfig


class SemanticSearchConfig(AppConfig):
    """Configuració de l'app de cerca semàntica."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "semantic_search"
    verbose_name = "Cerca Semàntica"
