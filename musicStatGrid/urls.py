from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate, name='generate'),
    path('connected/', views.connected, name='connected'),
    path('deezer_auth/', views.deezer_auth, name='deezer_auth'),
    path('deezer_callback/', views.deezer_callback, name='deezer_callback'),
]
