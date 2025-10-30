# Interface Citoyenne - Climate AI Collective

Documentation complète de l'interface permettant aux citoyens de consulter les propositions climatiques et de voter.

## Vue d'ensemble

L'interface citoyenne est composée de deux parties :

1. **API REST** (`services/citizen-api/`) - Backend FastAPI exposant les propositions et gérant les votes
2. **Frontend Web** (`frontend/`) - Interface utilisateur HTML/CSS/JavaScript pour consulter et voter

## Architecture

```
┌─────────────────┐
│   Frontend      │  ← Interface web statique (HTML/CSS/JS)
│   (localhost:   │
│   8080)         │
└────────┬────────┘
         │ HTTP REST
         ↓
┌─────────────────┐
│   API REST      │  ← Backend FastAPI
│   (localhost:   │
│   8002)         │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│  Fichiers Git                           │
│  - domains/*/proposals/*/proposal.json  │ ← Propositions
│  - services/citizen-api/data/votes.json│ ← Votes
└─────────────────────────────────────────┘
```

## Installation et lancement

### 1. Lancer l'API

```bash
# Se positionner dans le répertoire de l'API
cd services/citizen-api

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
python main.py
```

L'API sera accessible sur **http://localhost:8002**

### 2. Lancer le frontend

Dans un nouveau terminal :

```bash
# Se positionner dans le répertoire frontend
cd frontend

# Lancer un serveur HTTP simple
python -m http.server 8080
```

Le frontend sera accessible sur **http://localhost:8080**

## Fonctionnalités

### Pour les citoyens

#### 1. Consulter les propositions

- **Liste des propositions** : http://localhost:8080/index.html
  - Vue d'ensemble de toutes les propositions
  - Filtres par domaine (Transport, Énergie, etc.)
  - Filtres par statut (Générée, Validée, etc.)
  - Statistiques globales (nombre de propositions, votes, CO2 réductible)

- **Détail d'une proposition** : http://localhost:8080/proposal.html?id={id}
  - Informations complètes (actions, budget, impact CO2)
  - Résultats de validation
  - Résultats de simulation
  - Statistiques de vote

#### 2. Voter sur une proposition

Chaque proposition peut être évaluée sur 3 axes (échelle 1-10) :

- **Impact climatique** : Potentiel de réduction des émissions de CO2
- **Faisabilité** : Facilité de mise en œuvre (technique, budget, délai)
- **Désirabilité sociale** : Acceptabilité et bénéfices pour la population

Les citoyens peuvent également ajouter un commentaire optionnel.

#### 3. Voir les résultats des votes

Les résultats sont agrégés en temps réel et affichés :
- Dans la liste des propositions (note globale)
- Sur la page de détail (moyennes par axe + note globale)

### Pour les développeurs

#### Endpoints API

**Propositions :**
- `GET /api/v1/proposals` - Liste toutes les propositions
- `GET /api/v1/proposals?domain=transport` - Filtrer par domaine
- `GET /api/v1/proposals/{id}` - Détails d'une proposition
- `GET /api/v1/domains` - Liste des domaines disponibles

**Votes :**
- `POST /api/v1/proposals/{id}/vote` - Enregistrer un vote
- `GET /api/v1/proposals/{id}/votes` - Résumé des votes

**Système :**
- `GET /` - Page d'accueil de l'API
- `GET /health` - Status de l'API

Documentation interactive : http://localhost:8002/docs

## Exemples d'utilisation

### Lister les propositions

```bash
curl http://localhost:8002/api/v1/proposals
```

### Obtenir les détails d'une proposition

```bash
curl http://localhost:8002/api/v1/proposals/transport-33b6fba2
```

### Voter sur une proposition

```bash
curl -X POST http://localhost:8002/api/v1/proposals/transport-33b6fba2/vote \
  -H "Content-Type: application/json" \
  -d '{
    "impact_score": 9,
    "feasibility_score": 7,
    "desirability_score": 8,
    "comment": "Excellente proposition pour réduire les émissions"
  }'
```

### Obtenir le résumé des votes

