# -*- encoding: utf-8 -*-
"""
Utils functions needed by Sniwi class to make them more readable
"""
import asyncio
from operator import itemgetter
from urllib.parse import urlparse


def timer(timer):
    """
    Decorator template for method's class,
    will run itself every `timer` seconds.
    Is asynchronous

    params:
        timer: (str) name of the timer define in the class
        flag: (asyncio.Event()) set before entering the function
              and clear afterward
    """
    def _timer(f):
        async def wrapper(self, *args, **kwargs):
            while True:
                await asyncio.sleep(1)
                await f(self, *args, **kwargs)
        return wrapper
    return _timer


def top_three(d):
    """
    Get the three best items sorted by value in a dict

    params:
        d: dict or defaultdict

    returns:
        list of three or less elements
    """
    sorted_gen_values = sorted(d.items(), key=itemgetter(1), reverse=True)
    return [f'{k}: {v}' for k, v in sorted_gen_values][:3]


def get_section(url):
    """
    Get section from url

    params:
        url: (str)
    returns:
        section (str) if found else None
    example:
        http://my.site.com/pages/other returns /pages
        http://my.site.com/pages?query returns /pages
        /pages/other returns /pages
    """
    if url:
        path = urlparse(url).path
        if path.count('/') == 0:
            return None
        if path.count('/') == 1:
            return path
        else:
            return '/'.join(path.split('/', 2)[:2])
    return None
