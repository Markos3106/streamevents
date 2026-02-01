from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
import datetime
from PIL import Image
import os

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('gaming', 'Gaming'),
        ('music', 'Música'),
        ('talk', 'Xerrades'),
        ('education', 'Educació'),
        ('sports', 'Esports'),
        ('entertainment', 'Entreteniment'),
        ('technology', 'Tecnologia'),
        ('art', 'Art i Creativitat'),
        ('other', 'Altres'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Programat'),
        ('live', 'En Directe'),
        ('finished', 'Finalitzat'),
        ('cancelled', 'Cancel·lat'),
    ]

    title = models.CharField(max_length=200, verbose_name="Títol de l'esdeveniment")
    description = models.TextField(verbose_name="Descripció detallada")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuari creador")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Categoria")
    scheduled_date = models.DateTimeField(verbose_name="Data i hora programada")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Estat actual")
    thumbnail = models.ImageField(upload_to='events/thumbnails/', blank=True, null=True, verbose_name="Imatge de portada")
    max_viewers = models.PositiveIntegerField(default=100, verbose_name="Màxim espectadors")
    is_featured = models.BooleanField(default=False, verbose_name="Esdeveniment destacat")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de creació")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualització")
    tags = models.CharField(max_length=500, blank=True, verbose_name="Etiquetes separades per comes")
    stream_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL del streaming/demo")

    # Camps per a cerca semàntica (embeddings)
    # Nota: Usem TextField en lloc de JSONField per compatibilitat amb djongo
    # El vector s'emmagatzema com a JSON string serialitzat
    embedding = models.TextField(blank=True, null=True, verbose_name="Vector d'embedding (JSON)")
    embedding_model = models.CharField(max_length=200, blank=True, null=True, verbose_name="Model d'embedding")
    embedding_updated_at = models.DateTimeField(blank=True, null=True, verbose_name="Última actualització embedding")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.thumbnail:
            try:
                img = Image.open(self.thumbnail.path)
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size)
                    img.save(self.thumbnail.path)
            except Exception as e:
                pass # Fail silently if image processing fails


    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Esdeveniment'
        verbose_name_plural = 'Esdeveniments'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})

    @property
    def is_live(self):
        return self.status == 'live'

    @property
    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_date > timezone.now()

    def get_duration(self):
        category_durations = {
            'gaming': 180,        # 3 hores
            'music': 90,          # 1.5 hores  
            'talk': 60,           # 1 hora
            'education': 120,     # 2 hores
            'sports': 150,        # 2.5 hores
            'entertainment': 120, # 2 hores
            'technology': 90,     # 1.5 hores
            'art': 120,           # 2 hores
            'other': 90,          # 1.5 hores
        }
        minutes = category_durations.get(self.category, 90)
        return datetime.timedelta(minutes=minutes)

    def get_tags_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def get_stream_embed_url(self):
        if not self.stream_url:
            return None
        
        url = self.stream_url
        
        # If input looks like full URL
        if "http" in url or "www" in url:
            # YouTube Logic
            if "youtube.com/watch" in url:
                video_id = url.split("v=")[1].split("&")[0]
                return f"https://www.youtube.com/embed/{video_id}"
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
                return f"https://www.youtube.com/embed/{video_id}"
                
            # Twitch Logic
            elif "twitch.tv/" in url:
                channel_name = url.split("twitch.tv/")[1].split("/")[0]
                return f"https://player.twitch.tv/?channel={channel_name}&parent=localhost&parent=127.0.0.1"
                
        # Assume it's a raw YouTube Video ID if no http/www and length is reasonable (approx 11 chars)
        elif len(url) > 0:
             return f"https://www.youtube.com/embed/{url}"

        return None
