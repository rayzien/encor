"""
Specialized engagement action: user_interact.
Interacts with multiple photos/videos when visiting a target user's profile.
"""

import random
import logging
from playwright.async_api import Page
from engine.engagement.rules import EngagementRulesContainer
from engine.engagement.filters import EngagementFilters
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.engagement.user_interact")

async def execute_user_interact(page: Page, rate_limiter: RateLimiter, rules: EngagementRulesContainer, target_user: str, logger_callback=None) -> int:
    """
    Navigates to profile, scrapes up to rules.user_interact_amount posts, and likes/interacts with them.
    """
    if rules.user_interact_amount <= 0:
        return 0

    if not EngagementFilters.probability_roll(rules.user_interact_percentage):
        msg = f"Skipped user interact for @{target_user} due to probability roll ({rules.user_interact_percentage}%)"
        logger.info(msg)
        if logger_callback: logger_callback(msg)
        return 0

    interacted_count = 0
    try:
        posts = await InstagramScraper.get_user_recent_posts(page, target_user, amount=rules.user_interact_amount * 2)

        if rules.user_interact_randomize:
            random.shuffle(posts)

        target_posts = posts[:rules.user_interact_amount]

        for post_url in target_posts:
            await page.goto(post_url, wait_until="domcontentloaded")
            await rate_limiter.human_delay(0.5)

            # Extract post info
            likes, comments, media_type = await EngagementFilters.extract_post_stats(page)

            # Filter by media type if configured
            if rules.user_interact_media != "Any" and rules.user_interact_media != media_type:
                msg = f"Skipping post {post_url}: Media type ({media_type}) != required ({rules.user_interact_media})"
                logger.info(msg)
                if logger_callback: logger_callback(msg)
                continue

            # Check bounds
            if not EngagementFilters.is_liking_delimited(likes, rules.delimit_liking_min, rules.delimit_liking_max):
                continue

            like_btn = await page.query_selector("svg[aria-label='Like']:not([height='12'])")
            if like_btn:
                btn_wrapper = await page.evaluate_handle("el => el.closest('button') || el.parentElement", like_btn)
                if btn_wrapper:
                    await btn_wrapper.click()
                    interacted_count += 1
                    rate_limiter.record_action("like")
                    msg = f"Deep interaction: Liked post {post_url} of @{target_user}"
                    logger.info(msg)
                    if logger_callback: logger_callback(msg)
                    await rate_limiter.human_delay(1.0)

    except Exception as e:
        logger.error(f"Error executing user_interact for @{target_user}: {e}")

    return interacted_count
