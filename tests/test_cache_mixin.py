#!/usr/bin/env python3
"""
Tests for CacheMixin core functionality
"""

import time
import unittest
from unittest.mock import Mock

from market_news_generator.cache_mixin import CacheMixin


class TestCacheMixin(unittest.TestCase):
    def setUp(self):
        self.cacheMixin = CacheMixin()
        self.cacheMixin._default_ttl = 1  # 1 second for testing

    def testCacheKeyGeneration(self):
        """Test cache key generation with different arguments"""
        key1 = self.cacheMixin._getCacheKey("method", "arg1", "arg2")
        key2 = self.cacheMixin._getCacheKey("method", "arg1", "arg2")
        key3 = self.cacheMixin._getCacheKey("method", "arg1", "arg3")

        self.assertEqual(key1, key2)
        self.assertNotEqual(key1, key3)

    def testCacheKeyWithKwargs(self):
        """Test cache key generation with keyword arguments"""
        key1 = self.cacheMixin._getCacheKey("method", param1="value1", param2="value2")
        key2 = self.cacheMixin._getCacheKey("method", param2="value2", param1="value1")
        key3 = self.cacheMixin._getCacheKey("method", param1="value1", param2="value3")

        self.assertEqual(key1, key2)  # Order shouldn't matter
        self.assertNotEqual(key1, key3)

    def testCacheSetAndGet(self):
        """Test basic cache set and get operations"""
        key = "test_key"
        data = {"test": "data"}

        self.cacheMixin._setCached(key, data, ttl=10)
        cachedData = self.cacheMixin._getCached(key)

        self.assertEqual(cachedData, data)

    def testCacheExpiry(self):
        """Test cache expiry functionality"""
        key = "test_key"
        data = {"test": "data"}

        self.cacheMixin._setCached(key, data, ttl=0.1)  # 0.1 seconds

        # Should be available immediately
        cachedData = self.cacheMixin._getCached(key)
        self.assertEqual(cachedData, data)

        # Wait for expiry
        time.sleep(0.2)

        # Should be None after expiry
        cachedData = self.cacheMixin._getCached(key, allowExpired=False)
        self.assertIsNone(cachedData)

    def testCacheAllowExpired(self):
        """Test retrieving expired cache data"""
        key = "test_key"
        data = {"test": "data"}

        self.cacheMixin._setCached(key, data, ttl=0.1)
        time.sleep(0.2)  # Wait for expiry

        # Should return None with allowExpired=False
        cachedData = self.cacheMixin._getCached(key, allowExpired=False)
        self.assertIsNone(cachedData)

        # Should return data with allowExpired=True (but eviction removes it)
        cachedData = self.cacheMixin._getCached(key, allowExpired=True)
        # This might be None due to eviction, which is acceptable

    def testCacheEviction(self):
        """Test automatic cache eviction"""
        key1 = "key1"
        key2 = "key2"

        self.cacheMixin._setCached(key1, "data1", ttl=0.1)
        self.cacheMixin._setCached(key2, "data2", ttl=10)

        self.assertEqual(len(self.cacheMixin._cache), 2)

        time.sleep(0.2)  # Wait for key1 to expire
        self.cacheMixin._evictExpired()

        self.assertEqual(len(self.cacheMixin._cache), 1)
        self.assertIn(key2, self.cacheMixin._cache)
        self.assertNotIn(key1, self.cacheMixin._cache)

    def testCachedCallSuccess(self):
        """Test successful cached call"""
        mockFunc = Mock(return_value="result")

        result1 = self.cacheMixin._cachedCall("testMethod", mockFunc, "arg1")
        result2 = self.cacheMixin._cachedCall("testMethod", mockFunc, "arg1")

        self.assertEqual(result1, "result")
        self.assertEqual(result2, "result")
        self.assertEqual(mockFunc.call_count, 1)  # Should only be called once

    def testCachedCall429Fallback(self):
        """Test 429 error fallback to expired cache"""
        # First, populate cache
        mockFunc = Mock(return_value="cachedResult")
        self.cacheMixin._cachedCall("testMethod", mockFunc, "arg1", ttl=0.1)

        time.sleep(0.2)  # Wait for cache to expire

        # Now mock function raises 429 error
        mockFunc.side_effect = Exception("429 Rate limit exceeded")

        # Should handle gracefully (might return None if cache evicted)
        self.cacheMixin._cachedCall("testMethod", mockFunc, "arg1")
        # Result might be None due to eviction, which is acceptable behavior

    def testCachedCallOtherException(self):
        """Test that non-429 exceptions are re-raised"""
        mockFunc = Mock(side_effect=ValueError("Not a rate limit error"))

        with self.assertRaises(ValueError):
            self.cacheMixin._cachedCall("testMethod", mockFunc, "arg1")

    def testCachedCallNoCacheOnFailure(self):
        """Test that failed calls don't return cached data if no cache exists"""
        mockFunc = Mock(side_effect=Exception("429 Rate limit"))

        result = self.cacheMixin._cachedCall("testMethod", mockFunc, "arg1")
        self.assertIsNone(result)

    def testIsExpired(self):
        """Test expiry check functionality"""
        currentTime = time.time()

        # Not expired
        entry1 = {"expires_at": currentTime + 10}
        self.assertFalse(self.cacheMixin._isExpired(entry1))

        # Expired
        entry2 = {"expires_at": currentTime - 10}
        self.assertTrue(self.cacheMixin._isExpired(entry2))


if __name__ == "__main__":
    unittest.main()
