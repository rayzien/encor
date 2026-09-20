"""
Reusable Instagram DOM scraper utilities for hashtags, locations, followers, following, feed, and profiles.
"""

import asyncio
import logging
import re
from typing import List, Dict, Any
from playwright.async_api import Page

logger = logging.getLogger("encor.scraper")

class InstagramScraper:
    @staticmethod
    async def get_tag_posts(page: Page, tag: str, amount: int = 10, skip_top_posts: bool = True) -> List[str]:
        """Discover post URLs for a given hashtag."""
        clean_tag = tag.lstrip("#").strip()
        url = f"https://www.instagram.com/explore/tags/{clean_tag}/"
        logger.info(f"Navigating to hashtag: #{clean_tag} ({url})")
        
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        post_links = []
        scroll_attempts = 0
        
        while len(post_links) < amount and scroll_attempts < 10:
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll("a[href*='/p/'], a[href*='/reel/']"))
                           .map(a => a.href)
            """)
            
            # Deduplicate
            for link in links:
                if link not in post_links:
                    post_links.append(link)
            
            if len(post_links) >= amount:
                break
                
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(2)
            scroll_attempts += 1

        if skip_top_posts and len(post_links) > 9:
            # First 9 items on tag page are typically Top Posts grid
            logger.info("Skipping top 9 posts...")
            post_links = post_links[9:]

        return post_links[:amount]

    @staticmethod
    async def get_location_posts(page: Page, location: str, amount: int = 10, skip_top_posts: bool = True) -> List[str]:
        """Discover post URLs geotagged at a location ID/place."""
        clean_location = location.strip()
        url = f"https://www.instagram.com/explore/locations/{clean_location}/" if clean_location.isdigit() else f"https://www.instagram.com/explore/search/?q={clean_location}"
        logger.info(f"Navigating to location: {clean_location}")
        
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        post_links = []
        scroll_attempts = 0
        
        while len(post_links) < amount and scroll_attempts < 10:
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll("a[href*='/p/'], a[href*='/reel/']"))
                           .map(a => a.href)
            """)
            
            for link in links:
                if link not in post_links:
                    post_links.append(link)
            
            if len(post_links) >= amount:
                break
                
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(2)
            scroll_attempts += 1

        if skip_top_posts and len(post_links) > 9:
            post_links = post_links[9:]

        return post_links[:amount]

    @staticmethod
    async def get_user_followers(page: Page, target_user: str, amount: int = 20) -> List[str]:
        """Scrape follower usernames of a target account."""
        clean_user = target_user.lstrip("@").strip()
        url = f"https://www.instagram.com/{clean_user}/"
        logger.info(f"Scraping followers of @{clean_user}")
        
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Click on followers link
        followers_link = await page.query_selector(f"a[href*='/{clean_user}/followers/']")
        if not followers_link:
            logger.warning(f"Could not find followers link for @{clean_user}")
            return []
            
        await followers_link.click()
        await asyncio.sleep(3)
        
        followers = []
        scroll_attempts = 0
        
        while len(followers) < amount and scroll_attempts < 15:
            users = await page.evaluate("""
                () => {
                    const dialog = document.querySelector("div[role='dialog']");
                    if (!dialog) return [];
                    const links = Array.from(dialog.querySelectorAll("a[href^='/']"));
                    return links.map(a => a.getAttribute('href').replace(/\\//g, ''))
                                .filter(u => u && !['explore', 'reels', 'direct', 'stories'].includes(u));
                }
            """)
            
            for u in users:
                if u and u not in followers and u != clean_user:
                    followers.append(u)
                    
            if len(followers) >= amount:
                break
                
            # Scroll dialog container
            await page.evaluate("""
                () => {
                    const dialog = document.querySelector("div[role='dialog'] ul") || document.querySelector("div[role='dialog']");
                    if (dialog) dialog.scrollTop += 500;
                }
            """)
            await asyncio.sleep(1.5)
            scroll_attempts += 1

        return followers[:amount]

    @staticmethod
    async def get_user_following(page: Page, target_user: str, amount: int = 20) -> List[str]:
        """Scrape following usernames of a target account."""
        clean_user = target_user.lstrip("@").strip()
        url = f"https://www.instagram.com/{clean_user}/"
        logger.info(f"Scraping following of @{clean_user}")
        
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        following_link = await page.query_selector(f"a[href*='/{clean_user}/following/']")
        if not following_link:
            logger.warning(f"Could not find following link for @{clean_user}")
            return []
            
        await following_link.click()
        await asyncio.sleep(3)
        
        following = []
        scroll_attempts = 0
        
        while len(following) < amount and scroll_attempts < 15:
            users = await page.evaluate("""
                () => {
                    const dialog = document.querySelector("div[role='dialog']");
                    if (!dialog) return [];
                    const links = Array.from(dialog.querySelectorAll("a[href^='/']"));
                    return links.map(a => a.getAttribute('href').replace(/\\//g, ''))
                                .filter(u => u && !['explore', 'reels', 'direct', 'stories'].includes(u));
                }
            """)
            
            for u in users:
                if u and u not in following and u != clean_user:
                    following.append(u)
                    
            if len(following) >= amount:
                break
                
            await page.evaluate("""
                () => {
                    const dialog = document.querySelector("div[role='dialog'] ul") || document.querySelector("div[role='dialog']");
                    if (dialog) dialog.scrollTop += 500;
                }
            """)
            await asyncio.sleep(1.5)
            scroll_attempts += 1

        return following[:amount]

    @staticmethod
    async def get_feed_posts(page: Page, amount: int = 10) -> List[str]:
        """Extract post URLs from the current home feed."""
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        post_links = []
        scroll_attempts = 0
        
        while len(post_links) < amount and scroll_attempts < 10:
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll("article a[href*='/p/'], article a[href*='/reel/']"))
                           .map(a => a.href)
            """)
            
            for link in links:
                if link not in post_links:
                    post_links.append(link)
                    
            if len(post_links) >= amount:
                break
                
            await page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(2)
            scroll_attempts += 1

        return post_links[:amount]

    @staticmethod
    async def get_user_recent_posts(page: Page, username: str, amount: int = 3) -> List[str]:
        """Get recent post links from a user's profile page."""
        clean_user = username.lstrip("@").strip()
        url = f"https://www.instagram.com/{clean_user}/"
        logger.info(f"Getting recent posts for @{clean_user}")
        
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2.5)
        
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll("a[href*='/p/'], a[href*='/reel/']"))
                       .map(a => a.href)
        """)
        
        unique = []
        for l in links:
            if l not in unique:
                unique.append(l)
                
        return unique[:amount]
