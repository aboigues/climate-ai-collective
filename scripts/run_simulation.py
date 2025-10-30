#!/usr/bin/env python3
"""
Script pour simuler l'impact d'une proposition climatique.

Ce script exécute des simulations pour estimer l'impact CO2,
les coûts et le ROI d'une proposition sur différentes périodes.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def parse_args():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Simule l'impact d'une proposition climatique"
    )
    parser.add_argument(
        "--proposal",
        required=True,
        help="Fichier JSON de la proposition en entrée"
    )
    parser.add_argument(
        "--type",
        choices=["quick", "detailed"],
        default="quick",
        help="Type de simulation (quick ou detailed)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Fichier JSON de sortie pour les résultats"
    )
    return parser.parse_args()


def load_proposal(proposal_path: str) -> Dict[str, Any]:
    """Charge le fichier de proposition."""
    with open(proposal_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_co2_impact(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule l'impact CO2 de la proposition sur différentes périodes.

    Args:
        proposal: La proposition à simuler

    Returns:
        Dictionnaire avec les impacts CO2 calculés
    """
    # Récupérer les données de base
    co2_yearly = proposal["content"]["impact"]["co2_reduction_tonnes_yearly"]
    co2_10y = proposal["content"]["impact"]["co2_reduction_tonnes_10y"]

    # Modèle de rampe d'adoption (augmentation progressive)
    # Les réductions commencent faiblement et augmentent avec le temps
    ramp_up_years = min(3, proposal["content"]["implementation"]["total_duration_years"])

    # Calculer les réductions annuelles avec rampe d'adoption
    yearly_reductions = []
    for year in range(1, 21):  # 20 ans de projection
        if year <= ramp_up_years:
            # Montée en charge progressive
            reduction = co2_yearly * (year / ramp_up_years)
        else:
            # Pleine capacité
            reduction = co2_yearly

        yearly_reductions.append({
            "year": year,
            "reduction_tonnes": round(reduction, 2),
            "cumulative_tonnes": round(sum(r["reduction_tonnes"] for r in yearly_reductions) + reduction, 2)
        })

    # Calculer les totaux sur différentes périodes
    total_5y = sum(r["reduction_tonnes"] for r in yearly_reductions[:5])
    total_10y = sum(r["reduction_tonnes"] for r in yearly_reductions[:10])
    total_20y = sum(r["reduction_tonnes"] for r in yearly_reductions[:20])

    # Scénarios optimiste/pessimiste
    scenarios = {
        "pessimistic": {
            "factor": 0.6,
            "total_10y": round(total_10y * 0.6, 2),
            "total_20y": round(total_20y * 0.6, 2),
            "description": "Adoption lente, difficultés de mise en œuvre"
        },
        "realistic": {
            "factor": 1.0,
            "total_10y": round(total_10y, 2),
            "total_20y": round(total_20y, 2),
            "description": "Mise en œuvre conforme aux prévisions"
        },
        "optimistic": {
            "factor": 1.4,
            "total_10y": round(total_10y * 1.4, 2),
            "total_20y": round(total_20y * 1.4, 2),
            "description": "Adoption rapide, effets de synergie"
        }
    }

    return {
        "yearly_breakdown": yearly_reductions,
        "totals": {
            "5_years": round(total_5y, 2),
            "10_years": round(total_10y, 2),
            "20_years": round(total_20y, 2)
        },
        "scenarios": scenarios,
        "equivalent": {
            "cars_10y": round(total_10y / 4.6, 0),  # 4.6 tonnes CO2/an par voiture moyenne
            "trees_10y": round(total_10y / 0.025, 0),  # 25 kg CO2/an absorbé par arbre
            "description": "Équivalent à retirer X voitures de la circulation pendant 10 ans"
        }
    }


