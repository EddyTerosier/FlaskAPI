import streamlit as st
import aiohttp
import asyncio

API_URL = "http://127.0.0.1:5000"

st.title("Détails d'un film avec Streamlit")
movie_id = st.text_input("Entrer l'ID d'un film", value="550")


async def get_movie_details(movie_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/movie/{movie_id}") as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": "Impossible de récupérer les détails du film."}


if st.button("Détails du film"):
    if not movie_id:
        st.error("Entrer un ID de film.")
    else:
        result = asyncio.run(get_movie_details(movie_id))
        if "error" in result:
            st.error(result["error"])
        else:
            st.write(f"**Title**: {result['title']}")
            st.write(f"**Release Date**: {result['release_date']}")
            st.write(f"**Genres**: {', '.join(result['genres'])}")
            st.write(f"**Popularity**: {result['popularity']}")
            st.write(f"**Average Vote**: {result['vote_average']}")
