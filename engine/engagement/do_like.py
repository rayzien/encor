"""
Specialized engagement action: do_like + delimit_liking.
"""

import logging
from playwright.async_api import Page
from engine.engagement.rules import EngagementRulesContainer
from engine.engagement.filters import EngagementFilters
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.engagement.do_like")

async def execute_do_like(page: Page, rate_limiter: RateLimiter, rules: EngagementRulesContainer, post_url: str, post_likes: int, logger_callback=None) -> bool:
    """
    Evaluates probability, delimiter bounds, and likes target post if qualified.
    """
    if not rules.do_like_enabled:
        return False

    # Check probability roll
    if not EngagementFilters.probability_roll(rules.do_like_percentage):
        msg = f"Skipped like on {post_url} due to probability roll ({rules.do_like_percentage}%)"
        logger.info(msg)
        if logger_callback: logger_callback(msg)
        return False

    # Check delimit bounds
    if not EngagementFilters.is_liking_delimited(post_likes, rules.delimit_liking_min, rules.delimit_liking_max):
        msg = f"Skipped like on {post_url}: likes ({post_likes}) outside bounds [{rules.delimit_liking_min}, {rules.delimit_liking_max}]"
        logger.info(msg)
        if logger_callback: logger_callback(msg)
        return False

    try:
        like_btn = await page.query_selector("svg[aria-label='Like']:not([height='12'])")
        unlike_btn = await page.query_selector("svg[aria-label='Unlike']")

        if unlike_btn:
            msg = f"Post already liked: {post_url}"
            logger.info(msg)
            if logger_callback: logger_callback(msg)
            return False

        if like_btn:
            btn_wrapper = await page.evaluate_handle("el => el.closest('button') || el.parentElement", like_btn)
            if btn_wrapper:
                await btn_wrapper.click()
                rate_limiter.record_action("like")
                msg = f"Successfully liked post: {post_url}"
                logger.info(msg)
                if logger_callback: logger_callback(msg)
                await rate_limiter.human_delay(1.0)
                return True
    except Exception as e:
        logger.error(f"Error executing do_like on {post_url}: {e}")

    return False
