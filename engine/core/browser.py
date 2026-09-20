"""
Browser manager module using Playwright.
Handles launching browsers in headed or headless mode, page context creation, and human-like interactions.
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import os
import json
import logging

logger = logging.getLogger("encor.browser")

class BrowserManager:
    def __init__(self, headless: bool = False, slow_mo: int = 100):
        """
        :param headless: If False, runs in visible browser window (great for debugging).
        :param slow_mo: Delay in ms between operations to mimic human typing/clicking.
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser: Browser = None

    async def start(self):
        """Launch playwright browser instance."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            logger.info(f"Browser launched (headless={self.headless}).")

    async def create_context(self, cookies: list = None) -> BrowserContext:
        """Create an isolated browser context with user agent and optional saved cookies."""
        if not self.browser:
            await self.start()
            
        context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US"
        )
        
        if cookies:
            await context.add_cookies(cookies)
            logger.info("Loaded session cookies into context.")
            
        return context

    async def close(self):
        """Close browser instance."""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        logger.info("Browser closed.")
