# Guide de Contribution

Merci de votre intérêt pour Climate AI Collective ! 🌍

## 🎯 Comment Contribuer

Il existe plusieurs façons de contribuer à ce projet :

### 1. 💻 Contributions Code

#### Setup Développement Local

```bash
# Clone le repo
git clone https://github.com/votre-org/climate-ai-collective.git
cd climate-ai-collective

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Installer pre-commit hooks
pre-commit install
```

#### Process de Développement

1. Fork le repository
2. Créer une branche feature (`git checkout -b feature/amelioration-validation`)
3. Faire vos modifications
4. Tester localement (`pytest tests/`)
5. Commit avec des messages clairs
6. Push et créer une Pull Request

#### Standards de Code

- **Python**: PEP 8, type hints, docstrings
- **Tests**: Coverage minimum 80%
- **Pre-commit**: Black, flake8, mypy

### 2. 🔬 Contributions Scientifiques

#### Améliorer les Modèles de Simulation

Nous cherchons des experts pour :

- Valider les modèles climatiques
- Améliorer les facteurs d'émission
- Proposer de nouveaux modèles de simulation
- Enrichir les données de référence

**Process:**

1. Ouvrir une Issue avec le tag `science`
2. Proposer votre amélioration avec sources
3. Si approuvée, soumettre via PR dans `/context/scientific-data/`

### 3. 📊 Contributions Données

#### Enrichir le Contexte

Nous avons besoin de:

- Données d'émissions sectorielles
- Études de cas réels
- Facteurs d'émission régionaux
- Coûts de technologies

**Format:**

```json
{
  "source": "IPCC AR6",
  "date": "2023",
  "data": {...},
  "license": "CC-BY"
}
```

### 4. 🎨 Contributions UX/UI

Le dashboard citoyen a besoin de:

- Designers UX/UI
- Développeurs front-end (React/Vue)
- Experts en data visualization

Voir `/frontend/` pour le code de l'interface.

### 5. 📝 Contributions Documentation

- Améliorer la documentation technique
- Traduire en d'autres langues
- Créer des tutoriels
- Rédiger des guides d'utilisation

### 6. 💬 Review de Propositions IA

Vous pouvez reviewer les propositions générées par les IA:

1. Consulter les Pull Requests avec le label `ai-generated`
2. Lire la proposition et les simulations
3. Commenter avec votre expertise
4. Voter (une fois l'interface disponible)

**Ce que nous attendons:**

- Constructivité
- Arguments factuels
- Sources fiables
- Respect des autres contributeurs

## 🏗️ Architecture des Contributions

### Structure des Fichiers

```
climate-ai-collective/
├── services/          # Microservices Python
│   ├── orchestrator/  # Logique d'orchestration
│   ├── validation/    # Validation et simulation
│   └── github-integration/
├── kubernetes/        # Configuration K8s
├── context/          # Données scientifiques
└── domains/          # Propositions par domaine
```

### Types de Contributions

| Type | Difficulté | Impact | Fichiers |
|------|-----------|--------|----------|
| Fix bug | ⭐ | 🔥 | `services/*` |
| Nouvelle feature | ⭐⭐⭐ | 🔥🔥 | `services/*` |
| Amélioration modèle | ⭐⭐⭐⭐ | 🔥🔥🔥 | `services/validation/` |
| Nouvelle intégration | ⭐⭐⭐ | 🔥🔥 | `services/` |
| Documentation | ⭐ | 🔥 | `docs/` |

## 🐛 Signaler un Bug

Utilisez les GitHub Issues avec le template Bug Report:

```markdown
**Description**
Description claire du bug

**Reproduire**
1. Étape 1
2. Étape 2
3. ...

**Comportement attendu**
Ce qui devrait se passer

**Screenshots**
Si applicable

**Environnement**
- OS: 
- Python:
- Version:
```

## 💡 Proposer une Feature

Utilisez le template Feature Request:

```markdown
**Problème à résoudre**
Quel problème cette feature résout-elle?

**Solution proposée**
Description de la solution

**Alternatives considérées**
Autres approches possibles

**Impact**
Sur quels composants cela impacte?
```

## 🔒 Sécurité

Pour signaler une vulnérabilité de sécurité:

**NE PAS** créer une issue publique.

Envoyez un email à: security@climate-ai-collective.org

## 📋 Process de Review

1. **Triage** : L'équipe examine la PR (1-2 jours)
2. **Review technique** : Vérification code et tests
3. **Review scientifique** : Si pertinent (3-5 jours)
4. **CI/CD** : Tests automatiques
5. **Merge** : Si tout est vert ✅

### Critères d'Acceptation

- ✅ Tests passent
- ✅ Code coverage maintenu
- ✅ Documentation à jour
- ✅ Approuvé par au moins 1 mainteneur
- ✅ Validation scientifique si nécessaire

## 🌟 Reconnaissance

Tous les contributeurs sont reconnus dans:

- Le fichier CONTRIBUTORS.md
- Les release notes
- Le site web (à venir)

Les contributeurs majeurs peuvent devenir mainteneurs.

## 📜 Code de Conduite

Ce projet suit le [Contributor Covenant](https://www.contributor-covenant.org/).

En bref:

- 🤝 Soyez respectueux et inclusif
- 💬 Communiquez de manière constructive
- 🌍 Souvenez-vous de notre mission climatique
- ❤️ Assumez les meilleures intentions

## 🚀 Devenir Mainteneur

Après plusieurs contributions significatives, vous pouvez être invité à devenir mainteneur:

**Responsabilités:**

- Review de Pull Requests
- Triage des Issues
- Orientation technique
- Mentorat de nouveaux contributeurs

**Pour postuler:**

Envoyez un email à maintainers@climate-ai-collective.org avec:

- Vos contributions passées
- Votre motivation
- Votre expertise

## 📞 Questions?

- **GitHub Discussions**: Pour questions générales
- **Issues**: Pour bugs et features
- **Email**: contribute@climate-ai-collective.org

---

Merci de contribuer à la lutte contre le réchauffement climatique! 🌱
