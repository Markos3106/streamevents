from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserUpdateForm
from django.contrib.auth import get_user_model

User = get_user_model()

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registre complet! Benvingut/da, {}".format(user.username))
            return redirect('users:profile')
        else:
            messages.error(request, "Hi ha errors en el formulari. Revisa les dades.")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == "POST":
        form = CustomAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # Ara sempre és un usuari vàlid
            messages.success(request, "Sessió iniciada correctament!")
            return redirect('users:profile')
        else:
            messages.error(request, "Usuari o contrasenya incorrectes.")
    else:
        form = CustomAuthenticationForm()
    return render(request, "registration/login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Sessió tancada correctament.")
    return redirect("users:login")

@login_required
def profile_view(request):
    return render(request, "users/profile.html")

@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualitzat correctament!")
            return redirect('users:profile')
        else:
            messages.error(request, "Hi ha errors en el formulari.")
    else:
        form = CustomUserUpdateForm(instance=user)
    return render(request, "users/edit_profile.html", {"form": form})

def public_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "users/public_profile.html", {"user": user})
