"""
Specialized engagement action: do_comment + set_comments (spintax) + delimit_commenting.
"""

import random
import logging
from playwright.async_api import Page
from engine.engagement.rules import EngagementRulesContainer
from engine.engagement.filters import EngagementFilters
from engine.engagement.spintax import SpintaxParser
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.engagement.do_comment")

async def execute_do_comment(page: Page, rate_limiter: RateLimiter, rules: EngagementRulesContainer, post_url: str, comment_count: int, logger_callback=None) -> bool:
    """
    Evaluates commenting rules, checks comment bounds, spins spintax comments, and posts comments.
    """
    if not rules.do_comment_enabled or not rules.comments_spintax:
        return False

    if not EngagementFilters.probability_roll(rules.do_comment_percentage):
        msg = f"Skipped comment on {post_url} due to probability roll ({rules.do_comment_percentage}%)"
        logger.info(msg)
        if logger_callback: logger_callback(msg)
        return False

    if not EngagementFilters.is_commenting_delimited(comment_count, rules.delimit_commenting_min, rules.delimit_commenting_max):
        msg = f"Skipped comment on {post_url}: comments ({comment_count}) outside bounds [{rules.delimit_commenting_min}, {rules.delimit_commenting_max}]"
        logger.info(msg)
        if logger_callback: logger_callback(msg)
        return False

    try:
        comment_textarea = await page.query_selector("textarea[aria-label*='comment'], textarea[placeholder*='comment']")

        if comment_textarea:
            raw_spintax = random.choice(rules.comments_spintax)
            spun_comment = SpintaxParser.spin(raw_spintax)

            await comment_textarea.fill(spun_comment)
            await rate_limiter.human_delay(0.5)

            post_btn = await page.query_selector("button:has-text('Post'), div[role='button']:has-text('Post')")
            if post_btn:
                await post_btn.click()
                rate_limiter.record_action("comment")
                msg = f"Commented on {post_url}: '{spun_comment}'"
                logger.info(msg)
                if logger_callback: logger_callback(msg)
                await rate_limiter.human_delay(3.0)
                return True
    except Exception as e:
        logger.error(f"Error executing do_comment on {post_url}: {e}")

    return False
