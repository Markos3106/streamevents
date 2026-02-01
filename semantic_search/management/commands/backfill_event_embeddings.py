# -*- coding: utf-8 -*-
"""
Comanda per generar embeddings per a events existents.

Aquesta comanda processa tots els events sense embedding (o tots si s'utilitza --force)
i genera els vectors d'embedding corresponents utilitzant el model de sentence-transformers.

Ús:
    python manage.py backfill_event_embeddings           # Només events sense embedding
    python manage.py backfill_event_embeddings --force   # Tots els events
    python manage.py backfill_event_embeddings --limit 100  # Limitat a 100 events
"""
import json
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event
from semantic_search.services.embeddings import embed_text, model_name


class Command(BaseCommand):
    """Genera i desa embeddings per a Events existents."""
    
    help = "Genera i desa embeddings per a Events que encara no en tenen."

    def add_arguments(self, parser):
        """Defineix els arguments de la comanda."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recalcula embeddings encara que ja n'hi hagi",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limita el nombre d'events a processar (0 = tots)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Mostra informació detallada de cada event processat",
        )

    def handle(self, *args, **options):
        """Executa la generació d'embeddings."""
        force = options["force"]
        limit = options["limit"]
        verbose = options["verbose"]

        self.stdout.write(
            self.style.NOTICE(f"🔍 Model d'embeddings: {model_name()}")
        )

        # Obtenir tots els events i filtrar en Python
        # (djongo no suporta bé filtering sobre JSONField ni alguns order_by)
        all_events = list(Event.objects.all())
        
        if not force:
            # Només events sense embedding (filtratge en Python)
            # Ara embedding és un TextField amb JSON string
            events_to_process = [
                e for e in all_events 
                if not e.embedding or e.embedding.strip() == ''
            ]
            self.stdout.write(
                self.style.NOTICE(f"📌 Mode: només events sense embedding")
            )
        else:
            events_to_process = all_events
            self.stdout.write(
                self.style.WARNING(f"⚠️  Mode: recalcular TOTS els embeddings")
            )

        total_to_process = len(events_to_process)
        self.stdout.write(f"📊 Events a processar: {total_to_process}")

        if limit and limit > 0:
            events_to_process = events_to_process[:limit]
            self.stdout.write(f"🔢 Limitat a: {limit} events")

        processed = 0
        skipped = 0
        errors = 0

        for e in events_to_process:
            # Construir text representatiu de l'event
            text_parts = [
                (e.title or "").strip(),
                (e.description or "").strip(),
                (e.category or "").strip(),
                (e.tags or "").strip(),
            ]
            text = " | ".join([p for p in text_parts if p])

            if not text:
                if verbose:
                    self.stdout.write(
                        self.style.WARNING(f"  ⏭️  [{e.pk}] Sense text processable")
                    )
                skipped += 1
                continue

            try:
                # Generar embedding
                vec = embed_text(text)
                
                if not vec:
                    skipped += 1
                    continue
                
                # Actualitzar event (serialitzar embedding a JSON string)
                e.embedding = json.dumps(vec)
                e.embedding_model = model_name()
                e.embedding_updated_at = timezone.now()
                e.save(update_fields=["embedding", "embedding_model", "embedding_updated_at"])
                
                processed += 1
                
                if verbose:
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ [{e.pk}] {e.title[:50]}...")
                    )
                elif processed % 10 == 0:
                    self.stdout.write(f"  Processats: {processed}...")
                    
            except Exception as ex:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f"  ❌ [{e.pk}] Error: {str(ex)}")
                )

        # Resum final
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS(f"✅ Embeddings generats: {processed}"))
        if skipped:
            self.stdout.write(self.style.WARNING(f"⏭️  Events saltats: {skipped}"))
        if errors:
            self.stdout.write(self.style.ERROR(f"❌ Errors: {errors}"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
