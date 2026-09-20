"""
Specialized engagement action: do_comment_likes.
Likes top or recent comments on target posts to increase account visibility.
"""

import logging
from playwright.async_api import Page
from engine.engagement.rules import EngagementRulesContainer
from engine.engagement.filters import EngagementFilters
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.engagement.do_comment_likes")

async def execute_do_comment_likes(page: Page, rate_limiter: RateLimiter, rules: EngagementRulesContainer, post_url: str, logger_callback=None) -> int:
    """
    Finds comments on the post page and likes up to rules.comment_likes_max.
    """
    if not rules.do_comment_likes_enabled:
        return 0

    if not EngagementFilters.probability_roll(rules.do_comment_likes_percentage):
        return 0

    liked_count = 0
    try:
        # Find comment heart icons inside comment list
        comment_hearts = await page.query_selector_all("ul article svg[aria-label='Like'], ul li svg[aria-label='Like']")
        
        for heart in comment_hearts:
            if liked_count >= rules.comment_likes_max:
                break

            btn = await page.evaluate_handle("el => el.closest('button') || el.parentElement", heart)
            if btn:
                await btn.click()
                liked_count += 1
                rate_limiter.record_action("comment_like")
                msg = f"Liked a comment on post: {post_url}"
                logger.info(msg)
                if logger_callback: logger_callback(msg)
                await rate_limiter.human_delay(0.8)

    except Exception as e:
        logger.error(f"Error executing do_comment_likes on {post_url}: {e}")

    return liked_count
