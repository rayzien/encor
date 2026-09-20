"""
interact_by_users: Navigates directly to a target list of users' profiles and likes their recent posts without following.
"""

import random
import logging
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.interact_by_users")

async def interact_by_users(page: Page, rate_limiter: RateLimiter, usernames: List[str], amount: int = 1, randomize: bool = True, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}

    if not usernames:
        return results

    if randomize:
        random.shuffle(usernames)

    for raw_user in usernames:
        user = raw_user.lstrip("@").strip()
        if not user:
            continue

        msg = f"Interacting with target user @{user}"
        logger.info(msg)
        if logger_callback: logger_callback(msg)

        try:
            posts = await InstagramScraper.get_user_recent_posts(page, user, amount=amount)
            if not posts:
                results["skipped"] += 1
                continue

            for post_url in posts:
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
                        msg = f"Liked recent post of @{user}: {post_url}"
                        logger.info(msg)
                        if logger_callback: logger_callback(msg)
                        results["details"].append({"target": user, "status": "success", "action": "interact_like"})
                        await rate_limiter.human_delay(1.0)
                else:
                    results["skipped"] += 1
        except Exception as e:
            logger.error(f"Error interacting with @{user}: {e}")
            results["failed"] += 1

    return results
