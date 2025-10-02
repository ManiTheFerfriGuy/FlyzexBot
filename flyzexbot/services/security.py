from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from cryptography.fernet import Fernet, InvalidToken


class EncryptionManager:
    def __init__(self, key: bytes) -> None:
        self._fernet = Fernet(key)
        self._lock = asyncio.Lock()

    async def encrypt(self, data: bytes) -> bytes:
        async with self._lock:
            return self._fernet.encrypt(data)

    async def decrypt(self, token: bytes) -> Optional[bytes]:
        async with self._lock:
            try:
                return self._fernet.decrypt(token)
            except InvalidToken:
                return None


class RateLimitGuard:
    def __init__(self, interval: float, burst: int) -> None:
        self._interval = interval
        self._burst = burst
        self._entries: Dict[int, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: int) -> bool:
        async with self._lock:
            bucket = self._entries[key]
            now = time.monotonic()
            while bucket and now - bucket[0] > self._interval:
                bucket.popleft()
            if len(bucket) >= self._burst:
                return False
            bucket.append(now)
            return True