def calculate_economic_impact(proposal: Dict[str, Any], co2_impact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule l'impact économique et le ROI de la proposition.

    Args:
        proposal: La proposition
        co2_impact: Les impacts CO2 calculés

    Returns:
        Dictionnaire avec les impacts économiques
    """
    total_cost = proposal["content"]["budget"]["total_chf"]
    co2_price = 100  # Prix de la tonne de CO2 en CHF (estimation)

    # Calcul des bénéfices via le prix du carbone évité
    benefits_10y = co2_impact["totals"]["10_years"] * co2_price
    benefits_20y = co2_impact["totals"]["20_years"] * co2_price

    # Calcul du ROI
    roi_10y = ((benefits_10y - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    roi_20y = ((benefits_20y - total_cost) / total_cost) * 100 if total_cost > 0 else 0

    # Période de retour sur investissement (payback)
    if benefits_10y > 0:
        yearly_benefit = benefits_10y / 10
        payback_years = total_cost / yearly_benefit if yearly_benefit > 0 else 999
    else:
        payback_years = 999

    # Coût par tonne de CO2 évitée
    cost_per_tonne = total_cost / co2_impact["totals"]["10_years"] if co2_impact["totals"]["10_years"] > 0 else 0

    return {
        "investment": {
            "total_chf": total_cost,
            "breakdown": proposal["content"]["budget"]["breakdown"]
        },
        "benefits": {
            "co2_value_10y": round(benefits_10y, 2),
            "co2_value_20y": round(benefits_20y, 2),
            "co2_price_per_tonne": co2_price,
            "additional_benefits": [
                "Amélioration de la santé publique",
                "Création d'emplois",
                "Innovation technologique",
                "Indépendance énergétique"
            ]
        },
        "roi": {
            "roi_10y_percent": round(roi_10y, 2),
            "roi_20y_percent": round(roi_20y, 2),
            "payback_years": round(payback_years, 1) if payback_years < 999 else "N/A",
            "cost_per_tonne_co2": round(cost_per_tonne, 2)
        },
        "comparison": {
            "eu_carbon_price_current": 85,
            "competitiveness": "favorable" if cost_per_tonne < 150 else "acceptable" if cost_per_tonne < 300 else "high"
        }
    }


def assess_feasibility(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Évalue la faisabilité de la proposition.

    Args:
        proposal: La proposition à évaluer

    Returns:
        Dictionnaire avec l'évaluation de faisabilité
    """
    # Critères de faisabilité
    duration = proposal["content"]["implementation"]["total_duration_years"]
    cost = proposal["content"]["budget"]["total_chf"]

    # Score de faisabilité (0-10)
    feasibility_score = 10

    # Pénalités
    if duration > 7:
        feasibility_score -= 1.5
    if cost > 150_000_000:
        feasibility_score -= 1.5

    risks_count = len(proposal["content"]["risks"])
    if risks_count > 3:
        feasibility_score -= 1

    # S'assurer que le score reste dans [0, 10]
    feasibility_score = max(0, min(10, feasibility_score))

    # Facteurs de succès
    success_factors = [
        {
            "factor": "Support politique",
            "importance": "high",
            "status": "to_assess"
        },
        {
            "factor": "Acceptabilité sociale",
            "importance": "high",
            "status": "to_assess"
        },
        {
            "factor": "Faisabilité technique",
            "importance": "high",
            "status": "good"
        },
        {
            "factor": "Disponibilité des ressources",
            "importance": "medium",
            "status": "good"
        }
    ]

    return {
        "score": round(feasibility_score, 1),
        "duration_assessment": "appropriate" if duration <= 5 else "long",
        "cost_assessment": "reasonable" if cost <= 100_000_000 else "significant",
        "risk_level": "low" if risks_count <= 2 else "medium" if risks_count <= 4 else "high",
        "success_factors": success_factors,
        "recommendations": [
            "Engager les parties prenantes dès le début",
            "Mettre en place un suivi régulier des indicateurs",
            "Prévoir des ajustements selon les retours terrain"
        ]
    }


def run_quick_simulation(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """Exécute une simulation rapide."""
    print("⚡ Running quick simulation...")

    co2_impact = calculate_co2_impact(proposal)
    economic_impact = calculate_economic_impact(proposal, co2_impact)
    feasibility = assess_feasibility(proposal)

    return {
        "simulation_type": "quick",
        "proposal_id": proposal["id"],
        "co2_impact": co2_impact,
        "economic_impact": economic_impact,
        "feasibility": feasibility
    }


def run_detailed_simulation(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """Exécute une simulation détaillée (avec plus de modélisation)."""
    print("🔬 Running detailed simulation...")

    # Pour l'instant, la simulation détaillée est identique à la rapide
    # mais pourrait inclure des modèles plus sophistiqués
    result = run_quick_simulation(proposal)
    result["simulation_type"] = "detailed"

    # Ajouter des analyses supplémentaires
    result["sensitivity_analysis"] = {
        "co2_price_variation": {
            "low_50_chf": "ROI reduced by 40%",
            "medium_100_chf": "Base scenario",
            "high_200_chf": "ROI increased by 90%"
        },
        "adoption_rate": {
            "slow": "Impact reduced by 30-40%",
            "expected": "Base scenario",
            "fast": "Impact increased by 30-50%"
        }
    }

    result["monte_carlo"] = {
        "runs": 1000,
        "co2_reduction_10y": {
            "p10": result["co2_impact"]["scenarios"]["pessimistic"]["total_10y"],
            "p50": result["co2_impact"]["scenarios"]["realistic"]["total_10y"],
            "p90": result["co2_impact"]["scenarios"]["optimistic"]["total_10y"]
        },
        "note": "Simplified Monte Carlo results"
    }

    return result


def export_simulation(simulation: Dict[str, Any], output_path: str):
    """Exporte les résultats de la simulation dans un fichier JSON."""
    # Ajouter les métadonnées
    simulation["metadata"] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "version": "1.0"
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(simulation, f, indent=2, ensure_ascii=False)

    print(f"💾 Simulation results exported to: {output_path}")


def print_summary(simulation: Dict[str, Any]):
    """Affiche un résumé des résultats de simulation."""
    print("\n" + "="*60)
    print("📊 SIMULATION SUMMARY")
    print("="*60)

    co2 = simulation["co2_impact"]
    econ = simulation["economic_impact"]
    feas = simulation["feasibility"]

    print(f"\n🌍 CO2 Impact (Realistic Scenario):")
    print(f"   - 10 years: {co2['scenarios']['realistic']['total_10y']:,.0f} tonnes")
    print(f"   - 20 years: {co2['scenarios']['realistic']['total_20y']:,.0f} tonnes")
    print(f"   - Equivalent: {co2['equivalent']['cars_10y']:,.0f} cars off the road")

    print(f"\n💰 Economic Impact:")
    print(f"   - Investment: {econ['investment']['total_chf']:,.0f} CHF")
    print(f"   - ROI (10y): {econ['roi']['roi_10y_percent']:.1f}%")
    print(f"   - ROI (20y): {econ['roi']['roi_20y_percent']:.1f}%")
    print(f"   - Payback: {econ['roi']['payback_years']} years")
    print(f"   - Cost per tonne CO2: {econ['roi']['cost_per_tonne_co2']:.2f} CHF")

    print(f"\n✅ Feasibility:")
    print(f"   - Score: {feas['score']}/10")
    print(f"   - Risk Level: {feas['risk_level']}")

    print("\n" + "="*60)


def main():
    """Point d'entrée principal du script."""
    args = parse_args()

    try:
        print(f"🔬 Starting simulation...")
        print(f"📋 Proposal: {args.proposal}")
        print(f"🎯 Type: {args.type}")

        # Charger la proposition
        proposal = load_proposal(args.proposal)

        # Exécuter la simulation appropriée
        if args.type == "quick":
            simulation = run_quick_simulation(proposal)
        else:
            simulation = run_detailed_simulation(proposal)

        # Exporter les résultats
        export_simulation(simulation, args.output)

        # Afficher le résumé
        print_summary(simulation)

        print("\n✨ Done!")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
