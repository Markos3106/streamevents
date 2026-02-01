# -*- coding: utf-8 -*-
"""
Tests per a l'aplicació de cerca semàntica.
"""
from django.test import TestCase, Client
from django.urls import reverse

from events.models import Event
from users.models import CustomUser
from semantic_search.services.embeddings import embed_text, model_name
from semantic_search.services.ranker import cosine_top_k


class EmbeddingsServiceTest(TestCase):
    """Tests per al servei d'embeddings."""
    
    def test_embed_text_returns_list(self):
        """Verifica que embed_text retorna una llista de floats."""
        result = embed_text("concert de música")
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        self.assertIsInstance(result[0], float)
    
    def test_embed_empty_text_returns_empty(self):
        """Verifica que text buit retorna llista buida."""
        result = embed_text("")
        self.assertEqual(result, [])
        
        result = embed_text(None)
        self.assertEqual(result, [])
        
        result = embed_text("   ")
        self.assertEqual(result, [])
    
    def test_model_name_returns_string(self):
        """Verifica que model_name retorna el nom del model."""
        result = model_name()
        self.assertIsInstance(result, str)
        self.assertIn("paraphrase-multilingual", result)


class RankerServiceTest(TestCase):
    """Tests per al servei de ranking."""
    
    def test_cosine_top_k_empty_query(self):
        """Verifica que consulta buida retorna llista buida."""
        result = cosine_top_k([], [("obj", [0.1, 0.2])], k=5)
        self.assertEqual(result, [])
    
    def test_cosine_top_k_ordering(self):
        """Verifica que els resultats s'ordenen per similitud."""
        query = [1.0, 0.0, 0.0]
        items = [
            ("low", [0.1, 0.9, 0.0]),
            ("high", [0.9, 0.1, 0.0]),
            ("medium", [0.5, 0.5, 0.0]),
        ]
        result = cosine_top_k(query, items, k=3)
        
        # "high" hauria de ser primer (més similar a query)
        self.assertEqual(result[0][0], "high")
        self.assertEqual(result[2][0], "low")
    
    def test_cosine_top_k_respects_k(self):
        """Verifica que es respecta el límit k."""
        query = [1.0, 0.0]
        items = [(f"item{i}", [1.0, 0.0]) for i in range(10)]
        result = cosine_top_k(query, items, k=5)
        self.assertEqual(len(result), 5)
    
    def test_cosine_top_k_skips_empty_embeddings(self):
        """Verifica que items sense embedding es salten."""
        query = [1.0, 0.0]
        items = [
            ("valid", [1.0, 0.0]),
            ("no_emb", None),
            ("empty", []),
        ]
        result = cosine_top_k(query, items, k=5)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "valid")


class SemanticSearchViewTest(TestCase):
    """Tests per a la vista de cerca semàntica."""
    
    @classmethod
    def setUpTestData(cls):
        """Configura dades de test."""
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    def setUp(self):
        self.client = Client()
    
    def test_search_page_loads(self):
        """Verifica que la pàgina de cerca carrega correctament."""
        response = self.client.get(reverse("semantic_search:semantic"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "semantic_search/search.html")
    
    def test_search_with_query(self):
        """Verifica que la cerca amb query funciona."""
        response = self.client.get(
            reverse("semantic_search:semantic"),
            {"q": "concert música"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("query", response.context)
        self.assertEqual(response.context["query"], "concert música")
