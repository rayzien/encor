"""
follow_user_following: Scrapes the following list of a target account and follows them.
Optionally interacts (likes recent posts) with each followed user.
"""

import random
import logging
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.follow_user_following")

async def follow_user_following(page: Page, rate_limiter: RateLimiter, usernames: List[str], amount: int = 10, randomize: bool = True, interact: bool = False, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}

    if not usernames:
        return results

    if randomize:
        random.shuffle(usernames)

    per_target = max(1, amount // len(usernames))

    for target_user in usernames:
        if results["success"] >= amount:
            break

        msg = f"Fetching following list of @{target_user}"
        logger.info(msg)
        if logger_callback: logger_callback(msg)

        following_list = await InstagramScraper.get_user_following(page, target_user, amount=per_target * 2)

        if randomize:
            random.shuffle(following_list)

        for user in following_list:
            if results["success"] >= amount:
                break

            try:
                user_url = f"https://www.instagram.com/{user}/"
                await page.goto(user_url, wait_until="domcontentloaded")
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
                    msg = f"Followed @{user} (following of @{target_user})"
                    logger.info(msg)
                    if logger_callback: logger_callback(msg)

                    if interact:
                        posts = await InstagramScraper.get_user_recent_posts(page, user, amount=1)
                        if posts:
                            await page.goto(posts[0], wait_until="domcontentloaded")
                            like_btn = await page.query_selector("svg[aria-label='Like']:not([height='12'])")
                            if like_btn:
                                btn_wrapper = await page.evaluate_handle("el => el.closest('button') || el.parentElement", like_btn)
                                if btn_wrapper:
                                    await btn_wrapper.click()
                                    rate_limiter.record_action("like")

                    results["details"].append({"target": user, "status": "success", "action": "follow"})
                    await rate_limiter.human_delay(1.5)
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error following @{user}: {e}")
                results["failed"] += 1

    return results
