# Frontend Dockerfile pour Climate AI Collective
# Servit les fichiers statiques HTML/CSS/JS via nginx

FROM nginx:alpine

# Copier les fichiers statiques dans le répertoire nginx
COPY index.html proposal.html /usr/share/nginx/html/
COPY styles.css app.js proposal.js /usr/share/nginx/html/

# Copier la configuration nginx personnalisée
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Créer un script pour injecter l'URL de l'API au runtime
RUN echo '#!/bin/sh' > /docker-entrypoint.d/40-inject-api-url.sh && \
    echo 'set -e' >> /docker-entrypoint.d/40-inject-api-url.sh && \
    echo 'API_URL="${API_BASE_URL:-http://localhost:8002}"' >> /docker-entrypoint.d/40-inject-api-url.sh && \
    echo 'echo "Configuring API URL: $API_URL"' >> /docker-entrypoint.d/40-inject-api-url.sh && \
    echo 'sed -i "s|http://localhost:8002|$API_URL|g" /usr/share/nginx/html/app.js' >> /docker-entrypoint.d/40-inject-api-url.sh && \
    echo 'sed -i "s|http://localhost:8002|$API_URL|g" /usr/share/nginx/html/proposal.js' >> /docker-entrypoint.d/40-inject-api-url.sh && \
    chmod +x /docker-entrypoint.d/40-inject-api-url.sh

# Exposer le port 80
EXPOSE 80

# L'entrypoint par défaut de nginx:alpine gère déjà le démarrage
# Les scripts dans /docker-entrypoint.d/ sont exécutés automatiquement

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Labels pour métadonnées
LABEL maintainer="Climate AI Collective"
LABEL description="Frontend citoyen pour consultation et vote des propositions climatiques"
LABEL version="1.0"
