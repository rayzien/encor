"""
Data structure container for Safety Guardrails configuration.
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class SafetyRulesContainer:
    relationship_bounds_enabled: bool = True
    min_followers: int = 30
    max_followers: int = 50000
    min_following: int = 20
    max_following: int = 7500
    min_posts: int = 5
    max_posts: int = 10000
    potency_ratio: float = 0.0

    skip_private: bool = True
    private_percentage: int = 100
    skip_no_profile_pic: bool = True
    no_profile_pic_percentage: int = 100
    skip_business: bool = False
    skip_non_business: bool = False
    skip_business_categories: List[str] = field(default_factory=list)
    dont_skip_business_categories: List[str] = field(default_factory=list)
    skip_verified: bool = True

    mandatory_words: List[str] = field(default_factory=list)
    ignore_words: List[str] = field(default_factory=lambda: ["nsfw", "giveaway", "fake", "scam"])

    ignore_users: List[str] = field(default_factory=list)
    mandatory_language: List[str] = field(default_factory=lambda: ["LATIN"])
