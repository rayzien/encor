"""
like_by_feed: Scrolls through home feed and likes posts.
"""

import random
import logging
from typing import Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.like_by_feed")

async def like_by_feed(page: Page, rate_limiter: RateLimiter, amount: int = 10, randomize: bool = True, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}

    msg = f"Fetching home feed posts for {amount} likes"
    logger.info(msg)
    if logger_callback: logger_callback(msg)

    feed_posts = await InstagramScraper.get_feed_posts(page, amount=amount * 2)

    if randomize:
        random.shuffle(feed_posts)

    for post_url in feed_posts:
        if results["success"] >= amount:
            break

        try:
            await page.goto(post_url, wait_until="domcontentloaded")
            await rate_limiter.human_delay(0.5)

            like_btn = await page.query_selector("svg[aria-label='Like']:not([height='12'])")
            unlike_btn = await page.query_selector("svg[aria-label='Unlike']")

            if unlike_btn:
                results["skipped"] += 1
                continue

            if like_btn:
                btn_wrapper = await page.evaluate_handle("el => el.closest('button') || el.parentElement", like_btn)
                if btn_wrapper:
                    await btn_wrapper.click()
                    results["success"] += 1
                    rate_limiter.record_action("like")
                    msg = f"Liked feed post: {post_url}"
                    logger.info(msg)
                    if logger_callback: logger_callback(msg)
                    results["details"].append({"target": post_url, "status": "success", "action": "like"})
                    await rate_limiter.human_delay(1.0)
            else:
                results["skipped"] += 1
        except Exception as e:
            logger.error(f"Error liking feed post {post_url}: {e}")
            results["failed"] += 1

    return results
