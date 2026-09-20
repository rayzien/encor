"""
follow_by_list: Takes a pre-defined list of usernames (e.g. from file/config) and follows them with customized delays and interactions.
"""

import logging
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.scraper import InstagramScraper
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.follow_by_list")

async def follow_by_list(page: Page, rate_limiter: RateLimiter, followlist: List[str], times: int = 1, sleep_delay: float = 3.0, interact: bool = False, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}

    if not followlist:
        return results

    for iteration in range(times):
        for raw_user in followlist:
            user = raw_user.lstrip("@").strip()
            if not user:
                continue

            try:
                user_url = f"https://www.instagram.com/{user}/"
                await page.goto(user_url, wait_until="domcontentloaded")
                await rate_limiter.human_delay(sleep_delay / 3.0)

                follow_btn = await page.query_selector("button:has-text('Follow'):not(:has-text('Following'))")
                following_btn = await page.query_selector("button:has-text('Following')")

                if following_btn:
                    results["skipped"] += 1
                    continue

                if follow_btn:
                    await follow_btn.click()
                    results["success"] += 1
                    rate_limiter.record_action("follow")
                    msg = f"Followed custom list user: @{user}"
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
                    await rate_limiter.human_delay(sleep_delay / 2.0)
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error following list user @{user}: {e}")
                results["failed"] += 1

    return results
