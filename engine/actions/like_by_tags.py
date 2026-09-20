"""
like_by_tags: Discovers posts by searching hashtags and likes the target posts.
Supports skipping 'Top Posts' grid to only target 'Recent Posts' and randomizing choices.
"""

import random
import logging
import asyncio
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.like_by_tags")

async def like_by_tags(page: Page, rate_limiter: RateLimiter, tags: List[str], amount: int = 10, skip_top_posts: bool = True, randomize: bool = True, logger_callback=None) -> Dict[str, Any]:
    """
    Search hashtags, gather posts, and like them.
    """
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}
    
    if not tags:
        logger.warning("No tags provided for like_by_tags.")
        return results

    if randomize:
        random.shuffle(tags)

    per_tag_amount = max(1, amount // len(tags))
    
    for tag in tags:
        if results["success"] >= amount:
            break
            
        msg = f"Targeting tag: #{tag} for {per_tag_amount} likes"
        logger.info(msg)
        if logger_callback:
            logger_callback(msg)

        post_urls = await InstagramScraper.get_tag_posts(page, tag, amount=per_tag_amount * 2, skip_top_posts=skip_top_posts)
        
        if randomize:
            random.shuffle(post_urls)

        for post_url in post_urls:
            if results["success"] >= amount:
                break

            try:
                await page.goto(post_url, wait_until="domcontentloaded")
                await rate_limiter.human_delay(0.5)

                # Find like button (Heart icon)
                like_btn = await page.query_selector("svg[aria-label='Like']:not([height='12'])")
                unlike_btn = await page.query_selector("svg[aria-label='Unlike']")

                if unlike_btn:
                    msg = f"Already liked post: {post_url}"
                    logger.info(msg)
                    if logger_callback:
                        logger_callback(msg)
                    results["skipped"] += 1
                    continue

                if like_btn:
                    # Click parent button element
                    btn_wrapper = await page.evaluate_handle("el => el.closest('button') || el.parentElement", like_btn)
                    if btn_wrapper:
                        await btn_wrapper.click()
                        results["success"] += 1
                        rate_limiter.record_action("like")
                        msg = f"Successfully liked post: {post_url}"
                        logger.info(msg)
                        if logger_callback:
                            logger_callback(msg)
                        results["details"].append({"target": post_url, "status": "success", "action": "like"})
                        await rate_limiter.human_delay(1.0)
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error liking post {post_url}: {e}")
                results["failed"] += 1
                results["details"].append({"target": post_url, "status": "failed", "details": str(e)})

    return results
