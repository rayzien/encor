"""
Session manager for Instagram login and authentication.
"""

import json
import logging
import asyncio
from playwright.async_api import Page, BrowserContext

logger = logging.getLogger("encor.session")

class SessionManager:
    @staticmethod
    async def is_logged_in(page: Page) -> bool:
        """Check if current page is logged into Instagram."""
        try:
            # Check for home feed icon, profile icon, or search input
            await page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
            
            # Look for nav elements or profile icon
            nav_element = await page.query_selector("svg[aria-label='Home'], svg[aria-label='Direct'], a[href*='/accounts/edit/']")
            login_form = await page.query_selector("input[name='username']")
            
            if nav_element and not login_form:
                return True
            return False
        except Exception as e:
            logger.warning(f"Error checking login state: {e}")
            return False

    @staticmethod
    async def login(page: Page, context: BrowserContext, username: str, password: str) -> bool:
        """Perform login on Instagram and return extracted cookies."""
        logger.info(f"Attempting login for user: {username}")
        await page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
        await asyncio.sleep(2)

        # Accept cookies pop-up if present
        try:
            cookie_btn = await page.query_selector("button:has-text('Allow all cookies'), button:has-text('Accept All')")
            if cookie_btn:
                await cookie_btn.click()
                await asyncio.sleep(1)
        except Exception:
            pass

        # Fill credentials
        username_input = await page.query_selector("input[name='username']")
        password_input = await page.query_selector("input[name='password']")

        if not username_input or not password_input:
            logger.error("Login inputs not found on page.")
            return False

        await username_input.fill(username)
        await password_input.fill(password)
        
        login_btn = await page.query_selector("button[type='submit']")
        if login_btn:
            await login_btn.click()
        
        await asyncio.sleep(5)

        # Check for 'Not Now' save info buttons
        try:
            not_now = await page.query_selector("button:has-text('Not Now'), div[role='button']:has-text('Not Now')")
            if not_now:
                await not_now.click()
                await asyncio.sleep(2)
        except Exception:
            pass

        # Verify login success
        if await SessionManager.is_logged_in(page):
            logger.info(f"Login successful for {username}")
            cookies = await context.cookies()
            return cookies
        else:
            logger.error(f"Login failed for {username}. Check credentials or challenge.")
            return None
