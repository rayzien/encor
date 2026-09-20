"""
Rate limiter and randomized human behavior delays.
"""

import random
import asyncio
import logging

logger = logging.getLogger("encor.rate_limiter")

class RateLimiter:
    def __init__(self, delay_min: float = 3.0, delay_max: float = 8.0):
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.action_counts = {}

    async def human_delay(self, multiplier: float = 1.0):
        """Wait for a randomized duration resembling human interactions."""
        base_delay = random.uniform(self.delay_min, self.delay_max) * multiplier
        jitter = random.uniform(-0.5, 1.5)
        total_delay = max(1.0, base_delay + jitter)
        logger.debug(f"Human delay sleeping for {total_delay:.2f}s...")
        await asyncio.sleep(total_delay)

    def record_action(self, action_name: str):
        """Track action count per session."""
        self.action_counts[action_name] = self.action_counts.get(action_name, 0) + 1

    def get_count(self, action_name: str) -> int:
        return self.action_counts.get(action_name, 0)
