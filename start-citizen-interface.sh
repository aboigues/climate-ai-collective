#!/bin/bash

# Script de démarrage rapide pour l'interface citoyenne
# Climate AI Collective

set -e

echo "========================================"
echo "Climate AI Collective - Interface Citoyenne"
echo "========================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si l'API est déjà lancée
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo -e "${YELLOW}L'API est déjà lancée sur http://localhost:8002${NC}"
else
    echo "1. Installation des dépendances de l'API..."
    cd services/citizen-api
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Dépendances installées${NC}"
    echo ""

    echo "2. Lancement de l'API..."
    nohup python main.py > /tmp/citizen-api.log 2>&1 &
    API_PID=$!
    echo "API lancée (PID: $API_PID)"
    echo "Logs: /tmp/citizen-api.log"

    # Attendre que l'API soit prête
    echo -n "Attente du démarrage de l'API"
    for i in {1..10}; do
        if curl -s http://localhost:8002/health > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✓ API prête${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""

    cd ../..
fi

# Vérifier si le frontend est déjà lancé
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo -e "${YELLOW}Le frontend est déjà lancé sur http://localhost:8080${NC}"
else
    echo "3. Lancement du frontend..."
    cd frontend
    nohup python -m http.server 8080 > /tmp/citizen-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend lancé (PID: $FRONTEND_PID)"
    echo "Logs: /tmp/citizen-frontend.log"
    echo -e "${GREEN}✓ Frontend prêt${NC}"
    cd ..
fi

echo ""
echo "========================================"
echo -e "${GREEN}Système démarré avec succès !${NC}"
echo "========================================"
echo ""
echo "API:      http://localhost:8002"
echo "API docs: http://localhost:8002/docs"
echo "Frontend: http://localhost:8080"
echo ""
echo "Pour arrêter les services:"
echo "  killall python"
echo "  ou consultez /tmp/citizen-*.log pour les PIDs"
echo ""
echo "Documentation complète: CITIZEN_INTERFACE.md"
echo ""
