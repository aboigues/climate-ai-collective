"""
API REST pour l'interface citoyenne
Permet aux citoyens de consulter les propositions et de voter
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configuration
DOMAINS_PATH = Path(__file__).parent.parent.parent / "domains"
VOTES_PATH = Path(__file__).parent / "data" / "votes.json"

app = FastAPI(
    title="Climate AI Collective - Citizen API",
    description="API permettant aux citoyens de consulter les propositions et de voter",
    version="1.0.0"
)

# CORS pour permettre les appels depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, restreindre aux domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données

class ProposalSummary(BaseModel):
    """Résumé d'une proposition pour la liste"""
    id: str
    domain: str
    title: str
    description: str
    status: str
    co2_reduction_tonnes_10y: Optional[float] = None
    total_cost_chf: Optional[float] = None
    generated_at: str
    avg_impact_score: Optional[float] = None
    avg_feasibility_score: Optional[float] = None
    avg_desirability_score: Optional[float] = None
    total_votes: int = 0


class ProposalDetail(BaseModel):
    """Détails complets d'une proposition"""
    id: str
    domain: str
    title: str
    description: str
    status: str
    generated_at: str
    content: dict
    validation: Optional[dict] = None
    simulation: Optional[dict] = None
    voting_summary: Optional[dict] = None


class VoteRequest(BaseModel):
    """Requête de vote"""
    impact_score: int = Field(ge=1, le=10, description="Note d'impact climatique (1-10)")
    feasibility_score: int = Field(ge=1, le=10, description="Note de faisabilité (1-10)")
    desirability_score: int = Field(ge=1, le=10, description="Note de désirabilité (1-10)")
    comment: Optional[str] = Field(None, max_length=1000, description="Commentaire optionnel")
    citizen_id: Optional[str] = Field(None, description="ID du citoyen (optionnel)")


class VoteResponse(BaseModel):
    """Réponse après un vote"""
    vote_id: str
    proposal_id: str
    timestamp: str
    message: str


class VotingSummary(BaseModel):
    """Résumé des votes pour une proposition"""
    proposal_id: str
    total_votes: int
    avg_impact_score: float
    avg_feasibility_score: float
    avg_desirability_score: float
    avg_overall_score: float


# Fonctions utilitaires

def load_votes() -> dict:
    """Charge les votes depuis le fichier JSON"""
    if not VOTES_PATH.exists():
        return {"votes": [], "summaries": {}}

    with open(VOTES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_votes(votes_data: dict):
    """Sauvegarde les votes dans le fichier JSON"""
    VOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VOTES_PATH, 'w', encoding='utf-8') as f:
        json.dump(votes_data, f, indent=2, ensure_ascii=False)


def calculate_voting_summary(proposal_id: str, votes_data: dict) -> dict:
    """Calcule le résumé des votes pour une proposition"""
    proposal_votes = [v for v in votes_data["votes"] if v["proposal_id"] == proposal_id]

    if not proposal_votes:
        return {
            "total_votes": 0,
            "avg_impact_score": 0,
            "avg_feasibility_score": 0,
            "avg_desirability_score": 0,
            "avg_overall_score": 0
        }

    total = len(proposal_votes)
    avg_impact = sum(v["impact_score"] for v in proposal_votes) / total
    avg_feasibility = sum(v["feasibility_score"] for v in proposal_votes) / total
    avg_desirability = sum(v["desirability_score"] for v in proposal_votes) / total
    avg_overall = (avg_impact + avg_feasibility + avg_desirability) / 3

    return {
        "total_votes": total,
        "avg_impact_score": round(avg_impact, 2),
        "avg_feasibility_score": round(avg_feasibility, 2),
        "avg_desirability_score": round(avg_desirability, 2),
        "avg_overall_score": round(avg_overall, 2)
    }


