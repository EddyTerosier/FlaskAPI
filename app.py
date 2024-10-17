import aiohttp
from aiocache import cached, Cache
from flask import Flask, jsonify
import os
import asyncio
from dotenv import load_dotenv

# Charger la clé API
load_dotenv()
API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = "https://api.themoviedb.org/3"

# FLASK APP
app = Flask(__name__)


@app.route('/')
def home():
    return "Bienvenue sur l'API TMDB Flask"


@app.route('/movie/<int:movie_id>', methods=['GET'])
def movie_details(movie_id):
    movie = asyncio.run(get_movie_details(movie_id))
    return jsonify(movie)


# Fonction pour obtenir les détails d'un film avec retry
async def get_movie_details(movie_id):
    if not API_KEY:
        return {"error": "L'API TMDB n'est pas configurée."}

    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}"
    response = await get_with_retry([url])

    if response and response[0] and "title" in response[0]:
        data = response[0]
        return {
            "title": data.get("title"),
            "release_date": data.get("release_date"),
            "genres": [genre['name'] for genre in data.get("genres", [])],
            "popularity": data.get("popularity"),
            "vote_average": data.get("vote_average")
        }
    else:
        return {"error": "Impossible de récupérer les détails du film."}


# Fonction pour effectuer une requête avec retry utilisant les requêtes simultanées
async def get_with_retry(urls, max_retries=3, backoff_factor=2):
    retries = 0
    while retries < max_retries:
        try:
            results = await fetch_all(urls)
            if all(results):
                return results
            elif any(result is None for result in results):
                print("Certaines requêtes ont échoué. Attente avant de réessayer...")
                await asyncio.sleep(backoff_factor ** retries)
        except Exception as e:
            print(f"Une erreur est apparue : {e}")
        retries += 1
    return None


# Reste du code (fonctions `fetch`, `fetch_all`, etc.)


# Fonction pour effectuer une requête vers l'API TMDB de manière asynchrone avec mise en cache
@cached(ttl=3600, cache=Cache.MEMORY)
async def fetch(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Erreur {response.status} lors de la requête {url}")
            return None


# Fonction pour effectuer plusieurs requêtes à la fois
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)


if __name__ == "__main__":
    app.run(debug=True)
