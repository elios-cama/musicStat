import urllib.request

import PIL.Image
from django.shortcuts import render, redirect, HttpResponse
import requests
from django.urls import reverse
import io
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

        response_id = requests.get("https://api.deezer.com/user/me", params={"access_token": access_token})
        user_data = response_id.json()
        user_id = user_data["id"]

        request.session['user_id'] = user_id
        request.session['access_token'] = access_token
        return render(request, 'connected.html', {'access_token': access_token, 'code': code})
    else:
        return HttpResponse('Error: code not found in the callback.')


def fetching_most_liked_tracks(request):
    user_id = request.session.get('user_id')
    response = requests.get(f"https://api.deezer.com/user/{user_id}/tracks?index=0&limit=25").json()
    list_of_images = []
    for i in range(25):
        img = response['data'][i]['album']['cover_xl']
        with urllib.request.urlopen(img) as url:
            img_bytes = url.read()
        img = PIL.Image.open(io.BytesIO(img_bytes))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        list_of_images.append(img_bytes)

    # Create the collage
    collage = create_collage(1000, 1000, list_of_images)

    # Return the image as an HTTP response
    response = HttpResponse(content_type='image/png')
    response.write(collage.getvalue())
    return response


def create_collage(width, height, list_of_images):
    cols = 5
    rows = 5
    thumbnail_width = width // cols
    thumbnail_height = height // rows
    size = thumbnail_width, thumbnail_height
    new_im = PIL.Image.new('RGB', (width, height))
    ims = []
    for p in list_of_images:
        im = PIL.Image.open(p)
        im.thumbnail(size)
        ims.append(im)
    i = 0
    x = 0
    y = 0
    for col in range(cols):
        for row in range(rows):
            new_im.paste(ims[i], (x, y))
            i += 1
            y += thumbnail_height
        x += thumbnail_width
        y = 0

    img_bytes = io.BytesIO()
    new_im.save(img_bytes, format='PNG')
    return img_bytes
