"""
Spintax parser supporting nested expressions like:
"{Awesome|Great|Love this} {pic|shot|photo}!"
"""

import re
import random

class SpintaxParser:
    @staticmethod
    def spin(text: str) -> str:
        """
        Parse and spin a spintax string into a randomized output string.
        Handles pattern: {option1|option2|option3}
        """
        if not text:
            return ""

        pattern = re.compile(r"\{([^{}]+)\}")
        while True:
            match = pattern.search(text)
            if not match:
                break
            choices = match.group(1).split("|")
            text = text[:match.start()] + random.choice(choices) + text[match.end():]
        return text

    @staticmethod
    def get_variations_count(text: str) -> int:
        """
        Calculate total possible unique variations for a spintax template.
        """
        if not text:
            return 0
        matches = re.findall(r"\{([^{}]+)\}", text)
        if not matches:
            return 1
        count = 1
        for m in matches:
            count *= len(m.split("|"))
        return count
