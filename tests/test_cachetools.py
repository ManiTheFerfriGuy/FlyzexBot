from cachetools import LRUCache


def test_lru_cache_pop_default_none_returns_none():
    cache = LRUCache(maxsize=2)
    assert cache.pop("missing", None) is None


def test_lru_cache_pop_default_value_returned_when_missing():
    cache = LRUCache(maxsize=2)
    assert cache.pop("missing", "fallback") == "fallback"
