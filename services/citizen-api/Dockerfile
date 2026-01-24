FROM python:3.11-slim

# Mettre à jour les packages de sécurité pour corriger les vulnérabilités
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Mettre à jour pip
RUN pip install --no-cache-dir --upgrade pip

# Copier les requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Forcer la mise à jour de wheel pour corriger CVE-2026-24049
RUN pip install --no-cache-dir --upgrade --force-reinstall "wheel>=0.46.2"

# Copier le code de l'application
COPY main.py .

# Créer le répertoire pour les données de vote
RUN mkdir -p /app/data

# Exposer le port
EXPOSE 8002

# Lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
