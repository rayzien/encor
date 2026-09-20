"""
Specialized safety module: skip users based on private status, no profile pic, business status, and verification badge.
"""

import random
import logging
from typing import Tuple, Optional
from engine.safety.rules import SafetyRulesContainer

logger = logging.getLogger("encor.safety.profile_checker")

class ProfileAttributeChecker:
    @staticmethod
    def check_attributes(
        rules: SafetyRulesContainer,
        is_private: bool,
        has_profile_pic: bool,
        is_business: bool,
        business_category: Optional[str],
        is_verified: bool
    ) -> Tuple[bool, str]:
        """
        Validates profile boolean attributes and categories.
        """
        # 1. Skip private accounts
        if rules.skip_private and is_private:
            if random.randint(1, 100) <= rules.private_percentage:
                return False, f"Skipped private account (probability {rules.private_percentage}%)"

        # 2. Skip no profile pic
        if rules.skip_no_profile_pic and not has_profile_pic:
            if random.randint(1, 100) <= rules.no_profile_pic_percentage:
                return False, f"Skipped account without profile picture (probability {rules.no_profile_pic_percentage}%)"

        # 3. Skip verified blue checkmark
        if rules.skip_verified and is_verified:
            return False, "Skipped verified account"

        # 4. Skip business / non-business
        if rules.skip_business and is_business:
            return False, "Skipped business/creator account"

        if rules.skip_non_business and not is_business:
            return False, "Skipped non-business account"

        # 5. Category filters
        if business_category:
            clean_cat = business_category.lower().strip()
            if rules.skip_business_categories:
                blacklisted_cats = [c.lower().strip() for c in rules.skip_business_categories]
                if clean_cat in blacklisted_cats:
                    return False, f"Skipped business category '{business_category}'"

            if rules.dont_skip_business_categories:
                whitelisted_cats = [c.lower().strip() for c in rules.dont_skip_business_categories]
                if clean_cat not in whitelisted_cats:
                    return False, f"Business category '{business_category}' not in whitelist"

        return True, "Profile attributes passed"
