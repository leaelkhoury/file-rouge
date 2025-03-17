""" GET https://api.themoviedb.org/3/movie/550?api_key=f388326c5cac9ad23fde27ca61ce2a3c&language=fr-FR 
réponse réussie affiche: 200, fichier JSON
on utilise: GET POST PUT PATCH DELETE 

python:
python -m pip install requests
import requests
url = "https://api.themoviedb.org/3/movie/movie_id?language=fr-FR"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer f388326c5cac9ad23fde27ca61ce2a3c"
}
response = requests.get(url, headers=headers)
print(response.text)

http:
curl --request GET \
     --url 'https://api.themoviedb.org/3/movie/movie_id?language=fr-FR' \
     --header 'Authorization: Bearer f388326c5cac9ad23fde27ca61ce2a3c' \
     --header 'accept: application/json'

"""

import requests

# Remplace par ta clé API TMDB
API_KEY = "f388326c5cac9ad23fde27ca61ce2a3c"
BASE_URL = "https://api.themoviedb.org/3"

# Fonction pour récupérer les films populaires
def get_popular_movies():
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Retourne les films populaires en format JSON
    else:
        print(f"Erreur: {response.status_code}")
        return None

# Appel de la fonction et affichage des résultats
popular_movies = get_popular_movies()
if popular_movies:
    for movie in popular_movies['results'][:5]:  # Afficher les 5 premiers films populaires
        print(f"Title: {movie['title']}, Release Date: {movie['release_date']}")

# pip install duckdb

import duckdb
import requests
import pandas as pd

# Connexion à DuckDB (création d'un fichier si inexistant)
conn = duckdb.connect('movies.db')

# Créer une table films si elle n'existe pas déjà
conn.execute(''' 
    CREATE TABLE IF NOT EXISTS films ( 
        id INTEGER PRIMARY KEY, 
        title TEXT, 
        release_date TEXT, 
        vote_average REAL, 
        description TEXT, 
        genres TEXT, 
        vote_count INTEGER
    ); 
''')

# Créer une table ratings si elle n'existe pas déjà
conn.execute(''' 
    CREATE TABLE IF NOT EXISTS ratings ( 
        user_id INTEGER, 
        movie_id INTEGER, 
        rating REAL, 
        timestamp INTEGER 
    ); 
''')

# Remplacer par ta clé API TMDB
API_KEY = "f388326c5cac9ad23fde27ca61ce2a3c"
BASE_URL = "https://api.themoviedb.org/3"

# Fonction pour récupérer les films populaires
def get_popular_movies():
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']  # Retourne les films populaires en format JSON
    else:
        print(f"Erreur: {response.status_code}")
        return []

# Insérer les films récupérés dans la base de données
def insert_movies_to_db(movies):
    # Connexion à la base de données
    conn = duckdb.connect('movies.db')
    
    for movie in movies:
        # Vérifier si le film existe déjà dans la base de données
        movie_id = movie['id']
        result = conn.execute("SELECT COUNT(*) FROM films WHERE id = ?", (movie_id,)).fetchone()
        
        if result[0] == 0:  # Si le film n'existe pas, l'insérer
            # Gérer le cas où la clé 'genres' ou d'autres clés peuvent être manquantes
            genres = ', '.join([genre['name'] for genre in movie.get('genres', [])]) if 'genres' in movie else ''
            description = movie.get('overview', '')
            release_date = movie.get('release_date', '')
            vote_average = movie.get('vote_average', 0)
            vote_count = movie.get('vote_count', 0)

            conn.execute(''' 
                INSERT INTO films (id, title, genres, description, release_date, vote_average, vote_count) 
                VALUES (?, ?, ?, ?, ?, ?, ?) 
            ''', (movie['id'], movie['title'], genres, description, release_date, vote_average, vote_count))
        else:
            print(f"Le film avec l'id {movie_id} existe déjà dans la base.")

# Récupérer les films populaires et les insérer dans la base de données
movies = get_popular_movies()
insert_movies_to_db(movies)

# Charger les évaluations des utilisateurs depuis le fichier CSV "ratings.csv"
ratings_df = pd.read_csv('ratings.csv')

# Insérer les évaluations dans la base de données
def insert_ratings_to_db():
    for _, row in ratings_df.iterrows():
        conn.execute('''
            INSERT INTO ratings (user_id, movie_id, rating, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (row['userId'], row['movieId'], row['rating'], row['timestamp']))

insert_ratings_to_db()

# Vérifier l'insertion
result = conn.execute('SELECT * FROM films LIMIT 5').fetchall()
print("Films insérés:", result)

ratings_result = conn.execute('SELECT * FROM ratings LIMIT 5').fetchall()
print("Évaluations insérées:", ratings_result)

# Exporter la base de données sous forme de fichier SQL
conn.execute("EXPORT DATABASE 'movies.db' TO 'movies_backup.sql';")

# Fermer la connexion
conn.close()
