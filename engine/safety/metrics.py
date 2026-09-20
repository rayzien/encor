"""
Specialized safety module: relationship bounds & potency ratio.
"""

import logging
from typing import Tuple
from engine.safety.rules import SafetyRulesContainer

logger = logging.getLogger("encor.safety.metrics")

class RelationshipMetricsChecker:
    @staticmethod
    def check_bounds(rules: SafetyRulesContainer, followers: int, following: int, posts: int) -> Tuple[bool, str]:
        """
        Validates profile metrics against min/max bounds and potency ratio (followers / following).
        """
        if not rules.relationship_bounds_enabled:
            return True, "Relationship bounds disabled"

        if rules.min_followers is not None and followers < rules.min_followers:
            return False, f"Followers ({followers}) < min_followers ({rules.min_followers})"
        
        if rules.max_followers is not None and rules.max_followers > 0 and followers > rules.max_followers:
            return False, f"Followers ({followers}) > max_followers ({rules.max_followers})"

        if rules.min_following is not None and following < rules.min_following:
            return False, f"Following ({following}) < min_following ({rules.min_following})"

        if rules.max_following is not None and rules.max_following > 0 and following > rules.max_following:
            return False, f"Following ({following}) > max_following ({rules.max_following})"

        if rules.min_posts is not None and posts < rules.min_posts:
            return False, f"Posts ({posts}) < min_posts ({rules.min_posts})"

        if rules.max_posts is not None and rules.max_posts > 0 and posts > rules.max_posts:
            return False, f"Posts ({posts}) > max_posts ({rules.max_posts})"

        # Potency Ratio check (Followers-to-Following ratio)
        if rules.potency_ratio and rules.potency_ratio > 0.0:
            actual_ratio = followers / max(1, following)
            if actual_ratio < rules.potency_ratio:
                return False, f"Potency ratio ({actual_ratio:.2f}) < required ({rules.potency_ratio:.2f})"

        return True, "Relationship bounds passed"
