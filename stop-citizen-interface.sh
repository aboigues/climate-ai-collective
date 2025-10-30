#!/bin/bash

# Script d'arrêt pour l'interface citoyenne
# Climate AI Collective

echo "Arrêt de l'interface citoyenne..."

# Arrêter l'API (port 8002)
API_PID=$(lsof -ti:8002)
if [ ! -z "$API_PID" ]; then
    kill $API_PID
    echo "✓ API arrêtée (PID: $API_PID)"
else
    echo "✓ API n'était pas lancée"
fi

# Arrêter le frontend (port 8080)
FRONTEND_PID=$(lsof -ti:8080)
if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID
    echo "✓ Frontend arrêté (PID: $FRONTEND_PID)"
else
    echo "✓ Frontend n'était pas lancé"
fi

echo ""
echo "Tous les services ont été arrêtés."
