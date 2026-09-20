"""
Central Safety Guardrail orchestrator combining all Engine 3 safety modules:
- Relationship bounds & Potency ratio (metrics.py)
- Profile attributes, business/creator, verified badge (profile_checker.py)
- Mandatory & Ignore words (word_filters.py)
- Blacklist users (blacklist.py)
- Mandatory language character-set (language.py)
"""

import logging
from typing import Tuple, Dict, Any, Optional

from engine.safety.rules import SafetyRulesContainer
from engine.safety.metrics import RelationshipMetricsChecker
from engine.safety.profile_checker import ProfileAttributeChecker
from engine.safety.word_filters import WordFiltersChecker
from engine.safety.blacklist import UserBlacklistChecker
from engine.safety.language import LanguageChecker

logger = logging.getLogger("encor.safety.guardrail")

class SafetyGuardrail:
    @staticmethod
    def evaluate_profile(
        rules: SafetyRulesContainer,
        username: str,
        followers: int = 100,
        following: int = 100,
        posts: int = 10,
        bio: str = "",
        is_private: bool = False,
        has_profile_pic: bool = True,
        is_business: bool = False,
        business_category: Optional[str] = None,
        is_verified: bool = False
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Runs candidate profile through all safety guardrail checks.
        Returns (passed: bool, reason: str, audit_details: dict).
        """
        audit = {}

        # 1. User Blacklist Check
        ok, msg = UserBlacklistChecker.check_user(rules, username)
        audit["blacklist"] = {"passed": ok, "detail": msg}
        if not ok:
            logger.info(f"Guardrail failed for @{username}: {msg}")
            return False, msg, audit

        # 2. Relationship Bounds & Potency Ratio
        ok, msg = RelationshipMetricsChecker.check_bounds(rules, followers, following, posts)
        audit["metrics"] = {"passed": ok, "detail": msg}
        if not ok:
            logger.info(f"Guardrail failed for @{username}: {msg}")
            return False, msg, audit

        # 3. Profile Attributes & Business/Verified
        ok, msg = ProfileAttributeChecker.check_attributes(rules, is_private, has_profile_pic, is_business, business_category, is_verified)
        audit["attributes"] = {"passed": ok, "detail": msg}
        if not ok:
            logger.info(f"Guardrail failed for @{username}: {msg}")
            return False, msg, audit

        # 4. Mandatory & Ignore Words (Bio)
        ok, msg = WordFiltersChecker.check_words(rules, bio)
        audit["words"] = {"passed": ok, "detail": msg}
        if not ok:
            logger.info(f"Guardrail failed for @{username}: {msg}")
            return False, msg, audit

        # 5. Language Character-Set Filter
        ok, msg = LanguageChecker.check_language(rules, bio)
        audit["language"] = {"passed": ok, "detail": msg}
        if not ok:
            logger.info(f"Guardrail failed for @{username}: {msg}")
            return False, msg, audit

        return True, "All safety guardrails passed", audit
