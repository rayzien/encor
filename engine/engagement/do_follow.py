"""
Specialized engagement action: do_follow.
"""

import logging
from playwright.async_api import Page
from engine.engagement.rules import EngagementRulesContainer
from engine.engagement.filters import EngagementFilters
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.engagement.do_follow")

async def execute_do_follow(page: Page, rate_limiter: RateLimiter, rules: EngagementRulesContainer, target_user: str, logger_callback=None) -> bool:
    """
    Evaluates follow rules and follows target user if qualified.
    """
    if not rules.do_follow_enabled:
        return False

    if not EngagementFilters.probability_roll(rules.do_follow_percentage):
        msg = f"Skipped follow for @{target_user} due to probability roll ({rules.do_follow_percentage}%)"
        logger.info(msg)
        if logger_callback: logger_callback(msg)
        return False

    try:
        url = f"https://www.instagram.com/{target_user}/"
        if target_user not in page.url:
            await page.goto(url, wait_until="domcontentloaded")
            await rate_limiter.human_delay(0.5)

        follow_btn = await page.query_selector("button:has-text('Follow'):not(:has-text('Following'))")
        following_btn = await page.query_selector("button:has-text('Following')")

        if following_btn:
            msg = f"Already following @{target_user}"
            logger.info(msg)
            if logger_callback: logger_callback(msg)
            return False

        if follow_btn:
            await follow_btn.click()
            rate_limiter.record_action("follow")
            msg = f"Successfully followed @{target_user}"
            logger.info(msg)
            if logger_callback: logger_callback(msg)
            await rate_limiter.human_delay(1.2)
            return True
    except Exception as e:
        logger.error(f"Error executing do_follow for @{target_user}: {e}")

    return False
