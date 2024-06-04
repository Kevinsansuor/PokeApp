# views.py

from django.shortcuts import render
import requests
from .models import Pokemon_main, Pokemon_main_especies
import logging
from django.db.models import Q

def pokemon_search(request):
    query = request.GET.get('query')
    pokemon_data = None
    error_message = None
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    if query:
        # Perform a case-insensitive search on both the name and unique_id fields
        pokemon_obj = Pokemon_main.objects.filter(
            Q(name__iexact=query) | Q(unique_id=query)).first()


        if pokemon_obj:
            # If the Pokemon data exists, return it
            logging.info(f'busqueda de {query} en base de datos')

            pokemon_data = {
                'name': pokemon_obj.name,
                'id': pokemon_obj.unique_id,
                'description': pokemon_obj.description,
                'possible_values': pokemon_obj.possible_values,
                'image': pokemon_obj.image,
                'best_stat': pokemon_obj.best_stat,
                'best_stat_value': pokemon_obj.best_stat_value,
            }

            if not pokemon_data['name'] or not pokemon_data['id']:
                error_message = 'Invalid Pokemon data.'

        else:
            # If the Pokemon data does not exist, perform an API request
            if query.isdigit():
                pokemon_id = int(query)
                if pokemon_id > 151:
                    error_message = 'Solo se pueden buscar pokemones de primera generación.'
                else:
                    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}')
                    if response.status_code == 200:
                        data = response.json()
                        pokemon_data, error_message = fetch_pokemon_data(pokemon_id)
                    else:
                        error_message = 'Pokémon no encontrado.'
            else:
                response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{query.lower()}')
                if response.status_code == 200:
                    data = response.json()
                    if data['id'] > 151:
                        pokemon_data = None
                        error_message = 'Solo se pueden buscar pokemones de primera generación.'
                    else:
                        pokemon_data, error_message = fetch_pokemon_data(data['id'])
                else:
                    error_message = f'Lo sentimos no hay coincidencias para el Pokemon: ', query

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



def get_species_description(species_data):
    for flavor_text in species_data['flavor_text_entries']:
        if flavor_text['language']['name'] == 'es':
            return flavor_text['flavor_text']
    return 'No se ha encontrado una descripción para esta especie de Pokémon.'


def pokemon_species(request):
    query = request.GET.get('query')
    pokemon_data = None

    if query:
        # Buscar el Pokémon en la base de datos local
        pokemon_obj = Pokemon_main_especies.objects.filter(species__iexact=query).first()

        if pokemon_obj:
            # Si se encuentra el Pokémon, obtener su especie
            pokemon_data = {
                'name': pokemon_obj.name,
                'species': pokemon_obj.species
            }
        else:
            # Si no se encuentra en la base de datos, buscar en la API
            pokemon_data = fetch_pokemon_data_from_api(query)
            if pokemon_data:
                # Guardar los datos del Pokémon en la base de datos
                save_pokemon_data_to_database(pokemon_data)

    return render(request, 'species.html', {'pokemon_data': pokemon_data})

def fetch_pokemon_data_from_api(pokemon_name):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}')
    if response.status_code == 200:
        data = response.json()
        species_url = data['species']['url']
        species_response = requests.get(species_url)
        if species_response.status_code == 200:
            species_data = species_response.json()
            species_name = None
            for flavor_text in species_data['flavor_text_entries']:
                if flavor_text['language']['name'] == 'es':
                    species_name = flavor_text['flavor_text']
                    break
            if species_name:
                return {'name': pokemon_name, 'species': species_name, 'image': data['sprites']['front_default']}
    return None

def save_pokemon_data_to_database(pokemon_data):
    new_pokemon = Pokemon_main_especies(name=pokemon_data['name'], species=pokemon_data['species'])
    new_pokemon.save()
