# coding=utf-8

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from .forms import UserCreationForm, LoginForm
from general.views import activate_language
from torneos.views import torneo_jugar, proximos_torneos
from django.http import HttpRequest
import requests
from django.contrib.auth.models import User
import os


def change_en(request):
    request.session['myLanguage'] = 'en'
    return redirect('home')

def change_es(request):
    request.session['myLanguage'] = 'es'
    return redirect('home')

def change_fr(request):
    request.session['myLanguage'] = 'fr'
    return redirect('home')
    
# Create your views here.
# Home page
def home(request):
    activate_language(request)
    jugar = False
    hayProximosTorneos = False
    proximosTorneos = []
    if request.user.is_authenticated:
        res = torneo_jugar(request.user.id)
        jugar = res['ok']
        proximosTorneos = proximos_torneos(request.user.id)
        hayProximosTorneos = (len(proximosTorneos) > 0)
        #print(proximosTorneos)
        #print(jugar)
    context = { 'jugar': jugar, 
                      'proximosTorneos': proximosTorneos, 
                      'hayProximosTorneos': hayProximosTorneos }
    return render(request, 'base/home_t.html', context)

# signup page
def user_signup(request):
    activate_language(request)
    if request.method == 'POST': 
        # fin edición
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        # crear el html para editar (comienzo de edición)
        form = UserCreationForm()
    # crear el html para editar o error en form
    return render(request, 'base/signup_t.html', {'form': form})

def user_api(request):
    activate_language(request)
    url = request.build_absolute_uri()
    print("La URL actual es:", url)
    url_obj = requests.utils.urlparse(url)

# Usa el método parse_qs para obtener el código de autorización
    authorization_code = url_obj.query.split("=")[1] if "code" in url_obj.query else None

    # Parámetros necesarios para la solicitud POST
    client_id = 'u-s4t2ud-22fb4fcdf0439caa173afadfabf30acd4f9721420251db03960f190416055657'
    client_secret = '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'
    code =  authorization_code
    redirect_uri = 'http://localhost:443/api'  # Tu URL de redirección

    if code:
        print(authorization_code)

        # Realiza la solicitud POST a la URL de token de acceso
        data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        }
        response = requests.post('https://api.intra.42.fr/oauth/token', data=data)

        print(response)
        if response.status_code == 200:
            token = response.json().get('access_token')

            headers = {
                'Authorization': f'Bearer {token}'
            }

            # Hace una solicitud GET para obtener los detalles del usuario
            response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)

            if response.status_code == 200:
                username = response.json().get('login')
                # Muestra el nombre de usuario
                print(f"Nombre de usuario: {username}")
                if not User.objects.filter(username=username).exists():
                    usuario = User.objects.create_user(username=username, email='correo@ejemplo.com', password=token)
                    usuario.save()
                user = authenticate(request, username=username, password=token)
                if user:
                    login(request, user)    
                    return redirect('home')
            else:
                print(f"Error al obtener detalles del usuario: {response.status_code} - {response.text}")
        else:
            print(f"Error al obtener token de acceso: {response.status_code} - {response.text}")
    else:
        print("No se encontró el código de autorización en la URL.")
    return render(request, 'base/home_t.html')

# login page
def user_login(request):
    activate_language(request)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)    
                return redirect('home')
    else:
        form = LoginForm()
    # crear el html para editar o error en form
    return render(request, 'base/login_t.html', {'form': form})

# logout page
def user_logout(request):
    activate_language(request)
    logout(request)
    return redirect('home')

