# Citizen API - Interface Citoyenne

API REST permettant aux citoyens de consulter les propositions climatiques et de voter.

## Fonctionnalités

- **Consultation des propositions** : Liste et détails de toutes les propositions générées par le système
- **Système de vote** : Les citoyens peuvent voter sur 3 axes (impact, faisabilité, désirabilité)
- **Statistiques** : Résumés des votes agrégés en temps réel

## Installation

```bash
cd services/citizen-api

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python main.py
```

L'API sera accessible sur http://localhost:8002

## Endpoints

### Consultation des propositions

- `GET /api/v1/proposals` - Liste toutes les propositions
  - Query params: `domain` (optionnel), `status` (optionnel)
- `GET /api/v1/proposals/{id}` - Détails d'une proposition
- `GET /api/v1/domains` - Liste des domaines disponibles

### Vote

- `POST /api/v1/proposals/{id}/vote` - Voter sur une proposition
- `GET /api/v1/proposals/{id}/votes` - Résumé des votes

### Système

- `GET /` - Page d'accueil avec la liste des endpoints
- `GET /health` - Status de l'API

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

## Format du vote

Les votes sont notés sur une échelle de 1 à 10 sur 3 axes :

- **Impact climatique** (1-10) : Potentiel de réduction des émissions de CO2
- **Faisabilité** (1-10) : Facilité de mise en œuvre (technique, budget, délai)
- **Désirabilité sociale** (1-10) : Acceptabilité et bénéfices pour la population

## Stockage des données

Les votes sont stockés dans `services/citizen-api/data/votes.json`

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

## Docker

```bash
# Build
docker build -t citizen-api .

# Run
docker run -p 8002:8002 \
  -v $(pwd)/../../domains:/domains:ro \
  -v $(pwd)/data:/app/data \
  citizen-api
```

## Documentation interactive

Une fois l'API lancée, accédez à la documentation interactive :

- Swagger UI : http://localhost:8002/docs
- ReDoc : http://localhost:8002/redoc
