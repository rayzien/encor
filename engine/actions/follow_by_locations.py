"""
follow_by_locations: Follows authors who posted at specific geotags or locations.
"""

import logging
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.follow_by_locations")

async def follow_by_locations(page: Page, rate_limiter: RateLimiter, locations: List[str], amount: int = 10, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}
    
    if not locations:
        return results

    per_loc = max(1, amount // len(locations))

    for loc in locations:
        if results["success"] >= amount:
            break

        msg = f"Following post authors at location: {loc}"
        logger.info(msg)
        if logger_callback: logger_callback(msg)

        post_urls = await InstagramScraper.get_location_posts(page, loc, amount=per_loc * 2, skip_top_posts=True)

        for post_url in post_urls:
            if results["success"] >= amount:
                break

            try:
                await page.goto(post_url, wait_until="domcontentloaded")
                await rate_limiter.human_delay(0.5)

                follow_btn = await page.query_selector("button:has-text('Follow'):not(:has-text('Following'))")
                following_btn = await page.query_selector("button:has-text('Following')")

                if following_btn:
                    results["skipped"] += 1
                    continue

                if follow_btn:
                    await follow_btn.click()
                    results["success"] += 1
                    rate_limiter.record_action("follow")
                    msg = f"Followed author of geotagged post: {post_url}"
                    logger.info(msg)
                    if logger_callback: logger_callback(msg)
                    results["details"].append({"target": post_url, "status": "success", "action": "follow"})
                    await rate_limiter.human_delay(1.2)
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error following geotag author {post_url}: {e}")
                results["failed"] += 1

    return results
