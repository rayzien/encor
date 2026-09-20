"""
interact_user_following: Scrapes following list of a target account and likes their recent posts without following.
"""

import random
import logging
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.interact_user_following")

async def interact_user_following(page: Page, rate_limiter: RateLimiter, usernames: List[str], amount: int = 10, randomize: bool = True, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}

    if not usernames:
        return results

    if randomize:
        random.shuffle(usernames)

    per_target = max(1, amount // len(usernames))

    for target_user in usernames:
        if results["success"] >= amount:
            break

        msg = f"Fetching following of @{target_user} to interact"
        logger.info(msg)
        if logger_callback: logger_callback(msg)

        following_list = await InstagramScraper.get_user_following(page, target_user, amount=per_target * 2)

        if randomize:
            random.shuffle(following_list)

        for user in following_list:
            if results["success"] >= amount:
                break

            try:
                posts = await InstagramScraper.get_user_recent_posts(page, user, amount=1)
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
                            msg = f"Liked post of following @{user}"
                            logger.info(msg)
                            if logger_callback: logger_callback(msg)
                            results["details"].append({"target": user, "status": "success", "action": "interact_like"})
                            await rate_limiter.human_delay(1.0)
                    else:
                        results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error interacting with following user @{user}: {e}")
                results["failed"] += 1

    return results
