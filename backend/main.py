import duckdb
import pandas as pd
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from surprise import SVD, Reader, Dataset
from surprise.model_selection import train_test_split

app = FastAPI()

# Connexion à DuckDB
conn = duckdb.connect('movies.db')

# Modèle pour la réponse de film
class Movie(BaseModel):
    id: int
    title: str
    rating_predicted: float

# Endpoint pour récupérer des films recommandés pour un utilisateur
@app.get("/recommend_movies/{user_id}", response_model=dict)
def recommend_movies(user_id: int):
    # Charger les données de ratings depuis DuckDB
    ratings_df = pd.read_sql("SELECT * FROM ratings", conn)
    films_df = pd.read_sql("SELECT * FROM films", conn)
    
    # Construire l'ensemble de données pour surprise (user_id, film_id, rating)
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(ratings_df[['user_id', 'movie_id', 'rating']], reader)

    # Séparer les données en train et test
    trainset, testset = train_test_split(data, test_size=0.2)

    # Entraîner un modèle SVD
    algo = SVD()
    algo.fit(trainset)

    # Faire des prédictions pour l'utilisateur spécifié
    movie_ids = films_df['id'].unique()
    recommendations = []
    
    for movie_id in movie_ids:
        # Prédire la note de l'utilisateur pour chaque film non noté
        prediction = algo.predict(user_id, movie_id)
        recommendations.append({"id": movie_id, "title": films_df.loc[films_df['id'] == movie_id, 'title'].values[0], "rating_predicted": prediction.est})
    
    # Trier les recommandations par note prédite (de la plus haute à la plus basse)
    recommendations.sort(key=lambda x: x['rating_predicted'], reverse=True)

    # Retourner les 10 meilleures recommandations
    return {"user_id": user_id, "recommendations": recommendations[:10]}

# Lancer l'application FastAPI via Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
