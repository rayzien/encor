"""
story_viewer: Views stories of target users to increase visibility and engagement.
"""

import logging
import asyncio
from typing import List, Dict, Any
from playwright.async_api import Page
from engine.core.rate_limiter import RateLimiter

logger = logging.getLogger("encor.actions.story_viewer")

async def story_viewer(page: Page, rate_limiter: RateLimiter, target_users: List[str], amount: int = 10, logger_callback=None) -> Dict[str, Any]:
    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}

    if not target_users:
        return results

    for raw_user in target_users:
        if results["success"] >= amount:
            break

        user = raw_user.lstrip("@").strip()
        if not user:
            continue

        try:
            url = f"https://www.instagram.com/stories/{user}/"
            msg = f"Viewing stories of @{user}"
            logger.info(msg)
            if logger_callback: logger_callback(msg)

            await page.goto(url, wait_until="domcontentloaded")
            await rate_limiter.human_delay(2.0)

            # Check if story exists or redirected
            if "stories" in page.url:
                results["success"] += 1
                rate_limiter.record_action("story_view")
                results["details"].append({"target": user, "status": "success", "action": "story_view"})
                # Wait 5 seconds to simulate viewing story
                await asyncio.sleep(5)
            else:
                msg = f"No active story for @{user}"
                logger.info(msg)
                if logger_callback: logger_callback(msg)
                results["skipped"] += 1
        except Exception as e:
            logger.error(f"Error viewing story for @{user}: {e}")
            results["failed"] += 1

    return results
