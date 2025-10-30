"""
Climate AI Collective - Orchestrator Service

L'orchestrateur décide quel LLM utiliser pour chaque tâche et coordonne
l'exécution des plans complexes.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()


class TaskStep(BaseModel):
    """Une étape dans le plan d'exécution"""
    step: int
    llm: str
    action: str
    inputs: List[str]
    expected_output: str
    parallel_with: Optional[List[int]] = None


class ExecutionPlan(BaseModel):
    """Plan d'exécution généré par l'orchestrateur"""
    task_id: str
    domain: str
    plan: List[TaskStep]
    fallback: Dict[str, str] = Field(default_factory=dict)
    estimated_duration_minutes: int
    priority: str = "normal"


class LLMEndpoint(BaseModel):
    """Configuration d'un endpoint LLM"""
    name: str
    url: str
    model: str
    specialization: str
    cost_per_1k_tokens: float = 0.0  # Coût fictif pour priorisation


class Orchestrator:
    """
    Orchestrateur central qui coordonne les LLM workers
    """
    
    def __init__(self, config_path: str = "config/llm_endpoints.json"):
        self.endpoints = self._load_endpoints(config_path)
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logger.bind(service="orchestrator")
    
    def _load_endpoints(self, config_path: str) -> Dict[str, LLMEndpoint]:
        """Charge la configuration des endpoints LLM"""
        # Configuration par défaut pour développement
        default_config = {
            "orchestrator": {
                "name": "orchestrator",
                "url": "http://orchestrator-service:8000/v1",
                "model": "mistral-small",
                "specialization": "planning"
            },
            "mistral-large": {
                "name": "mistral-large",
                "url": "http://mistral-large-service:8000/v1",
                "model": "mistral-large",
                "specialization": "complex_generation"
            },
            "deepseek-r1": {
                "name": "deepseek-r1",
                "url": "http://deepseek-service:8000/v1",
                "model": "deepseek-r1",
                "specialization": "technical_validation"
            },
            "llama-3-3": {
                "name": "llama-3-3",
                "url": "http://llama-service:8000/v1",
                "model": "llama-3.3",
                "specialization": "synthesis"
            }
        }
        
        return {
            name: LLMEndpoint(**config)
            for name, config in default_config.items()
        }
    
    async def initialize(self):
        """Initialise les connexions"""
        self.session = aiohttp.ClientSession()
        self.logger.info("orchestrator_initialized", endpoints=list(self.endpoints.keys()))
    
    async def shutdown(self):
        """Ferme les connexions"""
        if self.session:
            await self.session.close()
    
    async def create_execution_plan(
        self,
        task_type: str,
        domain: str,
        context: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        Crée un plan d'exécution pour une tâche donnée
        """
        self.logger.info(
            "creating_execution_plan",
            task_type=task_type,
            domain=domain
        )
        
        # Appelle l'orchestrateur LLM pour créer le plan
        planning_prompt = self._build_planning_prompt(task_type, domain, context)
        
        response = await self.call_llm(
            endpoint="orchestrator",
            prompt=planning_prompt,
            temperature=0.2,
            max_tokens=2000
        )
        
        # Parse la réponse JSON
        try:
            plan_data = json.loads(response)
            plan = ExecutionPlan(
                task_id=f"{domain}_{datetime.now().isoformat()}",
                domain=domain,
                **plan_data
            )
            
            self.logger.info(
                "execution_plan_created",
                task_id=plan.task_id,
                steps=len(plan.plan)
            )
            
            return plan
        except json.JSONDecodeError as e:
            self.logger.error("plan_parsing_failed", error=str(e))
            # Fallback à un plan simple
            return self._create_fallback_plan(task_type, domain)
    
    def _build_planning_prompt(
        self,
        task_type: str,
        domain: str,
        context: Dict[str, Any]
    ) -> str:
        """Construit le prompt de planification"""
        
        available_llms = "\n".join([
            f"- {name}: {ep.specialization}" 
            for name, ep in self.endpoints.items()
        ])
        
        return f"""Tu es l'orchestrateur du Climate AI Collective. Ta mission est de créer un plan d'exécution optimal pour la tâche suivante.

TÂCHE: {task_type}
DOMAINE: {domain}

CONTEXTE:
{json.dumps(context, indent=2, ensure_ascii=False)}

LLM DISPONIBLES:
{available_llms}

INSTRUCTIONS:
1. Analyse la tâche et détermine les étapes nécessaires
2. Assigne chaque étape au LLM le plus approprié
3. Identifie les dépendances entre étapes
4. Optimise pour la qualité et l'efficacité

Réponds UNIQUEMENT avec un objet JSON valide selon ce format:
{{
    "plan": [
        {{
            "step": 1,
            "llm": "nom_du_llm",
            "action": "description_action",
            "inputs": ["input1", "input2"],
            "expected_output": "description_output"
        }}
    ],
    "fallback": {{
        "if_mistral_large_unavailable": "llama-3-3"
    }},
    "estimated_duration_minutes": 15,
    "priority": "high"
}}

NE RÉPONDS QU'AVEC LE JSON, RIEN D'AUTRE.
"""
    
    def _create_fallback_plan(self, task_type: str, domain: str) -> ExecutionPlan:
        """Crée un plan de secours simple"""
        return ExecutionPlan(
            task_id=f"{domain}_fallback_{datetime.now().isoformat()}",
            domain=domain,
            plan=[
                TaskStep(
                    step=1,
                    llm="mistral-large",
                    action="generate_proposal",
                    inputs=["context", "data"],
                    expected_output="proposal"
                )
            ],
            estimated_duration_minutes=10
        )
    
    async def execute_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Exécute un plan d'exécution
        """
        self.logger.info("executing_plan", task_id=plan.task_id)
        
        results = {}
        
        for step in plan.plan:
            self.logger.info(
                "executing_step",
                task_id=plan.task_id,
                step=step.step,
                llm=step.llm
            )
            
            # Récupère les inputs depuis les résultats précédents
            inputs = self._gather_inputs(step.inputs, results)
            
            # Construit le prompt pour cette étape
            prompt = self._build_step_prompt(step, inputs)
            
            # Appelle le LLM approprié
            try:
                response = await self.call_llm(
                    endpoint=step.llm,
                    prompt=prompt,
                    temperature=0.7 if "generate" in step.action else 0.2,
                    max_tokens=4000
                )
                
                results[f"step_{step.step}"] = {
                    "llm": step.llm,
                    "action": step.action,
                    "output": response,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                self.logger.error(
                    "step_execution_failed",
                    step=step.step,
                    error=str(e)
                )
                
                # Tente le fallback si disponible
                if step.llm in plan.fallback:
                    fallback_llm = plan.fallback[step.llm]
                    self.logger.info("attempting_fallback", fallback=fallback_llm)
                    
                    response = await self.call_llm(
                        endpoint=fallback_llm,
                        prompt=prompt,
                        temperature=0.7,
                        max_tokens=4000
                    )
                    
                    results[f"step_{step.step}"] = {
                        "llm": fallback_llm,
                        "action": step.action,
                        "output": response,
                        "timestamp": datetime.now().isoformat(),
                        "fallback": True
                    }
        
        self.logger.info("plan_execution_complete", task_id=plan.task_id)
        
        return {
            "task_id": plan.task_id,
            "domain": plan.domain,
            "results": results,
            "completed_at": datetime.now().isoformat()
        }
    
    def _gather_inputs(
        self,
        input_names: List[str],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Récupère les inputs depuis les résultats précédents"""
        inputs = {}
        
        for name in input_names:
            if name in previous_results:
                inputs[name] = previous_results[name].get("output", "")
            else:
                # Input externe (contexte, données)
                inputs[name] = f"[External data: {name}]"
        
        return inputs
    
    def _build_step_prompt(self, step: TaskStep, inputs: Dict[str, Any]) -> str:
        """Construit le prompt pour une étape"""
        
        inputs_text = "\n".join([
            f"{name}:\n{value}"
            for name, value in inputs.items()
        ])
        
        return f"""ACTION: {step.action}

INPUTS:
{inputs_text}

INSTRUCTIONS:
Exécute l'action demandée en utilisant les inputs fournis.
Produis un résultat de haute qualité qui sera utilisé pour les étapes suivantes.

OUTPUT ATTENDU: {step.expected_output}
"""
    
    async def call_llm(
        self,
        endpoint: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Appelle un LLM via son endpoint vLLM
        """
        if endpoint not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        ep = self.endpoints[endpoint]
        
        if not self.session:
            await self.initialize()
        
        url = f"{ep.url}/chat/completions"
        
        payload = {
            "model": ep.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"LLM call failed: {response.status} - {error_text}"
                    )
        
        except aiohttp.ClientError as e:
            self.logger.error(
                "llm_call_failed",
                endpoint=endpoint,
                error=str(e)
            )
            raise


async def main():
    """Point d'entrée principal"""
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    try:
        # Exemple d'utilisation
        plan = await orchestrator.create_execution_plan(
            task_type="generate_proposal",
            domain="transport",
            context={
                "previous_proposals": 42,
                "interdependencies": ["energie#38", "batiment#27"]
            }
        )
        
        results = await orchestrator.execute_plan(plan)
        
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
