"""
Central Task Runner engine for Encor.
Dispatches automation tasks to their respective action modules, manages browser lifecycle, and updates DB status and logs.
"""

import json
import logging
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from database import SessionLocal, AutomationTask, Account, TaskLog
from engine.core.browser import BrowserManager
from engine.core.session import SessionManager
from engine.core.rate_limiter import RateLimiter

# Import action modules
from engine.actions.like_by_tags import like_by_tags
from engine.actions.follow_by_tags import follow_by_tags
from engine.actions.like_by_locations import like_by_locations
from engine.actions.follow_by_locations import follow_by_locations
from engine.actions.follow_user_followers import follow_user_followers
from engine.actions.follow_user_following import follow_user_following
from engine.actions.follow_by_list import follow_by_list
from engine.actions.interact_by_users import interact_by_users
from engine.actions.interact_user_followers import interact_user_followers
from engine.actions.interact_user_following import interact_user_following
from engine.actions.like_by_feed import like_by_feed
from engine.actions.story_viewer import story_viewer
from engine.actions.comment_by_tags import comment_by_tags

logger = logging.getLogger("encor.task_runner")

async def execute_task(task_id: int):
    """
    Main asynchronous worker function to execute a task by ID.
    """
    db: Session = SessionLocal()
    try:
        task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
        if not task:
            logger.error(f"Task ID {task_id} not found.")
            return

        task.status = "running"
        task.updated_at = datetime.utcnow()
        db.commit()

        account = db.query(Account).filter(Account.id == task.account_id).first() if task.account_id else None
        
        # Parse task config
        config = json.loads(task.config_json or "{}")
        headless_mode = config.get("headless", False) # False allows visible window for easy debugging

        def log_callback(msg: str):
            logger.info(f"[Task {task_id}] {msg}")
            # Append log to task in DB
            task.log_output = (task.log_output or "") + f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] {msg}"
            db.commit()

        log_callback(f"Starting execution for task type: '{task.task_type}'")

        browser_mgr = BrowserManager(headless=headless_mode)
        await browser_mgr.start()

        cookies = json.loads(account.cookies_json) if account and account.cookies_json else None
        context = await browser_mgr.create_context(cookies=cookies)
        page = await context.new_page()

        # Handle login if credentials exist
        if account and account.username and account.password:
            logged_in = await SessionManager.is_logged_in(page)
            if not logged_in:
                log_callback(f"Authenticating account @{account.username}...")
                new_cookies = await SessionManager.login(page, context, account.username, account.password)
                if new_cookies:
                    account.cookies_json = json.dumps(new_cookies)
                    db.commit()
                    log_callback(f"Login successful. Cookies saved.")
                else:
                    log_callback("Authentication failed.")
                    task.status = "failed"
                    db.commit()
                    await browser_mgr.close()
                    return

        rate_limiter = RateLimiter(delay_min=config.get("delay_min", 3.0), delay_max=config.get("delay_max", 8.0))

        # Dispatch action based on task_type
        task_type = task.task_type
        amount = config.get("amount", 10)
        randomize = config.get("randomize", True)

        res = {"success": 0, "skipped": 0, "failed": 0, "details": []}

        if task_type == "like_by_tags":
            tags = config.get("tags", [])
            skip_top = config.get("skip_top_posts", True)
            res = await like_by_tags(page, rate_limiter, tags, amount=amount, skip_top_posts=skip_top, randomize=randomize, logger_callback=log_callback)

        elif task_type == "follow_by_tags":
            tags = config.get("tags", [])
            res = await follow_by_tags(page, rate_limiter, tags, amount=amount, randomize=randomize, logger_callback=log_callback)

        elif task_type == "like_by_locations":
            locations = config.get("locations", [])
            skip_top = config.get("skip_top_posts", True)
            res = await like_by_locations(page, rate_limiter, locations, amount=amount, skip_top_posts=skip_top, logger_callback=log_callback)

        elif task_type == "follow_by_locations":
            locations = config.get("locations", [])
            res = await follow_by_locations(page, rate_limiter, locations, amount=amount, logger_callback=log_callback)

        elif task_type == "follow_user_followers":
            usernames = config.get("usernames", [])
            interact = config.get("interact", False)
            res = await follow_user_followers(page, rate_limiter, usernames, amount=amount, randomize=randomize, interact=interact, logger_callback=log_callback)

        elif task_type == "follow_user_following":
            usernames = config.get("usernames", [])
            interact = config.get("interact", False)
            res = await follow_user_following(page, rate_limiter, usernames, amount=amount, randomize=randomize, interact=interact, logger_callback=log_callback)

        elif task_type == "follow_by_list":
            followlist = config.get("followlist", [])
            times = config.get("times", 1)
            sleep_delay = config.get("sleep_delay", 3.0)
            interact = config.get("interact", False)
            res = await follow_by_list(page, rate_limiter, followlist, times=times, sleep_delay=sleep_delay, interact=interact, logger_callback=log_callback)

        elif task_type == "interact_by_users":
            usernames = config.get("usernames", [])
            res = await interact_by_users(page, rate_limiter, usernames, amount=amount, randomize=randomize, logger_callback=log_callback)

        elif task_type == "interact_user_followers":
            usernames = config.get("usernames", [])
            res = await interact_user_followers(page, rate_limiter, usernames, amount=amount, randomize=randomize, logger_callback=log_callback)

        elif task_type == "interact_user_following":
            usernames = config.get("usernames", [])
            res = await interact_user_following(page, rate_limiter, usernames, amount=amount, randomize=randomize, logger_callback=log_callback)

        elif task_type == "like_by_feed":
            res = await like_by_feed(page, rate_limiter, amount=amount, randomize=randomize, logger_callback=log_callback)

        elif task_type == "story_viewer":
            target_users = config.get("target_users", [])
            res = await story_viewer(page, rate_limiter, target_users, amount=amount, logger_callback=log_callback)

        elif task_type == "comment_by_tags":
            tags = config.get("tags", [])
            comments = config.get("comments", ["Awesome!", "Nice post!", "Great shot!"])
            res = await comment_by_tags(page, rate_limiter, tags, comments, amount=amount, logger_callback=log_callback)

        else:
            log_callback(f"Unknown task type: {task_type}")

        # Record detailed log entries into DB
        for item in res.get("details", []):
            task_log = TaskLog(
                task_id=task.id,
                action=item.get("action", task_type),
                target=item.get("target", ""),
                status=item.get("status", "completed"),
                details=item.get("details", "")
            )
            db.add(task_log)

        task.progress = res.get("success", 0)
        task.total_target = amount
        task.status = "completed"
        task.updated_at = datetime.utcnow()
        db.commit()

        log_callback(f"Task completed successfully. Actions done: {res.get('success', 0)}")
        await browser_mgr.close()

    except Exception as e:
        logger.error(f"Task execution failed for ID {task_id}: {e}")
        try:
            task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
            if task:
                task.status = "failed"
                task.log_output = (task.log_output or "") + f"\n[ERROR] Task failed: {str(e)}"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
