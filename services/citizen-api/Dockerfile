FROM python:3.11-slim

# Mettre à jour les packages de sécurité pour corriger les vulnérabilités
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Mettre à jour pip et setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools

# Copier les requirements et constraints, puis installer les dépendances
# Constraints force les versions minimales pour CVE-2026-24049 (wheel) et CVE-2026-23949 (jaraco.context)
COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -c constraints.txt -r requirements.txt

# Supprimer les packages vendored vulnérables de setuptools
# CVE-2026-24049 (wheel) et CVE-2026-23949 (jaraco.context)
RUN find /usr/local -path "*/setuptools/_vendor/jaraco.context*" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local -path "*/setuptools/_vendor/wheel*" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local -path "*/wheel-0.45*" -exec rm -rf {} + 2>/dev/null || true

# Copier le code de l'application
COPY main.py .

# Créer le répertoire pour les données de vote
RUN mkdir -p /app/data

# Exposer le port
EXPOSE 8002

# Lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
