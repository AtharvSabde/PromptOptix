"""
PromptOptimizer Pro - Optimization Prompts
Meta-prompts for generating optimized prompt versions
"""

from typing import Dict, List, Any, Optional


def get_optimization_prompt(
    original_prompt: str,
    defects: List[Dict[str, Any]],
    techniques: List[Dict[str, Any]],
    context: Dict[str, Any]
) -> str:
    """
    Generate meta-prompt for LLM-based prompt optimization

    Uses defect remediations (plain-English improvement instructions) instead
    of technique names to avoid the LLM generating canonical technique templates.

    Args:
        original_prompt: The prompt to optimize
        defects: List of detected defects with their details
        techniques: List of techniques to apply (used for tracking only)
        context: Task type, domain, and other context

    Returns:
        Optimization prompt string
    """
    task_type = context.get("task_type", "general")
    domain = context.get("domain", "general")

    # Build improvement instructions from defect remediations
    # These are plain-English instructions that won't trigger template generation
    improvement_instructions = []
    for i, d in enumerate(defects, 1):
        name = d.get('name', 'Unknown')
        remediation = d.get('remediation', d.get('description', ''))
        improvement_instructions.append(f"{i}. **{name}**: {remediation}")

    improvements_text = "\n".join(improvement_instructions) if improvement_instructions else "General clarity and structure improvements needed."

    return f"""Rewrite and improve the following prompt. Your output must be a complete, ready-to-use prompt.

ORIGINAL PROMPT TO IMPROVE:
\"\"\"
{original_prompt}
\"\"\"

IMPROVEMENTS TO MAKE:
{improvements_text}

CONTEXT: This prompt is used for {task_type} tasks in the {domain} domain.

RULES YOU MUST FOLLOW:
1. Output a COMPLETE rewritten prompt - not a template or framework
2. KEEP every specific detail, instruction, and requirement from the original
3. NEVER use placeholders like [TASK], [ROLE], [INPUT], [NAME], [STEP], [Slot] etc.
4. The rewritten prompt must be similar in length to the original (not shorter)
5. Someone should be able to copy your output and use it immediately as a prompt
6. Only improve clarity, structure, and completeness - do not change the goal

Return ONLY this JSON:
{{
    "optimized_prompt": "the complete rewritten prompt here",
    "changes_made": [
        {{
            "change": "what was improved",
            "reason": "why this helps"
        }}
    ]
}}"""


def get_technique_application_prompt(
    prompt: str,
    technique: Dict[str, Any],
    target_defects: List[str]
) -> str:
    """
    Generate prompt for applying a single technique

    Args:
        prompt: Current prompt text
        technique: Technique to apply
        target_defects: List of defect IDs this technique should fix

    Returns:
        Technique application prompt
    """
    return f"""Apply the following prompt engineering technique to improve this prompt.

CURRENT PROMPT:
```
{prompt}
```

TECHNIQUE TO APPLY:
Name: {technique.get('name', 'Unknown')}
Description: {technique.get('description', '')}
When to use: {technique.get('when_to_use', '')}

Example of this technique:
{technique.get('example', 'No example provided')}

TARGET DEFECTS: {', '.join(target_defects)}

Apply this technique to fix the target defects while:
1. Maintaining the prompt's original purpose
2. Keeping the result natural and readable
3. Not over-engineering the solution

Return as JSON:
{{
    "modified_prompt": "<prompt with technique applied>",
    "modification_description": "<what was changed>",
    "defects_addressed": ["<which defects this fixes>"],
    "technique_fit": <0.0-1.0 how well technique fits this case>
}}

Respond ONLY with the JSON object."""


def get_incremental_optimization_prompt(
    original_prompt: str,
    current_prompt: str,
    iteration: int,
    remaining_defects: List[Dict[str, Any]],
    previous_changes: List[str]
) -> str:
    """
    Generate prompt for incremental optimization iteration

    Args:
        original_prompt: The original prompt
        current_prompt: Current state of prompt after previous iterations
        iteration: Current iteration number
        remaining_defects: Defects still to be fixed
        previous_changes: List of changes made in previous iterations

    Returns:
        Incremental optimization prompt
    """
    defect_list = "\n".join([
        f"- {d.get('id', 'Unknown')}: {d.get('name', 'Unknown')}"
        for d in remaining_defects
    ])

    changes_list = "\n".join([f"- {c}" for c in previous_changes]) if previous_changes else "None yet"

    return f"""Continue optimizing this prompt (Iteration {iteration}).

ORIGINAL PROMPT:
```
{original_prompt}
```

CURRENT STATE:
```
{current_prompt}
```

PREVIOUS CHANGES MADE:
{changes_list}

REMAINING DEFECTS TO ADDRESS:
{defect_list}

Make targeted improvements to address the remaining defects without:
1. Reverting previous beneficial changes
2. Making the prompt overly long or complex
3. Changing the fundamental intent

Return as JSON:
{{
    "improved_prompt": "<next iteration of prompt>",
    "changes_this_iteration": ["<change 1>", "<change 2>"],
    "defects_addressed": ["<defect IDs addressed>"],
    "remaining_concerns": ["<any remaining issues>"],
    "should_continue": <true/false whether more iterations needed>
}}

Respond ONLY with the JSON object."""


