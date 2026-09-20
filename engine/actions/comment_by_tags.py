"""
comment_by_tags: Discovers posts under hashtags and leaves randomized comments from a pre-set list.
"""

import random
import logging
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.comment_by_tags")

async def comment_by_tags(page: Page, rate_limiter: RateLimiter, tags: List[str], comments: List[str], amount: int = 5, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}

    if not tags or not comments:
        return results

    per_tag = max(1, amount // len(tags))

    for tag in tags:
        if results["success"] >= amount:
            break

        msg = f"Commenting on posts under #{tag}"
        logger.info(msg)
        if logger_callback: logger_callback(msg)

        post_urls = await InstagramScraper.get_tag_posts(page, tag, amount=per_tag * 2, skip_top_posts=True)

        for post_url in post_urls:
            if results["success"] >= amount:
                break

            try:
                await page.goto(post_url, wait_until="domcontentloaded")
                await rate_limiter.human_delay(1.0)

                comment_textarea = await page.query_selector("textarea[aria-label*='comment'], textarea[placeholder*='comment']")

                if comment_textarea:
                    selected_comment = random.choice(comments)
                    await comment_textarea.fill(selected_comment)
                    await rate_limiter.human_delay(0.5)

                    post_btn = await page.query_selector("button:has-text('Post'), div[role='button']:has-text('Post')")
                    if post_btn:
                        await post_btn.click()
                        results["success"] += 1
                        rate_limiter.record_action("comment")
                        msg = f"Commented on {post_url}: '{selected_comment}'"
                        logger.info(msg)
                        if logger_callback: logger_callback(msg)
                        results["details"].append({"target": post_url, "status": "success", "action": "comment", "details": selected_comment})
                        await rate_limiter.human_delay(3.0)
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error commenting on post {post_url}: {e}")
                results["failed"] += 1

    return results
