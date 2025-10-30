# Climate AI Collective - Makefile

.PHONY: help setup dev test clean deploy

# Default target
help:
	@echo "🌍 Climate AI Collective - Commandes Disponibles"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Configure l'environnement de développement"
	@echo "  make install        - Installe les dépendances Python"
	@echo ""
	@echo "Développement Local:"
	@echo "  make dev            - Lance l'environnement de dev (Docker Compose)"
	@echo "  make stop           - Arrête l'environnement de dev"
	@echo "  make logs           - Affiche les logs"
	@echo "  make shell          - Ouvre un shell dans le container orchestrator"
	@echo ""
	@echo "Tests:"
	@echo "  make test           - Lance tous les tests"
	@echo "  make test-unit      - Lance les tests unitaires"
	@echo "  make test-integration - Lance les tests d'intégration"
	@echo "  make coverage       - Génère un rapport de couverture"
	@echo ""
	@echo "Quality:"
	@echo "  make lint           - Vérifie le code avec flake8"
	@echo "  make format         - Formate le code avec black"
	@echo "  make type-check     - Vérifie les types avec mypy"
	@echo "  make quality        - Lance tous les checks qualité"
	@echo ""
	@echo "Kubernetes:"
	@echo "  make k8s-setup      - Configure Kubernetes sur Infomaniak"
	@echo "  make k8s-deploy     - Déploie sur Kubernetes"
	@echo "  make k8s-status     - Affiche le statut du cluster"
	@echo "  make k8s-logs       - Affiche les logs Kubernetes"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Nettoie les fichiers temporaires"
	@echo "  make clean-all      - Nettoie tout (incluant les volumes Docker)"

# Setup
setup:
	@echo "📦 Configuration de l'environnement..."
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install -r requirements-dev.txt
	./venv/bin/pre-commit install
	@echo "✅ Environnement configuré!"
	@echo ""
	@echo "Activez l'environnement virtuel avec:"
	@echo "  source venv/bin/activate"

install:
	pip install -r requirements.txt

# Development
dev:
	@echo "🚀 Démarrage de l'environnement de développement..."
	docker-compose up -d
	@echo ""
	@echo "✅ Services démarrés!"
	@echo "  - Orchestrator: http://localhost:8000"
	@echo "  - Validation: http://localhost:8001"
	@echo "  - MinIO: http://localhost:9001 (admin/admin)"
	@echo "  - Grafana: http://localhost:3000 (admin/admin)"
	@echo "  - Prometheus: http://localhost:9090"

stop:
	@echo "🛑 Arrêt de l'environnement..."
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec orchestrator /bin/bash

# Tests
test:
	@echo "🧪 Lancement des tests..."
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

coverage:
	pytest tests/ --cov=services --cov-report=html --cov-report=term
	@echo "📊 Rapport de couverture: htmlcov/index.html"

# Code Quality
lint:
	@echo "🔍 Vérification du code..."
	flake8 services/ tests/

format:
	@echo "✨ Formatage du code..."
	black services/ tests/

type-check:
	@echo "🔎 Vérification des types..."
	mypy services/

quality: lint type-check
	@echo "✅ Tous les checks qualité sont passés!"

# Kubernetes
k8s-setup:
	@echo "☸️  Configuration Kubernetes sur Infomaniak..."
	./scripts/setup-infomaniak.sh

k8s-deploy:
	@echo "🚀 Déploiement sur Kubernetes..."
	kubectl apply -k kubernetes/overlays/production

k8s-status:
	@echo "📊 Statut du cluster:"
	kubectl get pods -n climate-ai
	@echo ""
	kubectl get svc -n climate-ai

k8s-logs:
	kubectl logs -f -n climate-ai -l app=orchestrator

# Maintenance
clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/ .coverage
	@echo "✅ Nettoyage terminé!"

clean-all: clean
	@echo "🧹 Nettoyage complet..."
	docker-compose down -v
	rm -rf venv/
	@echo "✅ Nettoyage complet terminé!"

# Documentation
docs:
	@echo "📚 Génération de la documentation..."
	cd docs && make html
	@echo "✅ Documentation: docs/_build/html/index.html"

# Git Helpers
git-setup:
	@echo "🔧 Configuration Git pour le projet..."
	git config core.autocrlf input
	git config pull.rebase true
	pre-commit install
	@echo "✅ Git configuré!"

# Release
release-patch:
	@echo "🏷️  Release patch version..."
	bump2version patch
	git push && git push --tags

release-minor:
	@echo "🏷️  Release minor version..."
	bump2version minor
	git push && git push --tags

release-major:
	@echo "🏷️  Release major version..."
	bump2version major
	git push && git push --tags
