# views.py

from django.shortcuts import render
import requests
from .models import Pokemon_main

def pokemon_search(request):
    query = request.GET.get('query')
    pokemon_data = None
    error_message = None

    if query:
        
        # Verificar si la petición es un número
        if query.isdigit():
            pokemon_id = int(query)
            if pokemon_id > 151:
                error_message = 'Solo se pueden buscar pokemones de primera generación.'
                
            else:
                
                pokemon_obj = Pokemon_main.objects.filter(name__iexact=query).first()
        
                if pokemon_obj:
                # If the Pokemon data exists, return it
                    pokemon_data = {
                        'name': pokemon_obj.name,
                        'best_stat': pokemon_obj.best_stat,
                        'best_stat_value': pokemon_obj.best_stat_value,
                        'description': pokemon_obj.description,
                        'image': pokemon_obj.image,
                        'possible_values': pokemon_obj.possible_values,
                    }
                    
                    print(f'busqueda de', query, 'en base de datos')
                else:
                    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}')
                    if response.status_code == 200:
                        data = response.json()
                        pokemon_data = pokemon_data, error_message = fetch_pokemon_data(pokemon_id)
                    else:
                        error_message = 'Pokémon no encontrado.'
        else:
            
                # Verificar búsqueda por nombre
                    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{query.lower()}')
                    if response.status_code == 200:
                        data = response.json()
                        if data['id'] > 151:
                            pokemon_data = None
                            error_message = 'Solo se pueden buscar pokemones de primera generación.'
                        else:
                            pokemon_data = pokemon_data, error_message = fetch_pokemon_data(data['id'])

                    else:
                        error_message = f'Lo sentimos no hay coincidencias para el Pokemon: ' + query

    return render(request, 'index.html', {'pokemon_data': pokemon_data, 'error_message': error_message})

def fetch_pokemon_data(pokemon_id):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}')
    if response.status_code == 200:
        data = response.json()
        best_stat = max(data['stats'], key=lambda x: x['base_stat'])
        description = get_pokemon_description(data['species']['url'])
        possible_values = get_pokemon_possible_values(pokemon_id)
        
        pokemon_obj = Pokemon_main(
            name=data['name'],
            unique_id=data['id'],
            description=description,
            possible_values=possible_values,
            image=data['sprites']['front_default'],
            best_stat=best_stat['stat']['name'],
            best_stat_value=best_stat['base_stat'],
        )
        pokemon_obj.save()
        
        return {
            'name': data['name'],
            'best_stat': best_stat['stat']['name'],
            'best_stat_value': best_stat['base_stat'],
            'description': description,
            'image': data['sprites']['front_default'],
            'possible_values': possible_values,
        }, None
    return None, 'Pokémon no encontrado.'

def get_pokemon_description(species_url):
    response = requests.get(species_url)
    if response.status_code == 200:
        species_data = response.json()
        for entry in species_data['flavor_text_entries']:
            if entry['language']['name'] == 'es':
                return entry['flavor_text']
    return 'No se ha encontrado una descripción para este Pokemon.'

def get_pokemon_possible_values(pokemon_id):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}')
    if response.status_code == 200:
        data = response.json()
        stats = [stat['base_stat'] for stat in data['stats']]
        return ', '.join(map(str, stats))
    return 'Possible values not available.'
