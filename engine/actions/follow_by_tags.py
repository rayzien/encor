"""
follow_by_tags: Finds posts under specific hashtags and follows the authors of those posts.
"""

import random
import logging
import asyncio
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.follow_by_tags")

async def follow_by_tags(page: Page, rate_limiter: RateLimiter, tags: List[str], amount: int = 10, randomize: bool = True, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}
    
    if not tags:
        return results

    if randomize:
        random.shuffle(tags)

    per_tag_amount = max(1, amount // len(tags))

    for tag in tags:
        if results["success"] >= amount:
            break

        msg = f"Finding post authors under #{tag}"
        logger.info(msg)
        if logger_callback: logger_callback(msg)

        post_urls = await InstagramScraper.get_tag_posts(page, tag, amount=per_tag_amount * 2, skip_top_posts=True)
        if randomize:
            random.shuffle(post_urls)

        for post_url in post_urls:
            if results["success"] >= amount:
                break

            try:
                await page.goto(post_url, wait_until="domcontentloaded")
                await rate_limiter.human_delay(0.5)

                # Look for author username & follow button in post modal / page
                follow_btn = await page.query_selector("button:has-text('Follow'):not(:has-text('Following'))")
                following_btn = await page.query_selector("button:has-text('Following')")

                if following_btn:
                    msg = f"Already following author of {post_url}"
                    logger.info(msg)
                    if logger_callback: logger_callback(msg)
                    results["skipped"] += 1
                    continue

                if follow_btn:
                    await follow_btn.click()
                    results["success"] += 1
                    rate_limiter.record_action("follow")
                    msg = f"Successfully followed author of {post_url}"
                    logger.info(msg)
                    if logger_callback: logger_callback(msg)
                    results["details"].append({"target": post_url, "status": "success", "action": "follow"})
                    await rate_limiter.human_delay(1.2)
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error following author of {post_url}: {e}")
                results["failed"] += 1
                results["details"].append({"target": post_url, "status": "failed", "details": str(e)})

    return results
