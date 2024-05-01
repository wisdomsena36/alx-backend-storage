#!/usr/bin/env python3
"""A module for implementing an expiring web cache and tracker."""
import redis
import requests
from functools import wraps, cached_property
from typing import Callable

REDIS_STORE = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    """Decorator to cache the output of fetched data and track requests."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function for caching the output."""
        key_count = f'count:{url}'
        key_result = f'result:{url}'
        REDIS_STORE.incr(key_count)
        result = REDIS_STORE.get(key_result)
        if result:
            return result.decode('utf-8')
        result = method(url)
        REDIS_STORE.set(key_count, 0)
        REDIS_STORE.setex(key_result, 10, result)
        return result
    return wrapper


@data_cacher
def get_page(url: str) -> str:
    """Returns the content of a URL after caching the request's response."""
    return requests.get(url).text

