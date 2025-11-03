# Fichier : core/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')), # Le seul chemin défini en dehors de l'admin
]