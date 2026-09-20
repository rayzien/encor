"""
Engagement criteria filters for like/comment delimit bounds, media detection, and probability checks.
"""

import random
import logging
from typing import Optional, Tuple
from playwright.async_api import Page

logger = logging.getLogger("encor.engagement.filters")

class EngagementFilters:
    @staticmethod
    def probability_roll(percentage: int) -> bool:
        """Return True if random 1-100 roll is <= percentage."""
        if percentage >= 100:
            return True
        if percentage <= 0:
            return False
        return random.randint(1, 100) <= percentage

    @staticmethod
    async def extract_post_stats(page: Page) -> Tuple[int, int, str]:
        """
        Extract (likes_count, comments_count, media_type) from post page.
        """
        try:
            # Scrape likes count
            likes = await page.evaluate("""
                () => {
                    const likeEl = document.querySelector("a[href*='/liked_by/'] span, section span:has-text('likes')");
                    if (!likeEl) return 0;
                    const txt = likeEl.innerText.replace(/[^0-9]/g, '');
                    return parseInt(txt) || 0;
                }
            """)
            
            # Scrape comments count
            comments = await page.evaluate("""
                () => {
                    const commentEls = document.querySelectorAll("ul article, ul li[role='menuitem']");
                    return commentEls ? commentEls.length : 0;
                }
            """)

            # Detect media type (Video/Reel vs Photo)
            is_video = await page.query_selector("video, svg[aria-label='Clip'], svg[aria-label='Reel']")
            media_type = "Video" if is_video else "Photo"

            return likes, comments, media_type
        except Exception as e:
            logger.warning(f"Error extracting post stats: {e}")
            return 0, 0, "Photo"

    @staticmethod
    def is_liking_delimited(like_count: int, min_likes: int, max_likes: int) -> bool:
        """Return True if post like count falls within allowed bounds."""
        if min_likes is not None and like_count < min_likes:
            logger.info(f"Post skipped: like_count ({like_count}) < min_likes ({min_likes})")
            return False
        if max_likes is not None and max_likes > 0 and like_count > max_likes:
            logger.info(f"Post skipped: like_count ({like_count}) > max_likes ({max_likes})")
            return False
        return True

    @staticmethod
    def is_commenting_delimited(comment_count: int, min_comments: int, max_comments: int) -> bool:
        """Return True if post comment count falls within allowed bounds."""
        if min_comments is not None and comment_count < min_comments:
            logger.info(f"Post skipped: comment_count ({comment_count}) < min_comments ({min_comments})")
            return False
        if max_comments is not None and max_comments > 0 and comment_count > max_comments:
            logger.info(f"Post skipped: comment_count ({comment_count}) > max_comments ({max_comments})")
            return False
        return True