def get_style_optimization_prompt(
    prompt: str,
    target_style: str,
    examples: Optional[List[str]] = None
) -> str:
    """
    Generate prompt for style-based optimization

    Args:
        prompt: The prompt to optimize
        target_style: Desired style (formal, casual, technical, etc.)
        examples: Optional examples of the target style

    Returns:
        Style optimization prompt
    """
    examples_section = ""
    if examples:
        examples_text = "\n\n".join([f"Example {i+1}:\n{ex}" for i, ex in enumerate(examples)])
        examples_section = f"""
STYLE EXAMPLES:
{examples_text}
"""

    return f"""Rewrite this prompt to match the target style while preserving its meaning.

ORIGINAL PROMPT:
```
{prompt}
```

TARGET STYLE: {target_style}
{examples_section}
Style characteristics to apply:
- Formal: Professional language, complete sentences, no contractions
- Casual: Conversational tone, friendly language
- Technical: Precise terminology, detailed specifications
- Concise: Minimal words, direct instructions
- Detailed: Thorough explanations, examples included

Return as JSON:
{{
    "styled_prompt": "<prompt in target style>",
    "style_changes": ["<change made for style>"],
    "original_style": "<detected style of original>",
    "style_match_score": <0.0-1.0 how well it matches target style>
}}

Respond ONLY with the JSON object."""


def get_task_optimization_prompt(
    prompt: str,
    task_type: str,
    optimization_goal: str = "effectiveness"
) -> str:
    """
    Generate task-type specific optimization prompt

    Args:
        prompt: The prompt to optimize
        task_type: Type of task
        optimization_goal: What to optimize for (effectiveness, clarity, conciseness)

    Returns:
        Task-specific optimization prompt
    """
    task_tips = {
        "code_generation": """
For code generation:
- Specify the programming language explicitly
- Include function signature or interface requirements
- Mention error handling expectations
- Add example inputs/outputs if helpful
- Specify code style preferences""",

        "reasoning": """
For reasoning tasks:
- Structure the problem clearly
- Provide all relevant facts
- Ask for step-by-step reasoning
- Specify the expected conclusion format
- Include verification request if needed""",

        "creative_writing": """
For creative writing:
- Set the tone and style clearly
- Provide character/setting context
- Specify length and format
- Include themes or elements to incorporate
- Balance guidance with creative freedom""",

        "summarization": """
For summarization:
- Specify the target length
- Indicate what to focus on
- Mention what to exclude if needed
- Specify the summary format
- Include audience context"""
    }

    tips = task_tips.get(task_type, """
General optimization tips:
- Be specific about requirements
- Provide context where helpful
- Specify output format
- Include examples if complex""")

    return f"""Optimize this prompt specifically for {task_type} tasks.

ORIGINAL PROMPT:
```
{prompt}
```

OPTIMIZATION GOAL: {optimization_goal}

{tips}

Create an optimized version that:
1. Is better suited for {task_type} tasks
2. Achieves the optimization goal ({optimization_goal})
3. Maintains the original intent

Return as JSON:
{{
    "optimized_prompt": "<task-optimized prompt>",
    "task_specific_improvements": ["<improvement for this task type>"],
    "expected_improvement": "<what should be better>",
    "task_readiness_before": <1-10>,
    "task_readiness_after": <1-10>
}}

Respond ONLY with the JSON object."""


def get_safety_optimization_prompt(
    prompt: str,
    detected_risks: List[str]
) -> str:
    """
    Generate prompt for safety-focused optimization

    Args:
        prompt: The prompt to optimize
        detected_risks: List of detected security/safety risks

    Returns:
        Safety optimization prompt
    """
    risks_list = "\n".join([f"- {risk}" for risk in detected_risks])

    return f"""Optimize this prompt to address security and safety concerns.

ORIGINAL PROMPT:
```
{prompt}
```

DETECTED RISKS:
{risks_list}

Apply these safety measures:
1. Add input delimitation to prevent injection
2. Include explicit safety guidelines if needed
3. Sanitize any user input sections
4. Add appropriate constraints
5. Ensure no harmful content can be generated

Return as JSON:
{{
    "safe_prompt": "<safety-optimized prompt>",
    "safety_measures_applied": ["<measure 1>", "<measure 2>"],
    "risks_mitigated": ["<risk addressed>"],
    "remaining_concerns": ["<any residual risks>"],
    "safety_score_before": <1-10>,
    "safety_score_after": <1-10>
}}

Respond ONLY with the JSON object."""


def get_refinement_suggestions_prompt(
    prompt: str,
    analysis_results: Dict[str, Any]
) -> str:
    """
    Generate prompt for getting refinement suggestions

    Args:
        prompt: The analyzed prompt
        analysis_results: Results from previous analysis

    Returns:
        Refinement suggestions prompt
    """
    score = analysis_results.get("overall_score", 5)
    defects = analysis_results.get("defects", [])
    defects_summary = ", ".join([d.get("name", "Unknown") for d in defects[:5]])

    return f"""Based on the analysis results, suggest specific refinements for this prompt.

PROMPT:
```
{prompt}
```

ANALYSIS SUMMARY:
- Overall Score: {score}/10
- Main Issues: {defects_summary if defects_summary else "No major issues detected"}

Provide 3-5 specific, actionable refinement suggestions that would most improve this prompt.

Return as JSON:
{{
    "suggestions": [
        {{
            "priority": <1-5 where 1 is highest>,
            "category": "<clarity/completeness/structure/safety/effectiveness>",
            "suggestion": "<specific actionable suggestion>",
            "expected_impact": "<what improvement this would bring>",
            "example_implementation": "<how to implement this>"
        }}
    ],
    "quick_wins": ["<easy improvements>"],
    "major_overhaul_needed": <true/false>
}}

Respond ONLY with the JSON object."""


# Export all functions
__all__ = [
    "get_optimization_prompt",
    "get_technique_application_prompt",
    "get_incremental_optimization_prompt",
    "get_style_optimization_prompt",
    "get_task_optimization_prompt",
    "get_safety_optimization_prompt",
    "get_refinement_suggestions_prompt"
]
