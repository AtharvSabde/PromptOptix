"""
DGEO - Defect-Guided Evolutionary Optimization

A novel optimization algorithm that combines multi-agent defect detection
with evolutionary search. Unlike EvoPrompt's blind mutations, DGEO uses
detected defects to guide population initialization, crossover, and mutation.

Algorithm:
1. ANALYZE: Run 4-agent defect detection on original prompt
2. GENERATE POPULATION: Create N variants, each targeting different defect subsets
3. EVALUATE: Score each variant using multi-agent re-analysis
4. SELECT: Keep top variants (tournament selection)
5. CROSSOVER: LLM combines strengths of two high-scoring variants
6. MUTATE: Apply remaining defect remediations as directed mutations
7. REPEAT for N generations
8. RETURN: Best variant with full evolution history

Novel contribution: Defect-driven population seeding + defect-guided crossover
+ multi-agent fitness evaluation. No existing tool combines these.
"""

import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from ..utils import get_logger, OptimizationError
from ..config import Config
from .agent_orchestrator import get_orchestrator
from .llm_service import get_llm_service
from ..prompts.optimization_prompts import (
    get_dgeo_variant_prompt,
    get_dgeo_crossover_prompt,
    get_dgeo_mutation_prompt
)

logger = get_logger(__name__)


