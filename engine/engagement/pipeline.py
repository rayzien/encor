"""
Central Engagement Pipeline orchestrator combining all Engine 2 modules:
- do_like (with delimit_liking)
- do_comment (with spintax + delimit_commenting)
- do_comment_likes
- do_follow
- user_interact
- do_story
"""

import logging
from typing import Dict, Any
from playwright.async_api import Page

from engine.engagement.rules import EngagementRulesContainer
from engine.engagement.filters import EngagementFilters
from engine.engagement.do_like import execute_do_like
from engine.engagement.do_comment import execute_do_comment
from engine.engagement.do_comment_likes import execute_do_comment_likes
from engine.engagement.do_follow import execute_do_follow
from engine.engagement.user_interact import execute_user_interact
from engine.engagement.do_story import execute_do_story
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.engagement.pipeline")

class EngagementPipeline:
    @staticmethod
    async def process_post(page: Page, rate_limiter: RateLimiter, rules: EngagementRulesContainer, post_url: str, logger_callback=None) -> Dict[str, Any]:
        """
        Process a single target post through all configured engagement rules.
        """
        results = {"liked": False, "commented": False, "comment_likes": 0}

        await page.goto(post_url, wait_until="domcontentloaded")
        await rate_limiter.human_delay(0.5)

        likes_count, comments_count, media_type = await EngagementFilters.extract_post_stats(page)

        # 1. Do Like
        results["liked"] = await execute_do_like(page, rate_limiter, rules, post_url, likes_count, logger_callback=logger_callback)

        # 2. Do Comment
        results["commented"] = await execute_do_comment(page, rate_limiter, rules, post_url, comments_count, logger_callback=logger_callback)

        # 3. Do Comment Likes
        results["comment_likes"] = await execute_do_comment_likes(page, rate_limiter, rules, post_url, logger_callback=logger_callback)

        return results

    @staticmethod
    async def process_profile(page: Page, rate_limiter: RateLimiter, rules: EngagementRulesContainer, username: str, logger_callback=None) -> Dict[str, Any]:
        """
        Process a target user profile through all configured engagement rules.
        """
        results = {"followed": False, "story_viewed": False, "deep_interactions": 0}

        clean_user = username.lstrip("@").strip()

        # 1. Do Story
        results["story_viewed"] = await execute_do_story(page, rate_limiter, rules, clean_user, logger_callback=logger_callback)

        # 2. User Interact (Multi-post likes)
        results["deep_interactions"] = await execute_user_interact(page, rate_limiter, rules, clean_user, logger_callback=logger_callback)

        # 3. Do Follow
        results["followed"] = await execute_do_follow(page, rate_limiter, rules, clean_user, logger_callback=logger_callback)

        return results
