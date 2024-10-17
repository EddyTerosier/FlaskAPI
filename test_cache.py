# IMPORTS
import asyncio
import aiohttp
from aiocache import cached, Cache
import os
from dotenv import load_dotenv

# Charger la clé API
load_dotenv()
API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = "https://api.themoviedb.org/3"


# Fonction avec mise en cache pour effectuer une requête vers l'API TMDB
@cached(ttl=3600, cache=Cache.MEMORY)
async def fetch_with_cache(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Erreur {response.status} lors de la requête {url}")
            return None


# Fonction pour effectuer plusieurs requêtes à la fois
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_cache(session, url) for url in urls]
        return await asyncio.gather(*tasks)


# Exemple d'utilisation de fetch_all
urls = [
    f"{BASE_URL}/movie/550?api_key={API_KEY}",
    f"{BASE_URL}/movie/551?api_key={API_KEY}",
    f"{BASE_URL}/movie/552?api_key={API_KEY}"
]


# Fonction principale pour exécuter les requêtes
async def main():
    results = await fetch_all(urls)
    for result in results:
        print(result)


# Exécuter la fonction principale
if __name__ == "__main__":
    asyncio.run(main())
