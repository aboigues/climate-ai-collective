# Pull Request: Corriger les vulnérabilités de sécurité dans citizen-api

## 🔒 Résumé

Cette PR corrige 4 vulnérabilités de sécurité HIGH détectées par Trivy dans le service citizen-api.

## 🐛 Vulnérabilités Corrigées

### python-multipart (0.0.6 → 0.0.20)
- ✅ **CVE-2024-24762**: DoS vulnerability via streaming multipart parser
- ✅ **CVE-2024-53981**: DoS via deformation multipart/form-data boundary

### starlette (0.35.1 → ≥0.49.1)
- ✅ **CVE-2024-47874**: Denial of Service via multipart/form-data
- ✅ **CVE-2025-62727**: DoS via Range header merging

## 📦 Changements de Dépendances

```diff
- fastapi==0.109.0
+ fastapi==0.120.3

- uvicorn[standard]==0.27.0
+ uvicorn[standard]==0.32.1

- pydantic==2.5.3
+ pydantic==2.10.3

- python-multipart==0.0.6
+ python-multipart==0.0.20

+ starlette>=0.49.1,<0.50.0
```

## 🔧 Résolution des Conflits de Dépendances

La mise à jour a nécessité plusieurs itérations pour résoudre les conflits :
1. FastAPI 0.115.6 supportait uniquement starlette <0.42.0
2. Mise à jour vers FastAPI 0.120.3 qui supporte starlette <0.50.0
3. Ajout explicite de starlette >=0.49.1 pour garantir le correctif de sécurité

## ✅ Plan de Test

- [x] Mise à jour des dépendances dans requirements.txt
- [ ] Le build Docker doit réussir
- [ ] Le scan Trivy ne doit détecter aucune vulnérabilité HIGH ou CRITICAL
- [ ] L'API doit démarrer correctement
- [ ] Les endpoints existants doivent fonctionner normalement

## 📋 Checklist

- [x] Les dépendances sont mises à jour vers des versions sans vulnérabilités connues
- [x] Les versions sont compatibles entre elles
- [x] Le fichier requirements.txt est à jour
- [ ] Les tests CI/CD passent

## 🔗 Références

- [CVE-2024-24762](https://avd.aquasec.com/nvd/cve-2024-24762)
- [CVE-2024-53981](https://avd.aquasec.com/nvd/cve-2024-53981)
- [CVE-2024-47874](https://avd.aquasec.com/nvd/cve-2024-47874)
- [CVE-2025-62727](https://avd.aquasec.com/nvd/cve-2025-62727)

## 📝 Instructions pour créer la PR

### Titre de la PR
```
fix: Corriger les vulnérabilités de sécurité dans citizen-api
```

### Branche
- **Source**: `claude/fix-citizen-api-scan-011CUf82YKrppEaSxQmejLJK`
- **Target**: `main`

### URL pour créer la PR
```
https://github.com/aboigues/climate-ai-collective/compare/main...claude/fix-citizen-api-scan-011CUf82YKrppEaSxQmejLJK
```
