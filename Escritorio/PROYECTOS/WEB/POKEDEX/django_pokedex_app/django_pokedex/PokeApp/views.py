# views.py

from django.db import IntegrityError
from django.shortcuts import redirect, render
import requests
from .models import Pokemon_main, Pokemon_main_especies, Pokemon_main_evolutions, Usuario, PageView
import logging
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.shortcuts import render
from django.http import HttpResponse



@csrf_protect
def crear_usuario(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        # Validación de datos
        if not full_name or not email or not phone or not password:
            return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'error': 'Correo electrónico inválido'}, status=400)

        # Manejo de creación y actualización de usuario
        usuario, created = Usuario.objects.get_or_create(email=email)
        
        usuario.name = full_name
        usuario.phone = phone
        usuario.password = make_password(password)
        usuario.save()

        user_data = {
            'full_name': usuario.name,
            'email': usuario.email,
            'phone': usuario.phone,
        }

        # Almacenar los datos del usuario en la sesión
        request.session['user_data'] = user_data
        request.session['message'] = 'Usuario creado exitosamente' if created else 'Usuario actualizado exitosamente'

        # Redirigir al usuario a la página de inicio
        return redirect('pokemon_search')
    else:
        return HttpResponse('Solicitud inválida', status=400)

def pokemon_search(request):

    user_data = request.session.pop('user_data', None)
    message = request.session.pop('message', None)
    
    page_view, created = PageView.objects.get_or_create(id=1)
    page_view.view_count += 1
    page_view.save()
    
    query = request.GET.get('query')
    pokemon_data = None
    error_message = None
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    if query:
        #Perform a case-insensitive search on both the name and unique_id fields
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

    return render(request, 'index.html', {'pokemon_data': pokemon_data, 'error_message': error_message, 'view_count': page_view.view_count, 'user_data': user_data, 'message': message})

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
                save_pokemon_species_to_database(pokemon_data)

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
            for flavor_text in species_data['genera']:
                if flavor_text['language']['name'] == 'es':
                    species_name = flavor_text['genus']
                    break
            if species_name:
                return {'name': pokemon_name, 'species': species_name, 'image': data['sprites']['front_default']}
    return None

def save_pokemon_species_to_database(pokemon_data):
    try:
        Pokemon_main_especies.objects.create(name=pokemon_data['name'], species=pokemon_data['species'])
    except IntegrityError:
        # Registro ya existe, manejar la excepción adecuadamente o simplemente ignorarla
        pass


def pokemon_evolutions(request):
    # Retrieve the query parameter from the request
    query = request.GET.get('query')

    # Perform any necessary data retrieval or processing here
    # For example, you can fetch evolution data for the given query
    evolution_data = fetch_evolution_data(query)

    # Pass the necessary data to the template
    context = {
        'query': query,
        'evolution_data': evolution_data,
        # Add any other context variables you need
    }

    # Render the evoluciones.html template with the context data
    return render(request, 'evoluciones.html', context)


def fetch_evolution_data(pokemon_name):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{pokemon_name.lower()}')
    if response.status_code == 200:
        data = response.json()
        evolution_chain_url = data['evolution_chain']['url']
        evolution_chain_response = requests.get(evolution_chain_url)
        if evolution_chain_response.status_code == 200:
            evolution_chain_data = evolution_chain_response.json()
            evolution_data = parse_evolution_chain(evolution_chain_data)
            return evolution_data
    return None

def parse_evolution_chain(evolution_chain_data):
    evolution_data = []
    chain = evolution_chain_data['chain']
    
    # Función recursiva para explorar todas las ramas de la cadena de evolución
    def explore_chain(chain):
        while chain:
            evolution_details = chain['evolution_details'][0] if chain['evolution_details'] else None
            if 'species' in chain:
                pokemon_name = chain['species']['name'].capitalize()
                pokemon_image = fetch_pokemon_image(chain['species']['name'])
                evolution_data.append({
                    'name': pokemon_name,
                    'image': pokemon_image
                })
            if chain['evolves_to']:
                for next_chain in chain['evolves_to']:
                    explore_chain(next_chain)
            chain = None  # Termina el bucle

    explore_chain(chain)
    return evolution_data


def fetch_pokemon_image(pokemon_name):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}')
    if response.status_code == 200:
        data = response.json()
        return data['sprites']['front_default']
    return None

def pokemon_habilidades(request):
    # Retrieve the query parameter from the request
    query = request.GET.get('query')

    # Perform any necessary data retrieval or processing here
    # For example, you can fetch evolution data for the given query
    abilities_data = fetch_abilities_data(query)

    # Pass the necessary data to the template
    context = {
        'query': query,
        'abilities_data': abilities_data,
        # Add any other context variables you need
    }

    # Render the evoluciones.html template with the context data
    return render(request, 'habilidades.html', context)

def fetch_abilities_data(pokemon_name):
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}')
    if response.status_code == 200:
        data = response.json()
        abilities = []
        for ability_entry in data['abilities']:
            ability_name = ability_entry['ability']['name'].capitalize()
            abilities.append(ability_name)
        return {
            'primary_ability': abilities[0],
            'hidden_abilities': abilities[1:],
        }
    return None








