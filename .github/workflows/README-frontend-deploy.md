# Frontend Deployment Test Workflow

Ce workflow GitHub Actions teste et valide le déploiement du frontend de Climate AI Collective.

## 🎯 Objectif

Automatiser les tests de build et de déploiement du frontend pour garantir que:
- L'image Docker se construit correctement
- Tous les fichiers statiques sont présents
- Le serveur nginx fonctionne correctement
- Les manifestes Kubernetes sont valides
- L'injection de l'URL de l'API fonctionne

## 🚀 Déclenchement

Le workflow se déclenche dans les cas suivants:

### 1. Push sur les branches principales
```yaml
on:
  push:
    branches:
      - main
      - 'claude/**'
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-deploy.yml'
```

### 2. Pull Request
```yaml
on:
  pull_request:
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-deploy.yml'
```

### 3. Déclenchement manuel
Vous pouvez déclencher manuellement ce workflow depuis l'interface GitHub Actions avec l'option de pousser l'image vers le registry.

## 📋 Jobs du Workflow

### Job 1: `test-build`

Ce job teste la construction et le fonctionnement de l'image Docker du frontend.

#### Étapes:

1. **Checkout du code**
   - Récupère le code source

2. **Configuration de Docker Buildx**
   - Configure Docker pour le build multi-plateforme

3. **Build de l'image frontend**
   - Construit l'image Docker avec cache GitHub Actions
   - Tag: `climate-ai/frontend:test`

4. **Test de la structure de l'image**
   - Vérifie que tous les fichiers HTML, JS et CSS sont présents:
     - `index.html` - Page principale
     - `proposal.html` - Page de détail des propositions
     - `app.js` - JavaScript principal
     - `proposal.js` - JavaScript des propositions
     - `styles.css` - Feuille de styles
   - Vérifie la configuration nginx

5. **Démarrage du container**
   - Lance le container sur le port 8080
   - Injecte l'URL de l'API de test

6. **Test du endpoint de santé**
   - Vérifie que le serveur répond sur `http://localhost:8080/`
   - Vérifie le code HTTP 200 pour:
     - Page principale (`/`)
     - Page des propositions (`/proposal.html`)

7. **Test du contenu**
   - Vérifie que la page contient le titre "Climate AI Collective"
   - Vérifie l'accessibilité des ressources statiques:
     - `app.js` retourne 200
     - `styles.css` retourne 200

8. **Test de l'injection de l'URL de l'API**
   - Vérifie que l'URL de l'API est correctement injectée dans `app.js`
   - URL de test: `http://test-api:8002`

9. **Affichage des logs du container** (toujours exécuté)
   - Affiche les logs nginx pour debug

10. **Arrêt et suppression du container** (toujours exécuté)
    - Nettoyage des ressources

11. **Login au GitHub Container Registry** (optionnel)
    - Uniquement si déclenchement manuel avec `push_image=true`

12. **Push de l'image vers le registry** (optionnel)
    - Uniquement si déclenchement manuel avec `push_image=true`
    - Tags:
      - `ghcr.io/{owner}/climate-ai-frontend:latest`
      - `ghcr.io/{owner}/climate-ai-frontend:{sha}`

### Job 2: `test-kubernetes`

Ce job valide les manifestes Kubernetes du frontend.

#### Étapes:

1. **Checkout du code**
   - Récupère le code source

2. **Installation de kubectl**
   - Installe kubectl v1.29.0

3. **Validation des manifestes Kubernetes**
   - Vérifie l'existence de `deployment.yaml`
   - Valide la syntaxe YAML avec `kubectl --dry-run=client`

4. **Vérification de la configuration**
   - Vérifie que le déploiement a au moins 1 replica
   - Vérifie que le service expose le port 80
   - Vérifie que les health checks sont configurés:
     - Liveness probe
     - Readiness probe

### Job 3: `summary`

Ce job génère un résumé des tests dans GitHub Actions.

#### Contenu du résumé:
- ✅/❌ Statut du test Docker Build
- ✅/❌ Statut du test Kubernetes Manifests
- 📝 Prochaines étapes suggérées

## 🔧 Configuration Requise

### Secrets GitHub

Si vous souhaitez pousser l'image vers le registry:
- `GITHUB_TOKEN` - Fourni automatiquement par GitHub Actions

### Permissions

Le workflow nécessite les permissions suivantes:
- `contents: read` - Lecture du code
- `packages: write` - Écriture dans GitHub Container Registry

## 📊 Exemple de Sortie

### Test réussi ✅
```
🔍 Testing image structure...
✅ index.html found
✅ proposal.html found
✅ app.js found
✅ proposal.js found
✅ styles.css found
✅ nginx configuration found

🚀 Starting frontend container...
✅ Frontend is responding
✅ Main page returns 200 OK
✅ Proposal page returns 200 OK

📝 Testing page content...
✅ Main page contains expected title
✅ app.js is accessible
✅ styles.css is accessible

🔧 Testing API URL injection...
✅ API URL correctly injected in app.js

🔍 Validating Kubernetes manifests...
✅ Kubernetes manifests found
✅ Kubernetes manifests are valid
✅ Deployment has 2 replicas
✅ Service exposes port 80
✅ Liveness probe configured
✅ Readiness probe configured
```

## 🚀 Utilisation

### Déclenchement automatique

Le workflow se déclenche automatiquement à chaque:
- Push sur `main` ou branches `claude/**` avec modifications dans `frontend/`
- Pull Request avec modifications dans `frontend/`

### Déclenchement manuel avec push de l'image

1. Allez dans l'onglet "Actions" de votre repository
2. Sélectionnez "Frontend Deployment Test"
3. Cliquez sur "Run workflow"
4. Cochez "Push image to registry" si vous voulez pousser l'image
5. Cliquez sur "Run workflow"

## 🐛 Debug

### Le container ne démarre pas

Vérifiez les logs du container:
```bash
docker logs frontend-test
```

### Les tests de contenu échouent

Vérifiez que les fichiers HTML contiennent le texte attendu:
```bash
curl http://localhost:8080/ | grep "Climate AI Collective"
```

### L'injection de l'URL échoue

Vérifiez le script d'entrypoint dans le Dockerfile:
```bash
docker exec frontend-test cat /docker-entrypoint.d/40-inject-api-url.sh
```

## 📝 Notes

- Le workflow utilise le cache GitHub Actions pour accélérer les builds
- Les tests sont exécutés en parallèle quand c'est possible
- Le résumé est généré même si les tests échouent (`if: always()`)
- L'image n'est poussée vers le registry que lors d'un déclenchement manuel

## 🔄 Prochaines Étapes

Après que ce workflow réussisse, vous pouvez:
1. Déployer sur un environnement de staging
2. Exécuter des tests d'intégration avec l'API
3. Déployer en production
4. Mettre en place des tests E2E avec Playwright ou Cypress

## 📚 Ressources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
