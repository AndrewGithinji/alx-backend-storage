#!/usr/bin/env python3
"""
    String Redis
"""
from uuid import uuid4
from typing import Union, Callable
from functools import wraps
import redis

def count_calls(method: Callable = None) -> Callable:
    """ Decorator count calls """
    name = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapper method """
        self._redis.incr(name)
        result = method(self, *args, **kwargs)
        return result

    return wrapper
