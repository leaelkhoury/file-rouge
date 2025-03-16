### **Tutorial : Création d'un système distribué de recommandation de films avec filtrage collaboratif (Machine Learning)**

---

#### **Objectif général** :
Concevoir un système complet de **recommandation de films** basé sur le **Filtrage Collaboratif**, intégrant :
1. Une base de données centralisée et optimisée avec **DuckDB**.
2. Une **application back-end** pour fournir des recommandations via une API REST.
3. Une **application front-end** pour l’analyse des données et la visualisation des résultats.
4. Un déploiement automatisé en environnement distribué à l’aide de **Docker Compose**.

---

### **Description de la tâche** :

Votre objectif est de construire un projet de recommandations de films capable d'interagir avec une base de données DuckDB contenant des données sur des films et des évaluations réelles. Ce projet doit être structuré en 3 services principaux :
1. **Backend** (FastAPI) : Fournit des recommandations de films via une API REST.
2. **Frontend** (Streamlit) : Visualise les statistiques des films et les informations sur les utilisateurs (exemple : top films, distribution des notes...).
3. **Base de données centrale** (DuckDB) : Stocke les films, les données des utilisateurs et les évaluations.

Le système sera distribué et automatisé à l'aide de **Docker Compose** afin de garantir la reproductibilité entre environnements.

**Livrable attendu :** Un système complet permettant la collecte, le traitement, la recommandation et la visualisation des données.

---

## **Étapes du projet** :

