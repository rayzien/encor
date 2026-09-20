"""
Specialized safety module: mandatory words & ignore words filtering.
"""

import logging
from typing import Tuple
from engine.safety.rules import SafetyRulesContainer

logger = logging.getLogger("encor.safety.word_filters")

class WordFiltersChecker:
    @staticmethod
    def check_words(rules: SafetyRulesContainer, text_content: str) -> Tuple[bool, str]:
        """
        Validates bio or caption text against mandatory keywords and blacklisted ignore words.
        """
        if not text_content:
            if rules.mandatory_words:
                return False, "Text is empty but mandatory words are required"
            return True, "Word check passed (empty text)"

        lower_text = text_content.lower()

        # 1. Ignore Words (Blacklist)
        if rules.ignore_words:
            for word in rules.ignore_words:
                clean_word = word.lower().strip()
                if clean_word and clean_word in lower_text:
                    return False, f"Contains blacklisted word: '{word}'"

        # 2. Mandatory Words (Must contain at least one)
        if rules.mandatory_words:
            found_mandatory = False
            for word in rules.mandatory_words:
                clean_word = word.lower().strip()
                if clean_word and clean_word in lower_text:
                    found_mandatory = True
                    break
            if not found_mandatory:
                return False, f"Does not contain any mandatory words ({rules.mandatory_words})"

        return True, "Word filters passed"
