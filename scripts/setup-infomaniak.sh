#!/bin/bash
#
# Script de setup pour déployer Climate AI Collective sur Infomaniak Public Cloud
#

set -e

echo "🌍 Climate AI Collective - Setup sur Infomaniak"
echo "================================================"
echo ""

# Vérifications préalables
echo "📋 Vérification des prérequis..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl n'est pas installé"
    echo "Installation: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✅ Prérequis OK"
echo ""

# Configuration
echo "⚙️  Configuration..."
read -p "Voulez-vous utiliser un fichier de configuration existant? (y/n): " use_config

if [ "$use_config" = "y" ]; then
    read -p "Chemin du fichier config.yaml: " config_path
    cp "$config_path" config.yaml
else
    echo "Création d'une nouvelle configuration..."
    cat > config.yaml <<EOF
# Climate AI Collective - Configuration

# Infomaniak
infomaniak:
  project_id: "your-project-id"
  region: "ch-dc1"  # Geneva datacenter
  s3_endpoint: "https://s3.infomaniak.com"
  s3_bucket: "climate-ai-data"

# Kubernetes
kubernetes:
  namespace: "climate-ai"
  gpu_node_pool: "gpu-l4-pool"

# LLM Endpoints
llm:
  orchestrator:
    replicas: 1
    gpu_count: 1
  mistral_large:
    replicas: 1
    gpu_count: 2
  deepseek:
    replicas: 1
    gpu_count: 1
  llama:
    replicas: 0  # Scale to zero
    gpu_count: 1

# GitHub
github:
  repo: "votre-org/climate-ai-collective"
  
# Monitoring
monitoring:
  enabled: true
  prometheus: true
  grafana: true
EOF
    
    echo "⚠️  Veuillez éditer config.yaml avec vos valeurs"
    echo "Puis relancez ce script"
    exit 0
fi

echo ""
echo "🔐 Configuration des secrets..."

# Vérifier si les secrets existent
if [ ! -f "kubernetes/base/storage/secrets.yaml" ]; then
    echo "Création du fichier secrets..."
    
    read -p "Hugging Face Token (pour télécharger les modèles): " hf_token
    read -p "GitHub Token (pour l'intégration): " gh_token
    read -p "S3 Access Key (Infomaniak): " s3_key
    read -sp "S3 Secret Key (Infomaniak): " s3_secret
    echo ""
    read -sp "PostgreSQL Password: " pg_password
    echo ""
    
    cat > kubernetes/base/storage/secrets.yaml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: huggingface-secret
  namespace: climate-ai
type: Opaque
stringData:
  token: "${hf_token}"
---
apiVersion: v1
kind: Secret
metadata:
  name: github-secret
  namespace: climate-ai
type: Opaque
stringData:
  token: "${gh_token}"
---
apiVersion: v1
kind: Secret
metadata:
  name: s3-secret
  namespace: climate-ai
type: Opaque
stringData:
  access_key: "${s3_key}"
  secret_key: "${s3_secret}"
  endpoint: "https://s3.infomaniak.com"
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: climate-ai
type: Opaque
stringData:
  username: "climate_ai"
  password: "${pg_password}"
  database: "climate_ai_db"
EOF
    
    echo "✅ Secrets créés"
else
    echo "✅ Fichier secrets.yaml existe déjà"
fi

echo ""
echo "🚀 Déploiement sur Kubernetes..."

# Connexion au cluster
echo "Configuration du contexte Kubernetes..."
read -p "Nom du cluster Kubernetes: " cluster_name

kubectl config use-context "$cluster_name" || {
    echo "❌ Impossible de se connecter au cluster"
    echo "Configurez d'abord kubectl pour accéder à votre cluster Infomaniak"
    exit 1
}

# Création du namespace
echo "Création du namespace..."
kubectl apply -f kubernetes/base/namespace.yaml

# Application des secrets
echo "Application des secrets..."
kubectl apply -f kubernetes/base/storage/secrets.yaml

# Création des PVC
echo "Création des volumes de stockage..."
kubectl apply -f kubernetes/base/storage/pvc.yaml

# Attendre que les PVC soient bound
echo "Attente de la préparation des volumes..."
kubectl wait --for=jsonpath='{.status.phase}'=Bound \
    pvc/vllm-model-cache -n climate-ai --timeout=120s || {
    echo "⚠️  Timeout en attendant les PVC"
    echo "Les PVC sont peut-être encore en cours de provisioning"
}

# Déploiement de l'orchestrateur
echo "Déploiement de l'orchestrateur..."
kubectl apply -f kubernetes/base/orchestrator/deployment.yaml

# Déploiement des LLM workers
echo "Déploiement des LLM workers..."
kubectl apply -f kubernetes/base/llm-workers/

echo ""
echo "⏳ Attente du démarrage des pods..."
echo "Cela peut prendre 10-15 minutes (téléchargement des modèles)"
echo ""

# Surveiller les pods
kubectl get pods -n climate-ai -w &
WATCH_PID=$!

# Attendre que les pods soient prêts (timeout 20 minutes)
kubectl wait --for=condition=ready pod \
    -l component=llm \
    -n climate-ai \
    --timeout=1200s || {
    echo "⚠️  Certains pods ne sont pas prêts après 20 minutes"
    echo "Vérifiez les logs avec: kubectl logs -n climate-ai <pod-name>"
}

kill $WATCH_PID 2>/dev/null || true

echo ""
echo "✅ Déploiement terminé!"
echo ""
echo "📊 État du cluster:"
kubectl get pods -n climate-ai
echo ""
kubectl get svc -n climate-ai
echo ""

echo "🎉 Climate AI Collective est déployé!"
echo ""
echo "🔍 Commandes utiles:"
echo "  - Voir les logs de l'orchestrateur:"
echo "    kubectl logs -f -n climate-ai -l app=orchestrator"
echo ""
echo "  - Voir l'état des LLM:"
echo "    kubectl get pods -n climate-ai -l component=llm-worker"
echo ""
echo "  - Accéder à l'API de l'orchestrateur (port-forward):"
echo "    kubectl port-forward -n climate-ai svc/orchestrator-service 8000:8000"
echo ""
echo "  - Surveiller les ressources GPU:"
echo "    kubectl top pods -n climate-ai"
echo ""
echo "📖 Documentation: https://github.com/votre-org/climate-ai-collective"
echo ""
