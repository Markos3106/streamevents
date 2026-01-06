from django import forms
from .models import ChatMessage


# Llista de paraules prohibides per al filtre de moderació
FORBIDDEN_WORDS = [
    'idiota', 'imbecil', 'tonto', 'estupid',
    'merda', 'caga', 'cago',
    'puta', 'puto', 'cabron', 'cabro',
    'gilipollas', 'marica', 'maricon',
    'fill de puta', 'hijoputa',
]


class ChatMessageForm(forms.ModelForm):
    """Formulari per enviar missatges al xat."""
    
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Escriu el teu missatge...',
                'maxlength': 500,
            })
        }

    def clean_message(self):
        """
        Validació personalitzada del missatge:
        - Missatge no pot estar buit
        - Detectar paraules ofensives
        - Verificar longitud màxima
        """
        message = self.cleaned_data.get('message', '')
        
        # Netejar espais
        message = message.strip()
        
        # Verificar que no estigui buit
        if not message:
            raise forms.ValidationError("El missatge no pot estar buit.")
        
        # Verificar longitud màxima
        if len(message) > 500:
            raise forms.ValidationError("El missatge no pot superar els 500 caràcters.")
        
        # Detectar paraules ofensives
        message_lower = message.lower()
        for word in FORBIDDEN_WORDS:
            if word in message_lower:
                raise forms.ValidationError(
                    "El missatge conté paraules no permeses. "
                    "Si us plau, sigues respectuós amb la comunitat."
                )
        
        return message