```bash
curl http://localhost:8002/api/v1/proposals/transport-33b6fba2/votes
```

## Stockage des données

### Propositions

Les propositions sont stockées dans Git :

```
domains/
└── {domain}/
    └── proposals/
        └── {proposal_id}/
            ├── proposal.json      ← Proposition complète
            ├── validation.json    ← Résultats de validation
            └── simulation_quick.json ← Résultats de simulation
```

### Votes

Les votes sont stockés dans un fichier JSON :

```
services/citizen-api/data/votes.json
```

Structure :
```json
{
  "votes": [
    {
      "vote_id": "uuid",
      "proposal_id": "transport-xxx",
      "impact_score": 9,
      "feasibility_score": 7,
      "desirability_score": 8,
      "comment": "...",
      "citizen_id": "anonymous",
      "timestamp": "2025-10-30T..."
    }
  ],
  "summaries": {
    "transport-xxx": {
      "total_votes": 5,
      "avg_impact_score": 8.2,
      "avg_feasibility_score": 7.4,
      "avg_desirability_score": 8.8,
      "avg_overall_score": 8.13
    }
  }
}
```

## Tests

Les tests ont validé :

✅ API répond correctement (endpoint `/health`)
✅ Liste des propositions fonctionne
✅ Détails d'une proposition sont retournés
✅ Votes sont enregistrés correctement
✅ Statistiques sont calculées correctement
✅ Moyennes sont mises à jour après chaque vote

Exemple de résultats de test :
```bash
# Vote 1: impact=9, feasibility=7, desirability=8
# Vote 2: impact=10, feasibility=6, desirability=9

# Résultats agrégés:
# avg_impact_score: 9.5 (9+10)/2
# avg_feasibility_score: 6.5 (7+6)/2
# avg_desirability_score: 8.5 (8+9)/2
# avg_overall_score: 8.17 (9.5+6.5+8.5)/3
```

## Déploiement en production

### Docker

Un Dockerfile est fourni pour l'API :

```bash
cd services/citizen-api

# Build
docker build -t citizen-api .

# Run
docker run -p 8002:8002 \
  -v $(pwd)/../../domains:/home/user/climate-ai-collective/domains:ro \
  -v $(pwd)/data:/app/data \
  citizen-api
```

### Frontend statique

Le frontend peut être déployé sur n'importe quel serveur web statique :
- GitHub Pages
- Netlify
- Vercel
- Nginx
- Apache

**Important :** Mettre à jour l'URL de l'API dans `app.js` et `proposal.js` :

```javascript
const API_BASE_URL = 'https://api.climate-ai-collective.org';
```

## Améliorations futures

### Court terme
- [ ] Authentification des citoyens (optionnelle)
- [ ] Système de commentaires
- [ ] Pagination de la liste des propositions
- [ ] Export des propositions en PDF

### Moyen terme
- [ ] Graphiques interactifs pour les simulations
- [ ] Notifications en temps réel (WebSocket)
- [ ] Partage sur les réseaux sociaux
- [ ] Mode sombre

### Long terme
- [ ] Application mobile (React Native / Flutter)
- [ ] Analyse des votes (tendances, corrélations)
- [ ] Forum de discussion par proposition
- [ ] Système de recommandation de propositions

## Sécurité

### Recommandations

Pour un déploiement en production :

1. **CORS** : Restreindre les origines autorisées dans `main.py`
   ```python
   allow_origins=["https://dashboard.climate-ai-collective.org"]
   ```

2. **Rate limiting** : Limiter le nombre de votes par IP/utilisateur

3. **Validation** : Ajouter une validation CAPTCHA pour éviter les bots

4. **Authentification** : Implémenter OAuth2 ou JWT pour l'identification

5. **HTTPS** : Utiliser TLS/SSL en production

6. **Backup** : Sauvegarder régulièrement `votes.json`

## Support et contribution

- **Documentation API** : http://localhost:8002/docs
- **README API** : `services/citizen-api/README.md`
- **README Frontend** : `frontend/README.md`
- **Code source** : GitHub (projet open-source)

## Licence

Open-source - Voir le fichier LICENSE du projet principal