def find_all_proposals() -> List[dict]:
    """Trouve toutes les propositions dans le répertoire domains/"""
    proposals = []

    if not DOMAINS_PATH.exists():
        return proposals

    for domain_dir in DOMAINS_PATH.iterdir():
        if not domain_dir.is_dir():
            continue

        proposals_dir = domain_dir / "proposals"
        if not proposals_dir.exists():
            continue

        for proposal_dir in proposals_dir.iterdir():
            if not proposal_dir.is_dir():
                continue

            proposal_file = proposal_dir / "proposal.json"
            if not proposal_file.exists():
                continue

            try:
                with open(proposal_file, 'r', encoding='utf-8') as f:
                    proposal = json.load(f)
                    proposals.append(proposal)
            except Exception as e:
                print(f"Erreur lors du chargement de {proposal_file}: {e}")

    return proposals


def load_proposal_files(proposal_id: str, domain: str) -> dict:
    """Charge tous les fichiers d'une proposition (proposal, validation, simulation)"""
    proposal_dir = DOMAINS_PATH / domain / "proposals" / proposal_id

    result = {
        "proposal": None,
        "validation": None,
        "simulation": None
    }

    # Charger la proposition
    proposal_file = proposal_dir / "proposal.json"
    if proposal_file.exists():
        with open(proposal_file, 'r', encoding='utf-8') as f:
            result["proposal"] = json.load(f)

    # Charger la validation
    validation_file = proposal_dir / "validation.json"
    if validation_file.exists():
        with open(validation_file, 'r', encoding='utf-8') as f:
            result["validation"] = json.load(f)

    # Charger la simulation (essayer quick puis deep)
    simulation_file = proposal_dir / "simulation_quick.json"
    if not simulation_file.exists():
        simulation_file = proposal_dir / "simulation_deep.json"

    if simulation_file.exists():
        with open(simulation_file, 'r', encoding='utf-8') as f:
            result["simulation"] = json.load(f)

    return result


# Endpoints

@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Climate AI Collective - Citizen API",
        "version": "1.0.0",
        "endpoints": {
            "proposals": "/api/v1/proposals",
            "proposal_detail": "/api/v1/proposals/{id}",
            "vote": "/api/v1/proposals/{id}/vote",
            "voting_summary": "/api/v1/proposals/{id}/votes",
            "health": "/health"
        }
    }


