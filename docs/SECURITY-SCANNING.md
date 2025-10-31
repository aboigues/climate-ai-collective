# Security Scanning avec Trivy

Ce document explique comment utiliser Trivy pour scanner les vulnérabilités dans le projet Climate AI Collective.

## 🔒 Vue d'ensemble

Trivy est un scanner de vulnérabilités open-source qui analyse:
- Les dépendances Python (requirements.txt)
- Les images Docker
- Les configurations système
- Les fichiers de code source

Le projet est configuré pour bloquer les builds en cas de vulnérabilités **CRITICAL** ou **HIGH**.

## 🚀 Utilisation

### Scanner localement

Le projet inclut un script de scan local pour tester avant de pousser:

```bash
# Scanner tout (filesystem + toutes les images Docker)
./scripts/security-scan.sh all

# Scanner uniquement le filesystem et les dépendances
./scripts/security-scan.sh filesystem

# Scanner uniquement l'image Docker principale
./scripts/security-scan.sh docker-main

# Scanner uniquement l'image Docker frontend
./scripts/security-scan.sh docker-frontend

# Scanner uniquement l'image Docker citizen-api
./scripts/security-scan.sh docker-citizen-api
```

### Installation de Trivy

#### Ubuntu/Debian
```bash
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy
```

#### macOS
```bash
brew install aquasecurity/trivy/trivy
```

#### Autres systèmes
Télécharger depuis: https://github.com/aquasecurity/trivy/releases

### Workflow GitHub Actions

Le workflow `.github/workflows/trivy-security-scan.yml` s'exécute automatiquement:
- À chaque push sur `main` ou les branches `claude/**`
- À chaque pull request vers `main`
- Quotidiennement à 2h UTC (scan planifié)
- Manuellement via workflow_dispatch

#### Jobs du workflow

1. **scan-filesystem**: Scanne le code source et les dépendances Python
2. **scan-docker-main**: Scanne l'image Docker des services backend
3. **scan-docker-frontend**: Scanne l'image Docker du frontend
4. **scan-docker-citizen-api**: Scanne l'image Docker de l'API citoyenne
5. **summary**: Génère un résumé des résultats

## 🛡️ Niveaux de sévérité

Trivy classe les vulnérabilités en plusieurs niveaux:

- **CRITICAL**: Vulnérabilités critiques nécessitant une action immédiate ❌
- **HIGH**: Vulnérabilités importantes à corriger rapidement ❌
- **MEDIUM**: Vulnérabilités moyennes à planifier
- **LOW**: Vulnérabilités mineures
- **UNKNOWN**: Sévérité non déterminée

**Le build échoue uniquement pour CRITICAL et HIGH.**

## 📊 Résultats

### Via GitHub Actions
- Les résultats sont uploadés dans l'onglet **Security** > **Code scanning alerts**
- Format SARIF pour une intégration complète avec GitHub
- Résumé visible dans le step summary de chaque run

### Via CLI locale
- Output directement dans le terminal
- Format tableau pour une lecture facile
- Exit code 1 si vulnérabilités trouvées

## 🔧 Corriger les vulnérabilités

### Dépendances Python

1. Identifier la dépendance vulnérable dans le rapport Trivy
2. Vérifier s'il existe une version corrigée:
   ```bash
   pip index versions <package-name>
   ```
3. Mettre à jour `requirements.txt` avec la version sécurisée
4. Tester que l'application fonctionne toujours
5. Re-scanner pour vérifier la correction

### Images Docker

1. Vérifier si la vulnérabilité est dans l'image de base
2. Mettre à jour vers une version plus récente de l'image:
   ```dockerfile
   # Avant
   FROM python:3.11-slim

   # Après
   FROM python:3.11.8-slim  # Version spécifique avec correctifs
   ```
3. Ou changer d'image de base si nécessaire
4. Rebuilder et re-scanner

### Vulnérabilités non corrigeables

Si une vulnérabilité ne peut pas être corrigée immédiatement:

1. Évaluer le risque réel pour l'application
2. Si le risque est acceptable, ajouter la CVE à `.trivyignore`:
   ```
   # .trivyignore
   CVE-2024-12345  # Ne s'applique pas car nous n'utilisons pas la fonctionnalité X
   ```
3. Documenter la raison et la date de révision
4. Planifier une révision régulière (recommandé: chaque trimestre)

## 📝 Bonnes pratiques

1. **Scanner avant de pousser**: Utilisez le script local avant chaque commit important
2. **Réagir rapidement**: Corrigez les vulnérabilités CRITICAL/HIGH immédiatement
3. **Mettre à jour régulièrement**: Gardez les dépendances à jour proactivement
4. **Réviser .trivyignore**: Passez en revue les exceptions tous les 3 mois
5. **Utiliser des versions spécifiques**: Évitez `latest` dans les Dockerfiles
6. **Tester après correction**: Vérifiez que les mises à jour ne cassent rien

## 🔍 Commandes Trivy avancées

```bash
# Scanner avec plus de détails
trivy fs --severity CRITICAL,HIGH,MEDIUM .

# Scanner uniquement les dépendances Python
trivy fs --scanners vuln requirements.txt

# Scanner une image Docker spécifique
trivy image python:3.11-slim

# Générer un rapport JSON
trivy fs --format json --output report.json .

# Scanner sans utiliser le cache
trivy fs --no-cache .

# Scanner avec timeout personnalisé
trivy fs --timeout 10m .
```

## 📚 Ressources

- [Documentation Trivy](https://aquasecurity.github.io/trivy/)
- [Base de données des vulnérabilités](https://nvd.nist.gov/)
- [GitHub Advisory Database](https://github.com/advisories)
- [Python Security](https://python.org/dev/security/)

## 🆘 Support

En cas de questions ou problèmes avec Trivy:
1. Consulter la documentation officielle
2. Ouvrir une issue dans ce repository
3. Contacter l'équipe sécurité du projet
