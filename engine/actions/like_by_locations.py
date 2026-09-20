"""
like_by_locations: Targets posts geotagged at specific location IDs / places on Instagram.
"""

import random
import logging
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.like_by_locations")

async def like_by_locations(page: Page, rate_limiter: RateLimiter, locations: List[str], amount: int = 10, skip_top_posts: bool = True, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}
    
    if not locations:
        return results

    per_loc = max(1, amount // len(locations))

    for loc in locations:
        if results["success"] >= amount:
            break

        msg = f"Targeting location: {loc}"
        logger.info(msg)
        if logger_callback: logger_callback(msg)

        post_urls = await InstagramScraper.get_location_posts(page, loc, amount=per_loc * 2, skip_top_posts=skip_top_posts)

        for post_url in post_urls:
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
                        msg = f"Liked post at location {loc}: {post_url}"
                        logger.info(msg)
                        if logger_callback: logger_callback(msg)
                        results["details"].append({"target": post_url, "status": "success", "action": "like"})
                        await rate_limiter.human_delay(1.0)
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error liking location post {post_url}: {e}")
                results["failed"] += 1

    return results
