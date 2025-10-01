"""Security helpers for encryption and rate limiting."""
from __future__ import annotations

import asyncio
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


class EncryptionManager:
    """Handles encryption and decryption of the storage payload."""

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

