""" 
on pouvait utiliser from api import apiRouter comme on a vu en classe: 
@router.post("/recommendations/{user_id}")
@app.get("/recommendations/{user_id}")

mais on a choisi de faire autrement:
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from typing import List
from pydantic import BaseModel

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class Movie(BaseModel):
    id: int
    title: str
    genres: str
    description: str
    release_date: str
    vote_average: float

class Recommendation(BaseModel):
    id: int
    title: str
    rating_predicted: float

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[Recommendation]

# Connexion à DuckDB
conn = duckdb.connect('movies.db')

# Chargement des données et entraînement du modèle SVD
def load_data_and_train_model():
    # Charger les évaluations
    ratings_query = "SELECT user_id, movie_id, rating FROM ratings"
    ratings_df = conn.execute(ratings_query).fetchdf()
    
    # Configurer et entraîner le modèle
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(ratings_df[['user_id', 'movie_id', 'rating']], reader)
    trainset, _ = train_test_split(data, test_size=0.2)
    algo = SVD()
    algo.fit(trainset)
    
    return algo

# Initialiser le modèle (à faire au démarrage)
svd_model = load_data_and_train_model()

@app.get("/movies/", response_model=List[Movie])
def get_all_movies(limit: int = 100):
    """Récupère la liste des films"""
    query = f"SELECT id, title, genres, description, release_date, vote_average FROM films LIMIT {limit}"
    movies = conn.execute(query).fetchall()
    return [{
        "id": m[0],
        "title": m[1],
        "genres": m[2],
        "description": m[3],
        "release_date": m[4],
        "vote_average": m[5]
    } for m in movies]

@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    """Récupère les détails d'un film spécifique"""
    query = "SELECT id, title, genres, description, release_date, vote_average FROM films WHERE id = ?"
    movie = conn.execute(query, [movie_id]).fetchone()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Film non trouvé")
    
    return {
        "id": movie[0],
        "title": movie[1],
        "genres": movie[2],
        "description": movie[3],
        "release_date": movie[4],
        "vote_average": movie[5]
    }

@app.get("/recommend_movies/{user_id}", response_model=RecommendationResponse)
def recommend_movies(user_id: int, limit: int = 10):
    """Génère des recommandations personnalisées pour un utilisateur"""
    # 1. Récupérer les films déjà notés par l'utilisateur
    rated_query = "SELECT movie_id FROM ratings WHERE user_id = ?"
    rated_movies = conn.execute(rated_query, [user_id]).fetchall()
    rated_movie_ids = [m[0] for m in rated_movies]
    
    # 2. Récupérer tous les films non notés par l'utilisateur
    if rated_movie_ids:
        movies_query = f"""
            SELECT id, title FROM films 
            WHERE id NOT IN ({','.join(map(str, rated_movie_ids))})
        """
    else:
        movies_query = "SELECT id, title FROM films"
    
    all_movies = conn.execute(movies_query).fetchall()
    
    # 3. Faire des prédictions pour chaque film non noté
    recommendations = []
    for movie_id, title in all_movies:
        pred = svd_model.predict(uid=user_id, iid=movie_id)
        recommendations.append({
            "id": movie_id,
            "title": title,
            "rating_predicted": round(pred.est, 1)
        })
    
    # 4. Trier par note prédite et retourner les meilleurs
    recommendations.sort(key=lambda x: x["rating_predicted"], reverse=True)
    top_recommendations = recommendations[:limit]
    
    return {
        "user_id": user_id,
        "recommendations": top_recommendations
    }

@app.get("/statistics/{genre}/{year}", response_model=List[Movie])
def get_statistics(genre: str, year: str, limit: int = 10):
    """Récupère les films d'un genre et d'une année spécifique"""
    query = f"""
        SELECT id, title, genres, description, release_date, vote_average 
        FROM films 
        WHERE genres LIKE '%{genre}%' AND strftime('%Y', release_date) = '{year}'
        ORDER BY vote_average DESC
        LIMIT {limit}
    """
    movies = conn.execute(query).fetchall()
    
    return [{
        "id": m[0],
        "title": m[1],
        "genres": m[2],
        "description": m[3],
        "release_date": m[4],
        "vote_average": m[5]
    } for m in movies]


_____________________________________________________________________________________________________________________________________________________________

"""
 Explication du Code
GET /movie/{id} : Ce point de terminaison prend un id de film et retourne ses détails (titre, genres, description, etc.) depuis DuckDB.

POST /recommendations/{user_id} : Ce point de terminaison prend un user_id, génère des recommandations personnalisées en utilisant le modèle SVD et retourne les 10 films les mieux notés que l'utilisateur pourrait aimer. Le modèle SVD est formé sur les évaluations des utilisateurs et utilise les films non vus par l'utilisateur pour générer des prédictions.

GET /statistics/{gender}/{year} : Ce point de terminaison permet de récupérer des statistiques sur les films d'un genre spécifique et d'une année spécifique. Il retourne les 10 films les mieux notés pour ce genre et cette année.

Conclusion: on a une API FastAPI qui offre :
La récupération des détails d'un film spécifique.
Des recommandations personnalisées basées sur un modèle SVD de filtrage collaboratif.
Des statistiques sur les films, comme le top 10 des films les mieux notés d'un genre et d'une année donnés.


Pour exécuter l'application avec Docker :

1.Construire l'image Docker :
bash:

Copy
Edit
docker build -t backend .

2.Lancer le conteneur :

Copy
Edit
docker run -p 8000:8000 backend

3. Test de l'API
a. Obtenir les détails d'un film :
bash
Copy
Edit
curl http://localhost:8000/movie/299536

b. Obtenir des recommandations pour un utilisateur :
bash
Copy
Edit
curl -X 'POST' \
  'http://localhost:8000/recommendations/1' \
  -H 'Content-Type: application/json' \
  -d '{
  }'

"""
