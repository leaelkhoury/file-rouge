import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Movie Recommendation Dashboard", layout="wide")

# URL de l'API backend (à adapter selon votre déploiement)
API_URL = "http://localhost:8000"


# Utilise st.cache_data si disponible, sinon st.cache
cache_decorator = st.cache_data if hasattr(st, 'cache_data') else st.cache

# Fonctions pour récupérer les données depuis l'API
@cache_decorator
def get_all_movies():
    response = requests.get(f"{API_URL}/movies/?limit=10000")
    return pd.DataFrame(response.json())

@cache_decorator
def get_ratings():
    response = requests.get(f"{API_URL}/ratings/")
    return pd.DataFrame(response.json())

@cache_decorator
def get_recommendations(user_id):
    response = requests.get(f"{API_URL}/recommend_movies/{user_id}")
    return response.json()

# Chargement des données
movies_df = get_all_movies()
ratings_df = get_ratings()

# Sidebar pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choisir une section", 
                        ["Tableau de bord", "Recommandations", "Exploration des films"])

if page == "Tableau de bord":
    # Titre principal
    st.title("📊 Tableau de bord d'analyse des films")

    # 1. Distribution des notes moyennes des films
    st.header("Distribution des notes moyennes des films")
    fig, ax = plt.subplots()
    sns.histplot(movies_df['vote_average'], bins=20, kde=True, ax=ax)
    ax.set_xlabel("Note moyenne")
    ax.set_ylabel("Nombre de films")
    st.pyplot(fig)

    # 2. Évolution du nombre de films par année
    st.header("Évolution du nombre de films par année")
    movies_df['year'] = pd.to_datetime(movies_df['release_date']).dt.year
    films_par_an = movies_df.groupby('year').size().reset_index(name='count')
    
    fig, ax = plt.subplots()
    sns.lineplot(data=films_par_an, x='year', y='count', ax=ax)
    ax.set_xlabel("Année")
    ax.set_ylabel("Nombre de films")
    st.pyplot(fig)

    # 3. Top films par note moyenne
    st.header("Top 10 des films les mieux notés")
    top_films = movies_df.sort_values('vote_average', ascending=False).head(10)
    st.dataframe(top_films[['title', 'vote_average', 'genres', 'year']])

    # 4. Statistiques des utilisateurs
    st.header("Distribution des notes attribuées par les utilisateurs")
    if not ratings_df.empty:
        fig, ax = plt.subplots()
        sns.countplot(data=ratings_df, x='rating', ax=ax)
        ax.set_xlabel("Note")
        ax.set_ylabel("Nombre d'évaluations")
        st.pyplot(fig)
    else:
        st.warning("Aucune donnée d'évaluation disponible")

elif page == "Recommandations":
    st.title("🎬 Système de recommandation de films")
    
    # Formulaire pour saisir l'ID utilisateur
    user_id = st.number_input("Entrez un ID utilisateur (1-1000)", 
                             min_value=1, max_value=1000, value=1)
    
    if st.button("Obtenir des recommandations"):
        with st.spinner("Recherche des recommandations..."):
            try:
                recommendations = get_recommendations(user_id)
                
                st.subheader(f"Recommandations pour l'utilisateur {user_id}")
                rec_df = pd.DataFrame(recommendations['recommendations'])
                st.dataframe(rec_df[['title', 'rating_predicted']].sort_values('rating_predicted', ascending=False))
                
                # Visualisation des recommandations
                fig, ax = plt.subplots()
                sns.barplot(data=rec_df, x='rating_predicted', y='title', ax=ax)
                ax.set_xlabel("Note prédite")
                ax.set_ylabel("Film")
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Erreur lors de la récupération des recommandations: {e}")

elif page == "Exploration des films":
    st.title("🔍 Exploration des films")
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        selected_genre = st.selectbox("Filtrer par genre", 
                                     ['Tous'] + sorted(movies_df['genres'].str.split('|').explode().unique()))
    
    with col2:
        selected_year = st.selectbox("Filtrer par année", 
                                    ['Tous'] + sorted(movies_df['year'].unique(), reverse=True))
    
    # Application des filtres
    filtered_df = movies_df.copy()
    if selected_genre != 'Tous':
        filtered_df = filtered_df[filtered_df['genres'].str.contains(selected_genre)]
    if selected_year != 'Tous':
        filtered_df = filtered_df[filtered_df['year'] == selected_year]
    
    # Affichage des résultats
    st.subheader(f"Films {selected_genre if selected_genre != 'Tous' else ''} {selected_year if selected_year != 'Tous' else ''}")
    st.dataframe(filtered_df[['title', 'vote_average', 'genres', 'year']].sort_values('vote_average', ascending=False))
    
    # Statistiques par genre
    if selected_genre == 'Tous':
        st.header("Répartition des films par genre")
        genres_count = movies_df['genres'].str.split('|').explode().value_counts()
        fig, ax = plt.subplots(figsize=(10, 6))
        genres_count.plot(kind='bar', ax=ax)
        ax.set_xlabel("Genre")
        ax.set_ylabel("Nombre de films")
        st.pyplot(fig)

# Pied de page
st.sidebar.markdown("---")
st.sidebar.markdown("**Système de recommandation de films**")
st.sidebar.markdown("Utilise l'API FastAPI avec un modèle SVD")
___________________________________________________________________________________________________________________________________________________

"""
Explication du Code :
Streamlit (app.py) :

Visualisation des données : Vous utilisez seaborn et matplotlib pour afficher des graphiques sur la distribution des notes moyennes des films et l'évolution du nombre de films par année.
Recommandations personnalisées : Vous utilisez une interface Streamlit qui permet à l'utilisateur de saisir un user_id et affiche les films recommandés par l'API du back-end.
Dockerfile :

Ce fichier définit un conteneur Docker pour exécuter l'application Streamlit sur le port 8501.
requirements.txt :

Liste les bibliothèques nécessaires pour l'exécution de votre application Streamlit et pour la manipulation de données (pandas, matplotlib, seaborn, etc.).
Docker Compose :

Si vous utilisez Docker Compose, ce fichier orchestrera les services pour votre front-end, back-end, et la base de données DuckDB. Il crée un environnement isolé avec les conteneurs correspondants.
"""


"""
Comment Exécuter le Projet ?

Lancer le backend (FastAPI) :
bash:

pip install -r requirements.txt    ou bien      pip install streamlit fastapi uvicorn duckdb pandas matplotlib seaborn requests
uvicorn backend:app --reload
streamlit run app.py


Ouvrir dans le navigateur :

    API : http://localhost:8000/docs

    Dashboard : http://localhost:8501

Exemple de Résultat Attendu

Page "Analytique" : Des graphiques montrant que 60% des films ont une note entre 5 et 7, avec un pic de sorties en 2015.

Page "Recommandations" : Pour l'utilisateur 42, suggestion de Inception (note prédite: 4.8) et The Dark Knight (4.7).

Page "Exploration" : En filtrant par "Action" et "2020", affiche Tenet et Extraction.

""""
