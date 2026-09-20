"""
Specialized engagement action: do_story.
Views user active stories during profile interaction workflows.
"""

import logging
import asyncio
from playwright.async_api import Page
from engine.engagement.rules import EngagementRulesContainer
from engine.engagement.filters import EngagementFilters
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.engagement.do_story")

async def execute_do_story(page: Page, rate_limiter: RateLimiter, rules: EngagementRulesContainer, target_user: str, logger_callback=None) -> bool:
    """
    Checks if story viewing is enabled, navigates to user story, and simulates watching.
    """
    if not rules.do_story_enabled:
        return False

    if not EngagementFilters.probability_roll(rules.do_story_percentage):
        msg = f"Skipped story view for @{target_user} due to probability roll ({rules.do_story_percentage}%)"
        logger.info(msg)
        if logger_callback: logger_callback(msg)
        return False

    try:
        url = f"https://www.instagram.com/stories/{target_user}/"
        msg = f"Simulating story view for @{target_user}"
        logger.info(msg)
        if logger_callback: logger_callback(msg)

        await page.goto(url, wait_until="domcontentloaded")
        await rate_limiter.human_delay(2.0)

        if "stories" in page.url:
            rate_limiter.record_action("story_view")
            await asyncio.sleep(4.0)  # Simulate story viewing
            msg = f"Completed story view for @{target_user}"
            logger.info(msg)
            if logger_callback: logger_callback(msg)
            return True
        else:
            msg = f"No active story found for @{target_user}"
            logger.info(msg)
            if logger_callback: logger_callback(msg)
            return False
    except Exception as e:
        logger.error(f"Error executing do_story for @{target_user}: {e}")

    return False
