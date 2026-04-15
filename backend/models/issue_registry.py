"""
PromptOptimizer Pro - User Issue Registry
Maps user-reported issues to defect categories for targeted optimization
Based on: Nagpure et al., 2025 Survey Paper
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class IssueCategory(str, Enum):
    """Categories of user-reported issues"""
    OUTPUT_QUALITY = "output_quality"
    FORMAT_ISSUES = "format_issues"
    COMPREHENSION = "comprehension"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    SAFETY = "safety"
    PERFORMANCE = "performance"


@dataclass
class IssueDefinition:
    """Definition of a user-reported issue type"""
    id: str
    name: str
    category: IssueCategory
    description: str
    keywords: List[str]  # Keywords for NLP matching
    related_defects: List[str]  # Defect IDs (D001-D028)
    priority_boost: float  # How much to boost related defect priority (1.0 = no boost)
    suggested_techniques: List[str]  # Technique IDs (T001-T041)


# =============================================================================
# USER ISSUE REGISTRY - 20 Common Issues
# =============================================================================

ISSUE_REGISTRY: Dict[str, IssueDefinition] = {

    # =========================================================================
    # OUTPUT QUALITY ISSUES (5 issues)
    # =========================================================================

    "I001": IssueDefinition(
        id="I001",
        name="Output Too Verbose",
        category=IssueCategory.OUTPUT_QUALITY,
        description="Generated output is longer than expected or contains unnecessary details",
        keywords=[
            "verbose", "too long", "wordy", "excessive", "lengthy", "rambling",
            "bloated", "overlong", "drawn out", "too much detail", "too many words"
        ],
        related_defects=["D015", "D002", "D009"],
        priority_boost=1.5,
        suggested_techniques=["T006", "T005"]  # Constraint Addition, Output Format Specification
    ),

    "I002": IssueDefinition(
        id="I002",
        name="Output Too Short",
        category=IssueCategory.OUTPUT_QUALITY,
        description="Generated output lacks sufficient detail or depth",
        keywords=[
            "too short", "brief", "insufficient", "lacking detail", "incomplete",
            "not enough", "shallow", "superficial", "needs more", "expand"
        ],
        related_defects=["D002", "D015", "D019"],
        priority_boost=1.4,
        suggested_techniques=["T006", "T007", "T003"]  # Constraint Addition, Example Provision, CoT
    ),

    "I003": IssueDefinition(
        id="I003",
        name="Poor Writing Quality",
        category=IssueCategory.OUTPUT_QUALITY,
        description="Output has grammar issues, awkward phrasing, or poor flow",
        keywords=[
            "grammar", "poorly written", "awkward", "unclear writing", "bad flow",
            "choppy", "confusing sentences", "hard to read", "poorly structured"
        ],
        related_defects=["D007", "D006", "D018"],
        priority_boost=1.3,
        suggested_techniques=["T001", "T018"]  # Role Prompting, Tone specification
    ),

    "I004": IssueDefinition(
        id="I004",
        name="Repetitive Content",
        category=IssueCategory.OUTPUT_QUALITY,
        description="Output contains repeated information or redundant phrases",
        keywords=[
            "repetitive", "redundant", "repeated", "says the same thing",
            "duplicate", "keeps saying", "over and over", "circular"
        ],
        related_defects=["D003", "D006", "D015"],
        priority_boost=1.4,
        suggested_techniques=["T006", "T015"]  # Constraint Addition, Iterative Refinement
    ),

    "I005": IssueDefinition(
        id="I005",
        name="Lacks Creativity",
        category=IssueCategory.OUTPUT_QUALITY,
        description="Output is generic, predictable, or uninspiring",
        keywords=[
            "generic", "boring", "predictable", "lacks creativity", "uninspired",
            "bland", "cookie-cutter", "template-like", "not original", "uncreative"
        ],
        related_defects=["D018", "D002", "D019"],
        priority_boost=1.3,
        suggested_techniques=["T001", "T007", "T012"]  # Role Prompting, Examples, Metacognitive
    ),

    # =========================================================================
    # FORMAT ISSUES (4 issues)
    # =========================================================================

    "I006": IssueDefinition(
        id="I006",
        name="Wrong Output Format",
        category=IssueCategory.FORMAT_ISSUES,
        description="Output is not in the expected format (JSON, markdown, etc.)",
        keywords=[
            "wrong format", "not json", "not markdown", "formatting", "format error",
            "wrong structure", "bad format", "incorrect format", "needs json", "needs markdown"
        ],
        related_defects=["D008", "D015", "D020"],
        priority_boost=1.6,
        suggested_techniques=["T005", "T010", "T011"]  # Output Format, Template, Delimiters
    ),

    "I007": IssueDefinition(
        id="I007",
        name="Inconsistent Formatting",
        category=IssueCategory.FORMAT_ISSUES,
        description="Output formatting varies or is inconsistent throughout",
        keywords=[
            "inconsistent format", "mixed formatting", "format varies", "not uniform",
            "inconsistent style", "changes format", "format changes"
        ],
        related_defects=["D008", "D020", "D022"],
        priority_boost=1.4,
        suggested_techniques=["T005", "T007", "T010"]  # Output Format, Examples, Template
    ),

    "I008": IssueDefinition(
        id="I008",
        name="Missing Structure",
        category=IssueCategory.FORMAT_ISSUES,
        description="Output lacks proper organization, headers, or sections",
        keywords=[
            "no structure", "disorganized", "no headers", "wall of text",
            "unorganized", "needs sections", "no paragraphs", "no bullets"
        ],
        related_defects=["D006", "D008", "D015"],
        priority_boost=1.4,
        suggested_techniques=["T005", "T010", "T004"]  # Output Format, Template, Step-by-Step
    ),

    "I009": IssueDefinition(
        id="I009",
        name="Code Formatting Issues",
        category=IssueCategory.FORMAT_ISSUES,
        description="Code output has indentation, syntax, or style problems",
        keywords=[
            "code formatting", "indentation", "syntax error", "code style",
            "broken code", "malformed code", "code not working", "code issues"
        ],
        related_defects=["D007", "D008", "D020"],
        priority_boost=1.5,
        suggested_techniques=["T005", "T007", "T016"]  # Output Format, Examples, Syntax Validation
    ),

    # =========================================================================
    # COMPREHENSION ISSUES (3 issues)
    # =========================================================================

    "I010": IssueDefinition(
        id="I010",
        name="Misunderstood Instructions",
        category=IssueCategory.COMPREHENSION,
        description="Model interpreted the request incorrectly",
        keywords=[
            "misunderstood", "wrong interpretation", "not what I meant",
            "misinterpreted", "got it wrong", "confused", "didn't understand"
        ],
        related_defects=["D001", "D004", "D011"],
        priority_boost=1.6,
        suggested_techniques=["T003", "T007", "T021"]  # CoT, Examples, Clarity Enhancement
    ),

    "I011": IssueDefinition(
        id="I011",
        name="Off-Topic Response",
        category=IssueCategory.COMPREHENSION,
        description="Output addresses something different from what was asked",
        keywords=[
            "off topic", "irrelevant", "not related", "wrong topic",
            "different subject", "not what I asked", "unrelated", "tangent"
        ],
        related_defects=["D001", "D004", "D012"],
        priority_boost=1.5,
        suggested_techniques=["T006", "T021", "T003"]  # Constraints, Clarity, CoT
    ),

    "I012": IssueDefinition(
        id="I012",
        name="Partial Response",
        category=IssueCategory.COMPREHENSION,
        description="Output only addresses part of the request, missing key aspects",
        keywords=[
            "partial", "incomplete answer", "missing parts", "only answered half",
            "didn't address", "skipped", "forgot part", "partial response"
        ],
        related_defects=["D002", "D014", "D009"],
        priority_boost=1.5,
        suggested_techniques=["T004", "T009", "T014"]  # Step-by-Step, Decomposition, Chaining
    ),

    # =========================================================================
    # CONSISTENCY ISSUES (3 issues)
    # =========================================================================

    "I013": IssueDefinition(
        id="I013",
        name="Inconsistent Results",
        category=IssueCategory.CONSISTENCY,
        description="Different runs produce very different outputs for the same input",
        keywords=[
            "inconsistent", "different results", "varies", "not reproducible",
            "changes every time", "unstable", "unpredictable", "unreliable"
        ],
        related_defects=["D001", "D003", "D017"],
        priority_boost=1.5,
        suggested_techniques=["T013", "T007", "T006"]  # Self-Consistency, Examples, Constraints
    ),

    "I014": IssueDefinition(
        id="I014",
        name="Contradictory Information",
        category=IssueCategory.CONSISTENCY,
        description="Output contains statements that contradict each other",
        keywords=[
            "contradictory", "contradicts itself", "inconsistent info",
            "conflicting statements", "says opposite", "self-contradicting"
        ],
        related_defects=["D003", "D017", "D020"],
        priority_boost=1.6,
        suggested_techniques=["T013", "T015", "T003"]  # Self-Consistency, Iterative, CoT
    ),

    "I015": IssueDefinition(
        id="I015",
        name="Hallucinated Information",
        category=IssueCategory.CONSISTENCY,
        description="Output contains fabricated facts or incorrect information",
        keywords=[
            "hallucination", "made up", "fabricated", "incorrect facts",
            "wrong information", "false", "inaccurate", "invented", "fictional"
        ],
        related_defects=["D011", "D016", "D017"],
        priority_boost=1.7,
        suggested_techniques=["T008", "T003", "T013"]  # Context Enhancement, CoT, Self-Consistency
    ),

    # =========================================================================
    # COMPLETENESS ISSUES (2 issues)
    # =========================================================================

    "I016": IssueDefinition(
        id="I016",
        name="Missing Examples",
        category=IssueCategory.COMPLETENESS,
        description="Output lacks examples when they would be helpful",
        keywords=[
            "no examples", "needs examples", "missing examples", "show example",
            "illustrate", "demonstrate", "give example", "example please"
        ],
        related_defects=["D019", "D021", "D002"],
        priority_boost=1.3,
        suggested_techniques=["T007", "T002"]  # Example Provision, Few-Shot
    ),

    "I017": IssueDefinition(
        id="I017",
        name="Missing Explanation",
        category=IssueCategory.COMPLETENESS,
        description="Output lacks explanation of reasoning or methodology",
        keywords=[
            "no explanation", "why", "how does it work", "explain",
            "reasoning", "missing context", "needs explanation", "elaborate"
        ],
        related_defects=["D002", "D017", "D019"],
        priority_boost=1.3,
        suggested_techniques=["T003", "T012", "T004"]  # CoT, Metacognitive, Step-by-Step
    ),

    # =========================================================================
    # RELEVANCE & SAFETY ISSUES (3 issues)
    # =========================================================================

    "I018": IssueDefinition(
        id="I018",
        name="Outdated Information",
        category=IssueCategory.RELEVANCE,
        description="Output contains information that is no longer current or accurate",
        keywords=[
            "outdated", "old information", "not current", "out of date",
            "obsolete", "deprecated", "old version", "stale"
        ],
        related_defects=["D011", "D016"],
        priority_boost=1.4,
        suggested_techniques=["T008", "T006"]  # Context Enhancement, Constraints
    ),

    "I019": IssueDefinition(
        id="I019",
        name="Inappropriate Content",
        category=IssueCategory.SAFETY,
        description="Output contains content that is offensive, biased, or inappropriate",
        keywords=[
            "inappropriate", "offensive", "biased", "insensitive",
            "unprofessional", "rude", "disrespectful", "harmful"
        ],
        related_defects=["D024", "D026", "D027"],
        priority_boost=1.8,
        suggested_techniques=["T019", "T001"]  # Safety Guidelines, Role Prompting
    ),

    "I020": IssueDefinition(
        id="I020",
        name="Security Concerns",
        category=IssueCategory.SAFETY,
        description="Output may contain security vulnerabilities or unsafe code",
        keywords=[
            "security", "unsafe", "vulnerability", "insecure", "dangerous",
            "injection", "exploit", "security risk", "unsafe code"
        ],
        related_defects=["D023", "D024", "D025"],
        priority_boost=1.9,
        suggested_techniques=["T018", "T019", "T011"]  # Input Sandboxing, Safety, Delimiters
    ),
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_issue_by_id(issue_id: str) -> Optional[IssueDefinition]:
    """Get issue definition by ID"""
    return ISSUE_REGISTRY.get(issue_id)


def get_issues_by_category(category: IssueCategory) -> List[IssueDefinition]:
    """Get all issues in a specific category"""
    return [i for i in ISSUE_REGISTRY.values() if i.category == category]


def match_user_issue(user_text: str) -> List[IssueDefinition]:
    """
    Match user-described issue to known issue types using keyword matching

    Args:
        user_text: User's description of their issue

    Returns:
        List of matched IssueDefinitions, sorted by match strength
    """
    user_text_lower = user_text.lower()
    matches = []

    for issue in ISSUE_REGISTRY.values():
        # Count keyword matches
        match_count = 0
        matched_keywords = []

        for keyword in issue.keywords:
            if keyword.lower() in user_text_lower:
                match_count += 1
                matched_keywords.append(keyword)

        if match_count > 0:
            # Calculate match score based on keyword coverage
            match_score = match_count / len(issue.keywords)
            matches.append((issue, match_score, matched_keywords))

    # Sort by match score descending
    matches.sort(key=lambda x: x[1], reverse=True)

    # Return just the issues (not scores)
    return [m[0] for m in matches]


def match_user_issues_with_scores(user_text: str) -> List[Dict]:
    """
    Match user-described issue with detailed match information

    Args:
        user_text: User's description of their issue

    Returns:
        List of dicts with issue, score, and matched keywords
    """
    user_text_lower = user_text.lower()
    matches = []

    for issue in ISSUE_REGISTRY.values():
        match_count = 0
        matched_keywords = []

        for keyword in issue.keywords:
            if keyword.lower() in user_text_lower:
                match_count += 1
                matched_keywords.append(keyword)

        if match_count > 0:
            match_score = match_count / len(issue.keywords)
            matches.append({
                "issue": issue,
                "match_score": round(match_score, 3),
                "matched_keywords": matched_keywords,
                "related_defects": issue.related_defects,
                "priority_boost": issue.priority_boost
            })

    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches


def get_defects_for_issue(issue_id: str) -> List[str]:
    """Get related defect IDs for a given issue"""
    issue = ISSUE_REGISTRY.get(issue_id)
    return issue.related_defects if issue else []


def get_issues_for_defect(defect_id: str) -> List[IssueDefinition]:
    """Get all issues related to a specific defect"""
    return [
        issue for issue in ISSUE_REGISTRY.values()
        if defect_id in issue.related_defects
    ]


def get_techniques_for_issue(issue_id: str) -> List[str]:
    """Get suggested techniques for a given issue"""
    issue = ISSUE_REGISTRY.get(issue_id)
    return issue.suggested_techniques if issue else []


def get_all_issues() -> List[IssueDefinition]:
    """Get all issue definitions"""
    return list(ISSUE_REGISTRY.values())


def get_issue_categories() -> Dict[IssueCategory, List[IssueDefinition]]:
    """Get issues organized by category"""
    result = {}
    for category in IssueCategory:
        result[category] = get_issues_by_category(category)
    return result


def get_issues_summary() -> Dict[str, int]:
    """Get count of issues per category"""
    return {
        category.value: len(get_issues_by_category(category))
        for category in IssueCategory
    }


# =============================================================================
# Aggregate Functions for Multi-Issue Analysis
# =============================================================================

def aggregate_defect_priorities(user_issues: List[str]) -> Dict[str, float]:
    """
    Aggregate priority boosts from multiple user issues

    Args:
        user_issues: List of user-described issues

    Returns:
        Dict mapping defect IDs to their cumulative priority boost
    """
    defect_boosts = {}

    for issue_text in user_issues:
        matched_issues = match_user_issue(issue_text)

        for issue in matched_issues:
            for defect_id in issue.related_defects:
                if defect_id in defect_boosts:
                    # Stack boosts but with diminishing returns
                    current = defect_boosts[defect_id]
                    additional = (issue.priority_boost - 1.0) * 0.5
                    defect_boosts[defect_id] = min(current + additional, 2.5)
                else:
                    defect_boosts[defect_id] = issue.priority_boost

    return defect_boosts


def aggregate_suggested_techniques(user_issues: List[str]) -> List[str]:
    """
    Aggregate suggested techniques from matched issues

    Args:
        user_issues: List of user-described issues

    Returns:
        List of unique technique IDs, ordered by frequency
    """
    technique_counts = {}

    for issue_text in user_issues:
        matched_issues = match_user_issue(issue_text)

        for issue in matched_issues:
            for tech_id in issue.suggested_techniques:
                technique_counts[tech_id] = technique_counts.get(tech_id, 0) + 1

    # Sort by frequency
    sorted_techniques = sorted(
        technique_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [tech_id for tech_id, _ in sorted_techniques]


# Export
__all__ = [
    "IssueCategory",
    "IssueDefinition",
    "ISSUE_REGISTRY",
    "get_issue_by_id",
    "get_issues_by_category",
    "match_user_issue",
    "match_user_issues_with_scores",
    "get_defects_for_issue",
    "get_issues_for_defect",
    "get_techniques_for_issue",
    "get_all_issues",
    "get_issue_categories",
    "get_issues_summary",
    "aggregate_defect_priorities",
    "aggregate_suggested_techniques"
]
