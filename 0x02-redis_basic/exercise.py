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


def call_history(method: Callable) -> Callable:
    """ Decorator call history """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapper function """
        input_str = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input_str)

        output = method(self, *args, **kwargs)
        output_str = str(output)
        self._redis.rpush(method.__qualname__ + ":outputs", output_str)

        return output

    return wrapper


def replay(func: Callable):
    """ Replay function """
    r = redis.Redis()
    func_name = func.__qualname__
    number_calls = r.get(func_name)

    try:
        number_calls = int(number_calls.decode('utf-8'))
    except Exception:
        number_calls = 0

    print(f'{func_name} was called {number_calls} times:')

    ins = r.lrange(func_name + ":inputs", 0, -1)
    outs = r.lrange(func_name + ":outputs", 0, -1)

    for cin, cout in zip(ins, outs):
        try:
            cin = cin.decode('utf-8')
        except Exception:
            cin = ""
        try:
            cout = cout.decode('utf-8')
        except Exception:
            cout = ""

        print(f'{func_name}(*{cin}) -> {cout}')


class Cache:
    """ Functionality Redis """

    def __init__(self):
        """ Constructor """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @replay
    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
            Store the cache
            Args:
                data: bring the information to store
            Return:
                Key or number uuid
        """
        key = str(uuid4())

        self._redis.set(key, data)

        return key


def get(self, key: str, fn: Callable = None) -> Union[str, bytes, int, float]:
    """
        Retrieve the value from the cache
        Args:
            key: Key to retrieve the value
            fn: Optional function to transform the value
        Return:
            Retrieved value
    """
    value = self._redis.get(key)

    if fn:
        return fn(value)

    return value


def get_str(self, key: str) -> str:
    """ Retrieve a string value from the cache """
    value = self._redis.get(key)

    if value is not None:
        return value.decode("utf-8")

    return ""


def get_int(self, key: str) -> int:
    """ Retrieve an integer value from the cache """
    value = self._redis.get(key)

    if value is not None:
        try:
            return int(value.decode('utf-8'))
        except ValueError:
            pass

    return 0