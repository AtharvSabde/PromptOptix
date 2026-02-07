"""
PromptOptimizer Pro - LLM-Based Evaluation (G-EVAL Style)
Uses LLM to score outputs on multiple quality dimensions
Based on Nagpure et al. (2025) Survey - G-EVAL and ChatEval Methods
"""

from typing import Dict, List, Any, Optional

from ..utils import get_logger
from ..services.llm_service import get_llm_service

logger = get_logger(__name__)


class LLMEvaluator:
    """
    G-EVAL style LLM-based evaluation

    Uses an LLM to evaluate text quality across multiple dimensions:
    - Relevance: How well the output addresses the prompt
    - Coherence: Logical flow and organization
    - Consistency: Internal consistency of information
    - Fluency: Grammatical correctness and readability
    - Accuracy: Factual correctness (when applicable)

    This approach provides more nuanced evaluation than traditional
    NLP metrics, especially for creative or subjective tasks.
    """

    def __init__(self):
        """Initialize the LLM evaluator"""
        self.llm_service = get_llm_service()
        self.dimensions = [
            {
                "name": "relevance",
                "description": "How well does the output address the given prompt/task?",
                "criteria": "Score 1-10: 1=completely off-topic, 5=partially relevant, 10=perfectly addresses the task"
            },
            {
                "name": "coherence",
                "description": "How well-organized and logically structured is the output?",
                "criteria": "Score 1-10: 1=disorganized/confusing, 5=adequate structure, 10=excellent flow and organization"
            },
            {
                "name": "consistency",
                "description": "Is the output internally consistent without contradictions?",
                "criteria": "Score 1-10: 1=contradictory, 5=mostly consistent, 10=fully consistent"
            },
            {
                "name": "fluency",
                "description": "How grammatically correct and readable is the output?",
                "criteria": "Score 1-10: 1=many errors/hard to read, 5=some issues, 10=flawless language"
            },
            {
                "name": "helpfulness",
                "description": "How useful is the output for the intended purpose?",
                "criteria": "Score 1-10: 1=not useful, 5=somewhat useful, 10=extremely helpful"
            }
        ]
        logger.info("LLMEvaluator initialized with G-EVAL style evaluation")

    async def evaluate_output(
        self,
        prompt: str,
        output: str,
        reference: Optional[str] = None,
        task_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Evaluate output quality using LLM

        Args:
            prompt: The prompt that generated the output
            output: The output to evaluate
            reference: Optional reference/expected output for comparison
            task_type: Type of task for context

        Returns:
            Dict with dimension scores, overall score, and explanation
        """
        evaluation_prompt = self._build_evaluation_prompt(
            prompt=prompt,
            output=output,
            reference=reference,
            task_type=task_type
        )

        try:
            result = self.llm_service.call_with_json_response(
                prompt=evaluation_prompt,
                system_prompt=self._get_evaluator_system_prompt(),
                required_fields=["scores", "overall_score", "explanation", "strengths", "weaknesses"]
            )

            if result["success"]:
                parsed = result["parsed_response"]
                return {
                    "success": True,
                    "scores": parsed.get("scores", {}),
                    "overall_score": parsed.get("overall_score", 5.0),
                    "explanation": parsed.get("explanation", ""),
                    "strengths": parsed.get("strengths", []),
                    "weaknesses": parsed.get("weaknesses", []),
                    "evaluation_type": "g_eval"
                }
            else:
                logger.warning(f"LLM evaluation failed: {result.get('error')}")
                return self._default_evaluation()

        except Exception as e:
            logger.error(f"LLM evaluation error: {e}")
            return self._default_evaluation()

    def _get_evaluator_system_prompt(self) -> str:
        """Get the system prompt for the evaluator"""
        return """You are an expert evaluator assessing the quality of AI-generated outputs.
Your task is to objectively score outputs on multiple dimensions and provide constructive feedback.

Be fair and consistent in your scoring:
- Score 1-3: Poor quality, significant issues
- Score 4-6: Acceptable but with room for improvement
- Score 7-8: Good quality, minor issues
- Score 9-10: Excellent quality, minimal to no issues

Always provide specific, actionable feedback."""

    def _build_evaluation_prompt(
        self,
        prompt: str,
        output: str,
        reference: Optional[str],
        task_type: str
    ) -> str:
        """Build the evaluation prompt"""
        dimensions_text = "\n".join([
            f"- {d['name'].upper()}: {d['description']} {d['criteria']}"
            for d in self.dimensions
        ])

        reference_section = ""
        if reference:
            reference_section = f"""
REFERENCE OUTPUT (for comparison):
```
{reference}
```
"""

        return f"""Evaluate the following AI output quality.

TASK TYPE: {task_type}

ORIGINAL PROMPT:
```
{prompt}
```

OUTPUT TO EVALUATE:
```
{output}
```
{reference_section}
EVALUATION DIMENSIONS:
{dimensions_text}

Provide your evaluation as JSON with this EXACT structure:
{{
    "scores": {{
        "relevance": <1-10>,
        "coherence": <1-10>,
        "consistency": <1-10>,
        "fluency": <1-10>,
        "helpfulness": <1-10>
    }},
    "overall_score": <1-10 weighted average>,
    "explanation": "<2-3 sentence overall assessment>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"]
}}

