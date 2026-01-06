from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Event
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, time
from chat.forms import ChatMessageForm

def event_list_view(request):
    search_form = EventSearchForm(request.GET)
    events = Event.objects.all().order_by('-created_at')
    
    # Filter for featured events (shown at the top, or separate section)
    featured_events = events.filter(is_featured=True)[:3]

    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        category = search_form.cleaned_data.get('category')
        status = search_form.cleaned_data.get('status')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')

        if search_query:
            events = events.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        if category:
            events = events.filter(category=category)
        if status:
            events = events.filter(status=status)
        if date_from:
            # Convert date to datetime at start of day
            dt_from = datetime.combine(date_from, time.min)
            events = events.filter(scheduled_date__gte=dt_from)
        if date_to:
             # Convert date to datetime at end of day
            dt_to = datetime.combine(date_to, time.max)
            events = events.filter(scheduled_date__lte=dt_to)

    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'featured_events': featured_events,
    }
    return render(request, 'events/event_list.html', context)

def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    chat_form = ChatMessageForm()
    context = {
        'event': event,
        'chat_form': chat_form,
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def event_create_view(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Check for title uniqueness for this user
            title = form.cleaned_data['title']
            if Event.objects.filter(creator=request.user, title=title).exists():
                form.add_error('title', 'Ja tens un esdeveniment amb aquest títol.')
            else:
                event = form.save(commit=False)
                event.creator = request.user
                event.save()
                messages.success(request, 'Esdeveniment creat correctament!')
                return redirect(event.get_absolute_url())
    else:
        form = EventCreationForm()
    
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Crear Esdeveniment'})

@login_required
def event_update_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.creator != request.user:
        messages.error(request, "No tens permís per editar aquest esdeveniment.")
        return redirect('events:event_detail', pk=pk)

    if request.method == 'POST':
        form = EventUpdateForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Esdeveniment actualitzat!')
            return redirect(event.get_absolute_url())
    else:
        form = EventUpdateForm(instance=event)
    
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Editar Esdeveniment', 'event': event})

@login_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.creator != request.user:
        messages.error(request, "No tens permís per eliminar aquest esdeveniment.")
        return redirect('events:event_detail', pk=pk)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Esdeveniment eliminat.')
        return redirect('events:event_list')
    
    return render(request, 'events/event_confirm_delete.html', {'event': event})

@login_required
def my_events_view(request):
    status = request.GET.get('status')
    events = Event.objects.filter(creator=request.user).order_by('-created_at')
    
    if status:
        events = events.filter(status=status)
        
    context = {
        'events': events,
        'current_status': status
    }
    return render(request, 'events/my_events.html', context)

def events_by_category_view(request, category):
    # Validate category exists
    valid_categories = [c[0] for c in Event.CATEGORY_CHOICES]
    if category not in valid_categories:
        messages.error(request, "Categoria no vàlida.")
        return redirect('events:event_list')

    events = Event.objects.filter(category=category).order_by('-created_at')
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'category_name': dict(Event.CATEGORY_CHOICES).get(category),
        'category_slug': category
    }
    return render(request, 'events/event_list.html', context)
