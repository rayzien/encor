"""
Specialized safety module: mandatory_language Unicode character-set checker.
Analyzes bio/text characters (LATIN, CYRILLIC, ARABIC, CJK, GREEK, HEBREW).
"""

import unicodedata
import logging
from typing import Tuple, List
from engine.safety.rules import SafetyRulesContainer

logger = logging.getLogger("encor.safety.language")

class LanguageChecker:
    @staticmethod
    def detect_character_set(text: str) -> str:
        """
        Classifies predominant character set of input text.
        """
        if not text:
            return "UNKNOWN"

        counts = {"LATIN": 0, "CYRILLIC": 0, "ARABIC": 0, "CJK": 0, "GREEK": 0, "HEBREW": 0}

        for char in text:
            name = unicodedata.name(char, "")
            if "LATIN" in name:
                counts["LATIN"] += 1
            elif "CYRILLIC" in name:
                counts["CYRILLIC"] += 1
            elif "ARABIC" in name:
                counts["ARABIC"] += 1
            elif "CJK" in name or "HIRAGANA" in name or "KATAKANA" in name or "HANGUL" in name:
                counts["CJK"] += 1
            elif "GREEK" in name:
                counts["GREEK"] += 1
            elif "HEBREW" in name:
                counts["HEBREW"] += 1

        top_script = max(counts, key=counts.get)
        return top_script if counts[top_script] > 0 else "LATIN"

    @staticmethod
    def check_language(rules: SafetyRulesContainer, text_content: str) -> Tuple[bool, str]:
        """
        Validates whether text matches required mandatory_language character set.
        """
        if not rules.mandatory_language or not text_content:
            return True, "Language check passed (empty or default)"

        detected = LanguageChecker.detect_character_set(text_content)
        allowed = [lang.upper().strip() for lang in rules.mandatory_language]

        if detected not in allowed and "ANY" not in allowed:
            return False, f"Detected character set '{detected}' not in allowed mandatory_language ({rules.mandatory_language})"

        return True, f"Language check passed ({detected})"
