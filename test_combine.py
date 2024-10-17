# IMPORTS
import asyncio
import aiohttp
import os
import requests
import time
from dotenv import load_dotenv
from aiocache import cached, Cache

# Charger la clé API
load_dotenv()
API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = "https://api.themoviedb.org/3"


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


urls = [
    f"{BASE_URL}/movie/550?api_key={API_KEY}",
    f"{BASE_URL}/movie/551?api_key={API_KEY}",
    f"{BASE_URL}/movie/552?api_key={API_KEY}"
]


# Fonction principale pour exécuter les requêtes asynchrones
async def main():
    results = await get_with_retry(urls)
    for result in results:
        print(result)


# Exécuter la fonction principale
if __name__ == "__main__":
    asyncio.run(main())
