# TODO - Climate AI Collective

Feuille de route des évolutions et améliorations à apporter au projet.

## 🔥 Priorité Haute (Court Terme - 3-6 mois)

### Sécurité & Production

- [ ] **CORS**: Remplacer `allow_origins=["*"]` par une liste restreinte de domaines autorisés
- [ ] **Rate Limiting**: Implémenter un système de limitation de taux par IP/utilisateur
  - Protection contre le spam de votes
  - Protection des endpoints API
- [ ] **Anti-Bot**: Ajouter une validation CAPTCHA pour les votes
- [ ] **TLS/SSL**: Configurer HTTPS pour la production
- [ ] **Secrets Management**: Sécuriser la gestion des credentials Git et API keys
  - Utiliser Kubernetes secrets ou solution type Vault
- [ ] **Backup automatique**: Système de sauvegarde régulière de `votes.json` et proposals

### Interface Citoyenne

- [ ] **Authentication citoyenne** (optionnelle)
  - OAuth2 ou JWT
  - Lier les votes aux utilisateurs authentifiés
  - Permettre de modifier/supprimer ses propres votes
- [ ] **Pagination**: Implémenter la pagination pour la liste des propositions
  - Backend: paramètres `page` et `limit`
  - Frontend: boutons de navigation
- [ ] **Export PDF**: Permettre l'export des propositions en PDF
  - Génération côté backend avec bibliothèque type WeasyPrint
  - Bouton de téléchargement dans l'interface
- [ ] **Système de commentaires**: Permettre aux citoyens de commenter les propositions
  - API: POST/GET endpoints pour commentaires
  - Frontend: section commentaires sur `proposal.html`
  - Modération basique

### Validation & Simulation

- [ ] **Intégration simulation profonde**: Finaliser l'intégration du système de simulation détaillée
  - Actuellement seule la simulation rapide (~2-5 min) est utilisée
  - Ajouter des visualisations de simulation
- [ ] **Amélioration de la validation**: Raffiner les critères de validation LLM
  - Ajouter des métriques quantitatives supplémentaires
  - Tester avec des données réelles

### DevOps & Infrastructure

- [ ] **Monitoring amélioré**: Configurer alertes Prometheus/Grafana
  - Alertes sur échecs de validation
  - Alertes sur erreurs LLM
  - Métriques d'utilisation API
- [ ] **CI/CD**: Améliorer les workflows GitHub Actions
  - Tests automatiques sur PR
  - Déploiement automatique en staging
  - Smoke tests post-déploiement

## 🎯 Priorité Moyenne (Moyen Terme - 6-12 mois)

### Visualisation & UX

- [ ] **Graphiques interactifs**: Ajouter des visualisations pour les simulations
  - Charts.js ou Plotly.js pour les résultats de simulation
  - Visualisation de l'impact CO2 dans le temps
  - Comparaison entre propositions
- [ ] **Mode sombre**: Implémenter un thème sombre
  - Toggle dans l'interface
  - Préférence sauvegardée en localStorage
- [ ] **WebSocket**: Notifications en temps réel
  - Nouvelle proposition publiée
  - Changement de statut d'une proposition
  - Nombre de votes mis à jour en direct
- [ ] **Partage social**: Boutons de partage sur réseaux sociaux
  - Twitter, LinkedIn, Facebook
  - Génération d'images Open Graph

### Fonctionnalités Citoyennes

- [ ] **Filtres avancés**: Améliorer les filtres de propositions
  - Par impact CO2 estimé
  - Par budget
  - Par score de vote
  - Tri multi-critères
- [ ] **Favoris**: Permettre aux utilisateurs de marquer des propositions favorites
- [ ] **Historique de votes**: Voir l'historique de ses propres votes
- [ ] **Notifications par email**: Alertes sur nouvelles propositions par domaine d'intérêt

### Base de Données

- [ ] **Migration PostgreSQL complète**: Migrer `votes.json` vers PostgreSQL
  - Amélioration des performances
  - Requêtes complexes facilitées
  - Transactions ACID
- [ ] **Base de données pour propositions**: Indexer les propositions en DB
  - Actuellement stockées uniquement en Git
  - Amélioration des performances de recherche
  - API de recherche full-text

### IA & Orchestration

- [ ] **Multi-LLM voting**: Utiliser plusieurs LLMs pour générer et voter sur les propositions
  - Consensus entre modèles
  - Diversité des approches
- [ ] **Fine-tuning**: Entraîner un modèle spécialisé sur les données climatiques
- [ ] **Amélioration des prompts**: Itérer sur les prompts système
  - A/B testing de prompts
  - Versioning des prompts

## 🚀 Long Terme (12+ mois)

### Applications Mobiles

- [ ] **Application mobile**: Développer une app native
  - React Native ou Flutter
  - iOS + Android
  - Push notifications
  - Vote offline (synchronisation ultérieure)

### Analytique & Intelligence

- [ ] **Analytics de votes**: Système d'analyse de tendances
  - Dashboard analytics pour administrateurs
  - Tendances par domaine
  - Corrélations entre critères de vote
