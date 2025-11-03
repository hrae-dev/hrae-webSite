# Fichier : Home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # La vue est mappée à l'URL racine de l'application 'home/'
]