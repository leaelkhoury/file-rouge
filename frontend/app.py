"""IL FAUT FAIRE JAVA SCRIPT PAS PYTHON """

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# URL de l'API backend (remplacez par l'URL réelle de votre serveur FastAPI)
API_URL = "http://backend:8000"

# Fonction pour récupérer les recommandations d'un utilisateur
def get_recommendations(user_id):
    response = requests.post(f"{API_URL}/recommendations/{user_id}")
    if response.status_code == 200:
        return response.json()['recommendations']
    else:
        st.error("Erreur lors de la récupération des recommandations.")
        return []

# Fonction pour afficher la distribution des notes moyennes des films
def plot_average_ratings_distribution():
    # Charger les données des films et des notes (ou API)
    ratings_df = pd.read_csv('ratings.csv')
    avg_ratings = ratings_df.groupby('movieId')['rating'].mean()
    
    # Visualisation
    fig, ax = plt.subplots()
    sns.histplot(avg_ratings, bins=30, kde=True, ax=ax)
    ax.set_title("Distribution des notes moyennes des films")
    ax.set_xlabel("Note moyenne")
    ax.set_ylabel("Nombre de films")
    st.pyplot(fig)

# Fonction pour afficher l'évolution du nombre de films par année
def plot_movies_per_year():
    # Charger les données des films (ou API)
    movies_df = pd.read_csv('movies.csv')
    movies_df['year'] = pd.to_datetime(movies_df['release_date'], errors='coerce').dt.year
    movies_per_year = movies_df.groupby('year').size()
    
    # Visualisation
    fig, ax = plt.subplots()
    movies_per_year.plot(kind='bar', ax=ax)
    ax.set_title("Évolution du nombre de films par année")
    ax.set_xlabel("Année")
    ax.set_ylabel("Nombre de films")
    st.pyplot(fig)

# Fonction pour afficher les recommandations
def show_recommendations():
    # Formulaire pour saisir un user_id
    user_id = st.text_input("Entrez votre user_id pour obtenir des recommandations:")
    
    if user_id:
        try:
            user_id = int(user_id)
            recommendations = get_recommendations(user_id)
            
            if recommendations:
                st.write(f"Films recommandés pour l'utilisateur {user_id}:")
                for rec in recommendations:
                    st.write(f"**{rec['title']}** - Note prédite: {rec['rating_predicted']}")
            else:
                st.warning("Aucune recommandation disponible.")
        except ValueError:
            st.error("Veuillez entrer un identifiant utilisateur valide.")

# Interface principale de l'application
st.title("Dashboard des Films et Recommandations")

# Afficher les graphiques d'analyse
st.header("Analyse des Films")
plot_average_ratings_distribution()
plot_movies_per_year()

# Afficher les recommandations
st.header("Recommandations Personnalisées")
show_recommendations()

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