- [ ] **Système de recommandation**: Propositions recommandées par utilisateur
  - Basé sur l'historique de votes
  - Machine learning pour personnalisation
- [ ] **Prédiction d'impact**: ML pour prédire l'acceptation d'une proposition
  - Features: domaine, budget, impact CO2, etc.
  - Aide à la génération de propositions optimales

### Communauté & Collaboration

- [ ] **Forum de discussion**: Espace de discussion par proposition
  - Threads de discussion
  - Upvotes/downvotes
  - Modération communautaire
- [ ] **Propositions citoyennes**: Permettre aux citoyens de soumettre leurs propres propositions
  - Workflow de soumission
  - Validation par IA avant publication
  - Vote communautaire pour validation
- [ ] **API publique**: Ouvrir l'API pour développeurs tiers
  - Documentation OpenAPI/Swagger complète
  - Rate limiting par API key
  - Dashboard développeur
- [ ] **Internationalisation**: Support multi-langues complet
  - i18n frontend
  - Traduction automatique des propositions
  - Communautés par pays/région

### Gouvernance & Impact Réel

- [ ] **Connexion avec décideurs**: Interface pour les élus et décideurs
  - Dashboard dédié
  - Export de propositions validées
  - Suivi de mise en œuvre
- [ ] **Suivi d'implémentation**: Tracker les propositions réellement mises en place
  - Statut: proposé → voté → accepté → en cours → implémenté
  - Impact réel mesuré vs. estimé
- [ ] **Blockchain pour transparence**: Horodatage et traçabilité sur blockchain
  - Votes immuables
  - Historique des propositions
  - Transparence totale

## 🔧 Améliorations Techniques

### Code Quality

- [ ] **Couverture de tests**: Atteindre 80%+ de code coverage
  - Tests unitaires pour tous les services
  - Tests d'intégration API
  - Tests E2E frontend
- [ ] **Documentation API**: Générer documentation Swagger/ReDoc automatique
  - Déjà FastAPI, juste à activer et documenter
- [ ] **Type safety frontend**: Migrer vers TypeScript
  - Meilleure maintenabilité
  - Moins d'erreurs runtime
- [ ] **Refactoring**: Réduire la duplication de code
  - Utilitaires partagés
  - Composants réutilisables

### Performance

- [ ] **Cache Redis**: Implémenter cache pour requêtes fréquentes
  - Liste des propositions
  - Statistiques globales
  - Résultats de validation
- [ ] **CDN**: Servir assets statiques via CDN
  - Images, CSS, JS
  - Amélioration temps de chargement
- [ ] **Optimisation requêtes DB**: Indexation et optimisation
- [ ] **Lazy loading**: Charger images et données à la demande

### Observabilité

- [ ] **Tracing distribué**: Implémenter OpenTelemetry
  - Tracer les requêtes à travers les services
  - Identifier les goulots d'étranglement
- [ ] **Logs structurés**: Améliorer le logging
  - Déjà structlog, uniformiser l'usage
  - Centralisation avec ELK ou similaire
- [ ] **Métriques custom**: Ajouter métriques métier
  - Nombre de votes par jour
  - Taux de validation des propositions
  - Temps moyen de génération

## 📚 Documentation

- [ ] **Guides utilisateurs**: Documentation pour citoyens
  - Comment voter
  - Comprendre les propositions
  - FAQ
- [ ] **Architecture Decision Records**: Documenter les choix techniques
  - ADR pour décisions importantes
  - Justification des choix technologiques
- [ ] **API Examples**: Plus d'exemples d'utilisation API
  - Exemples curl
  - Exemples Python/JavaScript
- [ ] **Video tutorials**: Tutoriels vidéo
  - Pour utilisateurs finaux
  - Pour développeurs contributeurs

## 🌍 Expansion

- [ ] **Nouveaux domaines**: Ajouter d'autres domaines climatiques
  - Actuellement: transport, énergie, bâtiment, agriculture, industrie, transversal
  - Potentiels: déchets, eau, biodiversité, alimentation
- [ ] **Collaboration internationale**: Support multi-pays
  - Données scientifiques par pays
  - Adaptation des propositions au contexte local
- [ ] **Partenariats**: Collaboration avec ONG et gouvernements
  - APIs d'échange de données
  - Co-validation de propositions

---

## ✅ Récemment Complété

- [x] Interface citoyenne de base (liste + détail)
- [x] API REST pour propositions et votes
- [x] Système de vote 3 axes (Impact, Faisabilité, Désirabilité)
- [x] Agrégation de votes et statistiques
- [x] Frontend responsive HTML/CSS/JS
- [x] Orchestrateur LLM multi-modèles
- [x] Validation à 3 niveaux des propositions
- [x] Workflows GitHub Actions pour itérations automatiques
- [x] Stockage Git des propositions
- [x] Docker Compose pour environnement de dev
- [x] Manifests Kubernetes pour production
- [x] Documentation complète (README, QUICKSTART, CONTRIBUTING)

---

**Dernière mise à jour:** 30 octobre 2025
