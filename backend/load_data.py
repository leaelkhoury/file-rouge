import requests
import duckdb
import pandas as pd
import time

# Configuration de l'API
API_KEY = "f388326c5cac9ad23fde27ca61ce2a3c"
BASE_URL = "https://api.themoviedb.org/3"

# Connexion à DuckDB
conn = duckdb.connect('movies.db')

# Créer les tables si elles n'existent pas
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

conn.execute(''' 
    CREATE TABLE IF NOT EXISTS ratings ( 
        user_id INTEGER, 
        movie_id INTEGER, 
        rating REAL, 
        timestamp INTEGER 
    ); 
''')

def get_popular_movies(limit=500):
    movies = []
    page = 1

    while len(movies) < limit:
        url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&page={page}"
        response = requests.get(url)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            movies.extend(results)
        else:
            print(f"Erreur lors de la récupération des films (Page {page}): {response.status_code}")
            break
        
        page += 1
        if page > 25:  # Sécurité pour ne pas dépasser 25 pages
            break

    return movies[:limit]  # On prend seulement les 500 premiers films



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

# Charger les évaluations des utilisateurs depuis le fichier CSV "ratings.csv"
ratings_df = pd.read_csv('ratings.csv').head(500)

# Gérer les valeurs NaN dans les évaluations
ratings_df = ratings_df.dropna(subset=['userId', 'movieId', 'rating', 'timestamp'])  # Supprimer les lignes avec NaN
# Si vous préférez remplacer les NaN, vous pouvez aussi faire :
# ratings_df.fillna({'rating': 0, 'timestamp': 0}, inplace=True)  # Remplacer les NaN par 0 pour certaines colonnes

def insert_ratings_to_db(batch_size=100):
    batch = []
    
    for _, row in ratings_df.iterrows():
        batch.append((row['userId'], row['movieId'], row['rating'], row['timestamp']))
        
        if len(batch) >= batch_size:
            conn.executemany('''
                INSERT INTO ratings (user_id, movie_id, rating, timestamp)
                VALUES (?, ?, ?, ?)
            ''', batch)
            batch = []

    if batch:
        conn.executemany('''
            INSERT INTO ratings (user_id, movie_id, rating, timestamp)
            VALUES (?, ?, ?, ?)
        ''', batch)


movies = get_popular_movies()
insert_movies_to_db(movies)

def export_to_sql(conn, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        # Écrire l'en-tête
        f.write("-- SQL dump generated from DuckDB\n")
        f.write("BEGIN TRANSACTION;\n\n")
        
        # Schema des tables
        f.write("-- Table structure for films\n")
        f.write("DROP TABLE IF EXISTS films;\n")
        f.write('''CREATE TABLE films (
            id INTEGER PRIMARY KEY,
            title TEXT,
            release_date TEXT,
            vote_average REAL,
            description TEXT,
            genres TEXT,
            vote_count INTEGER
        );\n\n''')
        
        f.write("-- Table structure for ratings\n")
        f.write("DROP TABLE IF EXISTS ratings;\n")
        f.write('''CREATE TABLE ratings (
            user_id INTEGER,
            movie_id INTEGER,
            rating REAL,
            timestamp INTEGER
        );\n\n''')
        
        # Données des films
        f.write("-- Data for films\n")
        for row in conn.execute("SELECT * FROM films").fetchall():
            values = []
            for val in row:
                if val is None:
                    values.append("NULL")
                elif isinstance(val, str):
                    # Échapper les apostrophes et guillemets
                    escaped = val.replace("'", "''")
                    values.append(f"'{escaped}'")
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                else:
                    values.append(f"'{str(val)}'")
            
            f.write(f"INSERT INTO films VALUES ({','.join(values)});\n")
        
        # Données des ratings
        f.write("\n-- Data for ratings\n")
        for row in conn.execute("SELECT * FROM ratings").fetchall():
            values = []
            for val in row:
                if val is None:
                    values.append("NULL")
                elif isinstance(val, str):
                    escaped = val.replace("'", "''")
                    values.append(f"'{escaped}'")
                else:
                    values.append(str(val))
            
            f.write(f"INSERT INTO ratings VALUES ({','.join(values)});\n")
        
        f.write("\nCOMMIT;\n")

# Utilisation
export_to_sql(conn, 'movies_backup.sql')
conn.close()


# Connexion à la base de données
conn = duckdb.connect('movies.db')

# 1. Afficher le nombre total de films
total_films = conn.execute("SELECT COUNT(*) FROM films").fetchone()[0]
print(f"\n📊 Nombre total de films dans la base : {total_films}")

# 2. Afficher tous les champs des 5 premiers films
print("\n🎬 Exemple de films (tous les champs) :")
films_df = conn.execute("SELECT * FROM films LIMIT 5").fetchdf()
pd.set_option('display.max_columns', None)  # Afficher toutes les colonnes
pd.set_option('display.width', 1000)       # Largeur d'affichage
print(films_df)

# 3. Afficher les évaluations avec tous les champs
print("\n⭐ Exemple d'évaluations (tous les champs) :")
ratings_df = conn.execute("""
    SELECT r.*, f.title as film_title 
    FROM ratings r
    JOIN films f ON r.movie_id = f.id
    LIMIT 10
""").fetchdf()
print(ratings_df)

# 4. Statistiques détaillées
print("\n📈 Statistiques complètes :")

# Note moyenne globale
avg_rating = conn.execute("SELECT AVG(vote_average) FROM films").fetchone()[0]
print(f"- Note moyenne globale des films: {avg_rating:.2f}/10")

# Nombre total d'évaluations
total_ratings = conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]
print(f"- Nombre total d'évaluations: {total_ratings}")

# Nombre moyen d'évaluations par film
avg_ratings_per_film = conn.execute("""
    SELECT AVG(ratings_count) 
    FROM (
        SELECT movie_id, COUNT(*) as ratings_count 
        FROM ratings 
        GROUP BY movie_id
    )
""").fetchone()[0]
print(f"- Nombre moyen d'évaluations par film: {avg_ratings_per_film:.1f}")

# Film le mieux noté
best_movie = conn.execute("""
    SELECT title, vote_average 
    FROM films 
    ORDER BY vote_average DESC 
    LIMIT 1
""").fetchone()
print(f"- Film le mieux noté: '{best_movie[0]}' avec {best_movie[1]}/10")

# Utilisateur le plus actif
active_user = conn.execute("""
    SELECT user_id, COUNT(*) as rating_count
    FROM ratings
    GROUP BY user_id
    ORDER BY rating_count DESC
    LIMIT 1
""").fetchone()
print(f"- Utilisateur le plus actif: ID {active_user[0]} ({active_user[1]} évaluations)")

# Fermer la connexion
conn.close()
