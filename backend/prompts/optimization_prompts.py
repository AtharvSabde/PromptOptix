"""
PromptOptimizer Pro - Optimization Prompts
Meta-prompts for generating optimized prompt versions
"""

from typing import Dict, List, Any, Optional


def get_optimization_prompt(
    original_prompt: str,
    defects: List[Dict[str, Any]],
    techniques: List[Dict[str, Any]],
    context: Dict[str, Any],
    user_issues: Optional[List[str]] = None
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
        user_issues: Optional user-reported issues to prioritize

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

    # Build user issues section if provided
    user_issues_section = ""
    if user_issues:
        issues_list = "\n".join(f"- {issue}" for issue in user_issues)
        user_issues_section = f"""

USER-REPORTED ISSUES (PRIORITIZE THESE):
The user has specifically reported these problems with their prompt:
{issues_list}

Address these user-reported issues FIRST before applying general improvements.
"""

    return f"""Rewrite and improve the following prompt. Your output must be a complete, ready-to-use prompt.

ORIGINAL PROMPT TO IMPROVE:
\"\"\"
{original_prompt}
\"\"\"
{user_issues_section}
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


# ============================================================
# SHDT - Scored History with Defect Trajectories
# ============================================================

def get_shdt_optimization_prompt(
    original_prompt: str,
    trajectory: List[Dict[str, Any]],
    remaining_defects: List[Dict[str, Any]],
    context: Dict[str, Any]
) -> str:
    """
    Generate SHDT meta-prompt that includes full defect trajectory history.
    The LLM can see which changes caused which improvements (causal insight).

    Args:
        original_prompt: The original prompt
        trajectory: List of {version, prompt, score, defects_fixed, defects_remaining, improvement}
        remaining_defects: Defects still to be fixed
        context: Task type, domain context

    Returns:
        SHDT optimization prompt string
    """
    task_type = context.get("task_type", "general")
    domain = context.get("domain", "general")

    # Build trajectory history
    history_lines = []
    for entry in trajectory:
        version = entry.get("version", 0)
        score = entry.get("score", 0)
        fixed = entry.get("defects_fixed", [])
        remaining = entry.get("defects_remaining", [])
        improvement = entry.get("improvement", 0)

        fixed_text = ", ".join(fixed) if fixed else "none"
        remaining_text = ", ".join(remaining) if remaining else "none"

        if version == 0:
            history_lines.append(
                f"  v{version} (score {score:.1f}): Original prompt. "
                f"Defects detected: {remaining_text}"
            )
        else:
            history_lines.append(
                f"  v{version} (score {score:.1f}, +{improvement:.1f}): "
                f"Fixed: {fixed_text}. Remaining: {remaining_text}"
            )

    trajectory_text = "\n".join(history_lines)

    # Build remaining defects with remediations
    defect_instructions = []
    for d in remaining_defects:
        name = d.get("name", "Unknown")
        remediation = d.get("remediation", d.get("description", ""))
        defect_instructions.append(f"  - {d.get('id', '?')} ({name}): {remediation}")
    defects_text = "\n".join(defect_instructions) if defect_instructions else "  No specific defects remaining."

    # Get the latest prompt version
    latest_prompt = trajectory[-1].get("prompt", original_prompt) if trajectory else original_prompt

    return f"""You are optimizing a prompt through iterative improvement. Study the optimization history below to understand what changes helped and what still needs fixing.

OPTIMIZATION HISTORY (learn from what worked):
{trajectory_text}

CURRENT PROMPT (latest version):
\"\"\"
{latest_prompt}
\"\"\"

REMAINING DEFECTS TO FIX:
{defects_text}

CONTEXT: This is for {task_type} tasks in the {domain} domain.

INSTRUCTIONS:
1. Study the history to understand which types of changes improved the score
2. Apply similar successful patterns to fix the remaining defects
3. Output a COMPLETE rewritten prompt - not a template
4. KEEP all specific content from the current version
5. NEVER use placeholders like [TASK], [ROLE], [INPUT] etc.
6. The rewritten prompt must be similar length or longer than the current version

Return ONLY this JSON:
{{
    "optimized_prompt": "the complete improved prompt here",
    "changes_made": [
        {{
            "change": "what was improved",
            "target_defect": "which defect this addresses",
            "reason": "why this change helps based on trajectory patterns"
        }}
    ],
    "expected_improvement": "brief explanation of expected score change"
}}"""


# ============================================================
# CDRAF - Critic-Driven Refinement with Agent Feedback
# ============================================================

def get_cdraf_critique_refinement_prompt(
    optimized_prompt: str,
    agent_feedback: List[Dict[str, Any]],
    context: Dict[str, Any]
) -> str:
    """
    Generate CDRAF meta-prompt that uses multi-agent critique for directed refinement.

    Args:
        optimized_prompt: The prompt to refine
        agent_feedback: List of {agent, focus_area, issues: [{defect_id, name, description, confidence}]}
        context: Task type, domain context

    Returns:
        CDRAF refinement prompt string
    """
    task_type = context.get("task_type", "general")
    domain = context.get("domain", "general")

    # Build agent feedback section
    feedback_lines = []
    issue_count = 0
    for feedback in agent_feedback:
        agent_name = feedback.get("agent", "Unknown Agent")
        focus = feedback.get("focus_area", "")
        issues = feedback.get("issues", [])

        if issues:
            for issue in issues:
                issue_count += 1
                confidence = issue.get("confidence", 0)
                name = issue.get("name", "Unknown")
                remediation = issue.get("remediation", issue.get("description", ""))
                feedback_lines.append(
                    f"  {issue_count}. [{agent_name}] {name} (confidence: {confidence:.0%})\n"
                    f"     Fix: {remediation}"
                )
        else:
            feedback_lines.append(f"  [{agent_name}] No issues found in {focus}")

    feedback_text = "\n".join(feedback_lines)

    return f"""Your optimized prompt was reviewed by 4 specialist agents. Address their feedback to produce a refined version.

CURRENT PROMPT:
\"\"\"
{optimized_prompt}
\"\"\"

SPECIALIST AGENT FEEDBACK (highest priority first):
{feedback_text}

CONTEXT: This is for {task_type} tasks in the {domain} domain.

RULES:
1. Address each numbered issue from the agent feedback
2. Output a COMPLETE refined prompt - not a template
3. KEEP all existing content that wasn't flagged
4. NEVER use placeholders like [TASK], [ROLE], [INPUT] etc.
5. The refined prompt should be similar length or longer

Return ONLY this JSON:
{{
    "refined_prompt": "the complete refined prompt here",
    "issues_addressed": [
        {{
            "issue_number": 1,
            "agent": "which agent raised this",
            "fix_applied": "what was changed to address this"
        }}
    ],
    "issues_not_addressed": ["any issues that couldn't be reasonably fixed and why"]
}}"""


# ============================================================
# DGEO - Defect-Guided Evolutionary Optimization
# ============================================================

def get_dgeo_variant_prompt(
    original_prompt: str,
    target_defects: List[Dict[str, Any]],
    variant_focus: str,
    context: Dict[str, Any]
) -> str:
    """
    Generate a prompt variant targeting specific defects.

    Args:
        original_prompt: The original prompt
        target_defects: Specific defects this variant should fix
        variant_focus: Description of what this variant focuses on
        context: Task type, domain context

    Returns:
        DGEO variant generation prompt
    """
    task_type = context.get("task_type", "general")
    domain = context.get("domain", "general")

    defect_instructions = []
    for d in target_defects:
        name = d.get("name", "Unknown")
        remediation = d.get("remediation", d.get("description", ""))
        defect_instructions.append(f"  - {name}: {remediation}")
    defects_text = "\n".join(defect_instructions) if defect_instructions else "  General improvements"

    return f"""Rewrite the following prompt to specifically fix the targeted issues. Focus on: {variant_focus}

ORIGINAL PROMPT:
\"\"\"
{original_prompt}
\"\"\"

ISSUES TO FIX IN THIS VARIANT:
{defects_text}

CONTEXT: This is for {task_type} tasks in the {domain} domain.

RULES:
1. Output a COMPLETE rewritten prompt
2. Focus specifically on fixing the listed issues
3. KEEP all content not related to the issues
4. NEVER use placeholders like [TASK], [ROLE], [INPUT] etc.
5. Must be ready to copy-paste and use immediately

Return ONLY this JSON:
{{
    "variant_prompt": "the complete rewritten prompt here",
    "fixes_applied": ["brief description of each fix"]
}}"""


def get_dgeo_crossover_prompt(
    variant_a: str,
    variant_b: str,
    strengths_a: str,
    strengths_b: str,
    context: Dict[str, Any]
) -> str:
    """
    Generate a crossover prompt combining the best of two variants.

    Args:
        variant_a: First parent variant
        variant_b: Second parent variant
        strengths_a: What variant A does well
        strengths_b: What variant B does well
        context: Task type, domain context

    Returns:
        DGEO crossover prompt
    """
    task_type = context.get("task_type", "general")
    domain = context.get("domain", "general")

    return f"""Combine the best aspects of two prompt variants into a single improved version.

VARIANT A (excels at {strengths_a}):
\"\"\"
{variant_a}
\"\"\"

VARIANT B (excels at {strengths_b}):
\"\"\"
{variant_b}
\"\"\"

INSTRUCTION: Create a new prompt that combines:
- The {strengths_a} improvements from Variant A
- The {strengths_b} improvements from Variant B

CONTEXT: This is for {task_type} tasks in the {domain} domain.

RULES:
1. Output a COMPLETE prompt combining both variants' strengths
2. Do not lose any improvement from either variant
3. NEVER use placeholders like [TASK], [ROLE], [INPUT] etc.
4. Must be ready to copy-paste and use immediately
5. Resolve any conflicts by keeping whichever version is clearer

Return ONLY this JSON:
{{
    "crossover_prompt": "the combined prompt here",
    "from_variant_a": ["improvements kept from A"],
    "from_variant_b": ["improvements kept from B"]
}}"""


def get_dgeo_mutation_prompt(
    prompt: str,
    remaining_defects: List[Dict[str, Any]],
    context: Dict[str, Any]
) -> str:
    """
    Generate a mutation prompt that applies targeted defect remediations.

    Args:
        prompt: Current prompt to mutate
        remaining_defects: Defects to fix via mutation
        context: Task type, domain context

    Returns:
        DGEO mutation prompt
    """
    task_type = context.get("task_type", "general")
    domain = context.get("domain", "general")

    defect_instructions = []
    for d in remaining_defects:
        name = d.get("name", "Unknown")
        remediation = d.get("remediation", d.get("description", ""))
        defect_instructions.append(f"  - {name}: {remediation}")
    defects_text = "\n".join(defect_instructions) if defect_instructions else "  Minor general improvements"

    return f"""Make targeted improvements to this prompt to fix the remaining issues.

CURRENT PROMPT:
\"\"\"
{prompt}
\"\"\"

REMAINING ISSUES TO FIX:
{defects_text}

CONTEXT: This is for {task_type} tasks in the {domain} domain.

RULES:
1. Make minimal, targeted changes - do not rewrite unnecessarily
2. Fix the listed issues specifically
3. KEEP everything that is already working well
4. NEVER use placeholders like [TASK], [ROLE], [INPUT] etc.
5. Output the COMPLETE prompt with fixes applied

Return ONLY this JSON:
{{
    "mutated_prompt": "the complete prompt with targeted fixes",
    "mutations_applied": ["brief description of each targeted fix"]
}}"""


# Export all functions
__all__ = [
    "get_optimization_prompt",
    "get_technique_application_prompt",
    "get_incremental_optimization_prompt",
    "get_style_optimization_prompt",
    "get_task_optimization_prompt",
    "get_safety_optimization_prompt",
    "get_refinement_suggestions_prompt",
    "get_shdt_optimization_prompt",
    "get_cdraf_critique_refinement_prompt",
    "get_dgeo_variant_prompt",
    "get_dgeo_crossover_prompt",
    "get_dgeo_mutation_prompt"
]
