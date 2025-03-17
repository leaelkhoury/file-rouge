

from fastapi import FastAPI
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import duckdb
import pandas as pd
from typing import List, Dict

# Initialiser l'application FastAPI
app = FastAPI()

# Connexion à DuckDB
conn = duckdb.connect('movies.db')

# Charger les films et les évaluations depuis DuckDB
def load_data():
    # Charger les évaluations des utilisateurs
    ratings_df = conn.execute("SELECT * FROM ratings").fetchdf()

    # Charger les films
    films_df = conn.execute("SELECT id, title FROM films").fetchdf()
    
    return ratings_df, films_df

# Endpoint pour récupérer les détails d'un film par son id
@app.get("/movie/{id}")
async def get_movie_details(id: int):
    result = conn.execute("SELECT * FROM films WHERE id = ?", (id,)).fetchone()
    if result:
        movie_details = {
            "id": result[0],
            "title": result[1],
            "release_date": result[2],
            "vote_average": result[3],
            "description": result[4],
            "genres": result[5],
            "vote_count": result[6],
        }
        return movie_details
    else:
        return {"error": "Movie not found"}

# Endpoint pour obtenir des recommandations personnalisées pour un utilisateur
@app.post("/recommendations/{user_id}")
async def recommend_movies(user_id: int) -> Dict:
    # Charger les données de l'utilisateur et des films
    ratings_df, films_df = load_data()
    
    # Utiliser Surprise pour le modèle SVD
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(ratings_df[['user_id', 'movie_id', 'rating']], reader)
    trainset, testset = train_test_split(data, test_size=0.2)

    # Entraîner le modèle SVD
    algo = SVD()
    algo.fit(trainset)

    # Obtenir la liste des films non vus par l'utilisateur
    seen_movies = ratings_df[ratings_df['user_id'] == user_id]['movie_id'].tolist()
    unseen_movies = films_df[~films_df['id'].isin(seen_movies)]
    
    # Faire des prédictions pour les films non vus
    recommendations = []
    for movie_id in unseen_movies['id']:
        pred = algo.predict(user_id, movie_id)
        recommendations.append({
            "id": movie_id,
            "title": unseen_movies[unseen_movies['id'] == movie_id]['title'].values[0],
            "rating_predicted": pred.est,
        })
    
    # Trier les recommandations par note prédite
    recommendations = sorted(recommendations, key=lambda x: x['rating_predicted'], reverse=True)
    
    # Limiter à 10 recommandations
    recommendations = recommendations[:10]
    
    return {"user_id": user_id, "recommendations": recommendations}

# Endpoint pour récupérer des statistiques sur les films
@app.get("/statistics/{gender}/{year}")
async def get_statistics(gender: str, year: int) -> Dict:
    # Récupérer les films filtrés par genre et année
    query = f"SELECT * FROM films WHERE genres LIKE '%{gender}%' AND strftime('%Y', release_date) = '{year}'"
    result = conn.execute(query).fetchdf()

    # Calculer les 10 films les mieux notés
    top_rated_movies = result.sort_values(by='vote_average', ascending=False).head(10)

    statistics = {
        "top_rated_movies": top_rated_movies[['title', 'vote_average']].to_dict(orient='records'),
    }
    
    return statistics

# Lancer l'application avec uvicorn (si vous n'êtes pas dans un Dockerfile)
# uvicorn main:app --reload


_____________________________________________________________________________________________________________________________________________________________

"""
 Explication du Code
GET /movie/{id} : Ce point de terminaison prend un id de film et retourne ses détails (titre, genres, description, etc.) depuis DuckDB.

POST /recommendations/{user_id} : Ce point de terminaison prend un user_id, génère des recommandations personnalisées en utilisant le modèle SVD et retourne les 10 films les mieux notés que l'utilisateur pourrait aimer. Le modèle SVD est formé sur les évaluations des utilisateurs et utilise les films non vus par l'utilisateur pour générer des prédictions.

GET /statistics/{gender}/{year} : Ce point de terminaison permet de récupérer des statistiques sur les films d'un genre spécifique et d'une année spécifique. Il retourne les 10 films les mieux notés pour ce genre et cette année.
"""
