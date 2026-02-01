# -*- coding: utf-8 -*-
"""
URLs per a l'aplicació de cerca semàntica.
"""
from django.urls import path
from .views import semantic_search

app_name = "semantic_search"

urlpatterns = [
    path("semantic/", semantic_search, name="semantic"),
]
