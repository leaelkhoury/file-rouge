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

pip install duckdb

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

def insert_movies_to_db(movies, batch_size=100):
    # Connexion à la base de données
    conn = duckdb.connect('movies.db')
    
    # Initialiser une liste pour stocker les films à insérer
    batch = []
    
    for movie in movies:
        # Gérer les valeurs manquantes pour genres, description, etc.
        genres = ', '.join([genre['name'] for genre in movie.get('genres', [])]) if 'genres' in movie else ''
        description = movie.get('overview', '')
        release_date = movie.get('release_date', '')
        vote_average = movie.get('vote_average', 0)
        vote_count = movie.get('vote_count', 0)
        
        # Vérifier si le film existe déjà dans la base de données avant de l'ajouter
        movie_id = movie['id']
        result = conn.execute("SELECT COUNT(*) FROM films WHERE id = ?", (movie_id,)).fetchone()
        
        if result[0] == 0:  # Si le film n'existe pas, l'ajouter au batch
            batch.append((movie['id'], movie['title'], genres, description, release_date, vote_average, vote_count))
        
        # Si le batch a atteint la taille limite, insérer en une seule requête
        if len(batch) >= batch_size:
            conn.executemany('''
                INSERT INTO films (id, title, genres, description, release_date, vote_average, vote_count) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', batch)
            # Réinitialiser le batch après l'insertion
            batch = []
    
    # Insérer les films restants qui ne remplissent pas un batch complet
    if batch:
        conn.executemany('''
            INSERT INTO films (id, title, genres, description, release_date, vote_average, vote_count) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', batch)
# Récupérer les films populaires et les insérer dans la base de données
movies = get_popular_movies()
insert_movies_to_db(movies)

# Charger les évaluations des utilisateurs depuis le fichier CSV "ratings.csv"
ratings_df = pd.read_csv('ratings.csv')
def insert_ratings_to_db(batch_size=100):
    # Connexion à la base de données
    conn = duckdb.connect('movies.db')
    
    # Initialiser une liste pour stocker les évaluations à insérer
    batch = []
    
    for _, row in ratings_df.iterrows():
        # Ajouter les données de l'évaluation à la liste batch
        batch.append((row['userId'], row['movieId'], row['rating'], row['timestamp']))
        
        # Si le batch a atteint la taille limite, insérer en une seule requête
        if len(batch) >= batch_size:
            conn.executemany('''
                INSERT INTO ratings (user_id, movie_id, rating, timestamp)
                VALUES (?, ?, ?, ?)
            ''', batch)
            # Réinitialiser le batch après l'insertion
            batch = []
    
    # Insérer les évaluations restantes qui ne remplissent pas un batch complet
    if batch:
        conn.executemany('''
            INSERT INTO ratings (user_id, movie_id, rating, timestamp)
            VALUES (?, ?, ?, ?)
        ''', batch)
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
pip install fastapi uvicorn duckdb pandas scikit-surprise
