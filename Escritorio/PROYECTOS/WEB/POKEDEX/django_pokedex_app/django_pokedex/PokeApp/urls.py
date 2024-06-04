from django.urls import path
from . import views


urlpatterns = [
    path('', views.pokemon_search, name='pokemon_search'),
    path('pokemon_species/', views.pokemon_species, name='pokemon_species'),
    path('pokemon_evolutions', views.pokemon_evolutions, name='pokemon_evolutions'),
]



