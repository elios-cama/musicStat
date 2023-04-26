from django.shortcuts import render, redirect, HttpResponse
import requests
from django.urls import reverse

from musicStat import settings


def home(request):
    return render(request, 'home.html')


def generate(request):
    # The URL to redirect the user after authentication
    redirect_uri = request.build_absolute_uri('connected/')

    # The URL to start the OAuth2 authorization process with Deezer
    auth_url = f'https://connect.deezer.com/oauth/auth.php?app_id={570422}&redirect_uri={"https://elioscama.notion.site/Elios-Cama-806d4dd10"}&perms=basic_access,email&response_type=token'

    return redirect(auth_url)


def connected(request):
    return render(request, 'connected.html')


def deezer_auth(request):
    app_id = 570422
    redirect_uri = request.build_absolute_uri(reverse('deezer_callback'))
    auth_url = f'https://connect.deezer.com/oauth/auth.php?app_id={app_id}&redirect_uri={redirect_uri}&perms=basic_access,email'
    return redirect(auth_url)


def deezer_callback(request):
    code = request.GET.get('code')

    if code:
        access_token_url = f'https://connect.deezer.com/oauth/access_token.php?app_id={settings.DEEZER_APP_ID}&secret={settings.DEEZER_APP_SECRET}&code={code}'
        response = requests.get(access_token_url)
        access_token = response.text.split('=')[1].split('&')[0]

        # You can store the access token in the session, database, or use it for API calls.
        request.session['access_token'] = access_token
        return render(request, 'connected.html', {'access_token': access_token})
    else:
        return HttpResponse('Error: code not found in the callback.')