@app.get("/health")
def health():
    """Endpoint de santé"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/v1/proposals", response_model=List[ProposalSummary])
def list_proposals(domain: Optional[str] = None, status: Optional[str] = None):
    """
    Liste toutes les propositions

    Paramètres:
    - domain: Filtrer par domaine (transport, energie, etc.)
    - status: Filtrer par statut (generated, validated, etc.)
    """
    proposals = find_all_proposals()
    votes_data = load_votes()

    # Filtrer par domaine si spécifié
    if domain:
        proposals = [p for p in proposals if p.get("domain") == domain]

    # Filtrer par statut si spécifié
    if status:
        proposals = [p for p in proposals if p.get("status") == status]

    # Construire les résumés avec les statistiques de vote
    summaries = []
    for proposal in proposals:
        proposal_id = proposal.get("id")
        voting_summary = calculate_voting_summary(proposal_id, votes_data)

        # Extraire les informations de réduction CO2 et coût
        co2_reduction = None
        total_cost = None

        if "content" in proposal:
            content = proposal["content"]
            if "impact" in content:
                co2_reduction = content["impact"].get("co2_reduction_tonnes_10y")
            if "budget" in content:
                total_cost = content["budget"].get("total_chf")

        summaries.append(ProposalSummary(
            id=proposal.get("id", ""),
            domain=proposal.get("domain", ""),
            title=proposal.get("title", ""),
            description=proposal.get("description", ""),
            status=proposal.get("status", ""),
            co2_reduction_tonnes_10y=co2_reduction,
            total_cost_chf=total_cost,
            generated_at=proposal.get("generated_at", ""),
            avg_impact_score=voting_summary["avg_impact_score"] if voting_summary["total_votes"] > 0 else None,
            avg_feasibility_score=voting_summary["avg_feasibility_score"] if voting_summary["total_votes"] > 0 else None,
            avg_desirability_score=voting_summary["avg_desirability_score"] if voting_summary["total_votes"] > 0 else None,
            total_votes=voting_summary["total_votes"]
        ))

    # Trier par date de génération (plus récent en premier)
    summaries.sort(key=lambda x: x.generated_at, reverse=True)

    return summaries


@app.get("/api/v1/proposals/{proposal_id}", response_model=ProposalDetail)
def get_proposal(proposal_id: str):
    """
    Récupère les détails complets d'une proposition

    Inclut:
    - Les données de la proposition
    - Les résultats de validation
    - Les résultats de simulation
    - Le résumé des votes
    """
    proposals = find_all_proposals()
    proposal = next((p for p in proposals if p.get("id") == proposal_id), None)

    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposition {proposal_id} non trouvée")

    domain = proposal.get("domain")
    files = load_proposal_files(proposal_id, domain)

    if not files["proposal"]:
        raise HTTPException(status_code=404, detail=f"Fichier de proposition {proposal_id} non trouvé")

    # Calculer le résumé des votes
    votes_data = load_votes()
    voting_summary = calculate_voting_summary(proposal_id, votes_data)

    return ProposalDetail(
        id=files["proposal"].get("id", ""),
        domain=files["proposal"].get("domain", ""),
        title=files["proposal"].get("title", ""),
        description=files["proposal"].get("description", ""),
        status=files["proposal"].get("status", ""),
        generated_at=files["proposal"].get("generated_at", ""),
        content=files["proposal"].get("content", {}),
        validation=files["validation"],
        simulation=files["simulation"],
        voting_summary=voting_summary if voting_summary["total_votes"] > 0 else None
    )


@app.post("/api/v1/proposals/{proposal_id}/vote", response_model=VoteResponse)
def vote_on_proposal(proposal_id: str, vote: VoteRequest):
    """
    Voter sur une proposition

    Les citoyens peuvent noter chaque proposition sur 3 axes (1-10):
    - Impact climatique
    - Faisabilité
    - Désirabilité sociale
    """
    # Vérifier que la proposition existe
    proposals = find_all_proposals()
    proposal = next((p for p in proposals if p.get("id") == proposal_id), None)

    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposition {proposal_id} non trouvée")

    # Charger les votes existants
    votes_data = load_votes()

    # Créer le nouveau vote
    vote_id = str(uuid4())
    new_vote = {
        "vote_id": vote_id,
        "proposal_id": proposal_id,
        "impact_score": vote.impact_score,
        "feasibility_score": vote.feasibility_score,
        "desirability_score": vote.desirability_score,
        "comment": vote.comment,
        "citizen_id": vote.citizen_id or "anonymous",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Ajouter le vote
    votes_data["votes"].append(new_vote)

    # Mettre à jour le résumé
    summary = calculate_voting_summary(proposal_id, votes_data)
    votes_data["summaries"][proposal_id] = summary

    # Sauvegarder
    save_votes(votes_data)

    return VoteResponse(
        vote_id=vote_id,
        proposal_id=proposal_id,
        timestamp=new_vote["timestamp"],
        message=f"Vote enregistré avec succès ! Total de votes pour cette proposition: {summary['total_votes']}"
    )


@app.get("/api/v1/proposals/{proposal_id}/votes", response_model=VotingSummary)
def get_voting_summary(proposal_id: str):
    """
    Récupère le résumé des votes pour une proposition
    """
    # Vérifier que la proposition existe
    proposals = find_all_proposals()
    proposal = next((p for p in proposals if p.get("id") == proposal_id), None)

    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposition {proposal_id} non trouvée")

    # Charger les votes et calculer le résumé
    votes_data = load_votes()
    summary = calculate_voting_summary(proposal_id, votes_data)

    return VotingSummary(
        proposal_id=proposal_id,
        **summary
    )


@app.get("/api/v1/domains")
def list_domains():
    """Liste tous les domaines disponibles"""
    proposals = find_all_proposals()
    domains = list(set(p.get("domain") for p in proposals))
    domains.sort()

    return {
        "domains": domains,
        "count": len(domains)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
