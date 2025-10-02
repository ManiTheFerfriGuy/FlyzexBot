from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Tuple


class AnalyticsTracker:
    def __init__(self, flush_interval: float = 60.0) -> None:
        self._queue: asyncio.Queue[Tuple[str | None, float | None]] = asyncio.Queue()
        self._metrics: Dict[str, Dict[str, float]] = {}
        self._task: asyncio.Task[None] | None = None
        self._flush_interval = flush_interval
        self._logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return
        await self._queue.put((None, None))
        try:
            await self._task
        finally:
            self._task = None

    async def record(self, metric: str, value: float | None = None) -> None:
        await self._queue.put((metric, value))

    @asynccontextmanager
    async def track_time(self, metric: str) -> AsyncIterator[None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            await self.record(metric, elapsed)

    async def _run(self) -> None:
        next_flush = time.monotonic() + self._flush_interval
        try:
            while True:
                timeout = max(0.0, next_flush - time.monotonic())
                try:
                    metric, value = await asyncio.wait_for(self._queue.get(), timeout=timeout)
                except asyncio.TimeoutError:
                    await self._flush()
                    next_flush = time.monotonic() + self._flush_interval
                    continue
                if metric is None:
                    break
                async with self._lock:
                    bucket = self._metrics.setdefault(metric, {"count": 0.0, "total": 0.0, "max": 0.0})
                    bucket["count"] += 1.0
                    if value is not None:
                        bucket["total"] += value
                        bucket["max"] = max(bucket["max"], value)
                if time.monotonic() >= next_flush:
                    await self._flush()
                    next_flush = time.monotonic() + self._flush_interval
        except asyncio.CancelledError:
            raise
        finally:
            await self._flush()

    async def _flush(self) -> None:
        async with self._lock:
            if not self._metrics:
                return
            snapshot = {
                metric: {
                    "count": values["count"],
                    "avg": values["total"] / values["count"] if values["count"] else 0.0,
                    "max": values["max"],
                }
                for metric, values in self._metrics.items()
            }
            self._metrics.clear()
        self._logger.info("analytics_snapshot", extra={"metrics": snapshot})


class NullAnalytics:
    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def record(self, metric: str, value: float | None = None) -> None:
        return None

    @asynccontextmanager
    async def track_time(self, metric: str) -> AsyncIterator[None]:
        yield

