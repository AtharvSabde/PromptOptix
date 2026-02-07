"""
PromptOptimizer Pro - Analysis Prompts
Meta-prompts for comprehensive prompt analysis and defect severity assessment
"""

from typing import Dict, List, Any


def get_comprehensive_analysis_prompt(
    prompt: str,
    context: Dict[str, Any]
) -> str:
    """
    Generate meta-prompt for comprehensive multi-dimensional analysis

    Args:
        prompt: The prompt to analyze
        context: Context including task_type, domain, etc.

    Returns:
        Analysis prompt string
    """
    task_type = context.get("task_type", "general")
    domain = context.get("domain", "general")

    return f"""Analyze this prompt comprehensively across all quality dimensions.

PROMPT TO ANALYZE:
```
{prompt}
```

CONTEXT:
- Task Type: {task_type}
- Domain: {domain}

Evaluate on these dimensions (score 1-10 for each):

1. CLARITY: Is the prompt clear and unambiguous?
   - Are instructions easy to understand?
   - Are there vague terms that need definition?
   - Could this be interpreted multiple ways?

2. COMPLETENESS: Does it include all necessary information?
   - Is the task fully specified?
   - Are constraints and requirements stated?
   - Is context provided where needed?

3. STRUCTURE: Is it well-organized?
   - Is there logical flow?
   - Are different elements clearly separated?
   - Is formatting appropriate?

4. SAFETY: Are there any security or safety concerns?
   - Could this enable prompt injection?
   - Are there privacy concerns?
   - Could this lead to harmful outputs?

5. EFFECTIVENESS: Will this likely produce good results?
   - Are instructions actionable?
   - Is the scope appropriate?
   - Are success criteria clear?

Return your analysis as JSON:
{{
    "dimension_scores": {{
        "clarity": <1-10>,
        "completeness": <1-10>,
        "structure": <1-10>,
        "safety": <1-10>,
        "effectiveness": <1-10>
    }},
    "overall_score": <1-10 weighted average>,
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"],
    "quick_fixes": ["<fix 1>", "<fix 2>"],
    "critical_issues": ["<issue if any>"],
    "summary": "<2-3 sentence overall assessment>"
}}

Respond ONLY with the JSON object, no additional text."""


def get_defect_severity_prompt(
    defects: List[Dict[str, Any]],
    task_type: str,
    domain: str
) -> str:
    """
    Generate prompt for assessing defect severity in context

    Args:
        defects: List of detected defects
        task_type: Type of task
        domain: Domain context

    Returns:
        Severity assessment prompt
    """
    defect_list = "\n".join([
        f"- {d.get('id', 'Unknown')}: {d.get('name', 'Unknown')} (current severity: {d.get('severity', 'unknown')})"
        for d in defects
    ])

    return f"""Assess the severity of these detected prompt defects in context.

TASK TYPE: {task_type}
DOMAIN: {domain}

DETECTED DEFECTS:
{defect_list}

For each defect, consider:
1. How critical is this defect for the specific task type?
2. Could this defect cause the task to fail completely?
3. Is this a security/safety concern in this domain?
4. How difficult is this defect to fix?

Provide severity assessment as JSON:
{{
    "assessments": [
        {{
            "defect_id": "<D001>",
            "adjusted_severity": "<critical/high/medium/low>",
            "context_relevance": "<how relevant to task/domain>",
            "impact_description": "<what could go wrong>",
            "priority_rank": <1-N where 1 is highest priority>
        }}
    ],
    "summary": "<overall assessment>",
    "fix_order": ["<defect_id to fix first>", "<next>"]
}}

Respond ONLY with the JSON object."""


def get_task_specific_analysis_prompt(
    prompt: str,
    task_type: str
) -> str:
    """
    Generate task-specific analysis prompt

    Args:
        prompt: The prompt to analyze
        task_type: Specific task type

    Returns:
        Task-specific analysis prompt
    """
    task_criteria = {
        "code_generation": """
For CODE GENERATION, evaluate:
- Is the programming language specified?
- Are function requirements clear (inputs, outputs, behavior)?
- Are edge cases mentioned?
- Are code style preferences indicated?
- Are there security considerations?""",

        "reasoning": """
For REASONING tasks, evaluate:
- Is the problem statement clear?
- Are all relevant facts provided?
- Is the desired reasoning process specified?
- Are constraints on the solution stated?
- Is the expected output format clear?""",

        "creative_writing": """
For CREATIVE WRITING, evaluate:
- Is the genre/style specified?
- Are tone and voice requirements clear?
- Is the target audience defined?
- Are length/format constraints stated?
- Is there creative direction without being too restrictive?""",

        "summarization": """
For SUMMARIZATION tasks, evaluate:
- Is the source material properly provided?
- Are length constraints specified?
- Is the summary focus/perspective indicated?
- Are key points to include/exclude stated?
- Is the target audience specified?""",

        "question_answering": """
For QUESTION ANSWERING, evaluate:
- Is the question clear and specific?
- Is relevant context provided?
- Is the expected answer format specified?
- Are sources or knowledge boundaries stated?
- Is the level of detail expected indicated?""",

        "classification": """
For CLASSIFICATION tasks, evaluate:
- Are all possible categories defined?
- Are examples for each category provided?
- Is multi-label vs single-label specified?
- Are edge cases addressed?
- Is confidence/certainty expected in output?"""
    }

    criteria = task_criteria.get(task_type, """
For GENERAL tasks, evaluate:
- Is the objective clear?
- Are inputs and expected outputs defined?
- Are constraints specified?
- Is context provided?
- Is the scope appropriate?""")

    return f"""Perform task-specific analysis of this prompt.

TASK TYPE: {task_type}

PROMPT:
```
{prompt}
```

{criteria}

Return your analysis as JSON:
{{
    "task_type": "{task_type}",
    "task_requirements_met": <true/false>,
    "missing_requirements": ["<what's missing>"],
    "task_specific_issues": ["<issue specific to this task type>"],
    "task_specific_suggestions": ["<suggestion>"],
    "readiness_score": <1-10 how ready this prompt is for the task>,
    "explanation": "<brief explanation>"
}}

Respond ONLY with the JSON object."""


