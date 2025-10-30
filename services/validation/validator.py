"""
Climate AI Collective - Validation Service

Service de validation en trois couches:
1. Validation immédiate (structure, cohérence)
2. Simulation rapide (impact CO2, économique)
3. Simulation approfondie (modèles scientifiques)
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import numpy as np
import structlog
import aiohttp

logger = structlog.get_logger()


class ValidationResult(BaseModel):
    """Résultat de validation"""
    valid: bool
    score: float = Field(ge=0, le=10)
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ProposalValidator:
    """
    Validateur de propositions climatiques
    """
    
    def __init__(self, llm_endpoint: str = "http://deepseek-service:8000/v1"):
        self.llm_endpoint = llm_endpoint
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logger.bind(service="validator")
    
    async def initialize(self):
        """Initialise les connexions"""
        self.session = aiohttp.ClientSession()
    
    async def shutdown(self):
        """Ferme les connexions"""
        if self.session:
            await self.session.close()
    
    async def validate_proposal(self, proposal: Dict[str, Any]) -> ValidationResult:
        """
        Validation complète d'une proposition
        """
        self.logger.info("validating_proposal", proposal_id=proposal.get("id"))
        
        # 1. Validation structurelle
        structure_check = self.check_required_fields(proposal)
        
        if not structure_check["valid"]:
            return ValidationResult(
                valid=False,
                score=structure_check["score"] * 10,
                issues=structure_check["missing_fields"]
            )
        
        # 2. Validation scientifique par LLM
        coherence_check = await self.llm_coherence_check(proposal)
        
        # 3. Calcul du score final
        final_score = (structure_check["score"] + coherence_check["overall_score"]) / 2
        
        # 4. Déterminer si la proposition passe
        is_valid = (
            structure_check["score"] >= 0.9 and
            coherence_check["overall_score"] >= 7 and
            len(coherence_check["blocking_issues"]) == 0
        )
        
        return ValidationResult(
            valid=is_valid,
            score=final_score,
            issues=structure_check["missing_fields"] + coherence_check["blocking_issues"],
            recommendations=coherence_check["recommendations"]
        )
    
    def check_required_fields(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie que tous les champs obligatoires sont présents
        """
        required_fields = [
            "title",
            "domain",
            "description",
            "co2_reduction_estimate",
            "implementation_cost",
            "timeline",
            "stakeholders",
            "prerequisites",
            "risks",
            "scientific_references"
        ]
        
        missing = [field for field in required_fields if field not in proposal]
        
        score = (len(required_fields) - len(missing)) / len(required_fields)
        
        return {
            "valid": len(missing) == 0,
            "score": score,
            "missing_fields": missing
        }
    
    async def llm_coherence_check(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie la cohérence scientifique avec un LLM (DeepSeek)
        """
        prompt = f"""Tu es un expert scientifique chargé de valider des propositions climatiques.

Analyse cette proposition selon ces critères:

1. COHÉRENCE PHYSIQUE:
   - Les chiffres de réduction CO2 sont-ils réalistes?
   - Les ordres de grandeur sont-ils corrects?
   - Y a-t-il des violations de lois physiques?

2. COHÉRENCE ÉCONOMIQUE:
   - Le ratio coût/impact est-il dans des standards acceptables (<500 CHF/tonne CO2)?
   - Les coûts sont-ils estimés de façon crédible?

3. COHÉRENCE TEMPORELLE:
   - Le timeline est-il réaliste?
   - Les étapes sont-elles logiquement ordonnées?

4. QUALITÉ DES RÉFÉRENCES:
   - Les sources citées sont-elles pertinentes?
   - Manque-t-il des références essentielles?

PROPOSITION:
{json.dumps(proposal, indent=2, ensure_ascii=False)}

Réponds UNIQUEMENT avec un objet JSON valide:
{{
    "physical_coherence": {{"valid": true/false, "issues": ["issue1"]}},
    "economic_coherence": {{"valid": true/false, "issues": []}},
    "temporal_coherence": {{"valid": true/false, "issues": []}},
    "references_quality": {{"score": 0-10, "issues": []}},
    "overall_score": 0-10,
    "blocking_issues": [],
    "recommendations": ["rec1", "rec2"]
}}

NE RÉPONDS QU'AVEC LE JSON.
"""
        
        try:
            if not self.session:
                await self.initialize()
            
            async with self.session.post(
                f"{self.llm_endpoint}/chat/completions",
                json={
                    "model": "deepseek",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            ) as response:
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Parse le JSON de la réponse
                result = json.loads(content)
                return result
        
        except Exception as e:
            self.logger.error("llm_coherence_check_failed", error=str(e))
            
            # Fallback: validation basique
            return {
                "physical_coherence": {"valid": True, "issues": []},
                "economic_coherence": {"valid": True, "issues": []},
                "temporal_coherence": {"valid": True, "issues": []},
                "references_quality": {"score": 5, "issues": []},
                "overall_score": 5,
                "blocking_issues": [],
                "recommendations": ["Validation LLM indisponible - review manuelle requise"]
            }


class QuickSimulator:
    """
    Simulateur rapide pour estimation d'impact
    """
    
    def __init__(self):
        self.logger = logger.bind(service="quick_simulator")
    
    async def simulate(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulation rapide (2-5 minutes)
        """
        self.logger.info("running_quick_simulation", proposal_id=proposal.get("id"))
        
        results = {
            "co2_impact": await self.simulate_co2_impact(proposal),
            "economic_impact": self.simulate_economic_impact(proposal),
            "social_adoption": self.simulate_social_adoption(proposal),
            "confidence_level": "medium"
        }
        
        return results
    
    async def simulate_co2_impact(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modèle simplifié de réduction CO2
        """
        base_reduction = proposal.get("co2_reduction_estimate", 1000)  # tonnes/an
        timeline_months = proposal.get("timeline", 12)
        
        # Courbe d'adoption (logistique)
        timeline = np.arange(0, 120)  # 10 ans
        
        scenarios = {}
        
        for scenario_name, params in [
            ("pessimistic", {"adoption": 0.3, "efficiency": 0.7}),
            ("realistic", {"adoption": 0.6, "efficiency": 0.85}),
            ("optimistic", {"adoption": 0.9, "efficiency": 0.95})
        ]:
            # S-curve adoption
            adoption = 1 / (1 + np.exp(-0.1 * (timeline - timeline_months * 2)))
            adoption *= params["adoption"]
            
            # Réduction mensuelle
            monthly_reduction = base_reduction / 12 * adoption * params["efficiency"]
            cumulative = np.cumsum(monthly_reduction)
            
            scenarios[scenario_name] = {
                "monthly_reduction": monthly_reduction.tolist()[:12],  # 1ère année
                "total_10y": float(cumulative[-1]),
                "peak_monthly": float(np.max(monthly_reduction))
            }
        
        return {
            "scenarios": scenarios,
            "unit": "tonnes_co2",
            "confidence_interval": [
                scenarios["pessimistic"]["total_10y"],
                scenarios["optimistic"]["total_10y"]
            ]
        }
    
    def simulate_economic_impact(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modèle économique simplifié
        """
        capex = proposal.get("implementation_cost", 100000)
        timeline_months = proposal.get("timeline", 12)
        co2_reduction_annual = proposal.get("co2_reduction_estimate", 1000)
        
        # Opex ~ 5% du CAPEX annuel
        opex_annual = capex * 0.05
        
        # Économies (valeur du CO2 évité + bénéfices directs)
        carbon_price = 100  # CHF/tonne
        savings_annual = co2_reduction_annual * carbon_price * 1.3  # +30% co-bénéfices
        
        # Cash flow sur 20 ans
        years = 20
        cash_flow = []
        
        for year in range(years):
            if year == 0:
                cf = -capex
            else:
                cf = savings_annual - opex_annual
            cash_flow.append(cf)
        
        cumulative_cf = np.cumsum(cash_flow)
        
        # Payback
        payback_year = None
        for i, cf in enumerate(cumulative_cf):
            if cf > 0:
                payback_year = i
                break
        
        # NPV (discount 3%)
        discount_rate = 0.03
        npv = sum([
            cf / ((1 + discount_rate) ** year)
            for year, cf in enumerate(cash_flow)
        ])
        
        # Coût par tonne CO2
        cost_per_tonne = capex / (co2_reduction_annual * 10)  # Sur 10 ans
        
        return {
            "total_investment": capex,
            "annual_opex": opex_annual,
            "annual_savings": savings_annual,
            "npv_20y": round(npv, 2),
            "payback_years": payback_year,
            "roi_20y": round((cumulative_cf[-1] / capex) * 100, 1),
            "cost_per_tonne_co2": round(cost_per_tonne, 2),
            "assessment": "excellent" if cost_per_tonne < 200 else (
                "good" if cost_per_tonne < 500 else "acceptable"
            )
        }
    
    def simulate_social_adoption(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modèle d'adoption sociale (Bass diffusion)
        """
        # Paramètres Bass model
        p = 0.02  # Innovation coefficient
        q = 0.38  # Imitation coefficient
        
        timeline = np.arange(0, 120)
        m = 1.0  # Market potential normalisé
        
        # Bass diffusion
        adoption = []
        cumulative_adoption = 0
        
        for t in timeline:
            if t == 0:
                adoption.append(p * m)
            else:
                f_t = (p + q * cumulative_adoption / m) * (m - cumulative_adoption)
                adoption.append(f_t)
            cumulative_adoption += adoption[-1]
        
        adoption_curve = np.cumsum(adoption) / m
        
        return {
            "adoption_10y": float(adoption_curve[-1]),
            "adoption_curve": adoption_curve.tolist()[::12],  # Annuel
            "acceptability_score": 7.5,  # Placeholder
            "main_barriers": ["initial_cost", "behavior_change"],
            "enabling_factors": ["co_benefits", "social_proof"]
        }


async def main():
    """Test du validateur"""
    validator = ProposalValidator()
    simulator = QuickSimulator()
    
    await validator.initialize()
    
    try:
        # Proposition test
        test_proposal = {
            "id": "transport-001",
            "title": "Réseau de voies cyclables sécurisées",
            "domain": "transport",
            "description": "Création d'un réseau de 50km de pistes cyclables protégées",
            "co2_reduction_estimate": 5000,  # tonnes/an
            "implementation_cost": 10000000,  # CHF
            "timeline": 24,  # mois
            "stakeholders": ["ville", "canton", "associations"],
            "prerequisites": ["études de trafic", "budget validé"],
            "risks": ["opposition riverains", "dépassement coûts"],
            "scientific_references": [
                "IPCC AR6",
                "ECF Cycling Benefits Study 2023"
            ]
        }
        
        # Validation
        validation = await validator.validate_proposal(test_proposal)
        print("\n=== VALIDATION ===")
        print(json.dumps(validation.dict(), indent=2, ensure_ascii=False))
        
        # Simulation rapide
        if validation.valid:
            simulation = await simulator.simulate(test_proposal)
            print("\n=== SIMULATION RAPIDE ===")
            print(json.dumps(simulation, indent=2, ensure_ascii=False))
    
    finally:
        await validator.shutdown()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
