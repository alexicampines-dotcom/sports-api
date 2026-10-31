"""
Sistema de caché simple en memoria con TTL (Time-To-Live).
Permite responder en <5ms evitando llamadas repetitivas a la API externa.
"""
import time
import asyncio
from typing import Any, Optional, Dict, Tuple


class SimpleMemoryCache:
    def __init__(self, default_ttl: int = 60):
        self._cache: Dict[str, Tuple[float, int, Any]] = {}
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._cache:
                return None
            timestamp, ttl_val, data = self._cache[key]
            if time.time() - timestamp > ttl_val:
                del self._cache[key]
                return None
            return data

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        async with self._lock:
            ttl_val = ttl if ttl is not None else self._default_ttl
            self._cache[key] = (time.time(), ttl_val, value)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()


# Instancia global del caché
cache = SimpleMemoryCache(default_ttl=60)

