# Utiliser une image de base Python officielle avec Python 3.11
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt /app/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source dans le conteneur
COPY . ./app

# Exposer le port sur lequel FastAPI fonctionne (par défaut, FastAPI écoute sur le port 8000)
EXPOSE 8000

# Commande pour démarrer l'application FastAPI avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