Respond ONLY with the JSON object."""

    def _default_evaluation(self) -> Dict[str, Any]:
        """Return default evaluation when LLM fails"""
        return {
            "success": False,
            "scores": {
                "relevance": 5.0,
                "coherence": 5.0,
                "consistency": 5.0,
                "fluency": 5.0,
                "helpfulness": 5.0
            },
            "overall_score": 5.0,
            "explanation": "Unable to perform LLM evaluation - using default scores",
            "strengths": [],
            "weaknesses": ["Evaluation unavailable"],
            "evaluation_type": "default"
        }

    async def compare_outputs(
        self,
        prompt: str,
        original_output: str,
        optimized_output: str,
        task_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Compare two outputs and determine which is better

        Args:
            prompt: The prompt that generated both outputs
            original_output: Output from original prompt
            optimized_output: Output from optimized prompt
            task_type: Type of task for context

        Returns:
            Comparison results with winner and reasoning
        """
        comparison_prompt = self._build_comparison_prompt(
            prompt=prompt,
            output_a=original_output,
            output_b=optimized_output,
            task_type=task_type
        )

        try:
            result = self.llm_service.call_with_json_response(
                prompt=comparison_prompt,
                system_prompt="You are an expert evaluator comparing AI outputs. Be objective and fair.",
                required_fields=["winner", "confidence", "reasoning", "a_strengths", "b_strengths"]
            )

            if result["success"]:
                parsed = result["parsed_response"]
                winner = parsed.get("winner", "tie")

                return {
                    "success": True,
                    "winner": winner,
                    "winner_label": "original" if winner == "A" else "optimized" if winner == "B" else "tie",
                    "confidence": parsed.get("confidence", 0.5),
                    "reasoning": parsed.get("reasoning", ""),
                    "original_strengths": parsed.get("a_strengths", []),
                    "optimized_strengths": parsed.get("b_strengths", []),
                    "comparison_type": "pairwise"
                }
            else:
                return self._default_comparison()

        except Exception as e:
            logger.error(f"LLM comparison error: {e}")
            return self._default_comparison()

    def _build_comparison_prompt(
        self,
        prompt: str,
        output_a: str,
        output_b: str,
        task_type: str
    ) -> str:
        """Build the comparison prompt"""
        return f"""Compare these two AI outputs for the same prompt and determine which is better.

TASK TYPE: {task_type}

ORIGINAL PROMPT:
```
{prompt}
```

OUTPUT A (Original):
```
{output_a}
```

OUTPUT B (Optimized):
```
{output_b}
```

Compare on these criteria:
1. Relevance to the prompt
2. Quality and completeness of response
3. Clarity and organization
4. Helpfulness for the user

Provide your comparison as JSON:
{{
    "winner": "<A/B/tie>",
    "confidence": <0.0-1.0 how confident in this judgment>,
    "reasoning": "<explanation of why winner is better>",
    "a_strengths": ["<strength of A>"],
    "b_strengths": ["<strength of B>"]
}}

Respond ONLY with the JSON object."""

    def _default_comparison(self) -> Dict[str, Any]:
        """Return default comparison when LLM fails"""
        return {
            "success": False,
            "winner": "tie",
            "winner_label": "tie",
            "confidence": 0.5,
            "reasoning": "Unable to perform comparison - treating as tie",
            "original_strengths": [],
            "optimized_strengths": [],
            "comparison_type": "default"
        }

    async def evaluate_prompt_quality(
        self,
        prompt: str,
        task_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of a prompt itself (not its output)

        Args:
            prompt: The prompt to evaluate
            task_type: Type of task

        Returns:
            Prompt quality assessment
        """
        evaluation_prompt = f"""Evaluate the quality of this prompt for {task_type} tasks.

PROMPT TO EVALUATE:
```
{prompt}
```

Evaluate on:
1. CLARITY (1-10): Is it clear what the user wants?
2. COMPLETENESS (1-10): Does it provide all necessary information?
3. STRUCTURE (1-10): Is it well-organized?
4. SPECIFICITY (1-10): Is it specific enough to get good results?
5. SAFETY (1-10): Are there any potential issues (injection, harmful content)?

Provide your evaluation as JSON:
{{
    "scores": {{
        "clarity": <1-10>,
        "completeness": <1-10>,
        "structure": <1-10>,
        "specificity": <1-10>,
        "safety": <1-10>
    }},
    "overall_score": <1-10>,
    "quick_assessment": "<one sentence summary>",
    "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"]
}}

Respond ONLY with the JSON object."""

        try:
            result = self.llm_service.call_with_json_response(
                prompt=evaluation_prompt,
                system_prompt="You are an expert prompt engineer evaluating prompt quality.",
                required_fields=["scores", "overall_score", "quick_assessment"]
            )

            if result["success"]:
                parsed = result["parsed_response"]
                return {
                    "success": True,
                    "scores": parsed.get("scores", {}),
                    "overall_score": parsed.get("overall_score", 5.0),
                    "quick_assessment": parsed.get("quick_assessment", ""),
                    "improvement_suggestions": parsed.get("improvement_suggestions", []),
                    "evaluation_type": "prompt_quality"
                }
            else:
                return {
                    "success": False,
                    "scores": {},
                    "overall_score": 5.0,
                    "quick_assessment": "Unable to evaluate prompt",
                    "improvement_suggestions": [],
                    "evaluation_type": "default"
                }

        except Exception as e:
            logger.error(f"Prompt quality evaluation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
_llm_evaluator_instance = None


def get_llm_evaluator() -> LLMEvaluator:
    """Get or create singleton LLMEvaluator instance"""
    global _llm_evaluator_instance
    if _llm_evaluator_instance is None:
        _llm_evaluator_instance = LLMEvaluator()
    return _llm_evaluator_instance


# Export
__all__ = [
    "LLMEvaluator",
    "get_llm_evaluator"
]
