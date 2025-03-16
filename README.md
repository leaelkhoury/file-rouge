### **Cahier des charges : Système de Recommandation de Films **



#### **1. CONTEXTE DU PROJET**

En tant que plateforme de streaming de contenus audiovisuels, nous souhaitons développer une solution de **recommandation de films** qui repose sur des données réelles et utilise une approche de filtrage collaboratif. L'objectif est d'offrir une expérience utilisateur personnalisée en proposant une liste de films adaptés à leurs goûts et préférences, tout en permettant une analyse approfondie des données collectées.

---

#### **2. OBJECTIFS**

- Créer un système capable de **recommander des films personnalisés** à un utilisateur en fonction des goûts d'autres utilisateurs (filtrage collaboratif).
- Mettre en place une **base de données centrale** pour stocker et gérer les données des films et des évaluations.
- Concevoir une **interface front-end** intuitive pour visualiser les tendances des films (par exemple : films populaires, distributions des notes, tendances par genre).
- Exposer une API via un **backend** chargé de générer les recommandations.
- Déployer toute la solution dans un environnement distribué à l'aide de **conteneurs Docker**.

---

#### **3. DESCRIPTION DU PROJET**

Le système de recommandation sera composé de **3 services distincts** qui communiquent entre eux :

1. **Base de données centrale (DuckDB)**  
   - Stocke les données des films (extraites de l'API TMDB et du dataset Kaggle).
   - Retient les évaluations (notes attribuées par les utilisateurs aux films).
   - Stocke les prédictions générées pour les recommandations futures.

2. **Backend (API REST)**  
   - Fournit une **API REST** permettant :
	   - De récupérer des recommandations pour un utilisateur donné.
	   - D'interroger les films disponibles dans la base.
   - Implémente un **modèle de filtrage collaboratif** (basé sur la factorisation matricielle SVD ou autre technique).

3. **Frontend (Dashboard)**  
   - Fournit un outil visuel pour :
     - Analyser les données des films : distribution des notes, évolution de la popularité des films.
     - Afficher les recommandations générées par l'API backend pour un utilisateur spécifique.

L'ensemble du système sera orchestré à l'aide de **Docker Compose**. 

---

#### **4. FONCTIONNALITÉS ATTENDUES**

##### A. **Service Base de Données (DuckDB)**  
- Une base relationnelle avec deux principales tables :
  - **Films** : Stocke les informations sur les films récupérés des sources externes (TMDB et Kaggle).
    - Attributs : `id`, `title`, `genres`, `description`, `release_date`, `vote_average`, `vote_count`.
  - **Ratings** : Stocke les évaluations des utilisateurs.
    - Attributs : `user_id`, `film_id`, `rating`, `timestamp`.
- Exporte la base sous forme de fichier pour qu’elle puisse être interrogée par le backend et le frontend et d'autres services.

##### B. **Service Backend (API)**  
- Fournit un ensemble de **endpoints RESTful** :
  1. **GET /movie/{id}** : Retourne les détails d’un film spécifique par son identifiant.
  2. **POST /recommendations/{user_id}** : Retourne une liste de films recommandés pour l'utilisateur `user_id`.  
    - S'appuie sur un modèle de **filtrage collaboratif avec prédictions**.
    - Note prédite (`rating_predicted`) intégrée dans la réponse.
  3. **GET /statistics/{gender}/{year}** : Retourne des statistiques générales sur les films (par exemple, top 10 des films par note moyenne, distribution des genres).

##### C. **Service Frontend (Dashboard)**  
- Propose un design interactif basé sur Streamlit.
- Affiche :  
  1. Les **statistiques analytiques** sous forme de graphiques :
     - Distribution des notes moyennes des films.
     - Évolution du nombre de films par année./ genre
     - Top film / Top fim par genre / Années
  2. Les recommandations reçues via l’API pour un utilisateur donné.
     - Formulaire simple permettant de saisir un `user_id` et de récupérer 
     	- Ses films préférées
     	- Les recommandations correspondantes.

##### D. **Approche Machine Learning (Filtrage collaboratif)**  
- Modèle basé sur la **factorisation matricielle SVD** avec librairies comme `surprise` ou `scikit-learn`.
- Prend en compte les **évaluations existantes (ratings)** pour formuler des recommandations précises.
- Capable d’évaluer les performances du modèle avec des métriques telles que **RMSE** ou **MAE**.

##### E. **Orchestration avec Docker Compose**
- Tous les composants (backend, frontend, base de données) doivent être déployables ensemble via un fichier `docker-compose.yml`.
- L'ensemble des services doit communiquer correctement :
  - Backend interroge DuckDB via des volumes de données partagés.
  - Frontend consomme les endpoints REST exposés par le backend.
- Garantie de reproductibilité entre différents environnements (développement, production).

---

#### **5. RÉPARTITION DES RESSOURCES**

**Sources de données :**
1. **[TMDB API](https://developers.themoviedb.org/3/getting-started)**  
   - URL utile pour récupérer des films populaires :  
     `https://api.themoviedb.org/3/movie/popular`
   - Données principales : titre, vote_average, description, genres.

2. **[The Movies Dataset sur Kaggle](https://www.kaggle.com/rounakbanik/the-movies-dataset)**  
   - Données principales disponibles dans `ratings.csv` : user_id, film_id, notes, horodatage.

**Technologies :**
- **DuckDB** : Pour gérer la base de données.
- **Flask/FastAPI** : Pour implémenter le backend.
- **Streamlit/Dash** : Pour l'application frontend.
- **Docker Compose** : Pour déployer les services interconnectés.
- **Surprise ou Scikit-learn** : Pour les algorithmes de filtrage collaboratif.

---

#### **6. LIVRABLES ATTENDUS**

1. **Base DuckDB** contenant :
   - Le fichier .Sql pour crée les tables et les valeurs crée avec SqlAlchemy puis dumpé sours format SQL (dump de base de donnée)
   -  Les tables `films` et `ratings`, avec les données de TMDB et Kaggle correctement chargées.

2. **Code backend (API Flask/FastAPI)** :
   - Récupérer les données de DuckDB et fournir des recommandations basées sur des prédictions SVD.
   - Fournir les endpoints nécessaires décrits ci-dessus.

3. **Application frontend (dashboard)** :
   - Réaliser des visualisations interactives à partir de DuckDB.
   - Consommer les recommandations générées par le backend.

4. **Fichier Docker Compose** :
   - Déployer automatiquement tous les services.

5. **Documentation** :
   - Instructions pour installer, configurer, exécuter et tester le projet.



#### **7. DÉLAI D'EVALUATION**

Le projet doit être livré sous un délai de **6 semaines**, découpées comme suit :
1. **Semaine 1-2** : Collecte des données et configuration de la base DuckDB.
2. **Semaine 3-4** : Développement du backend et mise en œuvre du modèle de recommandation.
3. **Semaine 5** : Création de l'interface frontend.
4. **Semaine 6** : Integration finale et déploiement avec Docker Compose.

---

#### **8. CRITÈRES DE QUALITÉ**

---

1. **METHODOGIE** Suivi de méthodologie etudiée pendant le cours pour créer un code production (modules, logging, typing, error handling ... etc)
2. Code bien structuré et documenté.
3. Visualisation claire informative.

--- 

#### **9. RECOMPONSE**

Voyage tout frais payés à DisneyLand 🤥