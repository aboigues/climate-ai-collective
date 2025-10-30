# 🚀 Guide de Démarrage Rapide

Ce guide vous permet de démarrer avec Climate AI Collective en moins de 15 minutes.

## Option 1: Développement Local (Recommandé pour débuter)

### Prérequis
- Python 3.11+
- Docker & Docker Compose
- Git

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/votre-org/climate-ai-collective.git
cd climate-ai-collective

# 2. Configuration automatique
make setup

# 3. Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 4. Lancer les services
make dev
```

**C'est tout!** Les services sont maintenant accessibles:

- 🤖 **Orchestrator**: http://localhost:8000
- ✅ **Validation**: http://localhost:8001  
- 📦 **MinIO (S3)**: http://localhost:9001
- 📊 **Grafana**: http://localhost:3000
- 🔍 **Prometheus**: http://localhost:9090

### Test Rapide

```bash
# Tester le validateur
python services/validation/validator.py --test

# Tester l'orchestrateur
python services/orchestrator/main.py
```

### Arrêter les services

```bash
make stop
```

## Option 2: Déploiement Production sur Infomaniak

### Prérequis
- Compte Infomaniak Public Cloud
- kubectl configuré
- Accès à un cluster Kubernetes

### Installation

```bash
# 1. Cloner et configurer
git clone https://github.com/votre-org/climate-ai-collective.git
cd climate-ai-collective

# 2. Copier et éditer la configuration
cp config.example.yaml config.yaml
# Éditer config.yaml avec vos credentials

# 3. Lancer le setup automatique
make k8s-setup

# Suivre les instructions à l'écran
```

Le script configure automatiquement:
- ✅ Namespace Kubernetes
- ✅ Secrets et credentials
- ✅ Volumes de stockage (500GB pour modèles)
- ✅ Déploiements vLLM (Mistral, DeepSeek, Llama)
- ✅ Services et load balancers

### Vérifier le déploiement

```bash
# Statut du cluster
make k8s-status

# Logs de l'orchestrator
make k8s-logs
```

## Utilisation

### Déclencher une itération AI manuellement

Via GitHub Actions:
1. Aller sur l'onglet "Actions"
2. Sélectionner "AI Iteration Workflow"
3. Cliquer "Run workflow"
4. Choisir un domaine (transport, energie, etc.)

Via CLI:
```bash
python scripts/trigger_iteration.py --domain transport
```

### Consulter les propositions

Les propositions générées sont dans:
```
domains/
├── transport/proposals/
├── energie/proposals/
├── batiment/proposals/
└── ...
```

Chaque proposition contient:
- `proposal.json` - La proposition complète
- `validation.json` - Résultats de validation
- `simulation_quick.json` - Simulation rapide
- `simulation_deep.json` - Simulation approfondie (si applicable)

### Review d'une proposition

1. Une PR est créée automatiquement
2. Un bot AI (DeepSeek) fait une review automatique
3. Vous pouvez commenter et discuter
4. Vote citoyen (à venir)

## Architecture Simplifiée

```
┌─────────────────────────────────────────┐
│  GitHub Actions (Automatisation)        │
│  - Déclenchement hebdomadaire           │
│  - Création PR automatique              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  LLM Orchestrateur (Mistral Small)      │
│  - Planification des tâches             │
│  - Routing vers LLM spécialisés         │
└──────────────┬──────────────────────────┘
               │
     ┌─────────┼─────────┐
     │         │         │
┌────▼───┐ ┌──▼────┐ ┌──▼────┐
│Mistral │ │DeepSeek│ │ Llama │
│ Large  │ │  R1    │ │  3.3  │
└────┬───┘ └───┬────┘ └───┬───┘
     │         │          │
     └─────────┼──────────┘
               │
      ┌────────▼────────┐
      │   Validation    │
      │   + Simulation  │
      └────────┬────────┘
               │
      ┌────────▼────────┐
      │  GitHub Repo    │
      │  (Propositions) │
      └─────────────────┘
```

## Commandes Utiles

### Développement Local
```bash
make dev           # Démarre l'environnement
make stop          # Arrête l'environnement
make logs          # Affiche les logs
make test          # Lance les tests
make quality       # Vérifie la qualité du code
```

### Kubernetes
```bash
make k8s-deploy    # Déploie sur K8s
make k8s-status    # Statut du cluster
make k8s-logs      # Logs des pods
```

### Maintenance
```bash
make clean         # Nettoie les fichiers temporaires
make format        # Formate le code
```

## Configuration des Secrets

Pour le déploiement production, créer `kubernetes/base/storage/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: huggingface-secret
  namespace: climate-ai
stringData:
  token: "hf_your_token_here"
---
# ... autres secrets
```

⚠️ **Important**: Ne jamais commiter les secrets dans Git!

## Troubleshooting

### Les pods ne démarrent pas
```bash
# Vérifier les events
kubectl describe pod -n climate-ai <pod-name>

# Vérifier les logs
kubectl logs -n climate-ai <pod-name>
```

### Modèles LLM trop lents à charger
C'est normal! Le premier démarrage prend 10-15 minutes car les modèles sont téléchargés (~40-50GB).

Les démarrages suivants sont plus rapides grâce au cache.

### Erreur de mémoire GPU
Réduire `gpu_memory_utilization` dans les configs de déploiement (0.90 → 0.80).

## Prochaines Étapes

1. ✅ **Explorer le code**: Commencer par `services/orchestrator/main.py`
2. 📚 **Lire la doc**: Voir `docs/` pour plus de détails
3. 🤝 **Contribuer**: Voir `CONTRIBUTING.md`
4. 💬 **Rejoindre la communauté**: GitHub Discussions

## Ressources

- 📖 **Documentation complète**: [docs/](./docs/)
- 🐛 **Signaler un bug**: [GitHub Issues](https://github.com/votre-org/climate-ai-collective/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/votre-org/climate-ai-collective/discussions)
- 📧 **Contact**: hello@climate-ai-collective.org

---

🌍 **Bienvenue dans la lutte climatique propulsée par l'IA!** 🌱
