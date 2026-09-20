"""
Specialized safety module: ignore_users blacklist checker.
"""

import logging
from typing import Tuple
from engine.safety.rules import SafetyRulesContainer

logger = logging.getLogger("encor.safety.blacklist")

class UserBlacklistChecker:
    @staticmethod
    def check_user(rules: SafetyRulesContainer, username: str) -> Tuple[bool, str]:
        """
        Validates if target username is in the ignore_users blacklist.
        """
        if not username or not rules.ignore_users:
            return True, "User blacklist passed"

        clean_user = username.lstrip("@").strip().lower()
        blacklisted = [u.lstrip("@").strip().lower() for u in rules.ignore_users]

        if clean_user in blacklisted:
            return False, f"Username @{username} is in ignore_users blacklist"

        return True, "User blacklist passed"
