# users/forms.py
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Aquest email ja està registrat.")
        return email

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "display_name", "bio", "avatar")
        widgets = {
            "bio": forms.Textarea(attrs={"rows":3}),
            "avatar": forms.FileInput()
        }

class CustomAuthenticationForm(forms.Form):
    username = forms.CharField(label="Usuari o email")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    raise ValidationError("Usuari o contrasenya incorrectes.")
            else:
                username = username_or_email

            user = authenticate(self.request, username=username, password=password)
            if user is None:
                raise ValidationError("Usuari o contrasenya incorrectes.")
            self.user_cache = user

        return self.cleaned_data

    def get_user(self):
        return self.user_cache
