from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from events.models import Event
from .models import ChatMessage
from .forms import ChatMessageForm


@login_required
@require_POST
def chat_send_message(request, event_pk):
    """
    Vista per enviar missatges al xat.
    Retorna JSON amb les dades del missatge o errors.
    """
    # Obtenir l'esdeveniment (404 si no existeix)
    event = get_object_or_404(Event, pk=event_pk)
    
    # Verificar que l'esdeveniment està en directe
    if event.status != 'live':
        return JsonResponse({
            'success': False,
            'errors': {'event': 'El xat només està disponible quan l\'esdeveniment està en directe.'}
        }, status=400)
    
    # Processar el formulari
    form = ChatMessageForm(request.POST)
    
    if form.is_valid():
        # Crear missatge (commit=False)
        message = form.save(commit=False)
        message.user = request.user
        message.event = event
        message.save()
        
        # Retornar JsonResponse amb les dades del missatge
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'user': message.user.username,
                'display_name': message.get_user_display_name(),
                'message': message.message,
                'created_at': message.get_time_since(),
                'can_delete': message.can_delete(request.user),
                'is_highlighted': message.is_highlighted,
            }
        })
    else:
        # Retornar JsonResponse amb els errors
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


def chat_load_messages(request, event_pk):
    """
    Vista per carregar missatges del xat.
    Retorna JSON amb la llista de missatges.
    """
    # Obtenir l'esdeveniment
    event = get_object_or_404(Event, pk=event_pk)
    
    # Filtrar missatges: event, is_deleted=False
    # NO utilitzar select_related() amb MongoDB
    messages_qs = ChatMessage.objects.filter(
        event=event,
        is_deleted=False
    ).order_by('created_at')[:50]
    
    # Crear llista de diccionaris
    messages_list = []
    for msg in messages_qs:
        messages_list.append({
            'id': msg.id,
            'user': msg.user.username,
            'display_name': msg.get_user_display_name(),
            'message': msg.message,
            'created_at': msg.get_time_since(),
            'can_delete': msg.can_delete(request.user) if request.user.is_authenticated else False,
            'is_highlighted': msg.is_highlighted,
        })
    
    return JsonResponse({'messages': messages_list})


@login_required
@require_POST
def chat_delete_message(request, message_pk):
    """
    Vista per eliminar un missatge (soft delete).
    Retorna JSON amb èxit o error.
    """
    # Obtenir el missatge
    message = get_object_or_404(ChatMessage, pk=message_pk)
    
    # Verificar permisos amb can_delete()
    if not message.can_delete(request.user):
        return JsonResponse({
            'success': False,
            'error': 'No tens permís per eliminar aquest missatge.'
        }, status=403)
    
    # Marcar is_deleted=True (soft delete)
    message.is_deleted = True
    message.save()
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def chat_highlight_message(request, message_pk):
    """
    Vista per destacar/desdestacar un missatge.
    Només el creador de l'esdeveniment pot fer-ho.
    """
    # Obtenir el missatge
    message = get_object_or_404(ChatMessage, pk=message_pk)
    
    # Verificar que l'usuari és el creador de l'esdeveniment
    if request.user != message.event.creator:
        return JsonResponse({
            'success': False,
            'error': 'Només el creador de l\'esdeveniment pot destacar missatges.'
        }, status=403)
    
    # Toggle is_highlighted
    message.is_highlighted = not message.is_highlighted
    message.save()
    
    return JsonResponse({
        'success': True,
        'is_highlighted': message.is_highlighted
    })