class DGEOOptimizer:
    """
    Defect-Guided Evolutionary Optimization

    Maintains a population of prompt variants where each variant targets
    different defect subsets. Uses evolutionary operators (selection, crossover,
    mutation) guided by defect analysis to find optimal prompts.
    """

    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.llm_service = get_llm_service()
        self.logger = get_logger("DGEOOptimizer")

    async def optimize(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        analysis: Optional[Dict[str, Any]] = None,
        population_size: int = 5,
        generations: int = 3,
        optimization_level: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Run DGEO evolutionary optimization.

        Args:
            prompt: Original prompt to optimize
            context: Task type, domain context
            analysis: Pre-computed analysis (optional)
            population_size: Number of variants per generation (3-7)
            generations: Number of evolutionary generations (2-4)
            optimization_level: Affects population size and generations

        Returns:
            Best optimized prompt with full evolution history
        """
        if context is None:
            context = {}

        # Adjust parameters based on optimization level
        if optimization_level == "minimal":
            population_size = min(population_size, 3)
            generations = min(generations, 2)
        elif optimization_level == "aggressive":
            population_size = max(population_size, 5)
            generations = max(generations, 3)

        self.logger.info(
            f"Starting DGEO: population={population_size}, generations={generations}"
        )

        # Step 1: Analyze original prompt
        if analysis is None:
            analysis = await self.orchestrator.analyze_with_agents(prompt, context)

        original_score = analysis["overall_score"]
        defects = analysis.get("defects", [])

        if not defects:
            self.logger.info("DGEO: No defects found, returning original")
            return {
                "original_prompt": prompt,
                "best_prompt": prompt,
                "strategy": "dgeo",
                "original_score": original_score,
                "best_score": original_score,
                "total_improvement": 0.0,
                "evolution_history": [],
                "defects_before": [],
                "defects_after": [],
                "before_analysis": analysis,
                "after_analysis": analysis,
                "metadata": {"strategy": "dgeo", "note": "No defects to fix"}
            }

        # Step 2: Generate initial population (defect-guided)
        self.logger.info(f"DGEO: Generating initial population of {population_size} variants")
        population = await self._generate_initial_population(
            prompt, defects, context, population_size
        )

        # Step 3: Evaluate initial population
        population = await self._evaluate_population(population, context)

        evolution_history = [{
            "generation": 0,
            "variants": [
                {
                    "id": v["id"],
                    "score": v["score"],
                    "focus": v["focus"],
                    "defects_remaining": len(v.get("defects", []))
                }
                for v in population
            ],
            "best_score": max(v["score"] for v in population),
            "avg_score": sum(v["score"] for v in population) / len(population)
        }]

        self.logger.info(
            f"DGEO Gen 0: scores={[v['score'] for v in population]}, "
            f"best={max(v['score'] for v in population):.1f}"
        )

        # Step 4-7: Evolutionary loop
        for gen in range(1, generations + 1):
            self.logger.info(f"DGEO Generation {gen}/{generations}")

            # Selection: Keep top 50% (at least 2)
            population.sort(key=lambda v: v["score"], reverse=True)
            survivors = population[:max(2, len(population) // 2)]

            # Crossover: Combine top pairs
            offspring = []
            if len(survivors) >= 2:
                for i in range(0, len(survivors) - 1, 2):
                    child = await self._crossover(
                        survivors[i], survivors[i + 1], context
                    )
                    if child:
                        offspring.append(child)

            # Mutation: Apply remaining defect fixes to survivors
            mutants = []
            for variant in survivors[:2]:  # Mutate top 2
                mutant = await self._mutate(variant, context)
                if mutant:
                    mutants.append(mutant)

            # New population = survivors + offspring + mutants
            population = survivors + offspring + mutants

            # Evaluate new members
            unevaluated = [v for v in population if v.get("score") is None]
            if unevaluated:
                evaluated = await self._evaluate_population(unevaluated, context)
                for v in population:
                    if v.get("score") is None:
                        for ev in evaluated:
                            if ev["id"] == v["id"]:
                                v.update(ev)
                                break

            # Trim to population size
            population.sort(key=lambda v: v.get("score", 0), reverse=True)
            population = population[:population_size]

            gen_best = max(v.get("score", 0) for v in population)
            gen_avg = sum(v.get("score", 0) for v in population) / len(population)

            evolution_history.append({
                "generation": gen,
                "variants": [
                    {
                        "id": v["id"],
                        "score": v.get("score", 0),
                        "focus": v.get("focus", ""),
                        "defects_remaining": len(v.get("defects", [])),
                        "parent_ids": v.get("parent_ids", [])
                    }
                    for v in population
                ],
                "best_score": gen_best,
                "avg_score": round(gen_avg, 2)
            })

            self.logger.info(
                f"DGEO Gen {gen}: best={gen_best:.1f}, avg={gen_avg:.1f}, "
                f"pop_size={len(population)}"
            )

        # Select best variant
        population.sort(key=lambda v: v.get("score", 0), reverse=True)
        best_variant = population[0]

        # Final analysis of best
        final_analysis = await self.orchestrator.analyze_with_agents(
            best_variant["prompt"], context
        )

        return {
            "original_prompt": prompt,
            "best_prompt": best_variant["prompt"],
            "strategy": "dgeo",
            "original_score": original_score,
            "best_score": best_variant["score"],
            "total_improvement": round(best_variant["score"] - original_score, 2),
            "evolution_history": evolution_history,
            "population_final": [
                {"id": v["id"], "score": v.get("score", 0), "focus": v.get("focus", "")}
                for v in population[:5]
            ],
            "defects_before": defects,
            "defects_after": final_analysis.get("defects", []),
            "before_analysis": analysis,
            "after_analysis": final_analysis,
            "metadata": {
                "strategy": "dgeo",
                "population_size": population_size,
                "generations": generations,
                "total_variants_evaluated": sum(
                    len(g["variants"]) for g in evolution_history
                )
            }
        }

    async def _generate_initial_population(
        self,
        prompt: str,
        defects: List[Dict],
        context: Dict,
        size: int
    ) -> List[Dict]:
        """
        Generate initial population with defect-guided variant seeding.

        Each variant targets a different subset of defects:
        - Variant 1: Fix clarity defects (D001-D004)
        - Variant 2: Fix structure defects (D005-D009)
        - Variant 3: Fix context defects (D010-D014)
        - Variant 4: Fix all high-severity defects
        - Variant 5: Fix all detected defects
        """
        # Group defects by category
        clarity_defects = [d for d in defects if d.get("id", "").startswith(("D001", "D002", "D003", "D004"))]
        structure_defects = [d for d in defects if d.get("id", "").startswith(("D005", "D006", "D007", "D008", "D009"))]
        context_defects = [d for d in defects if d.get("id", "").startswith(("D01",))]
        high_severity = [d for d in defects if d.get("severity") in ("critical", "high")]

        # Define variant strategies
        variant_configs = [
            ("clarity", clarity_defects or defects[:2], "clarity and specificity"),
            ("structure", structure_defects or defects[:2], "structure and formatting"),
            ("context", context_defects or defects[:2], "context and completeness"),
            ("high_severity", high_severity or defects[:3], "high-severity issues"),
            ("all_defects", defects, "all detected defects")
        ]

        # Limit to requested size
        variant_configs = variant_configs[:size]

        # Generate variants in parallel
        tasks = []
        for variant_id, target_defects, focus in variant_configs:
            tasks.append(
                self._generate_variant(prompt, target_defects, focus, variant_id, context)
            )

        variants = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failures
        population = []
        for v in variants:
            if isinstance(v, Exception):
                self.logger.warning(f"DGEO: Variant generation failed: {v}")
            elif v is not None:
                population.append(v)

        # Ensure we have at least 2 variants
        if len(population) < 2:
            self.logger.warning("DGEO: Too few variants, adding original as fallback")
            population.append({
                "id": "original",
                "prompt": prompt,
                "focus": "original (unchanged)",
                "score": None,
                "defects": [],
                "parent_ids": []
            })

        return population

    async def _generate_variant(
        self,
        prompt: str,
        target_defects: List[Dict],
        focus: str,
        variant_id: str,
        context: Dict
    ) -> Optional[Dict]:
        """Generate a single variant targeting specific defects"""
        try:
            meta_prompt = get_dgeo_variant_prompt(
                original_prompt=prompt,
                target_defects=target_defects,
                variant_focus=focus,
                context=context
            )

            provider = context.get("provider") if context else None
            llm_result = await asyncio.to_thread(
                self.llm_service.call_with_json_response,
                prompt=meta_prompt,
                system_prompt="You are a prompt improvement specialist. Rewrite prompts to fix specific issues. Return only valid JSON.",
                temperature=0.5,  # Slightly higher for diversity
                max_tokens=4096,
                provider=provider,
                required_fields=["variant_prompt"],
                default={"variant_prompt": prompt, "fixes_applied": []},
                field_defaults={"variant_prompt": prompt, "fixes_applied": []}
            )

            parsed = llm_result["parsed_response"]

            variant_prompt = parsed["variant_prompt"]

            # Validate
            placeholder_pattern = r'\[(?:TASK|SLOT|NAME|INPUT|ROLE|DOMAIN|METHOD|STEP|ACTION|APPROACH|PROBLEM|TOPIC)[^\]]*\]'
            if re.search(placeholder_pattern, variant_prompt, re.IGNORECASE):
                self.logger.warning(f"DGEO variant {variant_id}: Contains placeholders, skipping")
                return None
            if len(variant_prompt) < len(prompt) * 0.3:
                self.logger.warning(f"DGEO variant {variant_id}: Too short, skipping")
                return None

            return {
                "id": variant_id,
                "prompt": variant_prompt,
                "focus": focus,
                "score": None,
                "defects": [],
                "parent_ids": [],
                "fixes_applied": parsed.get("fixes_applied", [])
            }

        except Exception as e:
            self.logger.warning(f"DGEO variant {variant_id} generation failed: {e}")
            return None

    async def _evaluate_population(
        self,
        population: List[Dict],
        context: Dict
    ) -> List[Dict]:
        """Evaluate all variants in population using multi-agent analysis"""
        tasks = []
        for variant in population:
            if variant.get("score") is None:
                tasks.append(self._evaluate_variant(variant, context))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"DGEO: Evaluation failed: {result}")
                population[i]["score"] = 0.0
            elif result is not None:
                # Find and update the matching variant
                for v in population:
                    if v["id"] == result["id"]:
                        v.update(result)
                        break

        return population

    async def _evaluate_variant(self, variant: Dict, context: Dict) -> Dict:
        """Evaluate a single variant"""
        try:
            analysis = await self.orchestrator.analyze_with_agents(
                variant["prompt"], context
            )
            variant["score"] = analysis["overall_score"]
            variant["defects"] = [d["id"] for d in analysis.get("defects", [])]
            return variant
        except Exception as e:
            self.logger.warning(f"DGEO: Failed to evaluate {variant['id']}: {e}")
            variant["score"] = 0.0
            return variant

    async def _crossover(
        self,
        variant_a: Dict,
        variant_b: Dict,
        context: Dict
    ) -> Optional[Dict]:
        """LLM-guided crossover combining strengths of two variants"""
        try:
            crossover_prompt = get_dgeo_crossover_prompt(
                variant_a=variant_a["prompt"],
                variant_b=variant_b["prompt"],
                strengths_a=variant_a.get("focus", "general improvements"),
                strengths_b=variant_b.get("focus", "general improvements"),
                context=context
            )

            provider = context.get("provider") if context else None
            llm_result = await asyncio.to_thread(
                self.llm_service.call_with_json_response,
                prompt=crossover_prompt,
                system_prompt="You are a prompt combination specialist. Merge the best aspects of two prompts. Return only valid JSON.",
                temperature=0.4,
                max_tokens=4096,
                provider=provider,
                required_fields=["crossover_prompt"],
                default={"crossover_prompt": variant_a["prompt"], "from_variant_a": [], "from_variant_b": []},
                field_defaults={"crossover_prompt": variant_a["prompt"], "from_variant_a": [], "from_variant_b": []}
            )

            parsed = llm_result["parsed_response"]

            child_prompt = parsed["crossover_prompt"]

            # Validate
            placeholder_pattern = r'\[(?:TASK|SLOT|NAME|INPUT|ROLE|DOMAIN|METHOD|STEP|ACTION|APPROACH|PROBLEM|TOPIC)[^\]]*\]'
            if re.search(placeholder_pattern, child_prompt, re.IGNORECASE):
                return None

            return {
                "id": f"cross_{variant_a['id']}_{variant_b['id']}",
                "prompt": child_prompt,
                "focus": f"crossover of {variant_a['focus']} + {variant_b['focus']}",
                "score": None,
                "defects": [],
                "parent_ids": [variant_a["id"], variant_b["id"]],
                "from_a": parsed.get("from_variant_a", []),
                "from_b": parsed.get("from_variant_b", [])
            }

        except Exception as e:
            self.logger.warning(f"DGEO crossover failed: {e}")
            return None

    async def _mutate(
        self,
        variant: Dict,
        context: Dict
    ) -> Optional[Dict]:
        """Apply targeted defect remediations as directed mutations"""
        remaining_defects = variant.get("defects", [])
        if not remaining_defects:
            return None

        # Get full defect info for remaining defects
        from ..models.defect_taxonomy import get_defect_by_id
        defect_details = []
        for defect_id in remaining_defects[:3]:  # Limit to top 3
            defect_def = get_defect_by_id(defect_id)
            if defect_def:
                defect_details.append({
                    "id": defect_id,
                    "name": defect_def.name,
                    "remediation": defect_def.remediation
                })

        if not defect_details:
            return None

        try:
            mutation_prompt = get_dgeo_mutation_prompt(
                prompt=variant["prompt"],
                remaining_defects=defect_details,
                context=context
            )

            provider = context.get("provider") if context else None
            llm_result = await asyncio.to_thread(
                self.llm_service.call_with_json_response,
                prompt=mutation_prompt,
                system_prompt="You are a prompt refinement specialist. Make targeted fixes to address specific issues. Return only valid JSON.",
                temperature=0.3,
                max_tokens=4096,
                provider=provider,
                required_fields=["mutated_prompt"],
                default={"mutated_prompt": variant["prompt"], "mutations_applied": []},
                field_defaults={"mutated_prompt": variant["prompt"], "mutations_applied": []}
            )

            parsed = llm_result["parsed_response"]

            mutated_prompt = parsed["mutated_prompt"]

            # Validate
            placeholder_pattern = r'\[(?:TASK|SLOT|NAME|INPUT|ROLE|DOMAIN|METHOD|STEP|ACTION|APPROACH|PROBLEM|TOPIC)[^\]]*\]'
            if re.search(placeholder_pattern, mutated_prompt, re.IGNORECASE):
                return None

            return {
                "id": f"mut_{variant['id']}",
                "prompt": mutated_prompt,
                "focus": f"mutation of {variant['focus']}",
                "score": None,
                "defects": [],
                "parent_ids": [variant["id"]],
                "mutations": parsed.get("mutations_applied", [])
            }

        except Exception as e:
            self.logger.warning(f"DGEO mutation failed: {e}")
            return None


# Singleton instance
_dgeo_optimizer = None


def get_dgeo_optimizer() -> DGEOOptimizer:
    """Get or create singleton DGEO optimizer instance"""
    global _dgeo_optimizer
    if _dgeo_optimizer is None:
        _dgeo_optimizer = DGEOOptimizer()
    return _dgeo_optimizer


__all__ = ["DGEOOptimizer", "get_dgeo_optimizer"]