def get_quick_analysis_prompt(prompt: str) -> str:
    """
    Generate prompt for quick/lightweight analysis

    Args:
        prompt: The prompt to analyze

    Returns:
        Quick analysis prompt
    """
    return f"""Quickly analyze this prompt for major issues.

PROMPT:
```
{prompt}
```

Check for:
1. Major ambiguities
2. Missing critical information
3. Security concerns
4. Obvious improvements

Return as JSON:
{{
    "has_major_issues": <true/false>,
    "issues": ["<issue>"],
    "quick_score": <1-10>,
    "one_line_assessment": "<single sentence>"
}}

Respond ONLY with the JSON object."""


def get_comparison_analysis_prompt(
    original_prompt: str,
    optimized_prompt: str,
    task_type: str
) -> str:
    """
    Generate prompt for comparing original vs optimized prompts

    Args:
        original_prompt: Original prompt
        optimized_prompt: Optimized prompt
        task_type: Type of task

    Returns:
        Comparison analysis prompt
    """
    return f"""Compare these two versions of a prompt and assess the optimization.

TASK TYPE: {task_type}

ORIGINAL PROMPT:
```
{original_prompt}
```

OPTIMIZED PROMPT:
```
{optimized_prompt}
```

Evaluate:
1. What improvements were made?
2. Were any important elements lost?
3. Is the optimized version better for the task?
4. Are there any new issues introduced?

Return as JSON:
{{
    "improvements": ["<improvement made>"],
    "potential_losses": ["<anything lost or degraded>"],
    "new_issues": ["<any new problems>"],
    "overall_improvement": <true/false>,
    "improvement_magnitude": "<significant/moderate/minor/none/worse>",
    "recommendation": "<keep optimized/keep original/needs more work>",
    "explanation": "<brief explanation of recommendation>"
}}

Respond ONLY with the JSON object."""


def get_domain_specific_analysis_prompt(
    prompt: str,
    domain: str
) -> str:
    """
    Generate domain-specific analysis prompt

    Args:
        prompt: The prompt to analyze
        domain: Specific domain

    Returns:
        Domain-specific analysis prompt
    """
    domain_considerations = {
        "software_engineering": """
- Are technical specifications precise?
- Are programming conventions followed?
- Are security best practices considered?
- Is the target environment specified?""",

        "healthcare": """
- Are medical terms used correctly?
- Is patient privacy protected (no PII)?
- Are disclaimers needed?
- Is medical advice appropriately framed?""",

        "legal": """
- Is legal terminology precise?
- Are jurisdictional considerations noted?
- Is confidentiality maintained?
- Are disclaimers about legal advice needed?""",

        "education": """
- Is the content age-appropriate?
- Are learning objectives clear?
- Is the difficulty level specified?
- Are pedagogical approaches considered?""",

        "business": """
- Is business context provided?
- Are stakeholders identified?
- Is confidentiality maintained?
- Is professional tone appropriate?"""
    }

    considerations = domain_considerations.get(domain, """
- Is domain-specific context provided?
- Are appropriate conventions followed?
- Are domain constraints considered?""")

    return f"""Analyze this prompt for domain-specific considerations.

DOMAIN: {domain}

PROMPT:
```
{prompt}
```

Domain-specific considerations:
{considerations}

Return as JSON:
{{
    "domain": "{domain}",
    "domain_appropriate": <true/false>,
    "domain_issues": ["<domain-specific issue>"],
    "domain_suggestions": ["<domain-specific suggestion>"],
    "domain_compliance_score": <1-10>,
    "notes": "<additional domain notes>"
}}

Respond ONLY with the JSON object."""


# Export all functions
__all__ = [
    "get_comprehensive_analysis_prompt",
    "get_defect_severity_prompt",
    "get_task_specific_analysis_prompt",
    "get_quick_analysis_prompt",
    "get_comparison_analysis_prompt",
    "get_domain_specific_analysis_prompt"
]
