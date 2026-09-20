"""
Data container for engagement configuration rules.
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class EngagementRulesContainer:
    do_like_enabled: bool = True
    do_like_percentage: int = 100
    delimit_liking_min: int = 5
    delimit_liking_max: int = 10000

    do_comment_enabled: bool = False
    do_comment_percentage: int = 100
    delimit_commenting_min: int = 0
    delimit_commenting_max: int = 500
    comments_spintax: List[str] = field(default_factory=lambda: ["{Awesome|Great|Love this} {pic|shot|photo}!"])
    
    do_comment_likes_enabled: bool = False
    do_comment_likes_percentage: int = 50
    comment_likes_max: int = 3

    do_follow_enabled: bool = True
    do_follow_percentage: int = 100

    user_interact_amount: int = 3
    user_interact_percentage: int = 100
    user_interact_randomize: bool = True
    user_interact_media: str = "Photo"  # Photo, Video, Any

    do_story_enabled: bool = True
    do_story_percentage: int = 100
