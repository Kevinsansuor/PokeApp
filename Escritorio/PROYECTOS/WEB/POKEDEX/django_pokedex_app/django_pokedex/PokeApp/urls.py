from django.urls import path
from . import views


urlpatterns = [
    path('', views.pokemon_search, name='pokemon_search'),
]



