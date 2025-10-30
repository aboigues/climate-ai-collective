#!/usr/bin/env python3
"""
Script pour charger le contexte d'un domaine climatique.

Ce script collecte toutes les informations pertinentes du repository
pour un domaine spécifique et les exporte dans un fichier JSON.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List


def parse_args():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Charge le contexte d'un domaine climatique"
    )
    parser.add_argument(
        "--domain",
        required=True,
        help="Domaine à traiter (transport, energie, batiment, agriculture, industrie, transversal)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Fichier JSON de sortie"
    )
    return parser.parse_args()


def load_domain_readme(domain: str, repo_root: Path) -> Dict[str, Any]:
    """Charge le README du domaine et extrait les informations clés."""
    readme_path = repo_root / "domains" / domain / "README.md"

    if not readme_path.exists():
        print(f"⚠️  README not found for domain '{domain}'", file=sys.stderr)
        return {
            "name": domain,
            "exists": False,
            "description": f"Domaine {domain}",
            "objectives": [],
            "subdomains": [],
            "resources": {}
        }

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extraction basique des sections
    domain_info = {
        "name": domain,
        "exists": True,
        "readme_content": content,
        "description": extract_description(content),
        "objectives": extract_section_list(content, "Objectifs"),
        "subdomains": extract_section_list(content, "Sous-domaines"),
        "resources": extract_section_dict(content, "Ressources")
    }

    return domain_info


def extract_description(content: str) -> str:
    """Extrait la première description du README."""
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('#') and i + 2 < len(lines):
            # Retourne la ligne suivant le premier titre
            next_line = lines[i + 2].strip()
            if next_line and not next_line.startswith('#'):
                return next_line
    return ""


def extract_section_list(content: str, section_name: str) -> List[str]:
    """Extrait une liste d'items d'une section."""
    items = []
    in_section = False

    for line in content.split('\n'):
        if section_name.lower() in line.lower() and line.startswith('#'):
            in_section = True
            continue

        if in_section:
            if line.startswith('#'):
                break
            if line.strip().startswith('-') or line.strip().startswith('*'):
                items.append(line.strip()[1:].strip())

    return items


def extract_section_dict(content: str, section_name: str) -> Dict[str, str]:
    """Extrait un dictionnaire de clés/valeurs d'une section."""
    section_dict = {}
    in_section = False
    current_subsection = None

    for line in content.split('\n'):
        if section_name.lower() in line.lower() and line.startswith('#'):
            in_section = True
            continue

        if in_section:
            if line.startswith('#'):
                if line.startswith('##'):
                    break
                current_subsection = line.strip('# ').strip()
                section_dict[current_subsection] = []
            elif line.strip().startswith('-') and current_subsection:
                section_dict[current_subsection].append(line.strip()[1:].strip())

    return section_dict


def load_emission_factors(repo_root: Path) -> Dict[str, Any]:
    """Charge les facteurs d'émission depuis le fichier JSON scientifique."""
    emission_factors_path = repo_root / "context" / "scientific-data" / "emission_factors.json"

    if not emission_factors_path.exists():
        print(f"⚠️  Emission factors file not found", file=sys.stderr)
        return {}

    with open(emission_factors_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_existing_proposals(domain: str, repo_root: Path) -> List[Dict[str, Any]]:
    """Liste les propositions existantes pour un domaine."""
    proposals_dir = repo_root / "domains" / domain / "proposals"
    proposals = []

    if not proposals_dir.exists():
        return proposals

    # Parcourir tous les sous-dossiers de propositions
    for proposal_dir in proposals_dir.iterdir():
        if proposal_dir.is_dir():
            proposal_json = proposal_dir / "proposal.json"
            if proposal_json.exists():
                with open(proposal_json, 'r', encoding='utf-8') as f:
                    proposal_data = json.load(f)
                    proposals.append({
                        "id": proposal_dir.name,
                        "path": str(proposal_dir.relative_to(repo_root)),
                        "data": proposal_data
                    })

    return proposals


def get_repo_stats(repo_root: Path) -> Dict[str, Any]:
    """Collecte des statistiques sur le repository."""
    stats = {
        "total_domains": 0,
        "total_proposals": 0,
        "domains_list": []
    }

    domains_dir = repo_root / "domains"
    if domains_dir.exists():
        for domain_dir in domains_dir.iterdir():
            if domain_dir.is_dir():
                stats["domains_list"].append(domain_dir.name)
                stats["total_domains"] += 1

                proposals_dir = domain_dir / "proposals"
                if proposals_dir.exists():
                    stats["total_proposals"] += sum(1 for p in proposals_dir.iterdir() if p.is_dir())

    return stats


def load_context(domain: str) -> Dict[str, Any]:
    """
    Charge tout le contexte nécessaire pour un domaine.

    Args:
        domain: Nom du domaine (transport, energie, etc.)

    Returns:
        Dictionnaire contenant tout le contexte structuré
    """
    # Déterminer le root du repository
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    print(f"📊 Loading context for domain: {domain}")
    print(f"📁 Repository root: {repo_root}")

    # Charger les différentes sources de données
    domain_info = load_domain_readme(domain, repo_root)
    emission_factors = load_emission_factors(repo_root)
    existing_proposals = list_existing_proposals(domain, repo_root)
    repo_stats = get_repo_stats(repo_root)

    # Filtrer les facteurs d'émission pertinents pour le domaine
    relevant_factors = {}
    if domain in emission_factors:
        relevant_factors[domain] = emission_factors[domain]

    # Toujours inclure les valeurs de référence
    if "reference_values" in emission_factors:
        relevant_factors["reference_values"] = emission_factors["reference_values"]

    # Construire le contexte complet
    context = {
        "domain": domain_info,
        "emission_factors": {
            "source": emission_factors.get("source", "Unknown"),
            "version": emission_factors.get("version", "Unknown"),
            "last_updated": emission_factors.get("last_updated", "Unknown"),
            "data": relevant_factors
        },
        "existing_proposals": {
            "count": len(existing_proposals),
            "proposals": existing_proposals
        },
        "repository": repo_stats,
        "metadata": {
            "generated_at": None,  # Sera rempli lors de l'export
            "schema_version": "1.0"
        }
    }

    print(f"✅ Context loaded successfully")
    print(f"   - Domain exists: {domain_info['exists']}")
    print(f"   - Existing proposals: {len(existing_proposals)}")
    print(f"   - Total domains in repo: {repo_stats['total_domains']}")

    return context


def export_context(context: Dict[str, Any], output_path: str):
    """Exporte le contexte dans un fichier JSON."""
    from datetime import datetime

    # Ajouter le timestamp
    context["metadata"]["generated_at"] = datetime.utcnow().isoformat() + "Z"

    # Créer le dossier parent si nécessaire
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Écrire le fichier JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(context, f, indent=2, ensure_ascii=False)

    print(f"💾 Context exported to: {output_path}")


def main():
    """Point d'entrée principal du script."""
    args = parse_args()

    try:
        # Charger le contexte
        context = load_context(args.domain)

        # Exporter le résultat
        export_context(context, args.output)

        print("✨ Done!")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
