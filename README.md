# Climate AI Collective 🌍

Un parlement d'intelligences artificielles open-source dédié à la lutte contre le réchauffement climatique, fonctionnant de manière décentralisée sur infrastructure souveraine.

## 🎯 Vision

Le Climate AI Collective est un système où plusieurs LLM locaux (Mistral, DeepSeek, Llama) collaborent pour générer, valider et simuler des propositions concrètes d'action climatique. Chaque proposition est versionnée sur GitHub, simulée scientifiquement, et soumise au vote citoyen.

## 🏗️ Architecture

### Stack Technique
- **Orchestration** : Kubernetes sur Infomaniak Public Cloud (100% énergie renouvelable)
- **LLM Inference** : vLLM avec Mistral Large, DeepSeek R1, Llama 3.3
- **Simulation** : FaIR (climate model), OSeMOSYS (energy), LCA (lifecycle)
- **Stockage** : S3 compatible (Infomaniak Object Storage) + PostgreSQL
- **Interface** : API REST + Dashboard Web

### Composants
```
┌─────────────────────────────────────────────────┐
│  LLM Orchestrator (Mistral Small)              │
│  Décide quelle IA appeler pour chaque tâche    │
└─────────────────┬───────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐    ┌───▼────┐    ┌──▼─────┐
│Mistral│    │DeepSeek│    │ Llama  │
│ Large │    │   R1   │    │  3.3   │
│Proposa│    │Validat.│    │Synthèse│
└───┬───┘    └───┬────┘    └──┬─────┘
    │            │            │
    └────────────┼────────────┘
                 │
         ┌───────▼────────┐
         │   Simulation   │
         │     Engine     │
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │  GitHub Repo   │
         │  (versioning)  │
         └────────────────┘
```

## 🚀 Démarrage Rapide

### Prérequis
- Compte Infomaniak Public Cloud
- kubectl installé
- Terraform >= 1.5 (optionnel)
- Python >= 3.10

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/votre-org/climate-ai-collective.git
cd climate-ai-collective

# 2. Configuration
cp config.example.yaml config.yaml
# Éditer config.yaml avec vos credentials Infomaniak

# 3. Créer l'infrastructure Kubernetes
./scripts/setup-infomaniak.sh

# 4. Déployer les services
kubectl apply -k kubernetes/overlays/production

# 5. Vérifier le déploiement
kubectl get pods -n climate-ai
```

### Test Local (sans Kubernetes)

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancer l'orchestrateur en mode dev
python services/orchestrator/main.py --mode dev

# Lancer une validation test
python services/validation/validator.py --test
```

## 📁 Structure du Projet

```
climate-ai-collective/
├── .github/workflows/      # CI/CD automatisé
├── kubernetes/             # Manifests K8s
│   ├── base/              # Configuration de base
│   └── overlays/          # Dev/Prod configs
├── services/              # Code Python des microservices
│   ├── orchestrator/      # LLM orchestrator
│   ├── validation/        # Validation engine
│   ├── simulation/        # Simulation models
│   └── github-integration/# GitHub sync
├── context/               # Données scientifiques & prompts
├── domains/               # Propositions par domaine
│   ├── transport/
│   ├── energie/
│   ├── batiment/
│   └── agriculture/
├── docs/                  # Documentation détaillée
└── scripts/               # Scripts de déploiement
```

## 🌱 Domaines Couverts

- **🚗 Transport** : Mobilité douce, électrification, transport collectif
- **⚡ Énergie** : Renouvelables, efficacité, stockage
- **🏢 Bâtiment** : Isolation, rénovation, matériaux biosourcés
- **🌾 Agriculture** : Agroécologie, séquestration carbone
- **🏭 Industrie** : Décarbonation, économie circulaire
- **💡 Transversal** : Politiques publiques, finance verte

## 🤖 Cycle d'Itération

1. **Déclenchement** : CronJob hebdomadaire par domaine
2. **Analyse** : L'orchestrateur lit le contexte GitHub
3. **Génération** : Un LLM spécialisé crée une proposition
4. **Validation** : DeepSeek vérifie la cohérence scientifique
5. **Simulation** : Modèles calculent l'impact CO2 et économique
6. **PR GitHub** : Proposition soumise avec tous les artefacts
7. **Review** : Autre IA + experts humains + vote citoyen
8. **Merge** : Si validée, intégration au corpus de connaissances

## 📊 Système de Simulation

### Validation Immédiate (<30s)
- Vérification structurelle
- Cohérence scientifique (LLM)
- Qualité des sources

### Simulation Rapide (2-5 min)
- Impact CO2 sur 10 ans
- Analyse coût-bénéfice
- Courbe d'adoption sociale
- Effets de bord

### Simulation Approfondie (30-120 min)
- Modèle climatique FaIR
- Analyse cycle de vie (LCA)
- Évaluation intégrée (IAM)
- Analyse de sensibilité

### Simulation Systémique (2-6h)
- Interactions entre propositions
- Optimisation de séquence
- Résilience du système

## 🗳️ Interface Citoyenne

Les citoyens peuvent :
- Consulter toutes les propositions et simulations
- Voter sur les propositions (impact, faisabilité, désirabilité)
- Commenter et suggérer des améliorations
- Suivre l'évolution des propositions
- Proposer de nouveaux domaines

**Dashboard public** : https://dashboard.climate-ai-collective.org (à venir)

## 💰 Coûts Estimés

### Setup Production (6-8 domaines actifs)
- GPU permanents (3-4x NVIDIA L4) : ~600-800 CHF/mois
- GPU on-demand (simulations) : ~100-200 CHF/mois
- Infrastructure (DB, storage, network) : ~100 CHF/mois
- **Total : 800-1100 CHF/mois**

### Comparaison
- APIs cloud (Claude/GPT-4) : ~1500-2000 CHF/mois
- **Économie : 40-60% + souveraineté totale**

## 🌍 Impact Environnemental

- **Infrastructure** : 100% énergie renouvelable (Infomaniak)
- **Compensation CO2** : 200% (Infomaniak)
- **Datacenters** : Sans climatisation
- **Efficacité** : Optimisation GPU pour minimiser la consommation

## 🤝 Contribution

Nous accueillons les contributions à tous les niveaux :

1. **Code** : Améliorations des modèles, optimisations
2. **Science** : Validation des modèles de simulation
3. **Données** : Enrichissement du contexte scientifique
4. **Propositions** : Nouvelles idées d'action climatique
5. **Review** : Expertise sur les propositions

Voir [CONTRIBUTING.md](./CONTRIBUTING.md) pour les guidelines.

## 📄 Licence

Ce projet est sous licence **MIT** - voir [LICENSE](./LICENSE).

Les modèles LLM utilisés ont leurs propres licences :
- Mistral : Apache 2.0
- Llama : Llama 3 Community License
- DeepSeek : MIT

## 🙏 Remerciements

- **Infomaniak** : Infrastructure cloud souveraine et verte
- **Anthropic, Mistral AI, Meta, DeepSeek** : Modèles open source
- **Communauté open source** : vLLM, FaIR, OSeMOSYS, etc.
- **IPCC** : Données scientifiques climatiques

## 📞 Contact

- **GitHub Issues** : Pour les bugs et features
- **Discussions** : Pour les questions générales
- **Email** : contact@climate-ai-collective.org

---

*"L'intelligence artificielle au service de l'intelligence collective pour le climat"* 🌱
