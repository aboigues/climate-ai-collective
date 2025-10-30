#!/usr/bin/env python3
"""
Script pour déclencher une itération IA via l'orchestrateur.

Ce script envoie une requête à l'orchestrateur pour générer
une nouvelle proposition climatique basée sur le contexte fourni.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
import time


def parse_args():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Déclenche une itération IA pour générer une proposition"
    )
    parser.add_argument(
        "--domain",
        required=True,
        help="Domaine à traiter"
    )
    parser.add_argument(
        "--context",
        required=True,
        help="Fichier JSON de contexte en entrée"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Fichier JSON de sortie pour la proposition"
    )
    parser.add_argument(
        "--orchestrator-url",
        default=os.environ.get("ORCHESTRATOR_URL", ""),
        help="URL de l'orchestrateur (ou variable d'environnement ORCHESTRATOR_URL)"
    )
    return parser.parse_args()


def load_context(context_path: str) -> Dict[str, Any]:
    """Charge le fichier de contexte."""
    with open(context_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def call_orchestrator(domain: str, context: Dict[str, Any], orchestrator_url: str) -> Dict[str, Any]:
    """
    Appelle l'orchestrateur pour générer une proposition.

    Args:
        domain: Nom du domaine
        context: Contexte chargé
        orchestrator_url: URL de l'orchestrateur

    Returns:
        La proposition générée
    """
    # Si l'URL de l'orchestrateur n'est pas fournie, générer une proposition mock
    if not orchestrator_url:
        print("⚠️  No orchestrator URL provided, generating mock proposal", file=sys.stderr)
        return generate_mock_proposal(domain, context)

    # TODO: Implémenter l'appel réel à l'orchestrateur
    # Pour l'instant, on génère une proposition mock
    print(f"🤖 Calling orchestrator at: {orchestrator_url}")
    print(f"   Domain: {domain}")

    try:
        import httpx

        response = httpx.post(
            f"{orchestrator_url}/api/v1/proposals/generate",
            json={
                "domain": domain,
                "context": context
            },
            timeout=300.0  # 5 minutes
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Orchestrator returned error: {response.status_code}", file=sys.stderr)
            print(f"   Falling back to mock proposal", file=sys.stderr)
            return generate_mock_proposal(domain, context)

    except Exception as e:
        print(f"❌ Failed to call orchestrator: {e}", file=sys.stderr)
        print(f"   Falling back to mock proposal", file=sys.stderr)
        return generate_mock_proposal(domain, context)


def generate_mock_proposal(domain: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Génère une proposition mock pour les tests.

    Cette fonction génère une proposition réaliste basée sur le domaine
    et le contexte, utilisable pour tester le workflow sans orchestrateur réel.
    """
    from datetime import datetime
    import uuid

    # Propositions types par domaine
    domain_proposals = {
        "transport": {
            "title": "Extension du réseau de pistes cyclables sécurisées",
            "description": "Création de 50 km de pistes cyclables protégées dans les zones urbaines pour favoriser la mobilité douce et réduire les émissions de CO2.",
            "actions": [
                "Identifier les axes prioritaires en collaboration avec les collectivités",
                "Concevoir des pistes séparées du trafic automobile",
                "Installer des stationnements vélo sécurisés aux points d'intérêt",
                "Mettre en place une signalétique claire et cohérente"
            ],
            "cost_estimate": 15000000,
            "timeframe_years": 3,
            "co2_reduction_potential": 8500
        },
        "energie": {
            "title": "Déploiement de panneaux solaires sur bâtiments publics",
            "description": "Installation de 100 MW de capacité solaire photovoltaïque sur les toitures de bâtiments publics existants.",
            "actions": [
                "Audit énergétique des bâtiments publics",
                "Sélection des sites les plus adaptés",
                "Installation des panneaux photovoltaïques",
                "Connexion au réseau et monitoring"
            ],
            "cost_estimate": 120000000,
            "timeframe_years": 4,
            "co2_reduction_potential": 45000
        },
        "batiment": {
            "title": "Programme de rénovation énergétique des logements anciens",
            "description": "Rénovation thermique de 1000 logements construits avant 1990 pour atteindre le standard Minergie.",
            "actions": [
                "Identification des bâtiments prioritaires",
                "Isolation renforcée (toiture, façades, sols)",
                "Remplacement des fenêtres par du double vitrage performant",
                "Installation de systèmes de chauffage efficaces (pompes à chaleur)"
            ],
            "cost_estimate": 80000000,
            "timeframe_years": 5,
            "co2_reduction_potential": 15000
        },
        "agriculture": {
            "title": "Transition vers l'agriculture régénérative",
            "description": "Accompagnement de 500 exploitations agricoles vers des pratiques régénératives séquestrant du carbone.",
            "actions": [
                "Formation des agriculteurs aux techniques régénératives",
                "Mise en place de cultures de couverture",
                "Réduction du labour et pratique du semis direct",
                "Agroforesterie et haies bocagères"
            ],
            "cost_estimate": 25000000,
            "timeframe_years": 5,
            "co2_reduction_potential": 35000
        },
        "industrie": {
            "title": "Décarbonation des processus industriels",
            "description": "Électrification et optimisation énergétique de 50 sites industriels pour réduire les émissions.",
            "actions": [
                "Audit énergétique complet des sites",
                "Remplacement des chaudières fossiles par des alternatives électriques",
                "Récupération de chaleur fatale",
                "Optimisation des processus de production"
            ],
            "cost_estimate": 200000000,
            "timeframe_years": 6,
            "co2_reduction_potential": 120000
        },
        "transversal": {
            "title": "Plateforme numérique d'accompagnement à la décarbonation",
            "description": "Création d'une plateforme digitale pour aider citoyens et entreprises à mesurer et réduire leur empreinte carbone.",
            "actions": [
                "Développement de la plateforme web et mobile",
                "Intégration de calculateurs d'empreinte carbone",
                "Recommandations personnalisées basées sur l'IA",
                "Communauté et gamification pour encourager l'action"
            ],
            "cost_estimate": 5000000,
            "timeframe_years": 2,
            "co2_reduction_potential": 50000
        }
    }

    # Sélectionner la proposition appropriée
    proposal_template = domain_proposals.get(domain, domain_proposals["transversal"])

    # Générer un ID unique
    proposal_id = str(uuid.uuid4())[:8]

    # Construire la proposition complète
    proposal = {
        "id": f"{domain}-{proposal_id}",
        "domain": domain,
        "title": proposal_template["title"],
        "description": proposal_template["description"],
        "status": "generated",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "generated_by": "mock-generator",
        "version": "1.0",
        "content": {
            "summary": proposal_template["description"],
            "actions": proposal_template["actions"],
            "implementation": {
                "phases": [
                    {
                        "name": "Phase 1: Préparation",
                        "duration_months": 6,
                        "tasks": ["Études préliminaires", "Consultations parties prenantes"]
                    },
                    {
                        "name": "Phase 2: Déploiement",
                        "duration_months": proposal_template["timeframe_years"] * 12 - 12,
                        "tasks": ["Mise en œuvre", "Suivi et ajustements"]
                    },
                    {
                        "name": "Phase 3: Évaluation",
                        "duration_months": 6,
                        "tasks": ["Mesure des impacts", "Rapport final"]
                    }
                ],
                "total_duration_years": proposal_template["timeframe_years"]
            },
            "budget": {
                "total_chf": proposal_template["cost_estimate"],
                "breakdown": {
                    "infrastructure": proposal_template["cost_estimate"] * 0.6,
                    "personnel": proposal_template["cost_estimate"] * 0.25,
                    "communication": proposal_template["cost_estimate"] * 0.05,
                    "contingency": proposal_template["cost_estimate"] * 0.1
                }
            },
            "impact": {
                "co2_reduction_tonnes_10y": proposal_template["co2_reduction_potential"],
                "co2_reduction_tonnes_yearly": proposal_template["co2_reduction_potential"] / 10,
                "additional_benefits": [
                    "Amélioration de la qualité de l'air",
                    "Création d'emplois locaux",
                    "Amélioration de la qualité de vie"
                ]
            },
            "risks": [
                {
                    "description": "Dépassement budgétaire",
                    "probability": "medium",
                    "mitigation": "Budget de contingence de 10%"
                },
                {
                    "description": "Retards administratifs",
                    "probability": "low",
                    "mitigation": "Anticipation des procédures"
                }
            ],
            "stakeholders": [
                "Collectivités locales",
                "Citoyens",
                "Entreprises locales",
                "Organisations environnementales"
            ]
        },
        "metadata": {
            "context_version": context.get("metadata", {}).get("schema_version", "unknown"),
            "is_mock": True
        }
    }

    return proposal


def export_proposal(proposal: Dict[str, Any], output_path: str):
    """Exporte la proposition dans un fichier JSON."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(proposal, f, indent=2, ensure_ascii=False)

    print(f"💾 Proposal exported to: {output_path}")


def main():
    """Point d'entrée principal du script."""
    args = parse_args()

    try:
        print(f"🚀 Starting AI iteration for domain: {args.domain}")

        # Charger le contexte
        print(f"📖 Loading context from: {args.context}")
        context = load_context(args.context)

        # Appeler l'orchestrateur
        print(f"🤖 Generating proposal...")
        proposal = call_orchestrator(args.domain, context, args.orchestrator_url)

        # Exporter la proposition
        export_proposal(proposal, args.output)

        print("✨ Done!")
        print(f"📋 Proposal ID: {proposal['id']}")
        print(f"📊 CO2 reduction potential: {proposal['content']['impact']['co2_reduction_tonnes_10y']} tonnes (10 years)")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
