from django import forms
from .models import Event
from django.utils import timezone

class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date', 'thumbnail', 'max_viewers', 'tags', 'stream_url']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'max_viewers': forms.NumberInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'stream_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean_scheduled_date(self):
        date = self.cleaned_data.get('scheduled_date')
        if date and date < timezone.now():
            raise forms.ValidationError("La data programada no pot ser en el passat.")
        return date

    def clean_max_viewers(self):
        max_viewers = self.cleaned_data.get('max_viewers')
        if max_viewers and (max_viewers < 1 or max_viewers > 1000):
            raise forms.ValidationError("El màxim d'espectadors ha d'estar entre 1 i 1000.")
        return max_viewers

class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date', 'thumbnail', 'max_viewers', 'tags', 'status', 'stream_url']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'max_viewers': forms.NumberInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'stream_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean_scheduled_date(self):
        date = self.cleaned_data.get('scheduled_date')
        if self.instance.status == 'live' and date != self.instance.scheduled_date:
            raise forms.ValidationError("No es pot canviar la data si l'esdeveniment ja està en directe.")
        return date

class EventSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cercar...'}))
    category = forms.ChoiceField(choices=[('', 'Totes')] + Event.CATEGORY_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(choices=[('', 'Tots')] + Event.STATUS_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
