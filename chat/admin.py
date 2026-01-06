from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin per gestionar els missatges del xat."""
    list_display = ['id', 'user', 'event', 'short_message', 'created_at', 'is_deleted', 'is_highlighted']
    list_filter = ['is_deleted', 'is_highlighted', 'created_at', 'event']
    search_fields = ['message', 'user__username', 'event__title']
    readonly_fields = ['created_at']
    list_editable = ['is_deleted', 'is_highlighted']
    ordering = ['-created_at']
    
    def short_message(self, obj):
        """Mostrar els primers 50 caràcters del missatge."""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Missatge'
