#!/usr/bin/env python3
"""
Cache mixin for handling rate limits and data expiry
"""

import time
from typing import Any, Dict, Optional


class CacheMixin:
    """Mixin to add caching with expiry and 429 fallback support"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 300  # 5 minutes default

    def _getCacheKey(self, methodName: str, *args, **kwargs) -> str:
        """Generate cache key from method and arguments"""
        keyParts = [methodName]
        keyParts.extend(str(arg) for arg in args)
        keyParts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return "|".join(keyParts)

    def _isExpired(self, cacheEntry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        return time.time() > cacheEntry["expires_at"]

    def _evictExpired(self):
        """Remove expired entries from cache"""
        currentTime = time.time()
        expiredKeys = [
            key
            for key, entry in self._cache.items()
            if currentTime > entry["expires_at"]
        ]
        for key in expiredKeys:
            del self._cache[key]

    def _getCached(self, cacheKey: str, allowExpired: bool = False) -> Optional[Any]:
        """Get cached value, optionally allowing expired data"""
        if not allowExpired:
            self._evictExpired()

        if cacheKey not in self._cache:
            return None

        entry = self._cache[cacheKey]

        if allowExpired or not self._isExpired(entry):
            return entry["data"]

        return None

    def _setCached(self, cacheKey: str, data: Any, ttl: Optional[int] = None) -> None:
        """Store data in cache with TTL"""
        if ttl is None:
            ttl = self._default_ttl

        self._cache[cacheKey] = {
            "data": data,
            "expires_at": time.time() + ttl,
            "created_at": time.time(),
        }

    def _cachedCall(
        self, methodName: str, methodFunc, *args, ttl: Optional[int] = None, **kwargs
    ) -> Any:
        """Execute method with caching and 429 fallback"""
        cacheKey = self._getCacheKey(methodName, *args, **kwargs)

        # Try to get fresh cached data first (but don't evict expired entries yet)
        if cacheKey in self._cache:
            entry = self._cache[cacheKey]
            if not self._isExpired(entry):
                return entry["data"]

        # Try to fetch new data
        try:
            result = methodFunc(*args, **kwargs)
            if result is not None:
                self._setCached(cacheKey, result, ttl)
                # Only evict expired entries after successful fetch
                self._evictExpired()
            return result  # Return result even if None
        except Exception as e:
            # Check if it's a rate limit error (429 or similar)
            errorStr = str(e).lower()
            if (
                "429" in errorStr
                or "rate limit exceeded" in errorStr
                or "too many requests" in errorStr
                or "rate limited" in errorStr
            ):
                # Return expired cache if available (don't evict first)
                if cacheKey in self._cache:
                    return self._cache[cacheKey]["data"]
                # No cache available, return None instead of raising
                return None
            # Re-raise other exceptions
            raise

        # No cached data available and fetch failed
        return None
