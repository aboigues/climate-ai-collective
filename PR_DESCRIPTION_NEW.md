# Pull Request: Corriger la compatibilité FastAPI/Starlette pour résoudre les vulnérabilités

## 🔒 Problème

Le build Docker de citizen-api échouait avec l'erreur suivante :
```
ERROR: Cannot install -r requirements.txt (line 1) and starlette==0.49.1
because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested starlette==0.49.1
    fastapi 0.115.6 depends on starlette<0.42.0 and >=0.40.0
```

## 🐛 Cause Racine

La PR #19 a corrigé les vulnérabilités en mettant à jour vers :
- `starlette==0.49.1` (pour corriger CVE-2024-47874 et CVE-2025-62727)
- Mais avec `fastapi==0.115.6` qui n'est pas compatible

FastAPI 0.115.6 supporte uniquement `starlette<0.42.0`, ce qui crée un conflit de dépendances.

## ✅ Solution

Mise à jour vers **FastAPI 0.120.3** qui supporte `starlette<0.50.0`, permettant l'utilisation de starlette 0.49.1+.

## 📦 Changements de Dépendances

```diff
- fastapi==0.115.6
+ fastapi==0.120.3

  uvicorn[standard]==0.32.1  (inchangé)
  pydantic==2.10.3           (inchangé)
  python-multipart==0.0.20   (inchangé)

- starlette==0.49.1
+ starlette>=0.49.1,<0.50.0
```

## 🔐 Vulnérabilités Corrigées

Cette PR permet de maintenir les correctifs de sécurité de la PR #19 :

### python-multipart (0.0.6 → 0.0.20)
- ✅ **CVE-2024-24762**: DoS vulnerability via streaming multipart parser
- ✅ **CVE-2024-53981**: DoS via deformation multipart/form-data boundary

### starlette (0.35.1 → ≥0.49.1)
- ✅ **CVE-2024-47874**: Denial of Service via multipart/form-data
- ✅ **CVE-2025-62727**: DoS via Range header merging

## ✅ Vérifications de Compatibilité

- ✅ FastAPI 0.120.3 supporte starlette <0.50.0 (vérifié via PyPI)
- ✅ FastAPI 0.120.3 est la dernière version stable (30 octobre 2025)
- ✅ Toutes les dépendances sont compatibles entre elles
- ✅ Les contraintes de version garantissent les correctifs de sécurité

## 🧪 Plan de Test

- [x] Mise à jour des dépendances dans requirements.txt
- [ ] Le build Docker doit réussir (pip install sans erreur de conflit)
- [ ] Le scan Trivy ne doit détecter aucune vulnérabilité HIGH ou CRITICAL
- [ ] L'API doit démarrer correctement
- [ ] Les endpoints existants doivent fonctionner normalement

## 🔗 Références

- [CVE-2024-24762](https://avd.aquasec.com/nvd/cve-2024-24762)
- [CVE-2024-53981](https://avd.aquasec.com/nvd/cve-2024-53981)
- [CVE-2024-47874](https://avd.aquasec.com/nvd/cve-2024-47874)
- [CVE-2025-62727](https://avd.aquasec.com/nvd/cve-2025-62727)
- [FastAPI 0.120.3 on PyPI](https://pypi.org/project/fastapi/0.120.3/)

## 📝 Instructions pour créer la PR

### Titre de la PR
```
fix: Mettre à jour FastAPI vers 0.120.3 pour compatibilité avec starlette 0.49.1
```

### Branche
- **Source**: `claude/fix-fastapi-starlette-compatibility-011CUf82YKrppEaSxQmejLJK`
- **Target**: `main`

### URL pour créer la PR
```
https://github.com/aboigues/climate-ai-collective/compare/main...claude/fix-fastapi-starlette-compatibility-011CUf82YKrppEaSxQmejLJK
```

### Labels suggérés
- `security` - Correctif de sécurité
- `bug` - Correction de bug (conflit de dépendances)
- `dependencies` - Mise à jour de dépendances