### **Étape 1 : Collecter les données**
Vous utiliserez deux sources pour les données liées aux films :
1. **[The Movie Database (TMDB) API](https://developers.themoviedb.org/3/getting-started)** :  
   Cette API vous aidera à collecter les données suivantes :
   - Informations sur les films (identifiant, titre, description, genres, moyenne des votes, date de sortie, etc.)
     ```python
     {
         "id": 550,
         "title": "Fight Club",
         "overview": "...",
         "genres": ["Drama", "Thriller"],
         "vote_average": 8.4,
         "vote_count": 25000,
         "release_date": "1999-10-15"
     }
     ```
   - API Key requise : Créez un compte gratuit et générez votre **clé API** [ici](https://www.themoviedb.org/).

   **Endpoints utiles :**
   - Obtenir des films populaires : [Endpoint TMDB Popular movies](https://developers.themoviedb.org/3/movies/get-popular-movies).

2. **[Dataset Kaggle](https://www.kaggle.com/rounakbanik/the-movies-dataset)** :  
   Le dataset de Kaggle contient des évaluations utilisateur anonymes et d'autres métadonnées utiles sur les films.
   - Données à télécharger :
     - Fichier `ratings.csv` pour obtenir les informations utilisateur et des notes filmées.

   **Structure du fichier `ratings.csv` :**
   | userId | movieId | rating | timestamp     |
   |--------|---------|--------|---------------|
   | 1      | 2478    | 4.0    | 964982703     |
   | 1      | 2674    | 5.0    | 964981247     |

---

### **Étape 2 : Préparer et stocker les données dans DuckDB**
1. Utilisez **DuckDB** comme base de données centralisée :
   - Installez DuckDB dans un environnement Python avec `pip install duckdb`.
   - Créez une base de données DuckDB pour centraliser vos données (films et notes).
   - Stockez les données des films et des évaluations dans des tables relationnelles.

2. **Modèle relationnel** des données dans DuckDB (structure suggérée) :
   - Table `films` :
     ```sql
     CREATE TABLE films (
         id INT PRIMARY KEY,
         title TEXT,
         description TEXT,
         genres TEXT,
         release_date DATE,
         vote_average FLOAT,
         vote_count INT
     );
     ```

   - Table `ratings` :
     ```sql
     CREATE TABLE ratings (
         user_id INT,
         film_id INT,
         rating FLOAT,
         timestamp INT
     );
     ```

---

### **Étape 3 : Implémentation du back-end**
1. Développez une **API REST** pour faire des recommandations :
   - Langage : Python (avec **FastAPI**).
   - L'API doit charger les données depuis DuckDB et permettre :
     - De récupérer la **liste de films**.
     - De générer des **recommandations personnalisées** (modèle de filtrage collaboratif).

   **Requête d'exemple à implémenter :**
   - Endpoint `/recommend_movies/{user_id}` :
     Retourne une liste des films recommandés pour un utilisateur spécifique (avec leurs titres).

   **Exemple de réponse JSON attendu :**
   ```json
   {
       "user_id": 1,
       "recommendations": [
           {"id": 299536, "title": "Avengers: Infinity War", "rating_predicted": 4.8},
           {"id": 120, "title": "The Lord of the Rings", "rating_predicted": 4.7}
       ]
   }
   ```

2. Implémentez le système de **Filtrage Collaboratif** :
   - Utilisez un modèle basé sur la **factorisation matricielle SVD** avec la librairie `surprise` ou `scikit-learn`.
   - Approche fil conducteur :
     - Construire un tableau `userId x movieId` depuis les tables `ratings` et `films`.
     - Former un modèle SVD pour prédire les notes des utilisateurs sur les films non notés.
   - Exemple avec **SVD** et `surprise` :
     ```python
     from surprise import Dataset, Reader, SVD
     from surprise.model_selection import train_test_split

     # Charger les données des évaluations
     reader = Reader(rating_scale=(0.5, 5.0))
     data = Dataset.load_from_df(ratings_df[['user_id', 'film_id', 'rating']], reader)

     # Split train/test et entraînement
     trainset, testset = train_test_split(data, test_size=0.2)
     algo = SVD()
     algo.fit(trainset)

     # Faire des prédictions
     predictions = algo.predict(uid=1, iid=299536)  # Prévisions pour user_id=1 pour le film #299536
     print(predictions.est)
     ```

---

### **Étape 4 : Implémentation du front-end**
Créez une application front-end interactive pour :
1. **Afficher les graphiques d’analyse des données publiées** :
   - Distribution des notes moyennes des films.
   - Evolution du nombre de films sortis par année.
   - Statistiques des utilisateurs (distribution des notes attribuées).
   - D'autres graphiques pertinents.

   Utilisez un **outil de visualisation** `Streamlit` intégré au front-end.

2. **Proposer une interface pour saisir un utilisateur (fictif)** et afficher les films recommandés en appelant l’API backend.

---

### **Étape 5 : Docker Compose pour l’orchestration**
Structurez votre système en trois conteneurs Docker :
1. Service **Backend** (API FastAPI).
2. Service **Frontend** (Streamlit).
3. Service **Base de données DuckDB**.

- Fichier `docker-compose.yml` dans le répertoire racine du projet:

Docker-compose permet de définir et exécuter des applications multi-conteneurs. Il permet de définir les services, les réseaux et les volumes de stockage nécessaires pour l'application. Il sera utilisé pour orchestrer les services backend, frontend et la base de données DuckDB.


Utilisation de docker-compose pour orchestrer les services (backend, frontend, base de données).

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    networks:
      - flix_network

  frontend:
    build:
      context: ./frontend
    ports:
      - "8501:8501"
    networks:
      - flix_network

  database:
    image: duckdb/duckdb:latest  # Utilisation d'une image Docker existante
    volumes:
      - ./data:/data  # Montage d'un volume pour stocker les données DuckDB
    networks:
      - flix_network

networks:
  flix_network:
    driver: bridge
```

Lancement des services (images Docker) avec docker-compose :
l'argument build permet de construire les images Docker à partir des fichiers Dockerfile présents dans les dossiers backend et frontend.

> [!CAUTION]  
> Les dockerfile du backend et front sont à compléter. Ils contiennent les commentaires pour vous guider.

```bash
docker-compose up --build
```

Lancement des services en arrière-plan (détaché) :

```bash
docker-compose up -d --build
```
---

### **Ressources :**
1. **TMDB API Documentation** :  
   [https://developers.themoviedb.org/3/getting-started](https://developers.themoviedb.org/3/getting-started)

2. **Dataset Kaggle** :  
   [https://www.kaggle.com/rounakbanik/the-movies-dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset)

3. **DuckDB Documentation** :  
   [https://duckdb.org/docs/introduction/](https://duckdb.org/docs/introduction/)

4. **Filtrage collaboratif avec Surprise** :  
   [https://surprise.readthedocs.io/en/stable/](https://surprise.readthedocs.io/en/stable/)

5. **Docker Compose Documentation** :
   [https://docs.docker.com/compose/](https://docs.docker.com/compose/)

---

### **Livrable final attendu :**
Un dépôt Git contenant :
1. Le **fichier Docker Compose** et ses services (backend, frontend, base de données).
2. Les scripts permettant de charger les données (TMDB/Kaggle) dans DuckDB.
3. Le code Python du backend pour les recommandations.
4. Le code Python du frontend avec les visualisations.
5. Une petite documentation pour expliquer comment lancer le projet.
