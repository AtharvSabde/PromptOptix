"""
PromptOptimizer Pro - Issue Matcher Service
Cross-references user-reported issues with detected defects for targeted optimization
"""

from typing import Dict, List, Any, Optional
from ..utils import get_logger
from ..models.issue_registry import (
    match_user_issue,
    match_user_issues_with_scores,
    aggregate_defect_priorities,
    aggregate_suggested_techniques,
    get_issues_for_defect,
    IssueDefinition,
    ISSUE_REGISTRY
)

logger = get_logger(__name__)

# Singleton instance
_issue_matcher_instance = None


class IssueMatcherService:
    """
    Service for matching user-reported issues to defects and providing
    targeted optimization recommendations.
    """

    def __init__(self):
        """Initialize the issue matcher service"""
        self.issue_registry = ISSUE_REGISTRY
        logger.info("IssueMatcherService initialized")

    def match_issues_to_defects(
        self,
        user_issues: List[str],
        detected_defects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Cross-reference user-reported issues with detected defects

        Args:
            user_issues: List of user-described issues
            detected_defects: List of defects detected by agents

        Returns:
            Dict containing:
                - matched_issues: Issues that map to detected defects
                - priority_adjustments: Defect ID -> priority boost mapping
                - additional_recommendations: Techniques to suggest
                - validation_score: How well agent findings match user experience
                - unmatched_user_issues: User issues with no corresponding defects
                - unmatched_defects: Defects not mentioned by user
        """
        if not user_issues:
            return {
                "matched_issues": [],
                "priority_adjustments": {},
                "additional_recommendations": [],
                "validation_score": 1.0,
                "unmatched_user_issues": [],
                "unmatched_defects": [d.get("id") for d in detected_defects]
            }

        # Match user issues to known issue types
        all_matched_issues = []
        issue_defect_mapping = {}

        for issue_text in user_issues:
            matches = match_user_issues_with_scores(issue_text)
            for match in matches:
                issue_id = match["issue"].id
                if issue_id not in issue_defect_mapping:
                    issue_defect_mapping[issue_id] = {
                        "issue": match["issue"],
                        "user_text": issue_text,
                        "match_score": match["match_score"],
                        "matched_keywords": match["matched_keywords"]
                    }
                    all_matched_issues.append(match)

        # Get priority adjustments
        priority_adjustments = aggregate_defect_priorities(user_issues)

        # Get suggested techniques
        additional_recommendations = aggregate_suggested_techniques(user_issues)

        # Calculate validation score
        validation_result = self._calculate_validation_score(
            user_issues=user_issues,
            matched_issues=all_matched_issues,
            detected_defects=detected_defects
        )

        return {
            "matched_issues": [
                {
                    "issue_id": m["issue"].id,
                    "issue_name": m["issue"].name,
                    "match_score": m["match_score"],
                    "matched_keywords": m["matched_keywords"],
                    "related_defects": m["issue"].related_defects,
                    "priority_boost": m["issue"].priority_boost
                }
                for m in all_matched_issues
            ],
            "priority_adjustments": priority_adjustments,
            "additional_recommendations": additional_recommendations,
            "validation_score": validation_result["score"],
            "unmatched_user_issues": validation_result["unmatched_user_issues"],
            "unmatched_defects": validation_result["unmatched_defects"],
            "validation_details": validation_result["details"]
        }

    def _calculate_validation_score(
        self,
        user_issues: List[str],
        matched_issues: List[Dict],
        detected_defects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate how well detected defects align with user-reported issues

        A high validation score means:
        - Detected defects match what users report
        - User issues are supported by defect detection

        Args:
            user_issues: Original user issue descriptions
            matched_issues: Issues matched from registry
            detected_defects: Defects detected by agents

        Returns:
            Validation score (0-1) and details
        """
        detected_defect_ids = set(d.get("id") for d in detected_defects)

        # Get all defects related to matched issues
        issue_related_defects = set()
        for match in matched_issues:
            for defect_id in match["issue"].related_defects:
                issue_related_defects.add(defect_id)

        if not issue_related_defects and not detected_defect_ids:
            return {
                "score": 1.0,
                "details": "No issues reported and no defects detected",
                "unmatched_user_issues": [],
                "unmatched_defects": []
            }

        if not issue_related_defects:
            return {
                "score": 0.7,  # Default score when no issues match
                "details": "User issues could not be mapped to known patterns",
                "unmatched_user_issues": user_issues,
                "unmatched_defects": list(detected_defect_ids)
            }

        # Calculate overlap
        overlap = issue_related_defects.intersection(detected_defect_ids)

        # Score components:
        # 1. What percentage of user-implied defects were detected?
        if issue_related_defects:
            user_coverage = len(overlap) / len(issue_related_defects)
        else:
            user_coverage = 1.0

        # 2. What percentage of detected defects match user concerns?
        if detected_defect_ids:
            detection_relevance = len(overlap) / len(detected_defect_ids)
        else:
            detection_relevance = 1.0

        # Combined score (weighted toward user coverage)
        validation_score = (user_coverage * 0.6) + (detection_relevance * 0.4)

        # Find unmatched items
        unmatched_user_defects = issue_related_defects - detected_defect_ids
        unmatched_detected = detected_defect_ids - issue_related_defects

        # Determine unmatched user issues
        unmatched_user_issues = []
        for issue_text in user_issues:
            matches = match_user_issue(issue_text)
            if not matches:
                unmatched_user_issues.append(issue_text)
            else:
                # Check if any matched defects were detected
                found_match = False
                for match in matches:
                    if any(d in detected_defect_ids for d in match.related_defects):
                        found_match = True
                        break
                if not found_match:
                    unmatched_user_issues.append(issue_text)

        details = []
        if overlap:
            details.append(f"Found {len(overlap)} defects matching user concerns")
        if unmatched_user_defects:
            details.append(f"User reported issues suggest {len(unmatched_user_defects)} defects not detected")
        if unmatched_detected:
            details.append(f"Detected {len(unmatched_detected)} additional defects beyond user concerns")

        return {
            "score": round(validation_score, 3),
            "details": "; ".join(details) if details else "Analysis complete",
            "unmatched_user_issues": unmatched_user_issues,
            "unmatched_defects": list(unmatched_detected),
            "overlap_defects": list(overlap),
            "user_coverage": round(user_coverage, 3),
            "detection_relevance": round(detection_relevance, 3)
        }

    def apply_priority_boosts(
        self,
        defects: List[Dict[str, Any]],
        user_issues: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Apply priority boosts to defects based on user issues

        Args:
            defects: List of detected defects
            user_issues: List of user-described issues

        Returns:
            Updated defects list with boosted confidence scores
        """
        if not user_issues:
            return defects

        priority_boosts = aggregate_defect_priorities(user_issues)

        boosted_defects = []
        for defect in defects:
            defect_copy = defect.copy()
            defect_id = defect_copy.get("id")

            if defect_id in priority_boosts:
                boost = priority_boosts[defect_id]
                original_confidence = defect_copy.get("confidence", 0.5)
                new_confidence = min(1.0, original_confidence * boost)

                defect_copy["confidence"] = new_confidence
                defect_copy["priority_boosted"] = True
                defect_copy["boost_factor"] = boost
                defect_copy["boost_reason"] = "Matches user-reported issue"

                logger.debug(
                    f"Boosted defect {defect_id} confidence: "
                    f"{original_confidence:.2f} -> {new_confidence:.2f} (x{boost:.2f})"
                )

            boosted_defects.append(defect_copy)

        # Re-sort by confidence after boosting
        boosted_defects.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        return boosted_defects

    def get_targeted_recommendations(
        self,
        user_issues: List[str],
        detected_defects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate targeted optimization recommendations based on user issues

        Args:
            user_issues: List of user-described issues
            detected_defects: List of defects detected by agents

        Returns:
            Targeted recommendations with explanations
        """
        match_result = self.match_issues_to_defects(user_issues, detected_defects)

        recommendations = []
        technique_explanations = {}

        # Get suggested techniques from matched issues
        for tech_id in match_result["additional_recommendations"]:
            if tech_id not in technique_explanations:
                # Find which issues suggested this technique
                suggesting_issues = []
                for match in match_result["matched_issues"]:
                    issue = ISSUE_REGISTRY.get(match["issue_id"])
                    if issue and tech_id in issue.suggested_techniques:
                        suggesting_issues.append(match["issue_name"])

                technique_explanations[tech_id] = suggesting_issues

        # Build recommendation list
        for tech_id, issues in technique_explanations.items():
            recommendations.append({
                "technique_id": tech_id,
                "reason": f"Addresses user concerns: {', '.join(issues)}",
                "priority": "high" if len(issues) > 1 else "medium",
                "source": "user_issues"
            })

        # Add recommendations for high-priority defects
        priority_defects = [
            d for d in detected_defects
            if d.get("id") in match_result["priority_adjustments"]
        ]

        for defect in priority_defects:
            defect_id = defect.get("id")
            boost = match_result["priority_adjustments"].get(defect_id, 1.0)
            if boost > 1.3:  # Only for significantly boosted defects
                recommendations.append({
                    "defect_id": defect_id,
                    "defect_name": defect.get("name", "Unknown"),
                    "reason": f"High priority based on user feedback (boost: x{boost:.1f})",
                    "priority": "high",
                    "source": "priority_boost"
                })

        return {
            "recommendations": recommendations,
            "technique_suggestions": list(technique_explanations.keys()),
            "high_priority_defects": [d.get("id") for d in priority_defects],
            "validation_score": match_result["validation_score"]
        }

    def generate_issue_summary(
        self,
        user_issues: List[str]
    ) -> Dict[str, Any]:
        """
        Generate a summary of user issues for reporting

        Args:
            user_issues: List of user-described issues

        Returns:
            Summary of matched issues and categories
        """
        if not user_issues:
            return {
                "total_issues": 0,
                "matched_issues": 0,
                "categories": {},
                "issues": []
            }

        all_matches = []
        category_counts = {}

        for issue_text in user_issues:
            matches = match_user_issues_with_scores(issue_text)
            for match in matches:
                category = match["issue"].category.value
                category_counts[category] = category_counts.get(category, 0) + 1
                all_matches.append({
                    "user_input": issue_text,
                    "matched_issue": match["issue"].name,
                    "category": category,
                    "confidence": match["match_score"]
                })

        return {
            "total_issues": len(user_issues),
            "matched_issues": len(set(m["matched_issue"] for m in all_matches)),
            "categories": category_counts,
            "issues": all_matches
        }


def get_issue_matcher() -> IssueMatcherService:
    """Get or create the singleton IssueMatcherService instance"""
    global _issue_matcher_instance
    if _issue_matcher_instance is None:
        _issue_matcher_instance = IssueMatcherService()
    return _issue_matcher_instance


# Export
__all__ = [
    "IssueMatcherService",
    "get_issue_matcher"
]
